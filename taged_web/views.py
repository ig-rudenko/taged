from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from elasticsearch_control.decorators import elasticsearch_check_available
from .api.views import get_note_or_404


@login_required
@elasticsearch_check_available
def main(request):
    return render(request, "notes/main.html")


@login_required
@elasticsearch_check_available
@permission_required(perm="taged_web.create_notes", raise_exception=True)
def create_note(request):
    return render(
        request,
        "notes/update_create.html",
        {"page_title": "Создание"},
    )


@login_required
@elasticsearch_check_available
@permission_required(perm="taged_web.update_notes", raise_exception=True)
def edit_note(request, note_id: str):
    note = get_note_or_404(note_id, request.user, values=["tags"])
    return render(
        request,
        "notes/update_create.html",
        {"page_title": f"Редактирование - {note.title}"},
    )


@login_required
@elasticsearch_check_available
def view_note(request, note_id: str):
    note = get_note_or_404(note_id, request.user, values=["tags"])
    return render(request, "notes/detail_view_note.html", {"title": note.title})
