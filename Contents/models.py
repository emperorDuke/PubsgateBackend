import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from Cores.models import ArticleTypeSection

from Journals.models import Journal, JournalSubjectArea

# Create your models here.


class Manuscript(models.Model):
    """
    Authors manuscript
    """

    title = models.CharField(_("title"), max_length=255)
    journal = models.ForeignKey(
        Journal, related_name="manuscripts", on_delete=models.PROTECT
    )
    subject_area = models.ForeignKey(
        JournalSubjectArea,
        related_name="manuscripts",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    word_count = models.PositiveIntegerField(
        _("word_count"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("manuscript")
        verbose_name_plural = _("manuscripts")
        ordering = ["-created_at"]
        db_table = "manuscripts"
        indexes = [models.Index(fields=["title"], name="title_idx")]

    def __str__(self) -> str:
        return self.journal.name


class ManuscriptSection(models.Model):
    """
    Sections of manuscript
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(
        Manuscript, related_name="sections", on_delete=models.CASCADE
    )
    section = models.ForeignKey(ArticleTypeSection, on_delete=models.CASCADE)
    content = models.TextField(_("content"), blank=True, null=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("manuscript_section")
        verbose_name_plural = _("manuscript_sections")
        ordering = ("created_at",)
        db_table = "manuscript_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["section", "manuscript"], name="unique_section"
            )
        ]

    def __str__(self):
        return self.section.name


class ManuscriptSubSection(models.Model):
    """
    Manuscript section sub sections
    """

    class Level(models.IntegerChoices):
        LEVEL_1 = 1, _("Level 1")
        LEVEL_2 = 2, _("Level 2")
        LEVEL_3 = 3, _("Level 3")
        LEVEL_4 = 4, _("Level 4")
        LEVEL_5 = 5, _("Level 5")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript_section = models.ForeignKey(
        ManuscriptSection, related_name="sub_sections", on_delete=models.CASCADE
    )
    level = models.IntegerField(
        _("level"), default=Level.LEVEL_1, choices=Level.choices
    )
    heading = models.CharField(_("heading"), max_length=255)
    body = models.TextField(_("body"))
    parent_id = models.UUIDField(_("parent_id"), blank=True, null=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("manuscript_sub_section")
        verbose_name_plural = _("manuscript_sub_sections")
        ordering = ("created_at",)
        db_table = "manuscript_sub_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["manuscript_section", "heading"], name="unique_heading"
            )
        ]

    def __str__(self):
        return self.heading


class ManuscriptFile(models.Model):
    """
    File associated with the manuscript
    """

    def file_path(instance, filename):
        journal_name = instance.manuscript.journal.name
        return "%s/manuscripts/%s/%s" % (journal_name, instance.manuscript.id, filename)

    class FileType(models.IntegerChoices):
        TABLE = 1, _("Table")
        FIGURE = 2, _("Figure")

    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    version = models.PositiveIntegerField(_("version"), blank=True, default=1)
    label_no = models.PositiveIntegerField(_("label_number"))
    label_on_manuscript = models.CharField(_("label_on_manuscript"), max_length=255)
    file_type = models.IntegerField(
        _("file_type"), choices=FileType.choices, default=FileType.FIGURE
    )
    doc = models.FileField(
        _("file"), max_length=255, blank=True, null=True, upload_to=file_path
    )
    image = models.ImageField(
        _("image"), max_length=255, blank=True, null=True, upload_to=file_path
    )
    manuscript = models.ForeignKey(
        Manuscript, related_name="files", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("manuscript_file")
        verbose_name_plural = _("manuscript_files")
        ordering = ["file_type", "label_no"]
        db_table = "manuscript_files"

    def __str__(self) -> str:
        return self.label_on_manuscript


class ManuscriptAuthor(models.Model):
    """
    Authors of the manuscript
    """

    first_name = models.CharField(_("first_name"), max_length=255)
    last_name = models.CharField(_("last_name"), max_length=255)
    email = models.EmailField(_("email"))
    affiliation = models.CharField(_("affiliation"), max_length=255)
    rank = models.PositiveBigIntegerField(_("rank"), default=1)
    is_corresponding = models.BooleanField(
        _("is_corresponding"), blank=True, default=False
    )
    manuscript = models.ForeignKey(
        Manuscript, related_name="authors", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("manuscript_author")
        verbose_name_plural = _("manuscript_authors")
        ordering = ("rank",)
        db_table = "manuscript_authors"
        constraints = [
            models.UniqueConstraint(
                fields=["rank", "manuscript", "email"], name="unique_author"
            )
        ]

    def __str__(self) -> str:
        return "s% s%" % (self.first_name, self.last_name)


# Keys words associaited with the manuscript
class ManuscriptKeywordTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(_("tag"), max_length=255)
    manuscript = models.ForeignKey(
        Manuscript, related_name="keyword_tags", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("manuscript_keyword")
        verbose_name_plural = _("manuscript_keywords")
        ordering = ("-created_at",)
        db_table = "manuscript_keyword_tags"
        constraints = [
            models.UniqueConstraint(fields=["tag", "manuscript"], name="unique_tag")
        ]

    def __str__(self) -> str:
        return self.tag


class ManuscriptReference(models.Model):
    """
    References associated with a manuscript
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=255)
    authors = models.JSONField(_("author"))
    year = models.CharField(_("year"), max_length=255)
    issue = models.CharField(_("issue"), max_length=200, blank=True, null=True)
    DOI = models.CharField(_("DOI"), max_length=255, blank=True, null=True)
    volume = models.CharField(_("volume"), max_length=100, blank=True, null=True)
    publisher = models.CharField(_("publisher"), max_length=255, blank=True, null=True)
    page_start = models.PositiveIntegerField(_("page_start"), blank=True, null=True)
    page_end = models.PositiveIntegerField(_("page_end"), blank=True, null=True)
    manuscript = models.ForeignKey(
        Manuscript, related_name="references", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("manuscript_reference")
        verbose_name_plural = _("manuscript_references")
        db_table = "manuscript_references"

    def __str__(self) -> str:
        return self.title
