# Generated by Django 4.1.5 on 2023-08-29 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0003_bookstatistic"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookstatistic",
            name="favorite",
            field=models.BooleanField(default=False),
        ),
    ]
