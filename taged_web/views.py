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
from dateconverter import DateConverter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from taged_web.elasticsearch_control import connect_elasticsearch
from taged_web import elasticsearch_control
from taged_web.models import Tags

from taged.settings import MEDIA_ROOT
from .forms import PostForm


def icon_path(file: str):
    icon = "file.png"
    file_suffix = file.split(".")[-1]

    if file_suffix in ["doc", "docx", "rtf"]:
        icon = "docx.png"
    if file_suffix in ["xls", "xlsx", "xlsm"]:
        icon = "xlsx.png"
    if file_suffix in ["pdf"]:
        icon = "pdf.png"
    if file_suffix in ["txt"]:
        icon = "txt.png"
    if file_suffix in ["drawio"]:
        icon = "drawio.png"
    if file_suffix in ["xml"]:
        icon = "xml.png"
    if file_suffix in ["vds", "vsdx"]:
        icon = "visio.png"
    if file_suffix in ["rar", "7z", "zip", "tar", "iso"]:
        icon = "archive.png"
    if file_suffix in ["png", "jpeg", "gif", "jpg", "bpm"]:
        icon = "img.png"

    return "images/icons/" + icon


@login_required
def autocomplete(request):
    es = elasticsearch_control.connect_elasticsearch()
    titles = elasticsearch_control.get_titles(es, request.GET.get("term"))
    return JsonResponse({"data": titles})


@login_required
def home(request):
    available_tags = (
        Tags.objects.all()
        if request.user.is_superuser
        else Tags.objects.filter(user__username=request.user.username)
    )
    # unavailable_tags = list({t.tag_name for t in Tags.objects.all()} - {t.tag_name for t in available_tags})

    tags_in = tags_off = tags_ = sorted(
        [{"tag": t.tag_name, "checked": False} for t in available_tags],
        key=lambda x: x["tag"].lower(),  # Сортируем по алфавиту
    )
    data = []
    posts_count = None

    if request.method == "GET":
        es = connect_elasticsearch()
        if es and request.user.is_superuser:
            # Просмотр последних статей доступен только суперпользователю
            data = elasticsearch_control.get_last_published(es)
            posts_count = elasticsearch_control.posts_count()

    if request.method == "POST":
        es = connect_elasticsearch()
        tags_in = dict(request.POST).get("tags-in")
        tags_off = dict(request.POST).get("tags-off") or []

        if (
            not request.POST.get("search", "")  # Если (нет поиска по слову)
            and not tags_in  # и (нет тегов)
            or set(tags_in or set())  # или (теги содержат запрещенные)
            - {t.tag_name for t in available_tags}  # (определяем разностью)
        ):
            return HttpResponseRedirect("/")

        # Поиск записей
        data = elasticsearch_control.find_posts(
            es,
            string=request.POST.get("search", ""),
            tags_in=tags_in,
            tags_off=tags_off,
        )

        for d in data:
            if isinstance(d["tags"], str):
                d["tags"] = [d["tags"]]
            # Проверяем прикрепленные файлы
            if os.path.exists(MEDIA_ROOT / f'{d["id"]}') and os.listdir(
                MEDIA_ROOT / f'{d["id"]}'
            ):
                d["files"] = True
            else:
                d["files"] = False

        tags_in = sorted(
            [
                {
                    "tag": t["tag"],
                    "checked": True if tags_in and t["tag"] in tags_in else False,
                }
                for t in tags_
            ],
            key=lambda x: x["tag"].lower(),  # Сортируем по алфавиту
        )
        tags_off = sorted(
            [
                {
                    "tag": t["tag"],
                    "checked": True if tags_off and t["tag"] in tags_off else False,
                }
                for t in tags_
            ],
            key=lambda x: x["tag"].lower(),  # Сортируем по алфавиту
        )

    return render(
        request,
        "home.html",
        {
            "posts_count": posts_count,
            "search_mode": request.method == "POST",
            "data": data,
            "superuser": request.user.is_superuser,
            "tags_in": tags_in,
            "tags_off": tags_off,
            "image": random.randint(0, 9),
            "search_text": request.POST.get("search") or "",
        },
    )


@login_required
def edit_post(request, post_id: str):
    """
    Редактирование существующей записи
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """

    # У супер пользователя доступны все теги
    # Список тегов ['tag1', 'tag2', ... ]
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

    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index="company", id=post_id)["_source"]  # Получаем запись по ID
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
            es = connect_elasticsearch()  # Подключаемся к elasticsearch

            # Список тегов, которые будут обновлены
            # Состоят из тегов, которые были у записи, но недоступные для пользователя + те, что он указал явно
            tags_to_save = [t for t in exists_tags if t not in available_tags] + dict(
                request.POST
            )["tags_checked"]

            # Обновляем существующую в elasticsearch запись
            update_post = elasticsearch_control.update_post(
                es,
                "company",
                {
                    "content": user_form.cleaned_data["input"],
                    "published_at": datetime.now(),
                    "tags": tags_to_save,
                    "title": user_form.cleaned_data["title"],
                },
                id_=post_id,
            )

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
            # Если не все поля были указаны
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
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index="company", id=post_id)["_source"]  # Получаем запись по ID
        # Если имеется всего один тег, то он имеет тип str, переводим его в list
        if isinstance(res["tags"], str):
            res["tags"] = [res["tags"]]
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
        raise Http404()

    res["superuser"] = request.user.is_superuser
    res["post_id"] = post_id

    d = res["published_at"]  # 2021-10-13T14:58:05.866799
    res["published_at"] = (
        str(DateConverter(f"{d[8:10]} {d[5:7]} {d[:4]}")) + " / " + d[11:19]
    )

    # Если имеются файлы у записи
    res["files"] = []
    if os.path.exists(MEDIA_ROOT / post_id) and os.listdir(MEDIA_ROOT / post_id):
        for file in os.listdir(MEDIA_ROOT / post_id):
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
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index="company", id=post_id)["_source"]  # Получаем запись по ID

    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
        return JsonResponse({"error": "not found"})

    return JsonResponse({"post": res["content"]})


@login_required
def create_post(request):
    """
    Создаем новую запись
    :param request: запрос
    :return:
    """

    available_tags = (
        [t.tag_name for t in Tags.objects.all()]
        if request.user.is_superuser
        else [
            t.tag_name
            for t in Tags.objects.filter(user__username=request.user.username)
        ]
    )

    user_form = PostForm()  # Создаем форму

    if request.method == "POST":
        user_form = PostForm(request.POST)  # Заполняем форму

        if user_form.is_valid():  # Проверяем форму
            # Подключение к серверу elasticsearch.
            es = connect_elasticsearch()
            # Создание записи в базе данных elasticsearch.
            res = elasticsearch_control.create_post(
                es,
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

            return HttpResponseRedirect(f'/post/{res["_id"]}')

        else:
            tags_checked = (
                dict(request.POST).get("tags_checked") or []
            )  # Выбранные теги

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

    tags_ = sorted(
        [{"tag": t, "cheched": False} for t in available_tags],
        key=lambda x: x["tag"].lower(),  # Сортируем по алфавиту
    )  # Если новая запись, то все теги изначально отключены

    # Клонируем заметку
    if request.GET.get("cl"):
        es = connect_elasticsearch()
        try:
            res = es.get(index="company", id=request.GET.get("cl"))[
                "_source"
            ]  # Получаем запись по ID
            # Если имеется всего один тег, то он имеет тип str, переводим его в list
            if isinstance(res["tags"], str):
                res["tags"] = [res["tags"]]

            # Только разрешенные теги добавятся в клонированную заметку
            res["tags"] = set(res["tags"]) & set(available_tags)

            res["input"] = res["content"]
            res["title"] += " (копия)"  # Добавляем в конце заголовка приписку (копия)

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
        {"tags": tags_, "superuser": request.user.is_superuser, "form": user_form},
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
    es = connect_elasticsearch()

    # Ищем пост по его ID
    post = es.search(
        index="company",
        _source=["_id", "tags"],
        query={"simple_query_string": {"query": post_id, "fields": ["_id"]}},
    )
    if post["_shards"]["successful"]:  # Если нашли
        post_tags = post["hits"]["hits"][0]["_source"]["tags"]  # Смотрим его теги

    else:
        print("ID not exist")
        raise Http404()

    # Если теги поста разрешены данному пользователю, то удаляем пост
    if set(post_tags).issubset(available_tags):
        print("delete:", post_id)
        es.delete(index="company", id=post_id)
        if os.path.exists(MEDIA_ROOT / post_id):
            # Если есть прикрепленные файлы
            for f in os.listdir(MEDIA_ROOT / post_id):
                os.remove(MEDIA_ROOT / post_id / f)  # Удаляем файл
            os.rmdir(MEDIA_ROOT / post_id)  # Удаляем папку

    return HttpResponseRedirect("/")


@login_required
def tags(request):
    """
    Смотрим и создаем теги
    :param request: запрос
    :return:
    """
    if not request.user.is_superuser:  # Только суперпользователи
        return HttpResponseRedirect("/")

    if request.method == "GET":
        all_tags = Tags.objects.all()  # Все существующие теги
        return render(request, "tags.html", {"tags": all_tags})

    if request.method == "POST":
        # Добавляем новый тег
        if request.POST.get("new_tag"):
            t = Tags()
            t.tag_name = request.POST["new_tag"]
            t.save()
        return HttpResponseRedirect("/tags")


@login_required
def delete_tag(request, tag_id):
    """
    Смотрим и создаем теги
    :param request: запрос
    :param tag_id: ID тега
    :return:
    """
    if not request.user.is_superuser:  # Только суперпользователи
        return HttpResponseRedirect("/")

    t = Tags.objects.get(id=tag_id)
    print(t.tag_name)
    t.delete()
    return HttpResponseRedirect("/tags")


@login_required
def users(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    u = User.objects.all()
    return render(request, "user_control/users.html", {"users": u})


@login_required
def user_access_edit(request, username):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")

    if request.method == "GET":
        if not username:
            return HttpResponseRedirect("/users")

        data = {}

        for tag in Tags.objects.all():
            try:
                is_enable = Tags.objects.get(id=tag.id).user.get(username=username)
            except Exception:
                is_enable = 0

            data[tag.id] = {
                "name": tag.tag_name,
                "checked": is_enable,
            }

        return render(
            request,
            "user_control/user_access_group.html",
            {"username": username, "data": data},
        )

    elif request.method == "POST":
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
