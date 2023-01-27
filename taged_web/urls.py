from django.urls import path
from . import views

# /notes/

urlpatterns = [
    path("", views.NotesListView.as_view(), name="notes-list"),
    path("<str:note_id>/edit/", views.EditNoteView.as_view(), name="note-edit"),
    path("<str:note_id>", views.show_note, name="note-show"),
    path("<str:note_id>/delete/", views.DeleteNoteView.as_view(), name="note-delete"),
    path("create/", views.CreateNoteView.as_view(), name="note-create"),
    path(
        "download/<str:note_id>/<str:file_name>",
        views.download_file,
        name="download-file",
    ),
    # TAGS
    path("tags/", views.TagsView.as_view(), name="notes-tags"),
    path("tags/<str:tag_id>/delete", views.DeleteTagsView.as_view(), name="delete-tag"),
]
