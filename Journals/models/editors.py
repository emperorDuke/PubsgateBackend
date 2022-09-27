import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .journals import Journal

# Create your models here.


class Editor(models.Model):
    """
    Editors working in a journal
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    affiliation = models.CharField(
        _("affiliation"), max_length=300, blank=True, null=True
    )
    phone_number = models.CharField(
        _("phone number"), max_length=255, blank=True, null=True
    )
    specialisation = models.CharField(
        _("specialisation"), max_length=255, blank=True, null=True
    )
    journals = models.ManyToManyField(
        Journal, related_name="editors", through="EditorJournalActivity"
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("started at"), auto_now_add=True)

    class Meta:
        verbose_name = "editor"
        verbose_name_plural = "editors"
        ordering = ["-created_at"]
        db_table = "editors"

    def __str__(self) -> str:
        return "%s, %s" % (self.user.first_name, self.affiliation)


class EditorJournalActivity(models.Model):
    """
    Editor's Journal activity
    """

    editor = models.ForeignKey(
        Editor, related_name="journal_activities", on_delete=models.CASCADE
    )
    journal = models.ForeignKey(
        Journal, related_name="editor_activities", on_delete=models.CASCADE
    )
    last_login = models.DateTimeField(_("last_login"), default=timezone.now)
    started_at = models.DateTimeField(_("started_at"), auto_now_add=True)

    class Meta:
        verbose_name = "editor journal activity"
        verbose_name_plural = "editor journal activities"
        ordering = ["-last_login"]
        db_table = "editor_journal_activities"
        constraints = [
            models.UniqueConstraint(
                fields=["editor", "journal"], name="unique_editor_journal_activities"
            )
        ]
