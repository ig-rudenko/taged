from rest_framework.response import Response
from rest_framework.views import APIView

from taged_web.api.serializers import NoteEditorSerializer
from taged_web.services.editor import NoteEditors, Editor


class RegisterNoteEditorAPIView(APIView):
    def post(self, request):
        serializer = NoteEditorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        editor = Editor(serializer.validated_data["editor"])
        editor.set_edit_note(serializer.validated_data["note"])
        return Response(serializer.validated_data, status=201)


class NoteEditorsListAPIView(APIView):
    def get(self, request, note_id: str):
        editors = NoteEditors(note_id).get_active_editors()
        return Response(editors)
