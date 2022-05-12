from django.apps import AppConfig


class SubmissionPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SubmissionPortal"

    def ready(self):
        import SubmissionPortal.signals.handlers
