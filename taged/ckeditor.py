import json

from ckeditor_uploader import utils
from ckeditor_uploader.views import ImageUploadView
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from taged_web.services.thumbnails import create_thumbnails


class CKEditorUploadView(ImageUploadView):
    def post(self, request, **kwargs):
        response = super().post(request, **kwargs)

        if response.headers["Content-Type"] == "application/json":
            # Если заголовок Content-Type равен application/json,
            # то изображение было добавлено в папку медиа файлов.
            data = json.loads(response.content)

            # Получаем путь к исходному изображению.
            image_path = settings.MEDIA_ROOT / data["url"].lstrip(settings.MEDIA_URL)

            # Создаем несколько превью изображения.
            thumbs = create_thumbnails(image_path)

            # Подменяем оригинальное изображение на превью большого размера,
            # чтобы не нагружать клиента оригинальным изображением.
            data["url"] = utils.get_media_url(thumbs["large"])

            return JsonResponse(data)

        return response


ckeditor_upload_api_view = csrf_exempt(CKEditorUploadView.as_view())
