import json
import graphene

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.core.signing import Signer

from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from Contents.models import ManuscriptSection
from Journals.models.journals import JournalReportQuestion

from Journals.permissions import (
    editor_in_chief_required,
    editor_is_required,
    is_editor_journal,
    reviewer_is_required,
)

from Journals.models import Journal, JournalPermission, Editor
from .input_types import EditorInput, ReportSectionInput
from .permissions import (
    has_handling_permission,
    is_assigned_submission,
    handling_permissions,
)

from .models import (
    EditorReport,
    JournalSubmission,
    JournalSubmissionEditorialTeam,
    ReviewerReport,
    ReviewerReportSection,
)
from .nodes import EditorReportNode, JournalSubmissionNode, ReviewerReportNode
from .signals.signals import has_notified_editor


class CreateJournalSubmissionMutation(graphene.relay.ClientIDMutation):
    """
    Create journal submission when author accept there submissions
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        author_submission_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        author_submission_id = input.get("author_submission_id")

        user = info.context.user
        author_submission = user.submissions.select_related("manuscript__journal").get(
            pk=from_global_id(author_submission_id).id
        )

        journal_submission = JournalSubmission.objects.create(
            author_submission=author_submission,
            stage="initial submission",
            journal=author_submission.manuscript.journal,
        )

        return CreateJournalSubmissionMutation(
            submission=journal_submission, message="success"
        )


class InviteReviewerMutation(graphene.relay.ClientIDMutation):
    """
    Invite nominated reviewers to review a submission
    """

    message = graphene.String()

    class Input:
        email_addresses = graphene.List(graphene.String, required=True)
        submission_id = graphene.ID(required=True)
        journal_id = graphene.ID(required=True)

    @classmethod
    @has_handling_permission()
    @is_editor_journal()
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        email_addresses = input.get("email_addresses")

        signer = Signer()

        journal_id = input.get("journal_id")
        submission_id = input.get("submission_id")

        signed_JSID = signer.sign_object(
            {
                "journal_id": from_global_id(journal_id).id,
                "submission_id": from_global_id(submission_id).id,
            }
        )

        journal = Journal.objects.get(pk=from_global_id(journal_id).id)
        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

        abstract_section = ManuscriptSection.objects.get(
            manuscript__author_submission__journal_submission__pk=submission.pk,
            section__name="abstract",
        )

        abstract = json.loads(abstract_section.content)[0]["children"][0]["text"]
        url = "/peer-review/invite?JSID={0}".format(signed_JSID)

        from_email = "{0}@pubsgate.com".format(journal.name)
        subject = "Invitation to be a reviewer for {0} journal".format(journal.name)
        text_content = "We are inviting you to review a manuscript"
        to = email_addresses
        html_content = (
            "<div><p> We are inviting you to review a manuscript,"
            "below this message is the abstract click on the link below to accept out invitation</p>"
            "<p>{0}</p><a>{1}</a></div>"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content.format(abstract, url), "text/html")
        msg.send()

        return InviteReviewerMutation(message="success")


class AcceptReviewerInvitation(graphene.relay.ClientIDMutation):
    """
    Accept invited reviewers
    """

    message = graphene.String()
    submission = graphene.Field(JournalSubmissionNode)

    class Input:
        jsid = graphene.String(required=True)

    @classmethod
    @reviewer_is_required
    @login_required
    def mutate(cls, root, info, input):
        signer = Signer()

        jsid = signer.unsign_object(input.get("jsid"))

        submission_id = jsid.get("submission_id")
        journal_id = jsid.get("journal_id")

        reviewer = info.context.user.reviewer

        submission = JournalSubmission.objects.get(
            pk=submission_id,
            journal__pk=journal_id,
        )

        submission.reviewers.add(reviewer)

        return AcceptReviewerInvitation(message="success", submission=submission)


class AcceptSubmission(graphene.relay.ClientIDMutation):
    """
    Accept submissions after critical and thorough reviews
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        journal_id = graphene.ID(required=True)
        submission_id = graphene.ID(required=True)
        is_accepted = graphene.Boolean(required=True)

    @classmethod
    @editor_in_chief_required()
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        is_accepted = input.get("is_accepted")
        submission_id = input.get("submission_id")

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)
        submission.is_accepted = timezone.now() if is_accepted else None
        submission.save()

        message = "success" if submission else "failed"

        return AcceptSubmission(message=message, submission=submission)


class AssignHandlingEditorsMutation(graphene.relay.ClientIDMutation):
    """
    Assign editors to a Journal submission and edit
    the submission where necessary
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        journal_id = graphene.ID(required=True)
        submission_id = graphene.ID(required=True)
        editors = graphene.List(EditorInput, required=True)

    @classmethod
    @editor_in_chief_required()
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        editors = input.get("editors")
        submission_id = input.get("submission_id")

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

        editor_data = {
            from_global_id(editor["editor_id"]).id: editor["role"] for editor in editors
        }

        editor_qs = Editor.objects.filter(pk__in=list(editor_data))
        members = submission.editorial_members.all()

        for editor_obj in editor_qs:
            if str(editor_obj.pk) in editor_data:
                editor_role = editor_data[str(editor_obj.pk)]

                for member in members:
                    if member.role == editor_role.value:
                        member.editor = editor_obj

        JournalSubmissionEditorialTeam.objects.bulk_update(members, ["editor"])

        message = "success" if submission else "failed"

        return AssignHandlingEditorsMutation(message=message, submission=submission)


class TransferHandlingPermission(graphene.relay.ClientIDMutation):
    """
    Assign the `edit_submssion` and `give_report` permissions and notify
    the next editorial member. Also, revoke the `edit_submission`and `give_report`
    permissions from the current editorial member, to prevent concurrent editing
    of the submission
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        journal_id = graphene.ID(required=True)
        submission_id = graphene.ID(required=True)
        editorial_member_id = graphene.ID(required=True)

    @classmethod
    @has_handling_permission()
    @is_editor_journal()
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        editorial_member_id = input.get("editorial_member_id")
        journal_id = input.get("journal_id")

        user = info.context.user
        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)
        permissions_qs = JournalPermission.objects.filter(
            journal__pk=from_global_id(journal_id).id,
            code_name__in=handling_permissions,
        )

        current_handler = submission.editorial_members.get(editor__user__pk=user.pk)
        next_handler = submission.editorial_members.get(
            pk=from_global_id(editorial_member_id).id
        )

        next_handler.permissions.add(*permissions_qs)
        current_handler.permissions.remove(*permissions_qs)

        next_handler_role = next_handler.get_role_display()

        submission.stage = "with {}".format(next_handler_role)
        submission.save()

        has_notified_editor.send(
            sender=JournalSubmission, email=next_handler.editor.user.email
        )

        return TransferHandlingPermission(message="success", submission=submission)


class CreateEditorReport(graphene.relay.ClientIDMutation):
    """
    Create Editor reports or comments on a submission
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()
    report = graphene.Field(EditorReportNode)

    class Input:
        report = graphene.String(required=True)
        submission_id = graphene.ID(required=True)
        journal_id = graphene.ID(required=True)

    @classmethod
    @has_handling_permission()
    @is_editor_journal()
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        report = input.get("report")
        editor = info.context.user.editor

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

        report_obj = EditorReport.objects.create(
            detail=report, editor=editor, journal_submission=submission
        )

        message = "success" if report_obj else "failed"

        return CreateEditorReport(
            message=message, submission=submission, report=report_obj
        )


class CreateReviewerReport(graphene.relay.ClientIDMutation):
    """
    Create reviewer reports for a submission.
    """

    submission = graphene.Field(JournalSubmissionNode)
    report = graphene.Field(ReviewerReportNode)
    message = graphene.String()

    class Input:
        submission_id = graphene.ID(required=True)
        journal_id = graphene.ID(required=True)
        report_sections = graphene.List(ReportSectionInput, required=True)

    @classmethod
    @is_assigned_submission()
    @reviewer_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        report_sections = input.get("report_sections")

        reviewer = info.context.user.reviewer

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

        report = ReviewerReport.objects.create(
            reviewer=reviewer, journal_submission=submission
        )

        sections_qs = JournalReportQuestion.objects.filter(
            pk__in=map(lambda x: from_global_id(x["question_id"]).id, report_sections)
        )

        ReviewerReportSection.objects.bulk_create(
            [
                ReviewerReportSection(
                    response=section.get("response"),
                    report=report,
                    section=sections_qs[i],
                )
                for i, section in enumerate(report_sections)
            ]
        )

        return CreateReviewerReport(
            message="success", submission=submission, report=report
        )
