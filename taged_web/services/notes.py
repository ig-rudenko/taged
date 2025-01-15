import re
from datetime import datetime, timedelta
from typing import TypeVar

from django.conf import settings
from django.contrib.humanize.templatetags import humanize
from django.core.cache import cache
from django.http import Http404
from jwt import encode as jwt_encode, decode as jwt_decode, PyJWTError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from elasticsearch_control.cache import get_or_cache
from taged_web.es_index import T_Values, PostIndex
from taged_web.filters import notes_records_filter
from taged_web.models import User
from taged_web.repo.exc import NotFoundError
from taged_web.repo.notes import get_repository
from .cache_version import CacheVersion
from .signals import register
from .tags import get_unavailable_tags, add_tags_to_user_if_not_exist

_notes_base_cache_key = "notes"
_notes_count_cache_key = "notesCount"


def get_note_or_404(note_id: str, user: User, values: list[T_Values] | None = None) -> PostIndex:
    try:
        note = get_repository().get(id_=note_id, values=values)
    except NotFoundError:
        raise Http404()
    if set(get_unavailable_tags(user)) & set(note.tags_list):
        # Если нет такой записи, либо пользователь не имеет к ней доступа
        raise Http404()
    return note


@register("created_note", "deleted_note")
def change_notes_count_callback(**kwargs):
    """При создании или удалении записи, нужно обновить кэш."""
    CacheVersion(_notes_count_cache_key).increment_version()  # кол-во записей
    CacheVersion(_notes_base_cache_key).increment_version()  # Записи


@register("updated_note")
def update_note_callback(**kwargs):
    """При обновлении записи, нужно обновить только кэш записей, без их кол-ва."""
    CacheVersion(_notes_base_cache_key).increment_version()  # Записи


def get_notes_count(user: User) -> int:
    timeout = 60 * 10
    version = CacheVersion(_notes_count_cache_key).get_version()
    user_cache_key: str = f"{_notes_count_cache_key}:{user.username}"  # type: ignore

    total_count: int | None = cache.get(user_cache_key, default=None, version=version)

    if total_count is None:
        paginator = get_repository().filter(tags_off=get_unavailable_tags(user))
        total_count = paginator.count
        cache.set(user_cache_key, total_count, timeout, version=version)

    return total_count


def get_note_detail(note: PostIndex) -> dict:
    note_json_data = note.json()
    repository = get_repository()

    note_json_data["published_at"] = humanize.naturaltime(note_json_data["published_at"])
    note_json_data["files"] = [file.json() for file in repository.get_files(note.id)]
    return note_json_data


def update_note(note: PostIndex, title: str, content: str, tags: list[str], user: User) -> PostIndex:
    """
    Обновляем существующую в elasticsearch запись.
    Смотрим какие именно поля изменились и обновляем только их.
    """
    updated_fields: list[T_Values] = ["published_at"]
    note.published_at = datetime.now()

    if title != note.title:
        note.title = title
        updated_fields.append("title")
    if content != note.content:
        note.content = content
        note.preview_image = note.get_first_image_url(content)
        updated_fields += ["content", "preview_image"]
    if tags != note.tags_list:
        note.tags = tags  # type: ignore
        updated_fields.append("tags")
        add_tags_to_user_if_not_exist(tags, user)

    get_repository().update(note.id, note.json(), values=updated_fields)
    return note


def get_notes(search: str, tags_in: list[str], page: str, user: User) -> Response:
    cache_timeout = 60 * 5

    # Если не указана строка поиска, то сортируем по времени создания
    sorted_by: T_Values | None = None if search else "published_at"

    # Получает записи от Elasticsearch.
    paginator = get_repository().filter(
        tags_off=get_unavailable_tags(user),
        tags_in=tags_in,
        string=search,  # search_translate(search),
        sort=sorted_by,
        sort_desc=True,
        values=["title", "tags", "published_at", "preview_image"],
        convert_result=notes_records_filter,
    )

    if not search and not tags_in and page == "1":
        # Получаем записи из кэша или они будут созданы по функции
        records: list = get_or_cache(
            function=paginator.get_page,
            kwargs={"page": page},
            unique_name=f"{_notes_base_cache_key}:{user.username}",
            cache_timeout=cache_timeout,
            version=CacheVersion(_notes_base_cache_key).get_version(),
        )
    else:
        records = paginator.get_page(page)

    records = add_file_mark(records)
    records = humanize_datetime(records)

    return Response(
        {
            "records": records,
            "totalRecords": paginator.count,
            "paginator": {
                "maxPages": paginator.max_pages,
                "perPage": paginator.per_page,
                "currentPage": paginator.page,
            },
        }
    )


def search_translate(search: str) -> str:
    ru = "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё"
    eng = "qwertyuiop[]asdfghjkl;'zxcvbnm,./`WERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~"
    eng_ru_layout = dict(zip(map(ord, eng), ru))
    ru_eng_layout = dict(zip(map(ord, ru), eng))
    return (search + " " + search.translate(eng_ru_layout) + " " + search.translate(ru_eng_layout)).strip()


_N = TypeVar("_N", bound=dict)


def add_file_mark(objects: list[_N]) -> list[_N]:
    for post in objects:
        post["filesCount"] = 0
        # Проверяем, существуют ли у записей прикрепленные файлы.
        for file in (settings.MEDIA_ROOT / f'{post["id"]}').glob("*"):
            if not file.is_file() or re.search(r"_thumb_(small|large)\.[a-z]+$", file.name):
                continue
            post["filesCount"] += 1
    return objects


def humanize_datetime(objects: list[_N]) -> list[_N]:
    for post in objects:
        post["published_at"] = humanize.naturaltime(datetime.strptime(post["published_at"], "%Y-%m-%dT%X.%f"))
    return objects


def create_temp_link(note: PostIndex, minutes: int) -> str:
    """
    Создает временную ссылку на запись.
    """
    token = jwt_encode(
        {
            "id": note.id,
            "exp": (datetime.now() + timedelta(minutes=minutes)).timestamp(),
        },
        key=settings.SIMPLE_JWT["SIGNING_KEY"],
        algorithm=settings.SIMPLE_JWT["ALGORITHM"],
    )
    return f"/temp/{token}"


def get_note_from_temp_link(token: str) -> PostIndex:
    """
    Получает запись по временной ссылке.
    """
    try:
        payload = jwt_decode(
            token,
            key=settings.SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
        )
    except PyJWTError:
        raise ValidationError("Invalid token")

    exp: int | None = payload.get("exp", None)
    note_id: str | None = payload.get("id", None)

    if exp is None or note_id is None:
        raise ValidationError("Invalid token")
    if datetime.fromtimestamp(exp) < datetime.now():
        raise ValidationError("Ссылка истекла")

    try:
        note = get_repository().get(note_id)
    except NotFoundError:
        raise ValidationError("Запись не найдена")
    return note
