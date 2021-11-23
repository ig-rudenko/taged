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
from django.urls import path, include
from taged_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('ajax/autocomplete/', views.autocomplete),
    path('accounts/', include('django.contrib.auth.urls')),
    path('edit/<str:post_id>', views.edit_post),
    path('post/<str:post_id>', views.show_post),
    path('delete/<str:post_id>', views.delete_post),
    path('create/', views.create_post),
    path('tags/', views.tags),
    path('delete/tag/<str:tag_id>', views.delete_tag),
    path('download/<str:post_id>/<str:file_name>', views.download_file),
]
