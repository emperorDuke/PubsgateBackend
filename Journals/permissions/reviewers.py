from functools import wraps
from graphql_jwt.decorators import context, user_passes_test
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id

from Journals.models.reviewers import Reviewer


reviewer_is_required = user_passes_test(
    lambda u: u.groups.filter(name="reviewers").exists()
)


def is_reviewer_journal(calls_relay_mutation=False, input_key="journal_id"):
    """
    Checks if the reviewer is a member of the given journal
    """

    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if calls_relay_mutation:
                input = kwargs.get("input")
                journal_id = input.get(input_key, None)
            else:
                journal_id = kwargs.get(input_key, None)

            id = from_global_id(journal_id).id

            if not journal_id:
                raise PermissionDenied("Journal ID is required")

            reviewer = Reviewer.objects.filter(
                journals__pk=from_global_id(journal_id).id, user__pk=context.user.pk
            )

            if not reviewer.exists():
                raise PermissionDenied("Forbiden action")

            return f(*args, **kwargs)

        return wrapper

    return decorator
