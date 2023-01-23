from django.urls import path
from . import views

# /notes/

urlpatterns = [
    path("", views.HomeView.as_view(), name="notes-list"),
    path("<str:note_id>/edit/", views.edit_post, name="note-edit"),
    path("<str:note_id>", views.show_post, name="note-show"),
    path("<str:note_id>/delete/", views.delete_post, name="note-delete"),
    path("create/", views.CreatePostView.as_view(), name="note-create"),
    path(
        "download/<str:note_id>/<str:file_name>",
        views.download_file,
        name="download-file",
    ),
    # TAGS
    path("tags/", views.TagsView.as_view(), name="notes-tags"),
    path("tags/<str:tag_id>/delete", views.DeleteTagsView.as_view(), name="delete-tag"),
]
