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
from taged_web.elasticsearch_control import ElasticsearchConnect
from books.forms import BookCreateFrom, SearchForm


@login_required
def create(request):
    """
    Если пользователь не является суперпользователем, верните 404. Если пользователь является суперпользователем и метод
    запроса POST, создайте новую запись книги в базе данных и сохраните загруженный файл на сервер.

    :param request: Объект запроса является экземпляром HttpRequest. Он содержит метаданные о запросе, такие как метод HTTP,
    хост, путь и т. д
    :return: объект ответа.
    """
    if not request.user.is_superuser:  # Не суперпользователям недоступно создание
        return HttpResponseNotFound()

    book_form = BookCreateFrom()

    if request.method == "POST":
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

    return render(request, "books/create.html", {"form": book_form, "type": "create"})


@login_required(login_url="accounts/login")
def update(request, book_id):
    """
    Функция update() принимает запрос и book_id, а затем обновляет книгу с заданным book_id данными из запроса.

    :param request: Это объект запроса, который передается из представления
    :param book_id: Идентификатор книги, которую мы обновляем
    """
    if not request.user.is_superuser:  # Не суперпользователям недоступно редактирование
        return HttpResponseNotFound()

    book_form = BookCreateFrom()

    if request.method == "GET":
        elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
        try:
            res = elastic_search.get(index="books", id=book_id)[
                "_source"
            ]  # Получаем запись по ID
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
        # Проверка правильности формы.
        if book_form.is_valid():
            elastic_search = ElasticsearchConnect()
            # Обновление книги новыми данными.
            res = elastic_search.update_post(
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

            return redirect(f'/books/about/{res.get("_id", "")}')

    return render(request, "books/create.html", {"form": book_form, "type": "update"})


@login_required
def delete(request, book_id):
    """
    удаляет книгу с идентификатором book_id.

    :param request: Это объект запроса, который передается Django
    :param book_id: Идентификатор книги, которую необходимо удалить
    """
    if not request.user.is_superuser:  # Не суперпользователям недоступно редактирование
        return HttpResponseNotFound()
    if request.method == "POST":
        # Подключаемся к Elasticsearch
        elastic_search = ElasticsearchConnect()

        # Поиск книги с заданным book_id.
        post = elastic_search.search(
            index="books",
            _source=["_id"],
            query={"simple_query_string": {"query": book_id, "fields": ["_id"]}},
        )
        if post["_shards"]["successful"]:  # Если нашли
            # Проверяем, существует ли путь к книге. Если да, то удаляет папку с книгой.
            if os.path.exists(f"{sys.path[0]}/media/books/{book_id}"):
                shutil.rmtree(f"{sys.path[0]}/media/books/{book_id}")
            print("delete:", book_id)
            # Удаление книги с указанным book_id.
            elastic_search.delete(index="books", id=book_id)
            return redirect("books")
        else:
            # Возвращает страницу ошибки 404.
            return render(request, "errors/404.html", status=404)
    else:
        return redirect("books")


@login_required
def show(request, book_id):
    """
    Он принимает запрос и book_id и возвращает ответ.

    :param request: Это объект запроса, который передается из представления.
    :param book_id: идентификатор книги, которую мы хотим показать.
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        res = elastic_search.get(index="books", id=book_id)[
            "_source"
        ]  # Получаем запись по ID
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
    return HttpResponseNotFound()


@login_required
def about_book(request, book_id):
    """
    Он принимает запрос и book_id и возвращает ответ.

    :param request: Объект запроса является первым параметром каждой функции представления. Он содержит информацию о
    запросе, который был сделан на сервер
    :param book_id: Идентификатор книги, которую мы рассматриваем
    """
    elastic_search = ElasticsearchConnect()  # Подключаемся к elasticsearch
    try:
        res = elastic_search.get(index="books", id=book_id)[
            "_source"
        ]  # Получаем запись по ID
        # Преобразование формата даты
        res["published_at"] = datetime.strptime(
            res["published_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        res["id"] = book_id
        return render(
            request, "books/about_book.html", {"book": res, "user": request.user}
        )
    # Перехват исключения, которое выдается, когда книга не найдена.
    except elasticsearch.exceptions.NotFoundError:
        print("ID not exist")
    return HttpResponseNotFound()


@login_required
def all_books(request):
    # Создание нового экземпляра класса SearchForm и передача данных request.GET.
    search_form = SearchForm(request.GET)
    print(request.GET)

    # Проверка, ввел ли пользователь текст поиска и год поиска.
    if request.GET.get("search_text") and request.GET.get("search_year"):
        # Текст + год
        # Запрос для elasticsearch.
        query = {
            "bool": {
                "must": [
                    # Запрос для поиска определенного года.
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
    # Поиск по описанию книги
    elif request.GET.get("search_text"):
        # Только поиск текста
        query = {
            "simple_query_string": {
                "query": request.GET["search_text"],
                "fields": ["title^2", "about", "author"],
            }
        }
    # Поиск книг по годам
    elif request.GET.get("search_year"):
        # Только год
        query = {"bool": {"must": [{"term": {"year": request.GET["search_year"]}}]}}
    else:
        query = {}

    # Подключение к серверу elasticsearch.
    elastic_search = ElasticsearchConnect()
    print(query)
    # Проверка корректности запроса и корректности формы поиска.
    if query and search_form.is_valid():
        # Ищем по полям, переданным в запросе
        result = elastic_search.search(
            size=100,
            index="books",
            _source=["title", "year", "author"],
            query=query,
            request_timeout=elastic_search.ELASTICSEARCH_request_timeout,
        )
        res_books = []
        print(result)
        if result:
            # Создаем список книг с ключами id, title, year, author
            # Проходит по всем книгам из базы данных и добавляет их в список `res_books`.
            for b in result["hits"]["hits"]:
                # Создание нового словаря с ключами из `b["_source"]` и ключом `id` со значением `b["_id"]`.
                res_books.append(dict(b["_source"], **{"id": b["_id"]}))
    else:
        # Резервный вариант, когда запрос недействителен.
        search_form.is_valid()
        elastic_search = ElasticsearchConnect()
        # Получение последних 100 книг из базы данных.
        res_books = elastic_search.get_last_published(index="books", limit=100)

    return render(
        request,
        "books/show.html",
        {"books": res_books, "user": request.user, "form": search_form.cleaned_data},
    )
