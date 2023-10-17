from django.urls import path

from . import views

# /notes/

app_name = "notes"

urlpatterns = [
    path("", views.main, name="main"),
    path("create/", views.create_note, name="note-create"),
    path("<str:note_id>/edit/", views.EditNoteView.as_view(), name="note-edit"),
    # path("<str:note_id>", views.show_note, name="note-show"),
    # path("<str:note_id>/delete/", views.DeleteNoteView.as_view(), name="note-delete"),
    path(
        "download/<str:note_id>/<str:file_name>",
        views.download_file,
        name="download-file",
    ),
    # TAGS
    # path("tags/", views.TagsView.as_view(), name="notes-tags"),
    # path("tag/<str:tag_id>/delete", views.DeleteTagsView.as_view(), name="delete-tag"),
]
