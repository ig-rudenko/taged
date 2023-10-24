import re
from datetime import datetime

from django.contrib.humanize.templatetags import humanize
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.core.files.uploadedfile import UploadedFile
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from elasticsearch import exceptions as es_exceptions

from elasticsearch_control.cache import get_or_cache
from elasticsearch_control.decorators import api_elasticsearch_check_available
from taged_web.api.permissions import NotePermission
from taged_web.api.serializers import (
    NoteSerializerNoTagsValidation,
    NoteSerializerTagsValidation,
)
from taged_web.es_index import PostIndex, T_Values
from taged_web.image_decoder import ReplaceImagesInHtml
from taged_web.models import User, Tags


def get_note_or_404(
    note_id: str, user: User, values: list[T_Values] = None
) -> PostIndex:
    note = PostIndex.get(id_=note_id, values=values)
    if note is None or set(user.unavailable_tags) & set(note.tags_list):
        # Если нет такой записи, либо пользователь не имеет к ней доступа
        raise Http404()
    return note


def clear_cache() -> None:
    all_usernames = User.objects.all().values_list("username", flat=True)
    keys = [f"{NotesCount.cache_key}.{username}" for username in all_usernames]
    keys += [
        f"{NotesListCreateAPIView.cache_key}.{username}" for username in all_usernames
    ]
    cache.delete_many(keys)


def add_tags_to_user_if_not_exist(tags_names: list[str], by_user: User) -> None:
    """
    Принимает строку названий тегов и создает отсутствующие из них.
    Затем добавляет их к пользователю.
    """
    new_tags = []
    for tag_name in tags_names:
        tag, created = Tags.objects.get_or_create(tag_name=tag_name)
        if created:
            new_tags.append(tag)
    by_user.tags_set.add(*new_tags)


class ListUserPermissions(GenericAPIView):
    def get(self, *args, **kwargs):
        # Получаем все права пользователей, которые связаны с данным приложением `taged_web`
        taged_web_permissions = filter(
            lambda x: x.startswith("taged_web"),
            self.request.user.get_all_permissions(),
        )
        # Приводим права "taged_web.update_note" к виду "update_note"
        permissions = map(lambda p: p.split(".")[1], taged_web_permissions)

        return Response(sorted(permissions))


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class AutocompleteAPIView(GenericAPIView):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.
    """

    def get(self, request: Request):
        try:
            titles = PostIndex.get_titles(
                string=request.GET.get("term"),
                unavailable_tags=request.user.unavailable_tags,
            )
        except es_exceptions.ConnectionError:
            return Response([], status=500)
        else:
            return Response(titles)


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesCount(GenericAPIView):
    """Получает кол-во записей от Elasticsearch"""

    cache_key = "NotesCount"
    cache_timeout = 60 * 10

    def get(self, request: Request):
        total_count = cache.get(f"{self.cache_key}.{request.user.username}")

        if not total_count:
            paginator = PostIndex.filter(
                tags_off=request.user.unavailable_tags,
            )
            total_count = paginator.count
            cache.set(
                f"{self.cache_key}.{request.user.username}",
                total_count,
                self.cache_timeout,
            )

        return Response({"totalCount": total_count})


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesListCreateAPIView(GenericAPIView):
    permission_classes = [NotePermission]
    cache_key = "last_updated_posts"
    cache_timeout = 60 * 10

    def get_serializer_class(self):
        """
        Если пользователь имеет право создавать новые теги, то вернется сериализатор,
        которых не проверяет полученные теги на их существование в базе
        :return:
        """
        if self.request.user.has_perms(["taged_web.add_tags"]):
            return NoteSerializerNoTagsValidation
        return NoteSerializerTagsValidation

    def get(self, request: Request):
        search = request.GET.get("search", "")
        tags_in = request.GET.getlist("tags-in", [])
        page = request.GET.get("page", "1")

        # Если не указана строка поиска, то сортируем по времени создания
        sorted_by = None if search else "published_at"

        # Получает записи от Elasticsearch.
        paginator = PostIndex.filter(
            tags_off=request.user.unavailable_tags,
            tags_in=tags_in,
            string=search,
            sort=sorted_by,
            sort_desc=True,
        )

        if not search and not tags_in and page == "1":
            # Получаем записи из кэша или они будут созданы по функции
            records = get_or_cache(
                function=paginator.get_page,
                kwargs={"page": page},
                unique_name=f"{self.cache_key}:{request.user.username}",
                cache_period=1,
            )
        else:
            records = paginator.get_page(page)

        self.add_file_mark(records)
        self.add_preview_image(records)
        self.remove_content(records)
        self.humanize_datetime(records)

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

    @staticmethod
    def add_file_mark(objects: list[dict]):
        for post in objects:
            post["filesCount"] = 0
            # Проверяем, существуют ли у записей прикрепленные файлы.
            for file in (settings.MEDIA_ROOT / f'{post["id"]}').glob("*"):
                if file.is_file():
                    post["filesCount"] += 1

    @staticmethod
    def add_preview_image(objects: list[dict]):
        for post in objects:
            post["previewImage"] = None
            first_image = re.search('<img .*?src="(\S+)"', post["content"])
            if first_image:
                post["previewImage"] = first_image.group(1)

    @staticmethod
    def remove_content(objects: list[dict], width: int = 70):
        for post in objects:
            del post["content"]

    @staticmethod
    def humanize_datetime(objects: list[dict], width: int = 70):
        for post in objects:
            post["published_at"] = humanize.naturaltime(
                datetime.strptime(
                    post["published_at"],
                    "%Y-%m-%dT%X.%f",
                )
            )

    def post(self, request: Request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "title": serializer.validated_data["title"],
            "tags": serializer.validated_data["tags"],
            "content": serializer.validated_data["content"],
        }

        add_tags_to_user_if_not_exist(data["tags"], request.user)

        # Ищем закодированные изображения (base64) в содержимом заметки.
        image_formatter = ReplaceImagesInHtml(data["content"])

        if not image_formatter.has_base64_encoded_images:
            # У содержимого заметки нет изображений закодированных с помощью base64,
            # то сохраняем как есть
            post = PostIndex.create(**data)
        else:
            # Если есть закодированные изображения.
            # Создаем запись в базе данных elasticsearch без содержимого.
            data["content"] = ""
            # Его мы обновим далее, заменив base64 изображения на ссылки.
            post = PostIndex.create(**data)

            # Сохраняем закодированные изображения как файлы
            # и заменяем у них атрибут src на ссылку файла.
            image_formatter.save_images_and_update_src(
                image_prefix="image",
                folder=f"{post.id}/content_images",
            )
            # Обновляем содержимое с измененными изображениями
            post.content = image_formatter.html
            post.save(values=["content"])

        # Обнуляем кеш
        clear_cache()

        return Response({"id": post.id}, status=201)

    @staticmethod
    def clear_cache():
        keys = [
            f"{NotesCount.cache_key}.{username}"
            for username in User.objects.all().values_list("username", flat=True)
        ]
        cache.delete_many(keys)


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NoteDetailUpdateAPIView(GenericAPIView):
    permission_classes = [NotePermission]

    def get_serializer_class(self):
        """
        Если пользователь имеет право создавать новые теги, то вернется сериализатор,
        которых не проверяет полученные теги на их существование в базе
        :return:
        """
        if self.request.user.has_perms(["taged_web.add_tags"]):
            return NoteSerializerNoTagsValidation
        return NoteSerializerTagsValidation

    def get(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, request.user)
        note_json_data = note.json()

        note_json_data["published_at"] = humanize.naturaltime(
            note_json_data["published_at"]
        )
        note_json_data["files"] = [file.json() for file in note.get_files()]
        return Response(note_json_data)

    def put(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, request.user)
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(note, serializer)
        cache.delete("last_updated_posts")
        return Response({"id": note.id, "published_at": note.published_at})

    def delete(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, request.user)
        note.delete()
        clear_cache()
        return Response(status=204)

    def perform_update(self, note: PostIndex, serializer):
        """
        Обновляем существующую в elasticsearch запись.
        Смотрим какие именно поля изменились и обновляем только их.
        """
        updated_fields: list[T_Values] = ["published_at"]
        note.published_at = datetime.now()

        new_title = serializer.validated_data["title"]
        new_content = serializer.validated_data["content"]
        new_tags = serializer.validated_data["tags"]

        if new_title != note.title:
            note.title = new_title
            updated_fields.append("title")
        if new_content != note.content:
            # Ищем закодированные изображения (base64) в содержимом заметки.
            image_formatter = ReplaceImagesInHtml(new_content)
            if image_formatter.has_base64_encoded_images:
                # Сохраняем закодированные изображения как файлы и заменяем у них атрибут src на ссылку файла.
                image_formatter.save_images_and_update_src(
                    image_prefix="image", folder=f"{note.id}/content_images"
                )
                # Обновляем содержимое с измененными изображениями
                new_content = image_formatter.html

            note.content = new_content
            updated_fields.append("content")
        if new_tags != note.tags_list:
            note.tags = new_tags
            updated_fields.append("tags")
            add_tags_to_user_if_not_exist(new_tags, self.request.user)

        note.save(values=updated_fields)


class NoteFilesListCreateAPIView(GenericAPIView):
    def get(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, request.user, values=["tags"])
        return Response([file.json() for file in note.get_files()])

    def post(self, request: Request, note_id: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи
        get_note_or_404(note_id, request.user, values=["tags"])

        files: dict[str, list[UploadedFile]] = dict(request.FILES)
        if files and files.get("files"):
            (settings.MEDIA_ROOT / note_id).mkdir(parents=True, exist_ok=True)
            # Создаем папку для текущей заметки
            for uploaded_file in files["files"]:  # Для каждого файла
                with open(
                    settings.MEDIA_ROOT / f"{note_id}/{uploaded_file.name}", "wb+"
                ) as file:
                    for chunk_ in uploaded_file.chunks():
                        file.write(chunk_)  # Записываем файл
        return Response({"filesCount": len(files)}, status=201)


class NoteFileDetailDeleteAPIView(GenericAPIView):
    def get(self, request: Request, note_id: str, file_name: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи, чтобы удалить её файл
        get_note_or_404(note_id, request.user, values=["tags"])

        # Отправляем пользователю файл
        file_path = settings.MEDIA_ROOT / note_id / file_name
        if file_path.exists():
            with file_path.open("rb") as file:
                response = HttpResponse(
                    file.read(), content_type="application/vnd.ms-excel"
                )
            response["Content-Disposition"] = f"inline; filename={file_name}"
            return response
        else:
            raise Http404()

    def delete(self, request: Request, note_id: str, file_name: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи, чтобы удалить её файл
        get_note_or_404(note_id, request.user, values=["tags"])

        file_path = settings.MEDIA_ROOT / note_id / file_name
        file_path.unlink()
        return Response(status=204)


class TagsListAPIView(ListAPIView):
    def get(self, *args, **kwargs):
        return Response(self.request.user.get_tags())
