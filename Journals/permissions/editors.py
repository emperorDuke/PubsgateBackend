from functools import wraps
from graphql_jwt.decorators import user_passes_test, context
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id

from ..models import Editor, EditorialMember

editor_is_required = user_passes_test(
    lambda u: u.groups.filter(name="editors").exists()
)


def is_editor_journal(input_key="journal_id"):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if "input" in kwargs and len(args) == 3:
                journal_id = kwargs["input"].get(input_key, None)
            else:
                journal_id = kwargs.get(input_key, None)

            if not journal_id:
                raise PermissionDenied("Journal ID is required")

            editor = Editor.objects.filter(
                journals__pk=from_global_id(journal_id).id, user__pk=context.user.pk
            )

            if not editor.exists():
                raise PermissionDenied(
                    "You do not have permission to perform this action"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator


def editor_in_chief_required(input_key="journal_id"):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):

            if "input" in kwargs and len(args) == 3:
                journal_id = kwargs["input"].get(input_key, None)
                journal_id = from_global_id(journal_id).id
            else:
                journal_id = kwargs.get(input_key, None)

            if not journal_id:
                raise PermissionDenied("Journal ID is required")

            journal_member = EditorialMember.objects.filter(
                journal__pk=journal_id,
                role=EditorialMember.Role.CHIEF,
                editor__user__pk=context.user.pk,
            )

            if not journal_member.exists():
                raise PermissionDenied(
                    "You do not have permission to perform this action"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator
