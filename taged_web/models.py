from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Tags(models.Model):
    tag_name = models.CharField(max_length=254, null=False)
    user = models.ManyToManyField(User)
