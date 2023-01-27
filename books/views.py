import os.path
import sys
import fitz
import shutil
from re import sub
from datetime import datetime

import elasticsearch

from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from taged.elasticsearch_control import (
    ElasticsearchConnect,
    elasticsearch_check_available,
)
from books.forms import BookCreateFrom, SearchForm


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class CreateBookView(View):
    """
    Создаем новую книгу
    """

    def get(self, request):
        return render(
            request,
            "books/create.html",
            {
                "form": BookCreateFrom(),
                "type": "create",
                "page_name": "book-create",
            },
        )

    def post(self, request):
        # Создаем новую запись
        book_form = BookCreateFrom(request.POST)
        # Проверяем, действительна ли форма и загружен ли файл.
        if book_form.is_valid() and request.FILES.get("book_file"):
            elastic_search = ElasticsearchConnect()
            res = elastic_search.create_post(
                "books",
                {
                    "title": book_form.cleaned_data["title"],
                    "author": book_form.cleaned_data["author"],
                    "year": str(book_form.cleaned_data["year"] or ""),
                    "about": book_form.cleaned_data["about"],
                    "published_at": datetime.now(),
                },
            )

            # Проверка успешности создания книги.
            if res and res.get("_id"):
                book_path = f'{sys.path[0]}/media/books/{res["_id"]}'
                # Проверяем, существует ли путь к книге.
                if not os.path.exists(book_path):
                    os.makedirs(book_path)  # Создаем папку для текущей книги
                # Получение файла из запроса.
                file = request.FILES["book_file"]

                # Фильтруем запрещенные символы
                file_name = sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file.name)

                # Открытие файла в бинарном режиме.
                with open(f"{book_path}/{file_name}", "wb+") as upload_file:
                    # Чтение файла по частям, а затем его запись.
                    for chunk_ in file.chunks():
                        upload_file.write(chunk_)  # Записываем файл

                # Получаем расширение файла
                file_format = file_name.split(".")[-1]
                # Проверяем, является ли файл pdf
                if file_format == "pdf":
                    doc = fitz.Document(f"{book_path}/{file_name}")
                    page = doc.load_page(0)
                    pix = page.get_pixmap()
                    pix.save(f"{book_path}/preview.png")
                # Проверка, является ли файл изображением.
                elif file_format in ["png", "jpg", "jpeg", "svg"]:
                    shutil.copyfile(
                        f"{book_path}/{file_name}", f"{book_path}/preview.png"
                    )
                else:
                    shutil.copyfile(
                        f"{sys.path[0]}/static/images/books/none_preview.png",
                        f"{book_path}/preview.png",
                    )

                return redirect(f'/books/about/{res["_id"]}')

        return render(
            request,
            "books/create.html",
            {
                "form": book_form,
                "type": "create",
                "page_name": "book-create",
            },
        )


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class UpdateBookView(View):
    """
    Обновляет книгу с заданным book_id данными из запроса.
    """

    def get(self, request, book_id: str):
        elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
        try:
            res = elastic_search.get(index="books", id=book_id)[
                "_source"
            ]  # Получаем запись по ID
        except elasticsearch.exceptions.NotFoundError:
            print("ID not exist")
            raise Http404()
        data = {
            "title": res["title"],
            "author": res["author"],
            "year": res["year"],
            "about": res["about"],
        }

        return render(
            request,
            "books/create.html",
            {
                "form": BookCreateFrom(data),
                "type": "update",
                "page_name": "book-edit",
            },
        )

    def post(self, request, book_id: str):
        # Создаем новую запись
        book_form = BookCreateFrom(request.POST)
        # Проверка правильности формы.
        if book_form.is_valid():
            elastic_search = ElasticsearchConnect()
            # Обновление книги новыми данными.
            res = elastic_search.update_post(
                "books",
                {
                    "title": book_form.cleaned_data["title"],
                    "author": book_form.cleaned_data["author"],
                    "year": str(book_form.cleaned_data["year"]),
                    "about": book_form.cleaned_data["about"],
                    "published_at": datetime.now(),
                },
                id_=book_id,
            )

            return redirect(reverse("book-show", args=[res.get("_id")]))

        return render(
            request,
            "books/create.html",
            {
                "form": book_form,
                "type": "update",
                "page_name": "book-edit",
            },
        )


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
@method_decorator(elasticsearch_check_available, name="dispatch")
class DeleteBookView(View):
    """
    Удаляет книгу с идентификатором book_id.
    """

    def post(self, request, book_id: str):
        # Подключаемся к Elasticsearch
        elastic_search = ElasticsearchConnect()

        try:
            # Поиск книги с заданным book_id.
            elastic_search.get(index="books", id=book_id)
        except elasticsearch.exceptions.NotFoundError:
            raise Http404()

        # Удаляет папку с книгой.
        shutil.rmtree(f"{sys.path[0]}/media/books/{book_id}", ignore_errors=True)

        # Удаление книги с указанным book_id.
        elastic_search.delete(index="books", id=book_id)

        return redirect("books-list")


@login_required
@elasticsearch_check_available
def show(request, book_id):
    """
    Он принимает запрос и book_id и возвращает ответ.

    :param request: Это объект запроса, который передается из представления.
    :param book_id: Идентификатор книги, которую мы хотим показать.
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        # Получаем запись по ID
        res = elastic_search.get(index="books", id=book_id)["_source"]
        if res:  # Проверяет, существует ли файл книги. Если да, то возвращает его.
            file_name = os.listdir(f"{sys.path[0]}/media/books/{book_id}")
            file_name = [f for f in file_name if f != "preview.png"]
            if file_name:
                return redirect(f"/media/books/{book_id}/{file_name[0]}")
    # Перехват исключения, которое выдается, когда книга не найдена.
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
    except IndexError:
        print("Book not exist")
    # Возвращаем ошибку 404.
    raise Http404()


@login_required
@elasticsearch_check_available
def about_book(request, book_id):
    """
    Он принимает запрос и book_id и возвращает ответ.

    :param request: Объект запроса является первым параметром каждой функции представления. Он содержит информацию о
    запросе, который был сделан на сервер.
    :param book_id: Идентификатор книги, которую мы рассматриваем.
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        # Получаем запись по ID
        res = elastic_search.get(index="books", id=book_id)["_source"]
        # Преобразование формата даты
        res["published_at"] = datetime.strptime(
            res["published_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        res["id"] = book_id
        return render(
            request,
            "books/about_book.html",
            {
                "book": res,
                "page_name": "book-about",
            },
        )
    # Перехват исключения, которое выдается, когда книга не найдена.
    except elasticsearch.exceptions.NotFoundError:
        raise Http404()


@login_required
@elasticsearch_check_available
def all_books(request):
    # Создание нового экземпляра класса SearchForm и передача данных request.GET.
    search_form = SearchForm(request.GET)
    # Подключение к серверу elasticsearch.
    elastic_search = ElasticsearchConnect()

    # Проверка корректности запроса и корректности формы поиска.
    search_form.is_valid()
    # Ищем по полям, переданным в запросе
    query_limiter = elastic_search.find_books(
        request.GET.get("search_text"),
        request.GET.get("search_year"),
    )
    res_books = query_limiter.get_page(request.GET.get("page"))

    return render(
        request,
        "books/show.html",
        {
            "paginator": query_limiter,
            "books": res_books,
            "page_name": "books-list",
            "form": search_form.cleaned_data,
        },
    )
