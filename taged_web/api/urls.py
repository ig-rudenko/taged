from django.urls import path

from . import views

# /api/notes/

app_name = "api:notes"

urlpatterns = [
    path("", views.NotesListCreateAPIView.as_view()),
    path("autocomplete", views.AutocompleteAPIView.as_view()),
    path("permissions", views.ListUserPermissions.as_view()),
    path("count", views.NotesCount.as_view()),
    path("tags", views.TagsListAPIView.as_view()),
    path("<str:note_id>", views.NoteDetailUpdateAPIView.as_view()),
    path("<str:note_id>/files", views.NoteFilesListCreateAPIView.as_view()),
    path(
        "<str:note_id>/files/<str:file_name>",
        views.NoteFileDetailDeleteAPIView.as_view(),
    ),
]
