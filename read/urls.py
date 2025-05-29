from django.urls import path

from .views import MainReadView, AddReadingLogView, daily_logs

app_name = "read"
urlpatterns = [
    path("read/", MainReadView, name="read"),
    path(
        "add-reading-log/<int:reading_id>/",
        AddReadingLogView.as_view(),
        name="add_reading_log",
    ),
    path("api/read/daily-logs/", daily_logs,name="daily-logs")
]
