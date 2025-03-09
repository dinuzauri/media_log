from django.contrib import admin
from django.db.models import Count
from django.forms import ValidationError
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Author,
    Book,
    Edition,
    Genre,
    Award,
    Reading,
    ReadingLog,
    Series,
    BookAward,
)


class BookAwardInline(admin.TabularInline):
    model = BookAward
    extra = 0
    fields = ["prize", "year", "book", "status"]
    ordering = ["-year"]


class BookInlineForSeries(admin.TabularInline):
    model = Book
    fields = ["series_order", "name", "author", "publish_year", "page_count"]
    extra = 0
    ordering = ["series_order"]


class BookInlineForAuthor(admin.TabularInline):
    model = Book
    fields = ["name", "publish_year", "series", "page_count"]
    extra = 0
    ordering = ["-publish_year"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    model = Book
    fields = (
        "name",
        "author",
        "language",
        "page_count",
        "publish_year",
        "genres",
        "series",
        "series_order",
    )
    list_display = (
        "name",
        "author",
        "language",
        "publish_year",
        "page_count",
    )
    inlines = [BookAwardInline]
    autocomplete_fields = ["genres"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    model = Author
    fields = ("name", "country", "nobel")
    list_display = ("name", "country", "nobel")
    inlines = [BookInlineForAuthor]


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "language",
        "format",
    )
    list_display = ("title", "get_author", "language", "format")

    @admin.display(description="Author")
    def get_author(self, obj):
        return obj.title.author.name

    # Enable sorting
    get_author.admin_order_field = "title__author"


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    inlines = [BookAwardInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "get_number_of_titles")

    # Show the number of books in each genre
    @admin.display(description="Number of Books")
    def get_number_of_titles(self, obj):
        return obj.book_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(book_count=Count("book"))


class ReadingLogInline(admin.TabularInline):
    model = ReadingLog
    extra = 1
    fields = ("date", "pages_read", "percentage_complete")
    readonly_fields = ("date",)

    def save_model(self, request, obj, form, change):
        if obj.pages_read is not None and obj.percentage_complete is not None:
            raise ValidationError("You can only enter pages read OR percentage read.")
        super().save_model(request, obj, form, change)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("edition", "current_status", "date_started", "date_finished")
    list_filter = ("current_status", "date_started", "date_finished")
    inlines = [ReadingLogInline]


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("reading", "date", "pages_read", "percentage_complete")
    list_filter = ("date",)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "get_number_of_volumes")
    fields = ("title", "author")
    inlines = [BookInlineForSeries]

    # Show the number of books in each series
    @admin.display(description="volumes")
    def get_number_of_volumes(self, obj):
        return obj.book_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(book_count=Count("book"))
