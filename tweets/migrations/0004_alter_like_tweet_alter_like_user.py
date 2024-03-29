# Generated by Django 4.1.7 on 2023-05-20 03:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tweets", "0003_like_like_unique_like"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="tweet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="likes", to="tweets.tweet"
            ),
        ),
        migrations.AlterField(
            model_name="like",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="likes", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
