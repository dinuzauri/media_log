# Generated by Django 5.1.7 on 2025-03-07 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="book",
            name="publish_year",
        ),
    ]
