from django.urls import path

from . import views

# /api/notes/

app_name = "api:notes"

urlpatterns = [
    path("", views.NotesListCreateAPIView.as_view()),
    path("autocomplete", views.AutocompleteAPIView.as_view()),
    path("count", views.NotesCount.as_view()),
    path("tags", views.TagsListAPIView.as_view()),
    path("get/<str:note_id>", views.NoteAPIView.as_view()),
    path("files/<str:note_id>", views.NoteFilesAPIView.as_view()),
]
