from functools import wraps
from graphql_jwt.decorators import context
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id

from PeerReviewPortal.models import JournalSubmission, JournalSubmissionEditorialTeam
from Journals.permissions import JournalPermissionChoice


def has_handling_permission(calls_relay_mutation=False, input_key="submission_id"):
    """
    The editor has a permission to handle the submission
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if calls_relay_mutation:
                input = kwargs.get("input")
                submission_id = input.get(input_key, None)
            else:
                submission_id = kwargs.get(input_key, None)

            if not submission_id:
                raise PermissionDenied("Submission ID is required")

            handler = JournalSubmissionEditorialTeam.filter(
                journal_submission__pk=from_global_id(submission_id).id,
                editor__user__pk=context.user.pk,
                permissions__code_name__in=(
                    JournalPermissionChoice.GIVE_REPORTS.value,
                    JournalPermissionChoice.EDIT_SUBMISSIONS.value,
                ),
            )

            if not handler.exists():
                raise PermissionDenied("Forbiden action")

            return f(*args, **kwargs)

        return wrapper

    return decorator


def is_assigned_submission(calls_relay_mutation=False, input_key="submission_id"):
    """
    Checks if reviewer is invited to review submissions
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if calls_relay_mutation:
                input = kwargs.get("input")
                submission_id = input.get(input_key, None)
            else:
                submission_id = kwargs.get(input_key, None)

            if not submission_id:
                raise PermissionDenied("Submission ID is required")

            submission = JournalSubmission.objects.filter(
                reviewers__pk=context.user.pk, pk=from_global_id(submission_id).id
            )

            if not submission.exists():
                raise PermissionDenied("Forbiden action")

            return f(*args, **kwargs)

        return wrapper

    return decorator
