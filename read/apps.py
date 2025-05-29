from django.apps import AppConfig


class ReadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "read"

    def ready(self):
        import read.signals