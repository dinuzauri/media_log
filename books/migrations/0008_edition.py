# Generated by Django 5.1.7 on 2025-03-07 10:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0007_genre_book_genres"),
    ]

    operations = [
        migrations.CreateModel(
            name="Edition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("publish_year", models.IntegerField(null=True)),
                ("language", models.CharField(max_length=20, null=True)),
                (
                    "format",
                    models.CharField(
                        choices=[("P", "Print"), ("D", "Digital"), ("A", "Audio")],
                        max_length=1,
                    ),
                ),
                (
                    "title",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="books.book"
                    ),
                ),
            ],
        ),
    ]
