# Generated by Django 4.1.7 on 2023-04-09 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="content",
            field=models.CharField(max_length=150),
        ),
    ]
