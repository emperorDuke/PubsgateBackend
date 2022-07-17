import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .editors import Editor
from .journals import Journal, JournalPermission


class Role(models.Model):
    """
    Editor's role in a journal or manuscript submission
    """

    class Role(models.IntegerChoices):
        CHIEF = 1, _("Editor in chief")
        LINE = 2, _("Line editor")
        COPY = 3, _("Copy editor")
        SECTION = 4, _("Section editor")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    role = models.IntegerField(
        _("role"),
        blank=True,
        choices=Role.choices,
        default=Role.SECTION,
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.get_role_display()


class EditorialMember(Role):
    """
    Editor's role in a journal
    """

    editor = models.ForeignKey(
        Editor,
        related_name="journal_roles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    access_login = models.CharField(_("access_login"), max_length=255)
    permissions = models.ManyToManyField(
        JournalPermission, related_name="journal_roles"
    )
    journal = models.ForeignKey(
        Journal, related_name="editorial_members", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("editorial member")
        verbose_name_plural = _("editorial members")
        db_table = "journal_editorial_members"
