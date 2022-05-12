from django.apps import AppConfig


class PeerReviewPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "PeerReviewPortal"

    def ready(self):
        import PeerReviewPortal.signals.handlers
