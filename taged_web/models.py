from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tags(models.Model):
    tag_name = models.CharField(max_length=254, null=False)
    user = models.ManyToManyField("taged_web.User")

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class User(AbstractUser):

    def __str__(self):
        return self.username

    class Meta:
        db_table = "auth_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
