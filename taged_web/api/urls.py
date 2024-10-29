from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .drafts_view import DraftsViewSet
from .editor_views import RegisterNoteEditorAPIView, NoteEditorsListAPIView

router = DefaultRouter()
router.register("", DraftsViewSet, basename="drafts")

# /api/notes/

app_name = "api-notes"

urlpatterns = [
    path("", views.NotesListCreateAPIView.as_view()),
    # Editors
    path("editors", RegisterNoteEditorAPIView.as_view(), name="register-note-editor"),
    path("editors/<str:note_id>", NoteEditorsListAPIView.as_view(), name="get-note-editors"),
    #
    path("autocomplete", views.AutocompleteAPIView.as_view()),
    path("permissions", views.ListUserPermissions.as_view()),
    path("count", views.NotesCount.as_view()),
    path("tags", views.TagsListAPIView.as_view()),
    path("temp/<str:note_id>", views.CreateNoteTempLinkAPIView.as_view()),
    path("temp/show/<str:token>", views.ShowNoteTempLinkAPIView.as_view()),
    path("<str:note_id>/files", views.NoteFilesListCreateAPIView.as_view()),
    path("<str:note_id>/files/<str:file_name>", views.NoteFileDetailDeleteAPIView.as_view()),
    path("<str:note_id>", views.NoteDetailUpdateAPIView.as_view()),
]
