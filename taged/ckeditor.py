from rest_framework.decorators import api_view
from ckeditor_uploader.views import upload as ckeditor_upload


@api_view(["GET", "POST"])
def ckeditor_upload_api_view(request, *args, **kwargs):
    return ckeditor_upload(request, *args, **kwargs)
