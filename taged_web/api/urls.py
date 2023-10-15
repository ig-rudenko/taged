from django.urls import path

from . import views

# /api/notes/

app_name = "api:notes"

urlpatterns = [
    path("", views.NotesListAPIView.as_view()),
    path("autocomplete", views.autocomplete),
    path("count", views.notes_count),
    path("tags", views.tags_list),
    path("get/<str:note_id>", views.note_view),
]
