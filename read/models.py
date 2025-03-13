from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    nobel = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Award(models.Model):
    name = models.CharField(max_length=50)
    about = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Series(models.Model):
    title = models.CharField(max_length=30)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        verbose_name_plural = "Series"


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    awards = models.ManyToManyField(Award, blank=True, through="BookAward")
    publish_year = models.IntegerField(null=True)
    language = models.CharField(max_length=20, null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    page_count = models.IntegerField(null=True)
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True)
    series_order = models.FloatField(null=True, blank=True)

    def clean(self):
        """Ensure series_order is required when series is not null"""
        if self.series and self.series_order is None:
            raise ValidationError(
                {
                    "series_order": "series_order is required when the book is a part of a series!"
                }
            )

    @property
    def status(self):
        editions = self.editions.all()
        if editions.filter(status="P").exists():
            return "In Progress"
        elif editions.filter(status="F").exists():
            return "Finished"
        else:
            return "Want to read"

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = [
            edition.average_rating
            for edition in self.editions.all()
            if edition.average_rating is not None
        ]
        return round(sum(ratings) / len(ratings), 2) if ratings else None


class BookAward(models.Model):
    STATUS_CHOICES = {"W": "won", "S": "shortlisted"}
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    prize = models.ForeignKey(Award, on_delete=models.CASCADE)
    year = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("book", "prize", "year")
        verbose_name_plural = "Book Awards"

    def __str__(self):
        return f"{self.prize.name}({self.year}): {self.book.title}"


class Edition(models.Model):
    FORMATS = {"P": "print", "D": "digital", "A": "audio"}
    STATUSES = {"W": "want to read", "P": "in progress", "F": "finished"}
    title = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="editions" )
    subtitle = models.CharField(null=True, blank=True, max_length=50)
    page_count = models.IntegerField(null=True, blank=True)
    publish_year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=20, null=True)
    format = models.CharField(max_length=1, choices=FORMATS)
    isbn = models.CharField(max_length=14, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUSES, default="W")

    def __str__(self):
        return f"{self.title.title} - {self.FORMATS.get(self.format)}"

    @property
    def average_rating(self):
        ratings = self.readings.filter(rating__isnull=False).values_list(
            "rating", flat=True
        )
        return round(sum(ratings) / len(ratings), 2) if ratings else None


class Reading(models.Model):
    STATUS = {"R": "currently reading", "F": "finished"}
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="readings" )
    date_started = models.DateField(null=True, blank=True)
    date_finished = models.DateField(null=True, blank=True)
    current_status = models.CharField(choices=STATUS, max_length=1, default="R")
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True
    )

    def __str__(self):
        return f"{self.edition.title.title}, started: {self.date_started}"

    @property
    def percentage_complete(self):
        latest_update = self.logs.order_by("-date").first()
        if not latest_update:
            return 0
        if latest_update.percentage_read is not None:
            return latest_update.percentage_read
        if latest_update.pages_read:
            total_pages = self.edition.page_count or self.edition.title.page_count
            return int((latest_update.pages_read / total_pages) * 100)
        return 0


class ReadingLog(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name="logs")
    date = models.DateTimeField(default=timezone.now)
    pages_read = models.IntegerField(null=True, blank=True)
    percentage_read = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.reading.edition.title.title} - {self.pages_read} pages on {self.date}"

    class Meta:
        verbose_name_plural = "Reading Logs"
