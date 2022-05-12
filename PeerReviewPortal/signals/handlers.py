from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives

from Journals.permissions import JournalPermissionChoice

from .signals import has_notified_editor

from ..models import JournalSubmission, JournalSubmissionEditorialTeam


@receiver(post_save, sender=JournalSubmission)
def create_editorial_roles(sender, instance, created, **kwargs):

    if created:
        journal = instance.journal
        members = JournalSubmissionEditorialTeam.objects.bulk_create(
            [
                JournalSubmissionEditorialTeam(
                    **{
                        "role": getattr(JournalSubmissionEditorialTeam.Role, role),
                        "journal_submission": instance,
                        "editor": journal.get_editorial_board_member(
                            getattr(JournalSubmissionEditorialTeam.Role, role),
                        ),
                    }
                )
                for role in filter(
                    lambda role: role != JournalSubmissionEditorialTeam.Role.CHIEF.name,
                    JournalSubmissionEditorialTeam.Role.names,
                )
            ]
        )

        ## assign individual editorial team members permissions ##
        for member in members:
            permission_qs = journal.permissions.filter(
                code_name=JournalPermissionChoice.VIEW_SUBMISSIONS.value
            )
            member.permissions.add(*permission_qs)


@receiver(has_notified_editor)
def notify_editor(sender, **kwargs):
    email = kwargs.get("email")

    subject, from_email = (
        "Dispatched journal",
        "PGreview@pubsgate.com",
    )

    html_content = "<p> A manuscript was transfered to you for processing.</p>"
    text_content = "A manuscript was transfered to you for processing."

    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])

    msg.attach_alternative(html_content, "text/html")
    msg.send()
