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
from taged_web import views
from django.views.static import serve
from taged import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    # NOTE
    path("", lambda x: HttpResponseRedirect("/notes"), name="home"),
    path("notes/", include("taged_web.urls")),
    # ACCOUNT
    path("accounts/", include("django.contrib.auth.urls")),
    path("logout", views.logout, name="submit-logout"),
    # BOOKS
    path("books/", include("books.urls")),
    # STATIC
    re_path(
        r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}
    ),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    # AJAX
    path("ajax/autocomplete/", views.autocomplete),
    path("ajax/extend_post/<post_id>", views.pre_show_post),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

handler404 = "taged_web.errors_views.page404"
handler500 = "taged_web.errors_views.page500"


# if settings.DEBUG:
#     urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
