"""taged URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from taged import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/notes/", include("taged_web.api.urls")),
    # NOTE
    path("", lambda x: HttpResponseRedirect("/notes"), name="home"),
    path("notes/", include("taged_web.urls")),
    # ACCOUNT
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # BOOKS
    # path("books/", include("books.urls")),
    # STATIC
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    # CKEDITOR
    path("ckeditor/", include("ckeditor_uploader.urls")),
]
