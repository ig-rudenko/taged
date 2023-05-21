import random
from datetime import datetime
from typing import List

from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
    Http404,
    HttpResponseForbidden,
)
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from elasticsearch import exceptions as es_exceptions

from taged_web.models import Tags
from taged.settings import MEDIA_ROOT
from elasticsearch_control.cache import get_or_cache
from elasticsearch_control.decorators import elasticsearch_check_available

from .forms import PostForm
from .es_index import PostIndex, T_Values
from .image_decoder import ReplaceImagesInHtml


def get_note(note_id: str) -> PostIndex:
    """
    ## Возвращаем заметку по её `note_id` или вызываем исключение `Http404`.
    """

    post = PostIndex.get(id_=note_id)
    if post is None:
        raise Http404()
    return post


@login_required
def autocomplete(request):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.

    :param request: Объект запроса.
    :return: Список заголовков.
    """

    try:
        titles = PostIndex.get_titles(string=request.GET.get("term"))
    except es_exceptions.ConnectionError:
        return JsonResponse({"data": None}, status=500)
    else:
        return JsonResponse({"data": titles})


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class NotesListView(View):
    def get(self, request):
        tags_in = request.GET.getlist("tags-in", [])
        tags_off = request.GET.getlist("tags-off", [])
        search_str = request.GET.get("search", "")

        available_tags = request.user.get_tags()
        posts_list = []
        posts_count = None
        paginator = None

        # Проверка того, является ли метод запроса GET и является ли пользователь суперпользователем. Если оба условия
        # выполняются, он получает последние опубликованные сообщения от Elasticsearch.
        if not tags_in and not tags_off and not search_str:
            if request.user.is_superuser:
                # Просмотр последних статей доступен только суперпользователю

                last_posts_paginator = PostIndex.filter(
                    sort="published_at", sort_desc=True, values=["title", "tags"]
                )

                # Ограничиваем кол-во полученных записей до 6
                last_posts_paginator.per_page = 6

                # Получаем записи из кэша или они будут созданы по функции
                posts_list = get_or_cache(
                    function=last_posts_paginator.get_page,
                    kwargs={"page": 1},
                    unique_name="last_updated_posts",
                    cache_period=60 * 10,
                )

                posts_count = last_posts_paginator.count

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
            paginator = PostIndex.filter(
                string=search_str,
                tags_in=tags_in,
                tags_off=tags_off,
            )
            posts_list = paginator.get_page(request.GET.get("page"))
            posts_count = paginator.count

        self.add_file_mark(posts_list)
        tags_in = self.mark_selected_tags(tags_in, available_tags)
        tags_off = self.mark_selected_tags(tags_off, available_tags)

        # Отрисовка страницы home.html с данными из базы данных.
        return render(
            request,
            "home.html",
            {
                "pagination": paginator,
                "posts_count": posts_count,
                "page_name": "notes-list",
                "has_search": bool(search_str),  # Был ли поиск по строке
                "data": posts_list,
                "tags_in": tags_in,
                "tags_off": tags_off,
                "image": f"images/cat{random.randint(0, 9)}.gif",
            },
        )

    @staticmethod
    def add_file_mark(objects: List[dict]):
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
class EditNoteView(View):
    """
    Редактирование существующей записи
    """

    def get(self, request, note_id: str):
        post = get_note(note_id)
        available_tags = request.user.get_tags()

        # Прикрепленные файлы
        data = {
            "files": post.get_files(),
            "page_name": "note-edit",
            "post": post,
            # Определяем, какие теги существуют в посте из разрешенных для пользователя и отмечаем их как checked
            "tags": [
                {
                    "name": tag,
                    "checked": tag in post.tags_list,
                }
                for tag in available_tags
            ],
            # Форма для пользователя с начальными данными
            "form": PostForm(
                {
                    "title": post.title,
                    "input": post.content,
                    "tags_checked": post.tags_list,
                }
            ),
        }

        return render(request, "edit_post.html", data)

    def post(self, request, note_id: str):
        user_form = PostForm(request.POST)
        post = get_note(note_id)

        if user_form.is_valid():  # Если данные были введены верно
            user_tags = request.user.get_tags()

            # Список тегов, которые будут обновлены.
            # Состоят из тегов, которые были у записи, но недоступные для пользователя
            tags_to_save = [t for t in post.tags_list if t not in user_tags]
            # Плюс те, что он указал явно
            tags_to_save += request.POST.getlist("tags_checked")

            image_formatter = ReplaceImagesInHtml(user_form.cleaned_data["input"])
            # Сохраняем закодированные изображения как файлы
            # и заменяем у них атрибут src на ссылку файла.
            image_formatter.save_images_and_update_src(
                image_prefix="image",
                folder=f"{note_id}/content_images",
            )
            # Теперь в содержимом заметки все изображения заменены на ссылки
            content = image_formatter.html

            # Обновляем существующую в elasticsearch запись
            # Смотрим какие именно поля изменились и обновляем только их
            updated_fields: List[T_Values] = ["published_at"]
            post.published_at = datetime.now()
            if user_form.cleaned_data["title"] != post.title:
                post.title = user_form.cleaned_data["title"]
                updated_fields.append("title")
            if user_form.cleaned_data["input"] != post.content:
                post.content = content
                updated_fields.append("content")
            if user_form.cleaned_data["tags_checked"] != post.tags_list:
                post.tags = tags_to_save
                updated_fields.append("tags")
            post.save(values=updated_fields)

            cache.delete("last_updated_posts")

            self.update_files(request, note_id)

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
                    for tag in request.user.get_tags()
                ],
                "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                "files": post.get_files(),
                "form": user_form,
                "page_name": "note-edit",
            }
            return render(request, "edit_post.html", res)

    @staticmethod
    def update_files(request, note_id):
        # Создаем папку для файлов
        (MEDIA_ROOT / note_id).mkdir(parents=True, exist_ok=True)

        for f in (MEDIA_ROOT / note_id).glob("*"):
            if f.is_dir():
                continue
            # Смотрим все прикрепленные файлы
            if not request.POST.get(f"checkbox_{f.name}"):
                # Если пользователь отключил данный файл
                f.unlink()  # Удаляем

        if request.FILES.get("files"):  # Если пользователь добавил файлы
            for uploaded_file in request.FILES.getlist("files"):
                # Для каждого файла
                with open(MEDIA_ROOT / note_id / uploaded_file.name, "wb+") as file:
                    for chunk_ in uploaded_file.chunks():
                        file.write(chunk_)  # Записываем файл


@login_required
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
    else:
        raise Http404()


@login_required
@elasticsearch_check_available
def show_note(request, note_id: str):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param note_id: ID записи в elasticsearch
    :return:
    """

    post = PostIndex.get(id_=note_id, values=["title", "published_at", "tags"])
    if post is None:
        raise Http404()

    data = {"post": post, "page_name": "note-show", "files": post.get_files()}

    return render(request, "post.html", data)


@login_required
@elasticsearch_check_available
def pre_show_note(request, post_id):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """

    post = PostIndex.get(id_=post_id, values=["content"])
    if post is None:
        data = {"error": "not found"}
    else:
        data = {"content": post.content}

    return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class CreateNoteView(View):
    """
    Создаем новую запись
    """

    @staticmethod
    def post(request):
        user_form = PostForm(request.POST)  # Заполняем форму

        if user_form.is_valid():  # Проверяем форму
            # Данные для сохранения

            data = {
                "title": user_form.cleaned_data["title"],
                "tags": request.POST.getlist("tags_checked"),
                "content": user_form.cleaned_data["input"],
            }

            # Ищем закодированные изображения (base64) в содержимом заметки.
            image_formatter = ReplaceImagesInHtml(user_form.cleaned_data["input"])

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

            if request.FILES.get("files"):
                (MEDIA_ROOT / post.id).mkdir(parents=True, exist_ok=True)
                # Создаем папку для текущей заметки
                for uploaded_file in dict(request.FILES)["files"]:  # Для каждого файла
                    with open(
                        MEDIA_ROOT / f"{post.id}/{uploaded_file.name}", "wb+"
                    ) as file:
                        for chunk_ in uploaded_file.chunks():
                            file.write(chunk_)  # Записываем файл

            # Обнуляем кеш
            cache.delete("all_posts_count")
            cache.delete("last_updated_posts")

            return HttpResponseRedirect(
                reverse("note-show", kwargs={"note_id": post.id})
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
                        for t in request.user.get_tags()
                    ],
                    "page_name": "note-create",
                    "error": "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                    "form": user_form,
                },
            )

    @staticmethod
    def get(request):
        user_form = PostForm()  # Создаем форму

        available_tags = request.user.get_tags()

        tags_ = sorted(
            [{"name": t, "checked": False} for t in available_tags],
            key=lambda x: x["name"].lower(),  # Сортируем по алфавиту
        )  # Если новая запись, то все теги изначально отключены

        # Клонируем заметку
        if request.GET.get("cl"):
            post_data = PostIndex.get(id_=request.GET.get("cl")).json()

            try:
                # Только разрешенные теги добавятся в клонированную заметку
                post_data["tags"] = set(post_data["tags"]) & set(available_tags)
                # Добавляем в конце заголовка приписку (копия)
                post_data["title"] += " (копия)"

                user_form = PostForm(
                    {
                        "title": post_data["title"],
                        "tags_checked": post_data["tags"],
                        "input": post_data["content"],
                    },
                )

                tags_ = [
                    {"name": t, "checked": t in post_data["tags"]}
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


@method_decorator(login_required, name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class DeleteNoteView(View):
    def post(self, request, note_id: str):
        # Смотрим разрешенные теги для данного пользователя
        available_tags = request.user.get_tags()

        post = PostIndex.get(id_=note_id, values=["tags"])
        if post is None:
            raise Http404()

        if set(post.tags_list).issubset(set(available_tags)):
            # Если теги поста разрешены данному пользователю, то удаляем пост
            post.delete()
            cache.delete("last_updated_posts")
            return HttpResponseRedirect("/")
        else:
            return HttpResponseForbidden()


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
