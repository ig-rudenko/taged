from django.db import models

# Create your models here.


class Tags(models.Model):
    tag_name = models.CharField(max_length=254, null=False)
