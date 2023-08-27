from typing import List

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
    def get_tags(self) -> List[str]:
        # Проверка, является ли пользователь суперпользователем или нет.
        # Если пользователь является суперпользователем, он вернет все теги.
        # Если пользователь не является суперпользователем, он вернет теги, связанные с пользователем.
        user_tags = (
            Tags.objects.all().values("tag_name")
            if self.is_superuser
            else self.tags_set.values("tag_name")
        )
        # Создание списка тегов доступных тегов
        return [t["tag_name"] for t in user_tags]

    def __str__(self):
        return self.username

    class Meta:
        db_table = "auth_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
