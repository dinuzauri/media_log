# Generated by Django 5.1.7 on 2025-03-07 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0005_alter_book_prize"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="book",
            name="prize",
        ),
        migrations.AddField(
            model_name="book",
            name="prize",
            field=models.ManyToManyField(blank=True, to="books.prize"),
        ),
    ]
