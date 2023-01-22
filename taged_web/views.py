import os.path
import random
import elasticsearch
from datetime import datetime

from django.shortcuts import render
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
    Http404,
    HttpResponseNotAllowed,
)

from django.views import View
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from taged_web.elasticsearch_control import ElasticsearchConnect
from taged_web.models import Tags

from taged.settings import MEDIA_ROOT
from .forms import PostForm


def icon_path(file: str):
    """
    Если расширение файла есть в списке расширений, вернуть значок для этого расширения

    :param file: Имя файла, который вы хотите отобразить
    :return: Путь к значку для типа файла
    """
    icon = "file.png"
    file_suffix = file.split(".")[-1]

    if file_suffix in ["doc", "docx", "rtf"]:
        icon = "docx.png"
    elif file_suffix in ["xls", "xlsx", "xlsm"]:
        icon = "xlsx.png"
    elif file_suffix in ["pdf"]:
        icon = "pdf.png"
    elif file_suffix in ["txt"]:
        icon = "txt.png"
    elif file_suffix in ["drawio"]:
        icon = "drawio.png"
    elif file_suffix in ["xml"]:
        icon = "xml.png"
    elif file_suffix in ["vds", "vsdx"]:
        icon = "visio.png"
    elif file_suffix in ["rar", "7z", "zip", "tar", "iso"]:
        icon = "archive.png"
    elif file_suffix in ["png", "jpeg", "gif", "jpg", "bpm"]:
        icon = "img.png"

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
    titles = elastic_search.get_titles(string=request.GET.get("term"))

    return JsonResponse({"data": titles})


@method_decorator(login_required, name="dispatch")
class HomeView(View):
    def get(self, request):
        elastic_search = ElasticsearchConnect()

        tags_in = request.GET.getlist("tags-in", [])
        tags_off = request.GET.getlist("tags-off", [])
        search_str = request.GET.get("search", "")

        # Проверка, является ли пользователь суперпользователем или нет. Если пользователь является суперпользователем, он
        # вернет все теги. Если пользователь не является суперпользователем, он вернет теги, связанные с пользователем.
        user_tags = (
            Tags.objects.all().values("tag_name")
            if request.user.is_superuser
            else Tags.objects.filter(user=request.user)
        )
        # Создание списка тегов доступных тегов
        available_tags = [t["tag_name"] for t in user_tags]
        data = []
        posts_count = None

        # Проверка того, является ли метод запроса GET и является ли пользователь суперпользователем. Если оба условия
        # выполняются, он получает последние опубликованные сообщения от Elasticsearch.
        if not tags_in and not tags_off and not search_str:

            if request.user.is_superuser:
                # Просмотр последних статей доступен только суперпользователю

                # Проверяем, есть ли в кеше last_updated_posts, и если да, то используем его
                data = cache.get("last_updated_posts")
                if not data:
                    # Если нет, то вычисляем
                    data = elastic_search.get_last_published(index="company")
                    # Установка кеша для last_updated_posts на значение data на 600 секунд.
                    cache.set("last_updated_posts", data, 600)

                # Проверяем, есть ли в кеше all_posts_count, и если да, то используем его
                posts_count = cache.get("all_posts_count")
                if not posts_count:
                    # Если нет, то вычисляем
                    posts_count = elastic_search.posts_count()
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
                "posts_count": posts_count,
                "data": data,
                "tags_in": tags_in,
                "tags_off": tags_off,
                "image": random.randint(0, 9),
            },
        )

    @staticmethod
    def add_file_mark(objects: list):
        for post in objects:
            if isinstance(post["tags"], str):
                post["tags"] = [post["tags"]]
            # Проверяем прикрепленные файлы
            # Проверяем, существует ли каталог и есть ли в нем какие-либо файлы.
            if os.path.exists(MEDIA_ROOT / f'{post["id"]}') and os.listdir(
                MEDIA_ROOT / f'{post["id"]}'
            ):
                post["files"] = True
            else:
                post["files"] = False

    @staticmethod
    def mark_selected_tags(selected_tags, available_tags):
        if not selected_tags:
            tags_ = [{"name": tag, "checked": False} for tag in available_tags]
        else:
            tags_ = [
                {
                    "name": tag,
                    "checked": True if tag in selected_tags else False,
                }
                for tag in available_tags
            ]
        return sorted(tags_, key=lambda x: x["name"].lower())  # Сортируем по алфавиту


@login_required
def edit_post(request, post_id: str):
    """
    Редактирование существующей записи
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    """

    # Проверка, является ли пользователь суперпользователем или нет. Если пользователь является суперпользователем, он
    # вернет все теги в базе данных. Если пользователь не является суперпользователем, он вернет все теги, доступные
    # пользователю.
    available_tags = (
        [t.tag_name for t in Tags.objects.all()]
        if request.user.is_superuser
        else [
            t.tag_name
            for t in Tags.objects.filter(user__username=request.user.username)
        ]
    )

    # Прикрепленные файлы
    files = []
    # Если существует папка для данного post_id и в ней есть файлы
    if os.path.exists(MEDIA_ROOT / post_id) and os.listdir(MEDIA_ROOT / post_id):
        for f in os.listdir(MEDIA_ROOT / post_id):
            # Добавляем имя файла + иконку в список
            files.append({"name": f, "icon": icon_path(f)})

    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        # Получаем запись по ID
        res = elastic_search.get(index="company", id=post_id)["_source"]
        if isinstance(res["tags"], str):
            res["tags"] = [res["tags"]]  # Переводим теги в список
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")  # Данный ID не существует
        raise Http404()

    res["post_id"] = post_id

    # сохраняем все теги, которые уже существуют у данного поста
    exists_tags = res["tags"]

    # Определяем, какие теги существуют в посте из разрешенных для пользователя и отмечаем их как checked
    res["tags"] = [
        {"tag": t, "checked": False if t not in res["tags"] else True}
        for t in available_tags
    ]

    # Прикрепленные файлы
    res["files"] = files

    # Форма для пользователя с начальными данными
    res["form"] = PostForm(
        {"title": res["title"], "input": res["content"], "tags_checked": res["tags"]}
    )

    if request.method == "POST":
        user_form = PostForm(request.POST)

        if user_form.is_valid():  # Если данные были введены верно

            # Список тегов, которые будут обновлены.
            # Состоят из тегов, которые были у записи, но недоступные для пользователя + те, что он указал явно
            tags_to_save = [t for t in exists_tags if t not in available_tags] + dict(
                request.POST
            )["tags_checked"]

            # Обновляем существующую в elasticsearch запись
            update_post = elastic_search.update_post(
                "company",
                {
                    "content": user_form.cleaned_data["input"],
                    "published_at": datetime.now(),
                    "tags": tags_to_save,
                    "title": user_form.cleaned_data["title"],
                },
                id_=post_id,
            )

            cache.delete("all_posts_count")
            cache.delete("last_updated_posts")

            # Прикрепленные файлы
            if os.path.exists(MEDIA_ROOT / post_id):
                for f in os.listdir(MEDIA_ROOT / post_id):
                    # Смотрим все, что есть
                    if not request.POST.get(f"checkbox_{f}"):
                        # Если пользователь отключил данный файл
                        os.remove(MEDIA_ROOT / post_id / f)  # Удаляем
            else:
                # Создаем папку для файлов, если нет
                os.makedirs(MEDIA_ROOT / post_id)

            if request.FILES.get("files"):  # Если пользователь добавил файлы
                for file in dict(request.FILES)["files"]:  # Для каждого файла
                    with open(MEDIA_ROOT / post_id / file.name, "wb+") as upload_file:
                        for chunk_ in file.chunks():
                            upload_file.write(chunk_)  # Записываем файл

            # Перенаправляем на обновленную запись
            return HttpResponseRedirect(f"/post/{post_id}")

        else:
            # Если не все поля были указаны.
            # Отправляем данные, которые были введены
            res = {
                "tags": [
                    {
                        "tag": t,
                        "checked": False
                        if t not in dict(request.POST).get("tags_checked", [])
                        else True,
                    }
                    for t in available_tags
                ],
                "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                "files": files,
                "form": user_form,
            }

    return render(request, "edit_post.html", res)


@login_required
def download_file(request, post_id: str, file_name: str):
    # Отправляем пользователю файл
    if os.path.exists(MEDIA_ROOT / post_id / file_name):
        with open(MEDIA_ROOT / post_id / file_name, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f"inline; filename={file_name}"
        return response


@login_required
def show_post(request, post_id: str):
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
        # Если имеется всего один тег, то он имеет тип str, переводим его в list
        if isinstance(res["tags"], str):
            res["tags"] = [res["tags"]]
    except elasticsearch.exceptions.NotFoundError:
        raise Http404()

    res["post_id"] = post_id

    # 2021-10-13T14:58:05.866799
    res["published_at"] = datetime.strptime(
        res["published_at"][:19], "%Y-%m-%dT%H:%M:%S"
    )

    # Если имеются файлы у записи
    res["files"] = []
    # Проверяем, существует ли каталог и есть ли в нем какие-либо файлы.
    if os.path.exists(MEDIA_ROOT / post_id) and os.listdir(MEDIA_ROOT / post_id):
        for file in os.listdir(MEDIA_ROOT / post_id):
            # Добавление файлов в текущем каталоге в список файлов.
            res["files"].append({"name": file, "icon": icon_path(file)})

    return render(request, "post.html", res)


@login_required
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

    except elasticsearch.exceptions.NotFoundError:
        return JsonResponse({"error": "not found"})


@method_decorator(login_required, name="dispatch")
class CreatePostView(View):
    """
    Создаем новую запись
    """

    def post(self, request):
        user_form = PostForm(request.POST)  # Заполняем форму

        available_tags = (
            [t.tag_name for t in Tags.objects.all()]
            if request.user.is_superuser
            else [t.tag_name for t in Tags.objects.filter(user=request.user)]
        )

        if user_form.is_valid():  # Проверяем форму
            # Подключение к серверу elasticsearch.
            elastic_search = ElasticsearchConnect()
            # Создание записи в базе данных elasticsearch.
            res = elastic_search.create_post(
                "company",
                {
                    "content": user_form.cleaned_data["input"],
                    "published_at": datetime.now(),
                    "tags": dict(request.POST)["tags_checked"],
                    "title": user_form.cleaned_data["title"],
                },
            )

            if res.get("_id") and request.FILES.get("files"):
                os.makedirs(MEDIA_ROOT / f"{res['_id']}")
                # Создаем папку для текущей заметки
                for file in dict(request.FILES)["files"]:  # Для каждого файла
                    with open(
                        MEDIA_ROOT / f'{res["_id"]}/{file.name}', "wb+"
                    ) as upload_file:
                        for chunk_ in file.chunks():
                            upload_file.write(chunk_)  # Записываем файл

            cache.delete("all_posts_count")
            cache.delete("last_updated_posts")

            return HttpResponseRedirect(f'/post/{res["_id"]}')

        else:
            # Выбранные теги
            tags_checked = dict(request.POST).get("tags_checked") or []

            # Если не все поля были указаны
            return render(
                request,
                "edit_post.html",
                {
                    "tags": [
                        {"tag": t, "checked": True if t in tags_checked else False}
                        for t in available_tags
                    ],
                    "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                    "form": user_form,
                },
            )

    def get(self, request):

        user_form = PostForm()  # Создаем форму

        available_tags = (
            [t.tag_name for t in Tags.objects.all()]
            if request.user.is_superuser
            else [t.tag_name for t in Tags.objects.filter(user=request.user)]
        )

        tags_ = sorted(
            [{"tag": t, "cheched": False} for t in available_tags],
            key=lambda x: x["tag"].lower(),  # Сортируем по алфавиту
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
                    {"tag": t, "checked": True if t in res["tags"] else False}
                    for t in available_tags
                ]
            except elasticsearch.exceptions.NotFoundError:
                pass

        return render(
            request,
            "edit_post.html",
            {
                "tags": tags_,
                "superuser": request.user.is_superuser,
                "form": user_form,
            },
        )


@login_required
def delete_post(request, post_id):
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
        query={"simple_query_string": {"query": post_id, "fields": ["_id"]}},
    )
    if post["_shards"]["successful"]:  # Если нашли
        post_tags = post["hits"]["hits"][0]["_source"]["tags"]  # Смотрим его теги
    else:
        raise Http404()

    if set(post_tags).issubset(available_tags):
        # Если теги поста разрешены данному пользователю, то удаляем пост
        elastic_search.delete(index="company", id=post_id)
        if os.path.exists(MEDIA_ROOT / post_id):
            # Если есть прикрепленные файлы
            for f in os.listdir(MEDIA_ROOT / post_id):
                os.remove(MEDIA_ROOT / post_id / f)  # Удаляем файл
            os.rmdir(MEDIA_ROOT / post_id)  # Удаляем папку

        cache.delete("all_posts_count")
        cache.delete("last_updated_posts")

    return HttpResponseRedirect("/")


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class TagsView(View):
    """
    Смотрим и создаем теги
    """

    def get(self, request):
        all_tags = Tags.objects.all()  # Все существующие теги
        return render(request, "tags.html", {"tags": all_tags})

    def post(self, request):
        # Добавляем новый тег
        if request.POST.get("new_tag"):
            t = Tags()
            t.tag_name = request.POST["new_tag"]
            t.save()
        return HttpResponseRedirect("/tags")


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class DeleteTagsView(View):
    """
    Удаляем теги
    """

    def post(self, request, tag_id):
        Tags.objects.filter(id=tag_id).delete()
        return HttpResponseRedirect("/tags")


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class UsersView(View):
    def get(self, request):
        return render(request, "user_control/users.html", {"users": User.objects.all()})


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class UserTagControlView(View):
    def get(self, request, username):
        if not username:
            return HttpResponseRedirect("/users")

        data = {}

        for tag in Tags.objects.all():
            try:
                is_enable = Tags.objects.get(id=tag.id, user__username=username)
            except Tags.DoesNotExist:
                is_enable = 0

            data[tag.id] = {
                "name": tag.tag_name,
                "checked": is_enable,
            }

        return render(
            request,
            "user_control/user_access_group.html",
            {
                "username": username,
                "data": data,
            },
        )

    def post(self, request, username):
        user = User.objects.get(username=username)  # Пользователь
        for tag in Tags.objects.all():
            if request.POST.get(f"tag_id_{tag.id}"):  # Если данная группа была выбрана
                user.tags_set.add(tag)  # Добавляем пользователя в группу
            else:
                user.tags_set.remove(tag)  # Удаляем

        return HttpResponseRedirect("/users")


@login_required
def logout(request):
    return render(request, "registration/logout.html")
