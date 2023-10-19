from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TagedWebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "taged_web"

    def ready(self):
        from .signals import create_permission

        post_migrate.connect(create_permission, sender=self)
