from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .drafts_view import DraftsViewSet

router = DefaultRouter()
router.register("drafts", DraftsViewSet, basename="drafts")

# /api/notes/

app_name = "api:notes"

urlpatterns = [
    path("", include(router.urls)),
    path("", views.NotesListCreateAPIView.as_view()),
    path("autocomplete", views.AutocompleteAPIView.as_view()),
    path("permissions", views.ListUserPermissions.as_view()),
    path("count", views.NotesCount.as_view()),
    path("tags", views.TagsListAPIView.as_view()),
    path("<str:note_id>", views.NoteDetailUpdateAPIView.as_view()),
    path("temp/<str:note_id>", views.CreateNoteTempLinkAPIView.as_view()),
    path("temp/show/<str:token>", views.ShowNoteTempLinkAPIView.as_view()),
    path("<str:note_id>/files", views.NoteFilesListCreateAPIView.as_view()),
    path("<str:note_id>/files/<str:file_name>", views.NoteFileDetailDeleteAPIView.as_view()),
]
