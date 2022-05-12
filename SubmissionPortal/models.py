import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from Cores.models import TermOfService
from Contents.models import Manuscript

# Create your models here.


class AuthorSubmission(models.Model):
    class ArticleType(models.IntegerChoices):
        RESEARCH_ARTICLE = 1, _("research article")
        REVIEW_ARTICLE = 2, _("review article")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE
    )
    article_type = models.IntegerField(_("article_type"), choices=ArticleType.choices)
    manuscript = models.OneToOneField(
        Manuscript, related_name="author_submission", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("submission")
        verbose_name_plural = _("submissions")
        ordering = ["-created_at"]
        db_table = "author_submissions"


class SubmissionStatus(models.Model):
    class SubmissionStatus(models.IntegerChoices):
        OFR = 1, _("out for review")
        WE = 2, _("is with editor")
        MA = 3, _("accepted")
        PU = 4, _("published")

    stage = models.IntegerField(
        _("stage"),
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.WE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author_submission = models.OneToOneField(
        AuthorSubmission, related_name="status", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("submission_status")
        verbose_name_plural = _("submission_status")
        ordering = ["-updated_at"]
        db_table = "author_submission_statuses"

    def __str__(self) -> str:
        return self.stage


class SubmissionFile(models.Model):
    def file_path(instance, filename):
        return "submissions/%s/%s" % (
            "_".join(instance.get_file_type_display().lower().split(" ")),
            filename,
        )

    class FileType(models.IntegerChoices):
        COVER_LETTER = 1, _("Cover letter")
        MANUSCRIPT = 2, _("Manuscript")
        SUPPLEMENTARY_DATA = 3, _("Supplementary data")

    author_submission = models.ForeignKey(
        AuthorSubmission, related_name="files", on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField(_("version"), blank=True, default=1)
    file_type = models.PositiveIntegerField(_("file type"), choices=FileType.choices)
    file = models.FileField(_("file"), max_length=255, upload_to=file_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("submission_file")
        verbose_name_plural = _("submission_files")
        ordering = ["-created_at"]
        db_table = "author_submission_files"

    def __str__(self) -> str:
        return self.file_type


# users agreement before manuscript submission
class SubmissionConditionAgreement(models.Model):
    class ResponseType(models.IntegerChoices):
        YES = 1, _("YES")
        NO = 2, _("NO")

    statement = models.TextField(_("statement"), blank=True, null=True)
    documented_at = models.DateTimeField(_("documented_at"), auto_now_add=True)
    response = models.IntegerField(
        _("response"), choices=ResponseType.choices, default=ResponseType.NO
    )
    author_submission = models.ForeignKey(
        AuthorSubmission, related_name="agreements", on_delete=models.CASCADE
    )
    term = models.ForeignKey(TermOfService, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("submission_condition_agreement")
        verbose_name = _("submission_condition_agreements")
        ordering = ["documented_at"]
        db_table = "author_submission_condition_agreements"

    def __str__(self) -> str:
        return self.term.question


# Manuscript APC
class ArticleProcessingCharge(models.Model):
    class PaymentStatus(models.IntegerChoices):
        SUCCESS = 1, _("successful")
        PENDING = 2, _("pending")
        FAILED = 3, _("failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(_("amount"), decimal_places=2, max_digits=15)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        _("payment status"),
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    author_submission = models.OneToOneField(
        AuthorSubmission, related_name="APC", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("article_processing_charge")
        verbose_name_plural = _("article_processing_charges")
        ordering = ["-created_at"]
        db_table = "article_processing_charges"

    def __str__(self) -> str:
        return self.amount
