from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import TruncDate
from django.views import View
from django.db.models import Sum

from read.models import Reading, ReadingLog


# Create your views here.
def MainReadView(request):
    currently_reading: Reading = Reading.objects.filter(current_status="R")
    return render(
        request,
        "read/main_read_page.html",
        {
            "currently_reading": currently_reading,
        },
    )


def daily_logs(request):
    """Provides JSON data for the heatmap"""
    daily_totals = (
        ReadingLog.objects.filter(page_difference__gt=0)
        .annotate(date_trunc=TruncDate("date"))
        .values("date_trunc")
        .annotate(total=Sum("page_difference"))
        .order_by("date_trunc")
    )

    data = [
        {"date": entry["date_trunc"].isoformat(), "value": entry["total"]}
        for entry in daily_totals
    ]
    return JsonResponse(data, safe=False)


class AddReadingLogView(View):
    def get(self, request, reading_id):
        reading = get_object_or_404(Reading, id=reading_id)
        last_log = reading.logs.order_by("-date").first()

        # Use a more explicit check for log type
        if last_log and last_log.pages_read is not None:
            last_log_type = "page"
            last_log_value = last_log.pages_read
        else:
            last_log_type = "percent"
            last_log_value = last_log.percentage_read if last_log else 0

        if request.headers.get("HX-Request"):
            # Render only the dropdown options
            # dropdown_html = render_to_string(
            #     "read/partials/dropdown_options.html", {"last_log_type": last_log_type}
            # )
            return render(
                request,
                "read/partials/dropdown_options.html",
                {"last_log_type": last_log_type},
            )

        return render(
            request,
            "read/main_read_page.html",
            {
                "last_log_type": last_log_type,
                "last_log_value": last_log_value,
                "reading": reading,
            },
        )

    def post(self, request, reading_id):
        reading = get_object_or_404(Reading, id=reading_id)
        log_type = request.POST.get("log_type").strip().replace('\\"', "")
        value = int(request.POST.get("value", 0))
        last_log = reading.logs.order_by("-date").first()
        last_log_value = (
            last_log.pages_read if log_type == "page" else last_log.percentage_read
        )
        if value < last_log_value:
            return JsonResponse(
                {
                    "success": False,
                    "errors": "Value must be greater than the last log",
                },
                status=400,
            )
        ReadingLog.objects.create(
            reading=reading,
            pages_read=value if log_type == "page" else None,
            percentage_read=value if log_type == "percent" else None,
        )
        return render(
            request, "read/partials/progress_update.html", {"reading": reading}
        )
