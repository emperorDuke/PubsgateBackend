from django.db import models
from django.utils.translation import gettext_lazy as _


class JournalPermissionChoice(models.TextChoices):
    GIVE_REPORTS = "give_reports", _("Can give submission reports")
    VIEW_SUBMISSIONS = "view_submissions", _("Can view submissions")
    ASSIGN_EDITORS = "assign_editors", _("Can assign editors")
    ASSIGN_REVIEWERS = "assign_reviewers", _("Can assign reviewers")
    DELETE_SUBMISSIONS = "delete_submissions", _("Can delete submissions")
    EDIT_SUBMISSIONS = "edit_submissions", _("Can edit submissions")
