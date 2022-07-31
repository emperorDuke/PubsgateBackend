import random
import string

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

from ..models import Journal, JournalPermission, Reviewer, Editor, EditorialMember
from ..permissions import JournalPermissionChoice


@receiver(post_save, sender=Editor)
def add_editor_to_group(sender, instance, created, *args, **kwargs):
    if created:
        editor_group = Group.objects.get(name="editors")

        if editor_group:
            instance.user.groups.add(editor_group)


@receiver(post_save, sender=Reviewer)
def add_editor_to_group(sender, instance, created, *args, **kwargs):
    if created:
        reviewer_group = Group.objects.get(name="reviewers")

        if reviewer_group:
            instance.user.groups.add(reviewer_group)


@receiver(post_save, sender=Journal)
def create_editorial_board_roles(sender, instance, created, *args, **kwargs):
    if created:
        JournalPermission.objects.bulk_create(
            [
                JournalPermission(
                    **{
                        "journal": instance,
                        "code_name": code_name,
                        "label": label,
                    }
                )
                for code_name, label in JournalPermissionChoice.choices
            ]
        )

        members = EditorialMember.objects.bulk_create(
            [
                EditorialMember(
                    **{
                        "role": getattr(EditorialMember.Role, role),
                        "journal": instance,
                        ### this is a temporary solution
                        "access_login": make_password(
                            "".join(
                                random.choice(string.ascii_letters) for i in range(6)
                            )
                        ),
                    }
                )
                for role in filter(
                    lambda role: role != EditorialMember.Role.CHIEF.name,
                    EditorialMember.Role.names,
                )
            ]
        )

        for member in members:
            permission_qs = instance.permissions.filter(
                code_name=JournalPermissionChoice.VIEW_SUBMISSIONS.value
            )
            member.permissions.add(*permission_qs)
