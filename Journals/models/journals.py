import uuid

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from Cores.models import JournalDetailType, SubjectDiscipline

# Create your models here.


class Journal(models.Model):
    """
    Journals pathnering with publisher
    """

    def upload_to(instance, filename):
        return "%s/logo/%s" % (instance.name, filename)

    class FrequencyType(models.IntegerChoices):
        ANNAUL = 1, _("annual")
        BIANNUAL = 2, _("bi-annual")

    class ModelType(models.IntegerChoices):
        GOLD_ACCESS = 1, _("open-access")
        HYBRID = 2, _("hybrid")

    name = models.CharField(_("name"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    access_options = models.IntegerField(
        _("access_model"), default=ModelType.GOLD_ACCESS, choices=ModelType.choices
    )
    issn = models.CharField(_("ISSN"), max_length=255, blank=False)
    publication_start_year = models.CharField(
        _("publication_start_year"),
        max_length=255,
        default=str(timezone.now().today().year),
    )
    publication_frequency = models.IntegerField(
        _("publication_frequency"),
        choices=FrequencyType.choices,
        default=FrequencyType.BIANNUAL,
    )
    iso_abbreviation = models.CharField(
        _("ISO_abbreviation"), max_length=255, null=True, default=None
    )
    logo = models.ImageField(_("logo"), upload_to=upload_to)
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

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super(Journal, self).save(*args, **kwargs)

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


class JournalDetail(models.Model):
    """
    The details of the journal like aim and scope, Author guidelines etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content = models.JSONField(_("content"))
    detail_type = models.ForeignKey(JournalDetailType, on_delete=models.CASCADE)
    journal = models.ForeignKey(
        Journal, related_name="details", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        db_table = "journal_details"
        verbose_name = _("journal detail")
        verbose_name_plural = _("journal details")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.detail_type.name


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
        verbose_name = _("journal_view_log")
        verbose_name_plural = _("journal_view_logs")
        ordering = ["-created_at"]


class JournalVolume(models.Model):
    name = models.CharField(_("name"), max_length=200)
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
