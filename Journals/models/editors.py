import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .journals import Journal

# Create your models here.


class Editor(models.Model):
    """
    Editors working in a journal
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    affiliation = models.CharField(_("affiliation"), max_length=300)
    phone_number = models.CharField(_("phone number"), max_length=255)
    specialisation = models.CharField(_("specialisation"), max_length=255)
    journals = models.ManyToManyField(Journal, related_name="editors")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(_("started at"), auto_now_add=True)

    class Meta:
        verbose_name = "editor"
        verbose_name_plural = "editors"
        ordering = ["-started_at"]
        db_table = "editors"

    def __str__(self) -> str:
        return "%s, %s" % (self.user.first_name, self.affiliation)
