from django.core.files.uploadedfile import UploadedFile
from django.utils.decorators import method_decorator
from elasticsearch import exceptions as es_exceptions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from elasticsearch_control.decorators import api_elasticsearch_check_available
from taged_web.api.permissions import NotePermission, NoteCreateLinkPermission
from taged_web.api.serializers import (
    NoteSerializerNoTagsValidation,
    NoteSerializerTagsValidation,
    CreateTempLinkSerializer,
)
from taged_web.es_index import PostIndex
from taged_web.repo.notes import get_repository
from taged_web.services.notes import (
    get_note_or_404,
    get_notes,
    update_note,
    get_note_detail,
    create_temp_link,
    get_note_from_temp_link,
    get_notes_count,
)
from taged_web.services.storage import add_files, get_file, delete_file
from taged_web.services.tags import get_unavailable_tags, add_tags_to_user_if_not_exist, get_available_tags
from .types import UserGenericAPIView
from ..services.signals import signals


class ListUserPermissions(UserGenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        # Получаем все права пользователей, которые связаны с данным приложением `taged_web`
        taged_web_permissions = filter(
            lambda x: x.startswith("taged_web"), self.request.user.get_all_permissions()
        )
        # Приводим права "taged_web.update_note" к виду "update_note"
        permissions = map(lambda p: p.split(".")[1], taged_web_permissions)

        return Response(sorted(permissions))


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class AutocompleteAPIView(UserGenericAPIView):
    """
    Подключаемся к серверу Elasticsearch, получаем начало заголовки документов,
    соответствующие поисковому запросу, и возвращаем их полные названия в виде ответа JSON.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        try:
            titles = get_repository().get_titles(
                string=request.GET.get("term", ""), unavailable_tags=get_unavailable_tags(self.current_user())
            )
        except es_exceptions.ConnectionError:
            return Response([], status=500)
        else:
            return Response(titles)


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesCount(UserGenericAPIView):
    """Получает кол-во записей от Elasticsearch"""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        total_count: int = get_notes_count(self.current_user())

        return Response({"totalCount": total_count})


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NotesListCreateAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NotePermission]

    def get_serializer_class(self):
        """
        Если пользователь имеет право создавать новые теги, то вернется сериализатор,
        которых не проверяет полученные теги на их существование в базе
        :return:
        """
        if self.request.user.has_perms(["taged_web.add_tags"]):
            return NoteSerializerNoTagsValidation
        return NoteSerializerTagsValidation

    def get(self, request: Request):
        search: str = request.GET.get("search", "")
        tags_in: list[str] = request.GET.getlist("tags-in", [])
        page: str = request.GET.get("page", "1")
        use_vectorize_search: bool = request.GET.get("use-vectorizer", "false") == "true"
        vectorizer_only: bool = request.GET.get("vectorizer-only", "false") == "true"

        return get_notes(search, tags_in, page, self.current_user(), use_vectorize_search, vectorizer_only)

    def post(self, request: Request):
        serializer = self.get_serializer_class()(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "title": serializer.validated_data["title"],
            "tags": serializer.validated_data["tags"],
            "content": serializer.validated_data["content"],
            "preview_image": PostIndex.get_first_image_url(serializer.validated_data["content"]),
        }
        add_tags_to_user_if_not_exist(data["tags"], self.current_user())
        post = get_repository().create(**data)

        signals.emit("created_note", note=post)  # Сигнал о создании записи

        return Response({"id": post.id}, status=201)


@method_decorator(api_elasticsearch_check_available, name="dispatch")
class NoteDetailUpdateAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NotePermission]

    def get_serializer_class(self):
        """
        Если пользователь имеет право создавать новые теги, то вернется сериализатор,
        которых не проверяет полученные теги на их существование в базе
        :return:
        """
        if self.request.user.has_perms(["taged_web.add_tags"]):
            return NoteSerializerNoTagsValidation
        return NoteSerializerTagsValidation

    def get(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, self.current_user())
        note_data = get_note_detail(note)
        return Response(note_data)

    def put(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, self.current_user())
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_note(
            note,
            serializer.validated_data["title"],
            serializer.validated_data["content"],
            serializer.validated_data["tags"],
            user=self.current_user(),
        )

        signals.emit("updated_note", note=note)  # Сигнал об изменении записи
        return Response({"id": note.id, "published_at": note.published_at})

    def delete(self, request: Request, note_id: str):
        note = get_note_or_404(note_id, self.current_user())
        get_repository().delete(note.id)
        signals.emit("deleted_note", note=note)  # Сигнал об удалении записи
        return Response(status=204)


class NoteFilesListCreateAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NotePermission]

    def get(self, request: Request, note_id: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи
        get_note_or_404(note_id, self.current_user(), values=["tags"])
        return Response([file.json() for file in get_repository().get_files(note_id)])

    def post(self, request: Request, note_id: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи
        get_note_or_404(note_id, self.current_user(), values=["tags"])
        files_data: dict[str, list[UploadedFile]] = dict(request.FILES or {})
        files = files_data.get("files", [])
        if files:
            add_files(files, note_id)

        return Response({"filesCount": len(files)}, status=201)


class NoteFileDetailDeleteAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NotePermission]

    def get(self, request: Request, note_id: str, file_name: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи.
        get_note_or_404(note_id, self.current_user(), values=["tags"])
        return get_file(note_id, file_name)  # Отправляем пользователю файл

    def delete(self, request: Request, note_id: str, file_name: str):
        # Проверяем, имеет ли пользователь доступ к текущей записи, чтобы удалить её файл
        get_note_or_404(note_id, self.current_user(), values=["tags"])

        delete_file(note_id, file_name)
        return Response(status=204)


class TagsListAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NotePermission]

    def get(self, request: Request, *args, **kwargs):
        return Response(get_available_tags(self.current_user()))


class CreateNoteTempLinkAPIView(UserGenericAPIView):
    permission_classes = [IsAuthenticated, NoteCreateLinkPermission]
    serializer_class = CreateTempLinkSerializer

    def post(self, request: Request, note_id: str, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = get_note_or_404(note_id, self.current_user())
        link = create_temp_link(note, serializer.validated_data["minutes"])

        return Response({"link": link})


class ShowNoteTempLinkAPIView(UserGenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str, *args, **kwargs):
        note = get_note_from_temp_link(token)
        note_json_data = get_note_detail(note)
        return Response(note_json_data)
