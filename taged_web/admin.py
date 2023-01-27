from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from taged.elasticsearch_control import ElasticsearchConnect
from .models import Tags


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ["tag_name", "users", "notes_count"]
    search_fields = ["tag_name"]
    list_filter = ["user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.es = ElasticsearchConnect()

    @admin.display(description="Пользователи")
    def users(self, tag: Tags):
        lines = ""
        for user in tag.user.all():
            lines += f"<li>{user.username}</li>"

        return mark_safe(lines)

    @admin.display(description="Кол-во записей")
    def notes_count(self, tag: Tags):
        return self.es.query_count(
            index="company",
            query={
                "match": {
                    "tags": tag.tag_name,
                }
            },
        )


class TagsInline(admin.TabularInline):
    model = Tags.user.through


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    inlines = [TagsInline]
