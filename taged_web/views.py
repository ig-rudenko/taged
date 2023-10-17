from datetime import datetime
from typing import List

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
    Http404,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from elasticsearch import exceptions as es_exceptions

from elasticsearch_control.decorators import elasticsearch_check_available
from taged.settings import MEDIA_ROOT
from taged_web.models import Tags
from .es_index import PostIndex, T_Values
from .forms import PostForm
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
@elasticsearch_check_available
def main(request):
    return render(request, "notes/main.html")

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
                    "tags_in": post.tags_list,
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
            tags_to_save += request.POST.getlist("tags_in")

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
            if user_form.cleaned_data["tags_in"] != post.tags_list:
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
                        "checked": tag in request.POST.getlist("tags_in", []),
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
@xframe_options_exempt
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
def show_note_data(request, post_id):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """
    fields = request.GET.getlist("fields", ["content"])

    post = PostIndex.get(id_=post_id, values=fields)
    if post is None:
        data = {"error": "not found"}
    else:
        data = {field: getattr(post, field) for field in fields}

    return JsonResponse(data)


@login_required
@elasticsearch_check_available
def create_note(request):
    """
    Создаем новую запись
    """
    return render(request, "notes/update_create.html")


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
