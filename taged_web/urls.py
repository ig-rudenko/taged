from django.urls import path

from . import views

# /notes/

app_name = "notes"

urlpatterns = [
    path("", views.main, name="main"),
    path("create/", views.create_note, name="note-create"),
    path("<str:note_id>/edit/", views.edit_note, name="note-edit"),
]
