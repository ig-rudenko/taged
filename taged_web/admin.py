from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Tags


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ["tag_name"]


admin.site.unregister(get_user_model())


class TagsInline(admin.TabularInline):
    model = Tags.user.through


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    inlines = [
        TagsInline,
    ]
