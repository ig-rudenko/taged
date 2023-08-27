from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Comment(models.Model):
    book_id = models.CharField(max_length=64)
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )


class BookStatistic(models.Model):
    book_id = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read = models.BooleanField(default=False, null=False)
