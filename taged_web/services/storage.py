from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse, Http404


def add_files(files: dict[str, list[UploadedFile]], note_id: str):
    if files and files.get("files"):
        (settings.MEDIA_ROOT / note_id).mkdir(parents=True, exist_ok=True)
        # Создаем папку для текущей заметки
        for uploaded_file in files["files"]:  # Для каждого файла
            with open(settings.MEDIA_ROOT / f"{note_id}/{uploaded_file.name}", "wb+") as file:
                for chunk_ in uploaded_file.chunks():
                    file.write(chunk_)  # Записываем файл


def get_file(note_id: str, file_name: str) -> HttpResponse:
    file_path = settings.MEDIA_ROOT / note_id / file_name
    if file_path.exists():
        with file_path.open("rb") as file:
            response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f"inline; filename={file_name}"
        return response
    else:
        raise Http404()


def delete_file(note_id: str, file_name: str):
    file_path = settings.MEDIA_ROOT / note_id / file_name
    file_path.unlink()
