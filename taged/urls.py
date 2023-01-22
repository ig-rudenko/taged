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
from django.urls import path, include, re_path
from taged_web import views
from django.views.static import serve
from taged import settings

# import debug_toolbar


urlpatterns = [
    path("admin/", admin.site.urls),
    # POSTS
    path("", views.HomeView.as_view()),
    path("edit/<str:post_id>", views.edit_post),
    path("post/<str:post_id>", views.show_post),
    path("delete/<str:post_id>", views.delete_post),
    path("create/", views.CreatePostView.as_view()),
    path("download/<str:post_id>/<str:file_name>", views.download_file),
    # TAGS
    path("tags/", views.TagsView.as_view()),
    path("delete/tag/<str:tag_id>", views.DeleteTagsView.as_view()),
    # ACCOUNT
    path("accounts/", include("django.contrib.auth.urls")),
    path("logout", views.logout),
    # USERS CONTROL
    path("users/", views.UsersView.as_view()),
    path("users/<username>", views.UserTagControlView.as_view()),
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
