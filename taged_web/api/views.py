import re
from datetime import datetime
from typing import List

from django.contrib.humanize.templatetags import humanize
from django.core.cache import cache
from django.http import Http404
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.generics import ListAPIView, GenericAPIView

from elasticsearch import exceptions as es_exceptions
from rest_framework.response import Response

from elasticsearch_control.cache import get_or_cache
from elasticsearch_control.decorators import api_elasticsearch_check_available
from taged_web.api.serializers import NoteSerializer
from taged_web.es_index import PostIndex
from taged_web.image_decoder import ReplaceImagesInHtml


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class AutocompleteAPIView(GenericAPIView):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.
    """

    def get(self, request):
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

    def get(self, request):
        paginator = PostIndex.filter(
            tags_off=request.user.unavailable_tags,
        )
        return Response({"totalCount": paginator.count})


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesListCreateAPIView(GenericAPIView):
    def get(self, request):
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
                unique_name=f"last_updated_posts:{request.user.username}",
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

    def post(self, request):
        serializer = NoteSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "title": serializer.validated_data["title"],
            "tags": serializer.validated_data["tags"],
            "content": serializer.validated_data["content"],
        }

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
        cache.delete("all_posts_count")
        cache.delete("last_updated_posts")

        return Response({"id": post.id}, status=201)


class NoteFilesAPIView(GenericAPIView):
    def post(self, request, note_id: str):
        files = dict(request.FILES)
        if files:
            (settings.MEDIA_ROOT / note_id).mkdir(parents=True, exist_ok=True)
            # Создаем папку для текущей заметки
            for uploaded_file in files["files"]:  # Для каждого файла
                with open(
                    settings.MEDIA_ROOT / f"{note_id}/{uploaded_file.name}", "wb+"
                ) as file:
                    for chunk_ in uploaded_file.chunks():
                        file.write(chunk_)  # Записываем файл
        return Response({"filesCount": len(files)}, status=201)


class TagsListAPIView(ListAPIView):
    def get(self, *args, **kwargs):
        return Response(self.request.user.get_tags())


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NoteAPIView(GenericAPIView):
    def get(self, request, note_id: str):
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
        return Response(note_json_data)
