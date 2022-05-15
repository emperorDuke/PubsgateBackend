from functools import wraps

from graphql_jwt.decorators import context
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id

from PeerReviewPortal.models import (
    JournalSubmission,
    JournalSubmissionEditorialTeam,
    ReviewerReport,
)
from Journals.permissions import JournalPermissionChoice


handling_permissions = (
    JournalPermissionChoice.GIVE_REPORTS.value,
    JournalPermissionChoice.EDIT_SUBMISSIONS.value,
)


def has_handling_permission(input_key="submission_id"):
    """
    The editor has a permission to handle the submission
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if "input" in kwargs and len(args) == 3:
                submission_id = kwargs["input"].get(input_key, None)
            else:
                submission_id = kwargs.get(input_key, None)

            if not submission_id:
                raise PermissionDenied("Submission ID is required")

            handler = JournalSubmissionEditorialTeam.objects.filter(
                journal_submission__pk=from_global_id(submission_id).id,
                editor__user__pk=context.user.pk,
                permissions__code_name__in=handling_permissions,
            )

            if not handler.exists():
                raise PermissionDenied(
                    "You do not have permission to perform this action"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator


def is_assigned_submission(input_key="submission_id"):
    """
    Checks if reviewer is invited to review submissions
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if "input" in kwargs and len(args) == 3:
                submission_id = kwargs["input"].get(input_key, None)
            else:
                submission_id = kwargs.get(input_key, None)

            if not submission_id:
                raise PermissionDenied("Submission ID is required")

            submission = JournalSubmission.objects.filter(
                reviewers__user__pk=context.user.pk, pk=from_global_id(submission_id).id
            )

            if not submission.exists():
                raise PermissionDenied(
                    "You do not have permission to perform this action"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator


def is_reviewer_report(input_key="report_id"):
    """
    Checks if reviewer owns the report
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if "input" in kwargs and len(args) == 3:
                report_id = kwargs["input"].get(input_key, None)
            else:
                report_id = kwargs.get(input_key, None)

            if not report_id:
                raise PermissionDenied("Report ID is required")

            report = ReviewerReport.objects.filter(
                pk=from_global_id(report_id).id, reviewer__user__pk=context.user.pk
            )

            if not report.exists():
                raise PermissionDenied(
                    "You do not have permission to perform this action"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator
