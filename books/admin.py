from django.contrib import admin
from django.db.models import Count
from django.forms import ValidationError

from .models import Author, Book, Edition, Genre, Prize, Reading, ReadingLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    model = Book
    fields = ("name", "author", "language", "publish_year", "prize", "genres")
    list_display = ("name", "author", "language", "publish_year", "display_prizes")
    autocomplete_fields = ("prize", "genres")

    @admin.display(description="Prizes")
    def display_prizes(self, obj):
        return ", ".join([prize.name for prize in obj.prize.all()])


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    model = Author
    fields = ("name", "country", "nobel")
    list_display = ("name", "country", "nobel")


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    model = Edition
    fields = ("title", "language", "format")
    list_display = ("title", "get_author", "language", "format")

    @admin.display(description="Author")
    def get_author(self, obj):
        return obj.title.author.name

    # Enable sorting
    get_author.admin_order_field = "title__author"


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


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
    list_filter=("current_status","date_started","date_finished")
    inlines=[ReadingLogInline]


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("reading", "date", "pages_read", "percentage_complete")
    list_filter = ("date",)
