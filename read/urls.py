from django.urls import path

from .views import MainReadView, AddReadingLogView

app_name = "read"
urlpatterns = [
    path("read/", MainReadView, name="read"),
    path(
        "add-reading-log/<int:reading_id>/",
        AddReadingLogView.as_view(),
        name="add_reading_log",
    ),
]
