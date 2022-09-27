from datetime import timedelta
from functools import wraps

import jwt
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import context, user_passes_test
from graphql_jwt.exceptions import PermissionDenied
from graphql_relay import from_global_id
from Journals.models.journals import JournalAuthToken

from ..models import Editor, EditorialMember, Journal

editor_is_required = user_passes_test(
    lambda u: u.groups.filter(name="editors").exists()
)


def manager_login_required(input_key="journal_id"):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            journal_id = kwargs.get(input_key, None)
            enc_token = kwargs.get("manager_auth_token", None)

            if not journal_id:
                raise PermissionDenied("Journal ID is required")

            if not enc_token:
                raise PermissionDenied("Manager auth token is required")

            if not JournalAuthToken.objects.filter(token=enc_token).exists():
                raise PermissionDenied("Journal auth token does not exist")

            journal = get_object_or_404(Journal, id=journal_id)

            decoded = jwt.decode(
                enc_token,
                journal.secret,
                issuer=journal.name,
                algorithms=["HS256"],
                leeway=timedelta(seconds=10),
                options={
                    "require": ["exp", "iss"],
                    "verify_exp": True,
                    "verify_iss": True,
                },
            )

            if not context.user.email == decoded["email"]:
                raise PermissionDenied("invalid user")

            return f(*args, **kwargs)

        return wrapper

    return decorator


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
