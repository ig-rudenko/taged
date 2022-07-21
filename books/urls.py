from django.urls import path
from books import views


urlpatterns = [
    path('', views.all_books, name='books'),
    path('create', views.create, name='create'),
    path('update/<book_id>', views.update, name='update'),
    path('<book_id>', views.show, name='show'),
    path('about/<book_id>', views.about_book, name='about_book'),
    path('delete/<book_id>', views.delete, name='delete')
]
