import uuid
from django.conf import settings

from django.db import models
from django.utils.translation import gettext_lazy as _

from .journals import Journal


class Reviewer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    is_anonymous = models.BooleanField(default=False)
    affiliation = models.CharField(_("affiliation"), max_length=255)
    journals = models.ManyToManyField(Journal, related_name="reviewers")
    started_at = models.DateTimeField(_("started_at"), auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "reviewers"
        verbose_name = _("reviewer")
        verbose_name_plural = _("reviewers")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return self.user.first_name
