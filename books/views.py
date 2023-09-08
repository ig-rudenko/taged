from datetime import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files import File
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from elasticsearch import exceptions as es_exceptions

from books.es_index import BookIndex
from books.forms import BookCreateFrom, SearchForm, CommentForm
from books.models import Comment, BookStatistic
from elasticsearch_control.decorators import elasticsearch_check_available


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
            book = BookIndex.create(
                title=book_form.cleaned_data["title"],
                author=book_form.cleaned_data["author"],
                year=str(book_form.cleaned_data["year"] or ""),
                about=book_form.cleaned_data["about"],
            )

            # Проверка успешности создания книги.
            if book:
                file: File = request.FILES["book_file"]
                book.set_file(file.name, file)
                return redirect(reverse("book-about", args=[book.id]))

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
        book = BookIndex.get(book_id)
        if book is None:
            raise Http404()

        return render(
            request,
            "books/create.html",
            {
                "form": BookCreateFrom(book.json()),
                "type": "update",
                "page_name": "book-edit",
            },
        )

    def post(self, request, book_id: str):
        # Создаем новую запись
        book_form = BookCreateFrom(request.POST)
        # Проверка правильности формы.
        if book_form.is_valid():
            book = BookIndex.get(book_id, values=["title"])
            if book is None:
                raise Http404()

            book.title = book_form.cleaned_data["title"]
            book.author = book_form.cleaned_data["author"]
            book.year = str(book_form.cleaned_data["year"])
            book.about = book_form.cleaned_data["about"]
            book.published_at = datetime.now()
            book.save()

            return redirect(reverse("book-about", args=[book.id]))

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
        book = BookIndex.get(book_id, values=["title"])

        if book is None:
            raise Http404()

        book.delete()

        return redirect("books-list")


@login_required
@elasticsearch_check_available
def show(request, book_id):
    """
    Возвращает файл книги
    """

    book = BookIndex.get(book_id, values=["title"])
    if book and book.get_file():
        return redirect(f"/media/books/{book.id}/{book.get_file().name}")
    raise Http404()


@login_required
@elasticsearch_check_available
def about_book(request, book_id):
    """
    Возвращает описание книги
    """
    try:
        # Получаем запись по ID
        book = BookIndex.get(id_=book_id)
        comments = Comment.objects.filter(book_id=book_id).select_related("user")
        book_stats, _ = BookStatistic.objects.get_or_create(
            book_id=book_id, user=request.user
        )

        return render(
            request,
            "books/about_book.html",
            {
                "book": book,
                "statistic": book_stats,
                "comments": comments,
            },
        )
    # Перехват исключения, которое выдается, когда книга не найдена.
    except es_exceptions.NotFoundError:
        raise Http404()


@login_required
@elasticsearch_check_available
def all_books(request):
    """
    Список всех книг
    """

    # Создание нового экземпляра класса SearchForm и передача данных request.GET.
    search_form = SearchForm(request.GET)
    # Проверка корректности запроса и корректности формы поиска.
    if not search_form.is_valid():
        return HttpResponseRedirect(reverse("books-list"))

    # Ищем по полям, переданным в запросе
    paginator = BookIndex.filter(
        search=search_form.cleaned_data["search_text"],
        year=search_form.cleaned_data["search_year"],
        values=["title", "author", "year"],
        sort="published_at",
        sort_desc=True,
    )
    books = paginator.get_page(search_form.cleaned_data["page"])

    books_list = []
    for book in books:
        book_stats, _ = BookStatistic.objects.get_or_create(
            book_id=book["id"], user=request.user
        )
        books_list.append(
            {
                "id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "year": book["year"],
                "statistic": book_stats
            }
        )

    return render(
        request,
        "books/show.html",
        {
            "paginator": paginator,
            "books": books_list,
            "page_name": "books-list",
            "form": search_form.cleaned_data,
        },
    )


def mark_as(request, book_id: str, mark_name: str):
    if request.method == "POST":
        book = BookIndex.get(book_id, values=["title"])
        if not book:
            raise Http404()
        BookStatistic.objects.update_or_create(
            defaults={
                mark_name: request.POST.get(mark_name) == "on",
                "user": request.user,
            },
            book_id=book_id,
        )

    return redirect(reverse("book-about", args=[book_id]))


@login_required
def mark_as_read(request, book_id: str):
    return mark_as(request, book_id, "read")


@login_required
def mark_as_favorite(request, book_id: str):
    return mark_as(request, book_id, "favorite")


@login_required
def add_comment(request, book_id: str):
    if request.method == "POST":
        book = BookIndex.get(book_id, values=["title"])
        if not book:
            raise Http404()

        form = CommentForm(data=request.POST)
        if form.is_valid():
            Comment.objects.create(
                book_id=book_id,
                user=request.user,
                text=form.cleaned_data["text"],
                rating=form.cleaned_data["rating"],
            )

    return redirect(reverse("book-about", args=[book_id]))
