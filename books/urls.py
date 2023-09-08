from django.urls import path

from books import views

# /books/

urlpatterns = [
    path("", views.all_books, name="books-list"),
    path("create", views.CreateBookView.as_view(), name="book-create"),
    path("update/<book_id>", views.UpdateBookView.as_view(), name="book-edit"),
    path("<book_id>", views.show, name="book-show"),
    path("about/<book_id>", views.about_book, name="book-about"),
    path("delete/<book_id>", views.DeleteBookView.as_view(), name="book-delete"),
    path("<book_id>/add-comment", views.add_comment, name="add-comment"),
    path("<book_id>/mark-as-read", views.mark_as_read, name="mark-as-read"),
    path("<book_id>/mark-as-favorite", views.mark_as_favorite, name="mark-as-favorite"),
]
