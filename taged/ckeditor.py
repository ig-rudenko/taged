import json
import re
from urllib.parse import unquote

from ckeditor_uploader.views import ImageUploadView
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from taged_web.services.thumbnails import create_thumbnails


class CKEditorUploadView(ImageUploadView):
    def post(self, request, **kwargs):
        response = super().post(request, **kwargs)

        if response.headers["Content-Type"] == "application/json":
            # Изображение было успешно добавлено в папку медиа файлов.
            data = json.loads(response.content)

            # Получаем путь к исходному изображению.
            image_path = settings.MEDIA_ROOT / unquote(data["url"]).lstrip(settings.MEDIA_URL)

            # Создаем несколько превью изображения.
            thumbs = create_thumbnails(image_path)

            if thumbs.get("large"):
                # Если было создано превью большого размера, то
                # подменяем оригинальное изображение, чтобы не нагружать клиента оригинальным.
                data["url"] = re.sub(
                    r"\.[a-z]+$",
                    lambda m: f"_thumb_large{m.group(0)}",
                    data["url"],
                )

            return JsonResponse(data)

        return response


ckeditor_upload_api_view = csrf_exempt(CKEditorUploadView.as_view())
