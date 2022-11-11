import os.path
import sys
import fitz
import shutil
from re import sub
from datetime import datetime

import elasticsearch

from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from taged_web.elasticsearch_control import connect_elasticsearch
from taged_web import elasticsearch_control
from books.forms import BookCreateFrom, SearchForm


@login_required
def create(request):
    if not request.user.is_superuser:  # Не суперпользователям недоступно создание
        return HttpResponseNotFound()

    book_form = BookCreateFrom()

    if request.method == "POST":
        # Создаем новую запись
        book_form = BookCreateFrom(request.POST)
        if book_form.is_valid() and request.FILES.get("book_file"):
            es = connect_elasticsearch()
            res = elasticsearch_control.create_post(
                es,
                "books",
                {
                    "title": book_form.cleaned_data["title"],
                    "author": book_form.cleaned_data["author"],
                    "year": str(book_form.cleaned_data["year"] or ""),
                    "about": book_form.cleaned_data["about"],
                    "published_at": datetime.now(),
                },
            )

            if res and res.get("_id"):
                book_path = f'{sys.path[0]}/media/books/{res["_id"]}'
                if not os.path.exists(book_path):
                    os.makedirs(book_path)  # Создаем папку для текущей книги
                file = request.FILES["book_file"]

                # Фильтруем запрещенные символы
                file_name = sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file.name)

                with open(f"{book_path}/{file_name}", "wb+") as upload_file:
                    for chunk_ in file.chunks():
                        upload_file.write(chunk_)  # Записываем файл

                # Добавляем превью, если файл PDF
                file_format = file_name.split(".")[-1]
                if file_format == "pdf":
                    doc = fitz.Document(f"{book_path}/{file_name}")
                    page = doc.load_page(0)
                    pix = page.get_pixmap()
                    pix.save(f"{book_path}/preview.png")
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

    return render(request, "books/create.html", {"form": book_form, "type": "create"})


@login_required(login_url="accounts/login")
def update(request, book_id):
    if not request.user.is_superuser:  # Не суперпользователям недоступно редактирование
        return HttpResponseNotFound()

    book_form = BookCreateFrom()

    if request.method == "GET":
        es = connect_elasticsearch()  # Подключаемся к elasticsearch
        try:
            res = es.get(index="books", id=book_id)["_source"]  # Получаем запись по ID
        except elasticsearch.exceptions.NotFoundError:
            print("ID not exist")
            return HttpResponseNotFound()
        data = {
            "title": res["title"],
            "author": res["author"],
            "year": res["year"],
            "about": res["about"],
        }
        book_form = BookCreateFrom(data)

    if request.method == "POST":
        # Создаем новую запись
        book_form = BookCreateFrom(request.POST)
        if book_form.is_valid():
            es = connect_elasticsearch()
            res = elasticsearch_control.update_post(
                es,
                "books",
                {
                    "title": book_form.cleaned_data["title"],
                    "author": book_form.cleaned_data["author"],
                    "year": str(book_form.cleaned_data["year"] or ""),
                    "about": book_form.cleaned_data["about"],
                    "published_at": datetime.now(),
                },
                id_=book_id,
            )

            return redirect(f'/books/about/{res["_id"]}')

    return render(request, "books/create.html", {"form": book_form, "type": "update"})


@login_required
def delete(request, book_id):
    if not request.user.is_superuser:  # Не суперпользователям недоступно редактирование
        return HttpResponseNotFound()
    if request.method == "POST":
        # Подключаемся к Elasticsearch
        es = connect_elasticsearch()

        # Ищем книгу по её ID
        post = es.search(
            index="books",
            _source=["_id"],
            query={"simple_query_string": {"query": book_id, "fields": ["_id"]}},
        )
        if post["_shards"]["successful"]:  # Если нашли
            if os.path.exists(f"{sys.path[0]}/media/books/{book_id}"):
                shutil.rmtree(f"{sys.path[0]}/media/books/{book_id}")
            print("delete:", book_id)
            es.delete(index="books", id=book_id)
            return redirect("books")
        else:
            return render(request, "errors/404.html", status=404)
    else:
        return redirect("books")


@login_required
def show(request, book_id):
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index="books", id=book_id)["_source"]  # Получаем запись по ID
        if res:
            file_name = os.listdir(f"{sys.path[0]}/media/books/{book_id}")
            file_name = [f for f in file_name if f != "preview.png"]
            if file_name:
                return redirect(f"/media/books/{book_id}/{file_name[0]}")
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
    except IndexError:
        print("Book not exist")
    return HttpResponseNotFound()


@login_required
def about_book(request, book_id):
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index="books", id=book_id)["_source"]  # Получаем запись по ID
        res["published_at"] = datetime.strptime(
            res["published_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        res["id"] = book_id
        return render(
            request, "books/about_book.html", {"book": res, "user": request.user}
        )
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
    return HttpResponseNotFound()


@login_required
def all_books(request):
    search_form = SearchForm(request.GET)
    print(request.GET)

    if request.GET.get("search_text") and request.GET.get("search_year"):
        # Текст + год
        query = {
            "bool": {
                "must": [
                    {"term": {"year": request.GET["search_year"]}},
                    {
                        "simple_query_string": {
                            "query": request.GET["search_text"],
                            "fields": ["title^2", "about", "author"],
                        }
                    },
                ]
            }
        }
    elif request.GET.get("search_text"):
        # Только поиск текста
        query = {
            "simple_query_string": {
                "query": request.GET["search_text"],
                "fields": ["title^2", "about", "author"],
            }
        }
    elif request.GET.get("search_year"):
        # Только год
        query = {"bool": {"must": [{"term": {"year": request.GET["search_year"]}}]}}
    else:
        query = {}

    es = connect_elasticsearch()
    print(query)
    if query and search_form.is_valid():
        # Ищем по полям, переданным в запросе
        result = es.search(
            size=100,
            index="books",
            _source=["title", "year", "author"],
            query=query,
            request_timeout=elasticsearch_control.ELASTICSEARCH_request_timeout,
        )
        res_books = []
        print(result)
        if result:
            # Создаем список книг с ключами id, title, year, author
            for b in result["hits"]["hits"]:
                res_books.append(dict(b["_source"], **{"id": b["_id"]}))
    else:
        search_form.is_valid()
        es = connect_elasticsearch()
        res_books = elasticsearch_control.get_last_published(
            es, index="books", limit=100
        )

    return render(
        request,
        "books/show.html",
        {"books": res_books, "user": request.user, "form": search_form.cleaned_data},
    )
