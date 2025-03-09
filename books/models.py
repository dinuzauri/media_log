from django.db import models
from django.forms import ValidationError


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
    name = models.CharField(max_length=50)
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
    def status(self):
        editions=self.edition_set.all()
        if editions.filter(status="P").exists():
            return "In Progress"
        elif editions.filter(status="F").exists():
            return "Finished"
        else:
            return "Want to read"
    def __str__(self):
        return self.name


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
        return f"{self.prize.name}({self.year}): {self.book.name}"


class Edition(models.Model):
    FORMATS = {"P": "print", "D": "digital", "A": "audio"}
    STATUSES = {"W": "want to read", "P": "in progress", "F": "finished"}
    title = models.ForeignKey(Book, on_delete=models.CASCADE)
    publish_year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=20, null=True)
    format = models.CharField(max_length=1, choices=FORMATS)
    isbn = models.CharField(max_length=14, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUSES, default="W")

    def __str__(self):
        return f"{self.title.name} - {self.FORMATS.get(self.format)}"


class Reading(models.Model):
    STATUS = {"R": "currently reading", "F": "finished"}
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)
    date_started = models.DateField(null=True)
    date_finished = models.DateField(null=True, blank=True)
    current_status = models.CharField(choices=STATUS, max_length=1, default="R")

    def __str__(self):
        return f"{self.edition.title.name} - {self.edition.title.author.name}: {self.date_started}"


class ReadingLog(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name="logs")
    date = models.DateTimeField(auto_now_add=True)
    pages_read = models.IntegerField(null=True, blank=True)
    percentage_complete = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.reading.edition.title.name} - {self.pages_read} pages on {self.date}"

    class Meta:
        verbose_name_plural = "Reading Logs"
