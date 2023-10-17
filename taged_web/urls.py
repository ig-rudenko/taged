from django.urls import path

from . import views

# /notes/

app_name = "notes"

urlpatterns = [
    path("", views.main, name="list"),
    path("create/", views.create_note, name="create"),
    path("<str:note_id>/edit/", views.edit_note, name="edit"),
    path("<str:note_id>", views.view_note, name="view"),
]
