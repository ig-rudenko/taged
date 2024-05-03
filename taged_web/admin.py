from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Tags
from .repo.notes import get_repository


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ["tag_name", "users", "notes_count"]
    search_fields = ["tag_name"]
    list_filter = ["user"]

    @admin.display(description="Пользователи")
    def users(self, tag: Tags):
        lines = ""
        for user in tag.user.all():
            lines += f"<li>{user.username}</li>"

        return mark_safe(lines)

    @admin.display(description="Кол-во записей")
    def notes_count(self, tag: Tags):
        return get_repository().tags_count(tag_name=tag.tag_name)


class TagsInline(admin.TabularInline):
    model = Tags.user.through


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    inlines = [TagsInline]
