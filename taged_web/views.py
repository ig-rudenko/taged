from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from elasticsearch_control.decorators import elasticsearch_check_available
from .api.views import get_note_or_404


@login_required
@elasticsearch_check_available
def main(request):
    return render(request, "notes/main.html")


@login_required
@elasticsearch_check_available
def create_note(request):
    return render(request, "notes/update_create.html")


@login_required
@elasticsearch_check_available
def edit_note(request, note_id: str):
    get_note_or_404(note_id, request.user, values=["tags"])
    return render(request, "notes/update_create.html")


@login_required
@elasticsearch_check_available
def view_note(request, note_id: str):
    get_note_or_404(note_id, request.user, values=["tags"])
    # return render(request, "notes/update_create.html")
