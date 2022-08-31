import random
import string
import uuid

from Cores.models import Discipline, InformationHeading
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphql import GraphQLError

# Create your models here.


class Journal(models.Model):
    """
    Journals pathnering with publisher
    """

    def upload_to(instance, filename):
        return "%s/logo/%s" % (instance.name, filename)

    class PublicationFrequency(models.IntegerChoices):
        ANNUALLY = 1, _("annually")
        BI_ANNUALLY = 2, _("bi-annually")
        TRI_ANNUALLY = 3, _("tri-annually")
        QUARTERLY = 4, _("quarterly")

    class ModelType(models.IntegerChoices):
        OPEN_ACCESS = 1, _("open-access")
        PARTIAL_ACCESS = 2, _("partial-access")

    name = models.CharField(_("name"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    access_options = models.IntegerField(
        _("access_model"), default=ModelType.OPEN_ACCESS, choices=ModelType.choices
    )
    issn = models.CharField(_("ISSN"), max_length=255, blank=False)
    publication_start_date = models.DateField(
        _("publication_start_date"), default=timezone.now
    )
    publication_frequency = models.IntegerField(
        _("publication_frequency"),
        choices=PublicationFrequency.choices,
        default=PublicationFrequency.BI_ANNUALLY,
    )
    iso_abbreviation = models.CharField(
        _("ISO_abbreviation"), max_length=255, null=True, default=None
    )
    logo = models.ImageField(_("logo"), upload_to=upload_to, null=True, blank=True)
    discipline = models.ForeignKey(
        Discipline, related_name="journals", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("journal")
        verbose_name_plural = _("journals")
        db_table = "journals"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super(Journal, self).save(*args, **kwargs)

    def make_editor_chief(self, editor):
        """
        Create the editorial member role and assign editor to it
        """
        if self.editorial_members.filter(role=1).exists():
            raise GraphQLError("an editor-in-chief already exists")

        member = self.editorial_members.create(
            role=1,
            editor=editor,
            journal=self,
            access_login=make_password(
                "".join(random.choice(string.ascii_letters) for i in range(6))
            ),
        )

        permission_qs = self.permissions.all()
        member.permissions.add(*permission_qs)

        return member

    def assign_editor_role(self, editor, role):
        """
        Assign the editor a role in the journal
        """
        if role.name == "CHIEF":
            raise GraphQLError("action forbidden: cannot make editor a chief")

        ## remove the editor from old role
        self.editorial_members.filter(editor=editor).update(editor=None)

        ## assign the editor a new role
        self.editorial_members.filter(role=role.value).update(editor=editor)

    def get_editorial_board_member(self, role):
        """
        Get the editor assign the role of interest
        """
        for member in self.editorial_members.all():
            if member.role == role.value:
                return member.editor


class RecruitmentApplication(models.Model):
    """
    Journals editor recruitment application lists
    """

    class Status(models.IntegerChoices):
        PROCESSING = 1, _("processing")
        ACCEPTED = 2, _("accept")
        REJECTED = 3, _("rejected")
        COMPLETED = 4, _("completed")

    class Role(models.IntegerChoices):
        EDITOR = 1, _("editor")
        REVIEWER = 2, _("reviewer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="editorial_applications",
        on_delete=models.CASCADE,
    )
    role = models.PositiveIntegerField(
        _("role"), default=Role.EDITOR, choices=Role.choices
    )
    journal = models.ForeignKey(
        Journal,
        related_name="recruitment_applications",
        on_delete=models.CASCADE,
    )
    status = models.IntegerField(
        _("recruitment_status"),
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("recruitment application")
        verbose_name_plural = _("recruitment applications")
        db_table = "recruitment_applications"
        ordering = ["-created_at"]


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
        constraints = [
            models.UniqueConstraint(
                fields=["name", "journal"], name="unique_journal_subject_areas"
            )
        ]

    def __str__(self) -> str:
        return self.name


class JournalBanner(models.Model):
    def upload_to(instance, filename):
        return "%s/banners/%s" % (instance.journal.name, filename)

    class PageSection(models.IntegerChoices):
        MAIN = 1, _("main")
        MIDDLE = 2, _("middle")
        BOTTOM = 3, _("bottom")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.ImageField(_("file"), upload_to=upload_to)
    journal = models.ForeignKey(
        Journal, related_name="banners", on_delete=models.CASCADE
    )
    section = models.IntegerField(
        _("section"),
        choices=PageSection.choices,
        default=PageSection.MAIN,
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        db_table = "journal_banners"
        verbose_name = _("journal_banner")
        verbose_name_plural = _("journal_banners")
        ordering = ["created_at"]


class JournalInformation(models.Model):
    """
    The details of the journal like aim and scope, Author guidelines etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content = models.JSONField(_("content"), blank=True, null=True)
    heading = models.ForeignKey(InformationHeading, on_delete=models.CASCADE)
    journal = models.ForeignKey(
        Journal, related_name="informations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        db_table = "journal_informations"
        verbose_name = _("journal information")
        verbose_name_plural = _("journal informations")
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["heading", "journal"], name="unique_journal_headings"
            )
        ]

    def __str__(self) -> str:
        return self.heading.name


class JournalViewLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ip_address = models.GenericIPAddressField(_("ip_address"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="view_logs",
        on_delete=models.CASCADE,
    )
    journal = models.ForeignKey(
        Journal, related_name="view_logs", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        db_table = "journal_view_logs"
        verbose_name = _("journal view log")
        verbose_name_plural = _("journal view logs")
        ordering = ["-created_at"]


class JournalVolume(models.Model):
    name = models.CharField(_("name"), max_length=200)
    is_active = models.BooleanField(_("is_active"), default=False)
    journal = models.ForeignKey(
        Journal, related_name="volumes", on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(_("added_at"), auto_now_add=True)

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
    is_active = models.BooleanField(_("is_active"), default=False)
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
        verbose_name = _("journal report question")
        verbose_name_plural = _("journal report questions")
        ordering = ["created_at"]
        db_table = "journal_report_questions"

    def __str__(self) -> str:
        return self.question
