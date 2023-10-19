from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class NotePermission(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return request.user.has_perms(["taged_web.crete_notes"])
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perms(["taged_web.update_notes"])
        if request.method == "DELETE":
            return request.user.has_perms(["taged_web.delete_notes"])
