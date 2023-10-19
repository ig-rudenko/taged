from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def create_permission(sender, **kwargs):
    content_type = ContentType.objects.get_for_model(sender.get_model("User"))
    permission, created = Permission.objects.get_or_create(
        codename="update_notes", name="Can update notes", content_type=content_type
    )
    if created:
        print("Permission `Can update notes` created:", permission)
