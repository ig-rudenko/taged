import re
from datetime import datetime
from typing import List

from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags import humanize
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from elasticsearch import exceptions as es_exceptions
from elasticsearch_control.cache import get_or_cache
from elasticsearch_control.decorators import api_elasticsearch_check_available
from taged_web.es_index import PostIndex
from taged_web.models import Tags


@login_required
@api_elasticsearch_check_available
def autocomplete(request):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.
    """
    try:
        titles = PostIndex.get_titles(
            string=request.GET.get("term"),
            unavailable_tags=request.user.unavailable_tags
        )
    except es_exceptions.ConnectionError:
        return JsonResponse([], status=500, safe=False)
    else:
        return JsonResponse(titles, status=200, safe=False)


@login_required
@api_elasticsearch_check_available
def notes_count(request):
    """Получает кол-во записей от Elasticsearch"""
    paginator = PostIndex.filter(
        tags_off=request.user.unavailable_tags,
    )
    return JsonResponse({"totalCount": paginator.count}, status=200)


@method_decorator(login_required, name="dispatch")
@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesListAPIView(View):
    def get(self, request):
        search = request.GET.get("search", "")
        tags_in = request.GET.getlist("tags-in", [])
        print(tags_in)
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
                unique_name=f"last_updated_posts:{request.user.username}",
                cache_period=1,
            )
        else:
            records = paginator.get_page(page)

        self.add_file_mark(records)
        self.add_preview_image(records)
        self.remove_content(records)
        self.humanize_datetime(records)

        return JsonResponse(
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
    def add_file_mark(objects: List[dict]):
        for post in objects:
            post["filesCount"] = 0
            # Проверяем, существуют ли у записей прикрепленные файлы.
            for file in (settings.MEDIA_ROOT / f'{post["id"]}').glob("*"):
                if file.is_file():
                    post["filesCount"] += 1

    @staticmethod
    def add_preview_image(objects: List[dict]):
        for post in objects:
            post["previewImage"] = None
            first_image = re.search('<img .*?src="(\S+)"', post["content"])
            if first_image:
                post["previewImage"] = first_image.group(1)

    @staticmethod
    def remove_content(objects: List[dict], width: int = 70):
        for post in objects:
            del post["content"]

    @staticmethod
    def humanize_datetime(objects: List[dict], width: int = 70):
        for post in objects:
            post["published_at"] = humanize.naturaltime(
                datetime.strptime(
                    post["published_at"],
                    "%Y-%m-%dT%X.%f",
                )
            )


@login_required
def tags_list(request):
    tags = request.user.get_tags()
    return JsonResponse(list(tags), status=200, safe=False)


@login_required
@api_elasticsearch_check_available
def note_view(request, note_id: str):
    note = PostIndex.get(id_=note_id)
    user_unavailable_tags = set(request.user.unavailable_tags)

    if note is None or user_unavailable_tags & set(note.tags_list):
        # Если нет такой записи, либо пользователь не имеет к ней доступа
        raise Http404()

    note_json_data = note.json()
    note_json_data["published_at"] = humanize.naturaltime(
        note_json_data["published_at"]
    )
    note_json_data["files"] = [file.json() for file in note.get_files()]
    return JsonResponse(note_json_data, status=200)
