import re
import random
import shutil

from datetime import datetime

from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
    Http404,
    HttpResponseNotAllowed,
)
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test

from elasticsearch import exceptions as es_exceptions

from taged.elasticsearch_control import (
    ElasticsearchConnect,
    elasticsearch_check_available,
)
from taged_web.models import Tags
from taged.settings import MEDIA_ROOT
from .image_decoder import ReplaceImagesInHtml
from .forms import PostForm


def icon_path(file: str):
    """
    Если расширение файла есть в списке расширений, вернуть значок для этого расширения

    :param file: Имя файла, который вы хотите отобразить
    :return: Путь к значку для типа файла
    """

    if re.match(r".+\.(docx?|rtf)$", file):
        icon = "docx.png"
    elif re.match(r".+\.xls[xm]?$", file):
        icon = "xlsx.png"
    elif re.match(r".+\.pdf$", file):
        icon = "pdf.png"
    elif re.match(r".+\.(txt|log)$", file):
        icon = "txt.png"
    elif re.match(r".+\.(drawio)$", file):
        icon = "drawio.png"
    elif re.match(r".+\.xml$", file):
        icon = "xml.png"
    elif re.match(r".+\.vsdx?$", file):
        icon = "visio.png"
    elif re.match(r".+\.(rar|7z|zip|tar[.gz]|iso)$", file):
        icon = "archive.png"
    elif re.match(r".+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$", file):
        icon = "img.png"
    else:
        icon = "file.png"

    # Возврат пути к иконке
    return "images/icons/" + icon


@login_required
def autocomplete(request):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.

    :param request: Объект запроса.
    :return: Список заголовков.
    """

    # Подключение к серверу elasticsearch.
    elastic_search = ElasticsearchConnect()
    try:
        titles = elastic_search.get_titles(string=request.GET.get("term"))
    except es_exceptions.ConnectionError:
        return JsonResponse({"data": None}, status=500)

    return JsonResponse({"data": titles})


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class HomeView(View):
    def get(self, request):
        elastic_search = ElasticsearchConnect()

        tags_in = request.GET.getlist("tags-in", [])
        tags_off = request.GET.getlist("tags-off", [])
        search_str = request.GET.get("search", "")

        # Проверка, является ли пользователь суперпользователем или нет.
        # Если пользователь является суперпользователем, он вернет все теги.
        # Если пользователь не является суперпользователем, он вернет теги, связанные с пользователем.
        user_tags = (
            Tags.objects.all().values("tag_name")
            if request.user.is_superuser
            else Tags.objects.filter(user=request.user).values("tag_name")
        )
        # Создание списка тегов доступных тегов
        available_tags = [t["tag_name"] for t in user_tags]
        data = []
        posts_count = None
        query_limiter = None

        # Проверка того, является ли метод запроса GET и является ли пользователь суперпользователем. Если оба условия
        # выполняются, он получает последние опубликованные сообщения от Elasticsearch.
        if not tags_in and not tags_off and not search_str:

            if request.user.is_superuser:
                # Просмотр последних статей доступен только суперпользователю

                # Проверяем, есть ли в кеше last_updated_posts, и если да, то используем его
                data = cache.get("last_updated_posts")
                if not data:
                    # Если нет, то вычисляем
                    data = elastic_search.get_last_published(index="company", limit=6)
                    # Установка кеша для last_updated_posts на значение data на 600 секунд.
                    cache.set("last_updated_posts", data, 600)

                # Проверяем, есть ли в кеше all_posts_count, и если да, то используем его
                posts_count = cache.get("all_posts_count")
                if not posts_count:
                    # Если нет, то вычисляем
                    posts_count = elastic_search.query_count("company")
                    # Установка кеша для all_posts_count на значение posts_count на 600 секунд.
                    cache.set("all_posts_count", posts_count, 600)

        else:
            # Проверка, ввел ли пользователь поисковый запрос или теги.
            # Если нет, он перенаправляет пользователя на домашнюю страницу.
            if (
                not search_str  # Если (нет поиска по слову)
                and not tags_in  # и (нет тегов)
                or set(tags_in or set())  # или (теги содержат запрещенные)
                - set(available_tags)  # (определяем разностью)
            ):
                return HttpResponseRedirect("/")

            # Поиск постов в базе данных elasticsearch.
            query_limiter = elastic_search.find_posts(
                string=search_str,
                tags_in=tags_in,
                tags_off=tags_off,
            )
            data = query_limiter.get_page(request.GET.get("page"))
            posts_count = query_limiter.count

        self.add_file_mark(data)
        tags_in = self.mark_selected_tags(tags_in, available_tags)
        tags_off = self.mark_selected_tags(tags_off, available_tags)

        # Отрисовка страницы home.html с данными из базы данных.
        return render(
            request,
            "home.html",
            {
                "pagination": query_limiter,
                "posts_count": posts_count,
                "page_name": "notes-list",
                "data": data,
                "tags_in": tags_in,
                "tags_off": tags_off,
                "image": f"images/cat{random.randint(0, 9)}.gif",
            },
        )

    @staticmethod
    def add_file_mark(objects: list):
        for post in objects:
            # Проверяем, существуют ли у записей прикрепленные файлы.
            for file in (MEDIA_ROOT / f'{post["id"]}').glob("*"):
                if file.is_file():
                    post["files"] = True
                    break  # Если нашли файл, прекращаем поиск
            else:
                # Если не нашли файлы
                post["files"] = False

    @staticmethod
    def mark_selected_tags(selected_tags, available_tags):
        if not selected_tags:
            tags_ = [{"name": tag, "checked": False} for tag in available_tags]
        else:
            tags_ = [
                {
                    "name": tag,
                    "checked": tag in selected_tags,
                }
                for tag in available_tags
            ]
        return sorted(tags_, key=lambda x: x["name"].lower())  # Сортируем по алфавиту


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class EditPostView(View):
    """
    Редактирование существующей записи
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Подключаемся к elasticsearch
        self.elasticsearch = ElasticsearchConnect()
        self.available_tags = []

    def set_available_tags(self):
        """
        ## Если пользователь является суперпользователем, то значение ```self.available_tags```
         будет содержать все теги в базе данных, в противном случае - только доступные пользователю.
        """

        tags_qs = (
            Tags.objects.all()
            if self.request.user.is_superuser
            else self.request.user.tags_set.all()
        )
        self.available_tags = [t.tag_name for t in tags_qs]

    def get_note(self, note_id: str) -> dict:
        """
        ## Возвращаем заметку по её ```note_id``` или вызываем исключение Http404.
        """

        try:
            # Получаем запись по ID
            res = self.elasticsearch.get(index="company", id=note_id)["_source"]
            if isinstance(res["tags"], str):
                res["tags"] = [res["tags"]]  # Переводим теги в список
        except es_exceptions.NotFoundError:
            # Данный ID не существует
            raise Http404()
        else:
            return res

    def get_files(self, note_id: str) -> list:
        """
        ## Возвращаем список файлов, которые прикреплены к заметке

        :return: [{ "name": file_name, "icon": icon_path }, ...]
        """

        files = []
        # Если существует папка для данного post_id и в ней есть файлы
        for f in (MEDIA_ROOT / note_id).glob("*"):
            if f.is_file():
                # Добавляем имя файла + иконку в список
                files.append({"name": f.name, "icon": icon_path(f.name)})
        return files

    def get(self, request, note_id: str):

        res = self.get_note(note_id)
        self.set_available_tags()

        # Прикрепленные файлы
        res["files"] = self.get_files(note_id)
        res["post_id"] = note_id
        res["page_name"] = "note-edit"

        # Определяем, какие теги существуют в посте из разрешенных для пользователя и отмечаем их как checked
        res["tags"] = [
            {
                "name": tag,
                "checked": tag in res["tags"],
            }
            for tag in self.available_tags
        ]

        # Форма для пользователя с начальными данными
        res["form"] = PostForm(
            {
                "title": res["title"],
                "input": res["content"],
                "tags_checked": res["tags"],
            }
        )
        return render(request, "edit_post.html", res)

    def post(self, request, note_id: str):
        user_form = PostForm(request.POST)
        files = self.get_files(note_id)
        self.set_available_tags()

        if user_form.is_valid():  # Если данные были введены верно

            res = self.get_note(note_id)
            res["post_id"] = note_id
            res["page_name"] = "note-edit"

            # Список тегов, которые будут обновлены.
            # Состоят из тегов, которые были у записи, но недоступные для пользователя
            tags_to_save = [t for t in res["tags"] if t not in self.available_tags]
            # Плюс те, что он указал явно
            tags_to_save += request.POST.getlist("tags_checked")

            image_formatter = ReplaceImagesInHtml(user_form.cleaned_data["input"])
            # Сохраняем закодированные изображения как файлы
            # и заменяем у них атрибут src на ссылку файла.
            image_formatter.save_images_and_update_src(
                image_prefix="image",
                folder=f"{note_id}/content_images",
            )

            # Обновляем существующую в elasticsearch запись
            self.elasticsearch.update_post(
                "company",
                {
                    "content": image_formatter.html,
                    "published_at": datetime.now(),
                    "tags": tags_to_save,
                    "title": user_form.cleaned_data["title"],
                },
                id_=note_id,
            )

            cache.delete("all_posts_count")
            cache.delete("last_updated_posts")

            for f in (MEDIA_ROOT / note_id).glob("*"):
                if f.is_dir():
                    continue
                # Смотрим все прикрепленные файлы
                if not request.POST.get(f"checkbox_{f.name}"):
                    # Если пользователь отключил данный файл
                    f.unlink()  # Удаляем

            # Создаем папку для файлов
            (MEDIA_ROOT / note_id).mkdir(parents=True, exist_ok=True)

            if request.FILES.get("files"):  # Если пользователь добавил файлы
                for uploaded_file in request.FILES.getlist("files"):
                    # Для каждого файла
                    with open(MEDIA_ROOT / note_id / uploaded_file.name, "wb+") as file:
                        for chunk_ in uploaded_file.chunks():
                            file.write(chunk_)  # Записываем файл

            # Перенаправляем на обновленную запись
            return HttpResponseRedirect(
                reverse("note-show", kwargs={"note_id": note_id})
            )

        else:
            # Если не все поля были указаны.
            # Отправляем данные, которые были введены
            res = {
                "tags": [
                    {
                        "name": tag,
                        "checked": tag in request.POST.getlist("tags_checked", []),
                    }
                    for tag in self.available_tags
                ],
                "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                "files": files,
                "form": user_form,
                "page_name": "note-edit",
            }

        return render(request, "edit_post.html", res)


@login_required
@elasticsearch_check_available
def download_file(request, note_id: str, file_name: str):
    # Отправляем пользователю файл
    file_path = MEDIA_ROOT / note_id / file_name
    if file_path.exists():
        with file_path.open("rb") as file:
            response = HttpResponse(
                file.read(), content_type="application/vnd.ms-excel"
            )
        response["Content-Disposition"] = f"inline; filename={file_name}"
        return response


@login_required
@elasticsearch_check_available
def show_post(request, note_id: str):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param note_id: ID записи в elasticsearch
    :return:
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        # Получаем запись по ID
        res = elastic_search.get(index="company", id=note_id)["_source"]
        # Если имеется всего один тег, то он имеет тип str, переводим его в list
        if isinstance(res["tags"], str):
            res["tags"] = [res["tags"]]
    except es_exceptions.NotFoundError:
        raise Http404()

    res["post_id"] = note_id

    # 2021-10-13T14:58:05.866799
    res["published_at"] = datetime.strptime(
        res["published_at"][:19], "%Y-%m-%dT%H:%M:%S"
    )

    res["page_name"] = "note-show"

    res["files"] = []
    # Проверяем, существует ли каталог и есть ли в нем какие-либо файлы.
    for file in (MEDIA_ROOT / note_id).glob("*"):
        if file.is_dir():
            continue
        # Добавление файлов в текущем каталоге в список файлов.
        res["files"].append({"name": file.name, "icon": icon_path(file.name)})

    return render(request, "post.html", res)


@login_required
@elasticsearch_check_available
def pre_show_post(request, post_id):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        # Получаем запись по ID
        res = elastic_search.get(index="company", id=post_id)["_source"]
        return JsonResponse({"post": res["content"]})

    except es_exceptions.NotFoundError:
        return JsonResponse({"error": "not found"})


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class CreatePostView(View):
    """
    Создаем новую запись
    """

    @staticmethod
    def post(request):
        user_form = PostForm(request.POST)  # Заполняем форму

        available_tags = (
            [t.tag_name for t in Tags.objects.all()]
            if request.user.is_superuser
            else [t.tag_name for t in Tags.objects.filter(user=request.user)]
        )

        if user_form.is_valid():  # Проверяем форму

            # Данные для сохранения
            post_data = {
                "content": user_form.cleaned_data["input"],
                "published_at": datetime.now(),
                "tags": request.POST.getlist("tags_checked"),
                "title": user_form.cleaned_data["title"],
            }

            # Подключение к серверу elasticsearch.
            elastic_search = ElasticsearchConnect()

            # Ищем закодированные изображения (base64) в содержимом заметки.
            image_formatter = ReplaceImagesInHtml(user_form.cleaned_data["input"])

            # Если есть закодированные изображения
            if image_formatter.has_base64_encoded_images:

                # Создаем запись в базе данных elasticsearch без содержимого.
                post_data["content"] = ""
                # Его мы обновим далее, заменив base64 изображения на ссылки.
                res = elastic_search.create_post("company", post_data)

                # Сохраняем закодированные изображения как файлы
                # и заменяем у них атрибут src на ссылку файла.
                image_formatter.save_images_and_update_src(
                    image_prefix="image",
                    folder=f'{res["_id"]}/content_images',
                )
                # Обновляем содержимое с измененными изображениями
                elastic_search.update_post(
                    index_name="company",
                    record={"content": image_formatter.html},
                    id_=res["_id"],
                )

            else:
                # У содержимого заметки нет изображений закодированных с помощью base64,
                # то сохраняем как есть
                res = elastic_search.create_post("company", post_data)

            if res.get("_id") and request.FILES.get("files"):
                (MEDIA_ROOT / f"{res['_id']}").mkdir(parents=True, exist_ok=True)
                # Создаем папку для текущей заметки
                for uploaded_file in dict(request.FILES)["files"]:  # Для каждого файла
                    with open(
                        MEDIA_ROOT / f'{res["_id"]}/{uploaded_file.name}', "wb+"
                    ) as file:
                        for chunk_ in uploaded_file.chunks():
                            file.write(chunk_)  # Записываем файл

            # Обнуляем кеш
            cache.delete("all_posts_count")
            cache.delete("last_updated_posts")

            return HttpResponseRedirect(
                reverse("note-show", kwargs={"note_id": res["_id"]})
            )

        else:
            # Выбранные теги
            tags_checked = dict(request.POST).get("tags_checked") or []

            # Если не все поля были указаны
            return render(
                request,
                "edit_post.html",
                {
                    "tags": [
                        {"name": t, "checked": True if t in tags_checked else False}
                        for t in available_tags
                    ],
                    "page_name": "note-create",
                    "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                    "form": user_form,
                },
            )

    @staticmethod
    def get(request):

        user_form = PostForm()  # Создаем форму

        available_tags = (
            [t.tag_name for t in Tags.objects.all()]
            if request.user.is_superuser
            else [t.tag_name for t in Tags.objects.filter(user=request.user)]
        )

        tags_ = sorted(
            [{"name": t, "cheched": False} for t in available_tags],
            key=lambda x: x["name"].lower(),  # Сортируем по алфавиту
        )  # Если новая запись, то все теги изначально отключены

        # Клонируем заметку
        if request.GET.get("cl"):
            elastic_search = ElasticsearchConnect()
            try:
                res = elastic_search.get(index="company", id=request.GET.get("cl"))[
                    "_source"
                ]  # Получаем запись по ID
                # Если имеется всего один тег, то он имеет тип str, переводим его в list
                if isinstance(res["tags"], str):
                    res["tags"] = [res["tags"]]

                # Только разрешенные теги добавятся в клонированную заметку
                res["tags"] = set(res["tags"]) & set(available_tags)
                res["input"] = res["content"]
                # Добавляем в конце заголовка приписку (копия)
                res["title"] += " (копия)"

                user_form = PostForm(res)

                tags_ = [
                    {"name": t, "checked": True if t in res["tags"] else False}
                    for t in available_tags
                ]
            except es_exceptions.NotFoundError:
                pass

        return render(
            request,
            "edit_post.html",
            {
                "tags": tags_,
                "page_name": "note-create",
                "superuser": request.user.is_superuser,
                "form": user_form,
            },
        )


@login_required
@elasticsearch_check_available
def delete_post(request, note_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["post"])

    # Смотрим разрешенные теги для данного пользователя
    available_tags = (
        [t.tag_name for t in Tags.objects.all()]
        if request.user.is_superuser
        else [
            t.tag_name
            for t in Tags.objects.filter(user__username=request.user.username)
        ]
    )

    # Подключаемся к Elasticsearch
    elastic_search = ElasticsearchConnect()

    # Ищем пост по его ID
    post = elastic_search.search(
        index="company",
        _source=["_id", "tags"],
        query={
            "simple_query_string": {
                "query": note_id,
                "fields": ["_id"],
            }
        },
    )
    if post["_shards"]["successful"]:  # Если нашли
        post_tags = post["hits"]["hits"][0]["_source"]["tags"]  # Смотрим его теги
    else:
        raise Http404()

    if set(post_tags).issubset(available_tags):
        # Если теги поста разрешены данному пользователю, то удаляем пост
        elastic_search.delete(index="company", id=note_id)
        if (MEDIA_ROOT / note_id).exists():
            # Если есть прикрепленные файлы
            shutil.rmtree(MEDIA_ROOT / note_id)

        cache.delete("all_posts_count")
        cache.delete("last_updated_posts")

    return HttpResponseRedirect("/")


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class TagsView(View):
    """
    Смотрим и создаем теги
    """

    @staticmethod
    def get(request):
        all_tags = Tags.objects.all()  # Все существующие теги
        return render(
            request,
            "tags.html",
            {
                "tags": all_tags,
                "page_name": "notes-tags",
            },
        )

    @staticmethod
    def post(request):
        # Добавляем новый тег
        if request.POST.get("new_tag"):
            t = Tags()
            t.tag_name = request.POST["new_tag"]
            t.save()
        return HttpResponseRedirect(reverse("notes-tags"))


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class DeleteTagsView(View):
    """
    Удаляем теги
    """

    @staticmethod
    def post(request, tag_id):
        Tags.objects.filter(id=tag_id).delete()
        return HttpResponseRedirect("/tags")


@login_required
def logout(request):
    return render(request, "registration/logout.html")
