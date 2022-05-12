import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from Journals.models import Journal, JournalPermission, Role, Editor, Reviewer
from Journals.models.journals import JournalReportQuestion
from SubmissionPortal.models import AuthorSubmission

# Create your models here.


class JournalSubmission(models.Model):
    author_submission = models.OneToOneField(AuthorSubmission, on_delete=models.CASCADE)
    reviewers = models.ManyToManyField(Reviewer, related_name="submissions")
    stage = models.CharField(_("stage"), max_length=255)
    is_accepted = models.DateTimeField(
        _("is_accepted"), null=True, blank=True, default=None
    )
    journal = models.ForeignKey(
        Journal, related_name="submissions", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    class Meta:
        db_table = "journal_submissions"
        verbose_name = _("journal submission")
        verbose_name_plural = _("journal submissions")
        ordering = ("-created_at",)


class JournalSubmissionEditorialTeam(Role):
    """
    Editor's role in a journal submission
    """

    journal_submission = models.ForeignKey(
        JournalSubmission, related_name="editorial_members", on_delete=models.CASCADE
    )
    permissions = models.ManyToManyField(
        JournalPermission, related_name="journal_submission_roles"
    )
    editor = models.ForeignKey(
        Editor,
        related_name="submission_editorial_roles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("journal submission editorial team")
        verbose_name_plural = _("journal submission editorial teams")
        db_table = "journal_submission_editorial_teams"
        ordering = ("-created_at",)


class EditorReport(models.Model):
    """
    Journal submissions Editors report
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    report = models.TextField(_("report"))
    editor = models.ForeignKey(Editor, related_name="reports", on_delete=models.CASCADE)
    journal_submission = models.ForeignKey(
        JournalSubmission, related_name="editors_reports", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        db_table = "journal_submission_editor_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["report", "editor", "journal_submission"],
                name="unique_editor_report",
            )
        ]

    def __str__(self):
        return self.report


class ReviewerReport(models.Model):
    """
    Reviewer structure report
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    journal_submission = models.ForeignKey(
        JournalSubmission, related_name="reviewer_reports", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("reviewer_report")
        verbose_name_plural = _("reviewer_reports")
        ordering = ("-created_at",)
        db_table = "reviewer_reports"
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "journal_submission"], name="unique_reviewer_report"
            )
        ]


class ReviewerReportSection(models.Model):
    """
    Review report sections
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    response = models.TextField(_("response"))
    section = models.ForeignKey(JournalReportQuestion, on_delete=models.CASCADE)
    report = models.ForeignKey(
        ReviewerReport, on_delete=models.CASCADE, related_name="sections"
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("reviewer_report_section")
        verbose_name_plural = _("reviewer_report_sections")
        ordering = ("-created_at",)
        db_table = "reviewer_report_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["report", "section"],
                name="unique_report_section",
            )
        ]

    def __str__(self) -> str:
        return self.section.question
