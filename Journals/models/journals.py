import re
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from Cores.models import JournalDetailType, SubjectDiscipline

# Create your models here.


class Journal(models.Model):
    """
    Journals pathnering with publisher
    """

    name = models.CharField(_("journal name"), max_length=255, blank=False, unique=True)
    is_open_access = models.BooleanField(_("is_open_access"), default=False)
    subject_dicipline = models.ForeignKey(
        SubjectDiscipline, related_name="journals", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("journal")
        verbose_name_plural = _("journals")
        db_table = "journals"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def add_editorial_member(self, editor, role):
        """
        Create the editorial member role and assign editor to it
        """
        member = self.editorial_members.create(role=role, editor=editor, journal=self)

        permission_qs = self.permissions.all()
        member.permissions.add(*permission_qs)

        return member

    def assign_editor_role(self, editor, role):
        """
        Assign the editor a role in the journal
        """
        member = self.editorial_members.get(role=role.value)

        member.editor = editor
        member.save()

        return member

    def get_editorial_board_member(self, role):
        """
        Get the editor assign the role of interest
        """
        for member in self.editorial_members.all():
            if member.role == role.value:
                return member.editor


class JournalPermission(models.Model):
    """
    Journal internal permissions
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code_name = models.CharField(_("code_name"), max_length=255)
    label = models.CharField(_("label"), max_length=255)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    journal = models.ForeignKey(
        Journal, related_name="permissions", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("journal permission")
        verbose_name_plural = _("journal permissions")
        db_table = "journal_permissions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.code_name


class JournalSubjectArea(models.Model):
    """
    Subjects supported by journal
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(_("name"), max_length=255)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    journal = models.ForeignKey(
        Journal, related_name="subjects", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "journal_subjects"
        verbose_name = _("journal subject")
        verbose_name_plural = _("journal subjects")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class JournalBanner(models.Model):
    def upload_to(instance, filename):
        return "%s/banners/%s" % (instance.journal.name, filename)

    class PageSection(models.TextChoices):
        MAIN = (
            "main",
            _("main"),
        )
        MID = (
            "middle",
            _("middle"),
        )
        BOT = (
            "bottom",
            _("bottom"),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.ImageField(_("file"), upload_to=upload_to)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    journal = models.ForeignKey(
        Journal, related_name="banners", on_delete=models.CASCADE
    )

    section = models.CharField(
        _("section"),
        max_length=70,
        choices=PageSection.choices,
        default=PageSection.MAIN,
    )

    class Meta:
        db_table = "journal_banners"
        verbose_name = _("journal_banner")
        verbose_name_plural = _("journal_banners")
        ordering = ["created_at"]


class JournalDetail(models.Model):
    """
    The details of the journal like aim and scope, Author guidelines etc.
    """

    def upload_to(instance, filename):
        return "%s/details/%s" % (instance.journal.name, filename)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.FileField(_("file"), upload_to=upload_to)
    detail = models.TextField(_("datail"), blank=True, null=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    detail_type = models.ForeignKey(JournalDetailType, on_delete=models.CASCADE)

    journal = models.ForeignKey(
        Journal, related_name="details", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "journal_details"
        verbose_name = _("journal detail")
        verbose_name_plural = _("journal details")
        ordering = ["created_at"]


class JournalViewLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ip_address = models.GenericIPAddressField(_("ip_address"))
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="view_logs",
        on_delete=models.CASCADE,
    )
    journal = models.ForeignKey(
        Journal, related_name="view_logs", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "journal_view_logs"
        verbose_name = _("journal_view_log")
        verbose_name_plural = _("journal_view_logs")
        ordering = ["-created_at"]


class JournalVolume(models.Model):
    name = models.CharField(_("name"), max_length=200)
    added_at = models.DateTimeField(_("added_at"), auto_now_add=True)

    journal = models.ForeignKey(
        Journal, related_name="volumes", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "journal_volumes"
        verbose_name = _("journal_volume")
        verbose_name_plural = _("journal_volumes")
        ordering = ["-added_at"]

    def __str__(self) -> str:
        return self.name


class JournalVolumeIssue(models.Model):
    name = models.CharField(_("name"), max_length=200)
    is_special = models.BooleanField(default=False)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    volume = models.ForeignKey(
        JournalVolume, related_name="issues", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "journal_volume_issues"
        verbose_name = _("journal_volume_issue")
        verbose_name_plural = _("journal_volume_issues")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class JournalReportQuestion(models.Model):
    question = models.CharField(_("question"), max_length=255)
    hint = models.CharField(_("hint"), max_length=255)
    has_long_answer = models.BooleanField(_("has_long_answer"), default=False)
    options = models.JSONField(_("options"), blank=True, null=True)
    journal = models.ForeignKey(
        Journal, related_name="review_questions", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("journal_report_question")
        verbose_name_plural = _("journal_report_questions")
        ordering = ["created_at"]
        db_table = "journal_report_questions"

    def __str__(self) -> str:
        return self.question


# class JournalSetting(models.Model):
#     label = models.CharField(_("label"), max_length=255)
#     hint = models.CharField(_("hint"), max_length=255)
#     options = models.JSONField(_("options"), blank=True, null=True)
#     group = models.CharField(_("group"), max_length=255)
#     journal = models.ForeignKey(
#         Journal, related_name="settings", on_delete=models.CASCADE
#     )


# class JournalSettingState(models.Model):
#     setting = models.ForeignKey(
#         JournalSetting, related_name="states", on_delete=models.CASCADE
#     )
#     state = models.CharField(_("state"), max_length=255)
