from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ReadingLog
from django.db import transaction


@receiver(post_save, sender=ReadingLog)
def update_subsequent_on_save(sender, instance, **kwargs):
    """Handle updates to existing logs"""
    instance.update_subsequent_logs()


@receiver(post_delete, sender=ReadingLog)
def update_after_delete(sender, instance, **kwargs):
    # Find new previous log
     with transaction.atomic():
        prev_log = (
            ReadingLog.objects.filter(reading=instance.reading)
            .filter(date__lt=instance.date)
            .order_by("-date")
            .first()
        )

        # Update subsequent logs
        if prev_log:
            prev_log.update_subsequent_logs()
        else:
            # If no previous log, update from start
            first_log = (
                ReadingLog.objects.filter(reading=instance.reading).order_by("date").first()
            )
            if first_log:
                first_log.update_subsequent_logs()
