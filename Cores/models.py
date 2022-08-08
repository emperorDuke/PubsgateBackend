from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

# Create your models here.


class SubjectDiscipline(models.Model):
    """
    Subject disciplines supported by the publisher
    """

    name = models.CharField(_("discipline"), max_length=255, blank=False, unique=True)
    slug = models.CharField(_("slug"), max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("subject_discipline")
        verbose_name_plural = _("subject_disciplines")
        ordering = ("name",)
        db_table = "subject_displicines"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super(SubjectDiscipline, self).save(*args, **kwargs)


class TermOfService(models.Model):
    """
    Publishers terms of services
    """

    section = models.CharField(_("section"), max_length=255)
    question = models.CharField(_("question"), max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    discipline = models.ManyToManyField(SubjectDiscipline, related_name="terms")
    group = models.CharField(_("group"), max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("term_of_service")
        verbose_name_plural = _("terms_of_service")
        ordering = ("-created_at",)
        db_table = "terms_of_services"

    def __str__(self) -> str:
        return self.question


class ArticleType(models.Model):
    """T
    The types of articles supported by this publisher
    """

    name = models.CharField(_("name"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("article_type")
        verbose_name_plural = _("article_types")
        ordering = ("-created_at",)
        db_table = "article_types"

    def __str__(self) -> str:
        return self.name


class ArticleTypeSection(models.Model):
    """
    The form fields associated with articles types
    """

    name = models.CharField(_("name"), max_length=255)
    article_type = models.ForeignKey(
        ArticleType, related_name="sections", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("article_type_section")
        verbose_name_plural = _("article_type_sections")
        ordering = ("created_at",)
        db_table = "article_type_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "article_type"], name="unique_sections"
            )
        ]

    def __str__(self) -> str:
        return self.name


class JournalDetailType(models.Model):
    """
    Journal detail types
    e.g about, aim and scope, guidelines etc
    """

    name = models.CharField(_("name"), max_length=255)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        verbose_name = _("journal detail type")
        verbose_name_plural = _("journal detail types")
        ordering = ("created_at",)
        db_table = "journal_detail_types"

    def __str__(self) -> str:
        return self.name
