from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def create_permission(sender, **kwargs):
    content_type = ContentType.objects.get_for_model(sender.get_model("User"))
    extra_permissions = [
        ("update_notes", "Can update notes"),
        ("create_notes", "Can create notes"),
        ("delete_notes", "Can delete notes"),
    ]

    for codename, name in extra_permissions:
        Permission.objects.get_or_create(
            codename=codename, name=name, content_type=content_type
        )
