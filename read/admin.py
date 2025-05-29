from django.contrib import admin
from django.db.models import Count
from django.forms import ValidationError

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
    classes = ["collapse"]


class BookInlineForSeries(admin.TabularInline):
    model = Book
    fields = ["series_order", "title", "author", "publish_year", "page_count"]
    extra = 0
    ordering = ["series_order"]


class BookInlineForAuthor(admin.TabularInline):
    model = Book
    fields = ["title", "publish_year", "series", "page_count"]
    extra = 0
    ordering = ["-publish_year"]


class ReadingInLine(admin.TabularInline):
    model = Reading
    extra = 0
    fields = ["date_started", "date_finished", "current_status"]
    ordering = ["-date_finished"]


class EditionsInLine(admin.TabularInline):
    model = Edition
    extra = 0
    fields = (
        "subtitle",
        "format",
        "language",
        "status",
    )
    classes = ["collapse"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    model = Book
    fields = (
        "title",
        "author",
        "language",
        "page_count",
        "publish_year",
        "genres",
        "series",
        "series_order",
        "status",
        "get_rating",
    )
    list_display = (
        "title",
        "author",
        "language",
        "publish_year",
        "page_count",
        "status_display",
        "get_rating",
    )

    readonly_fields = ("status", "get_rating")
    inlines = [BookAwardInline, EditionsInLine]
    autocomplete_fields = ["genres", "author"]
    search_fields = ("title",)
    list_filter = (
        "author",
        "language",
        "genres",
        "publish_year",
    )

    # display a property in admin
    @admin.display(description="Status")
    def status_display(self, obj):
        return obj.status

    @admin.display(description="Rating")
    def get_rating(self, obj):
        return obj.average_rating


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    model = Author
    fields = ("name", "country", "nobel")
    list_display = ("name", "country", "nobel")
    inlines = [BookInlineForAuthor]
    search_fields = ("name",)


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "subtitle",
        "language",
        "format",
        "publish_year",
        "isbn",
        "status",
        "get_rating",
    )
    list_display = (
        "title",
        "get_author",
        "language",
        "format",
        "status",
        "get_rating",
    )
    inlines = [ReadingInLine]
    autocomplete_fields = ("title",)
    list_filter = ("format", "status", "language")
    readonly_fields = ("get_rating",)

    @admin.display(description="Author")
    def get_author(self, obj):
        return obj.title.author.name

    # Enable sorting
    get_author.admin_order_field = "title__author"

    @admin.display(description="Rating")
    def get_rating(self, obj):
        return obj.average_rating


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
    extra = 0
    fields = ("date", "pages_read", "percentage_read")

    def save_model(self, request, obj, form, change):
        if obj.pages_read is not None and obj.percentage_read is not None:
            raise ValidationError("You can only enter pages read OR percentage read.")
        super().save_model(request, obj, form, change)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    fields = (
        "edition",
        "current_status",
        "date_started",
        "date_finished",
        "percentage_complete",
        "rating",
    )

    list_display = (
        "edition",
        "current_status",
        "date_started",
        "date_finished",
        "percentage_complete",
        "rating",
    )
    list_filter = (
        "current_status",
        "date_started",
        "date_finished",
    )
    inlines = [ReadingLogInline]
    search_fields = ("edition",)
    readonly_fields = ("percentage_complete",)

    @admin.display(description="Percentage Complete")
    def percentage_complete(self, obj):
        return obj.percentage_complete


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("reading", "date", "pages_read", "percentage_read")
    fields = (
        "reading",
        "date",
        "pages_read",
        "percentage_read",
        "resolved_page_count",
        "computed_pages",
        "page_difference",
    )
    readonly_fields = (
        "resolved_page_count",
        "computed_pages",
        "page_difference",
    )
    list_filter = ("date",)
    autocomplete_fields = ("reading",)


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


@admin.register(BookAward)
class BookAwardAdmin(admin.ModelAdmin):
    list_display = ("book", "prize", "year", "status")
    fields = ("book", "prize", "year", "status")
    autocomplete_fields = ("book",)
    list_filter = (
        "prize",
        "status",
        "year",
    )
