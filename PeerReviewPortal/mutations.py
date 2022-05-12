import base64
import graphene

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from Journals.models.journals import JournalReportQuestion

from Journals.permissions import (
    editor_in_chief_required,
    editor_is_required,
    is_editor_journal,
    reviewer_is_required,
    JournalPermissionChoice,
)

from Journals.models import Journal, JournalPermission, Editor, EditorialMember
from .input_types import EditorInput, ReportSectionInput
from .permissions import has_handling_permission, is_assigned_submission

from .models import (
    EditorReport,
    JournalSubmission,
    JournalSubmissionEditorialTeam,
    ReviewerReport,
    ReviewerReportSection,
)
from .nodes import JournalSubmissionNode, ReviewerReportNode
from .signals.signals import has_notified_editor


class CreateJournalSubmissionMutation(graphene.relay.ClientIDMutation):
    """
    Create journal submission when author accept there submissions
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        submission_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")

        user = info.context.user
        author_submission = user.submissions.select_related("manuscript__journal").get(
            pk=from_global_id(submission_id).id
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
    @has_handling_permission(True)
    @is_editor_journal(True)
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        email_addresses = input.get("email_addresses")
        journal_id = base64.b64encode(input.get("journal_id"))
        submission_id = base64.b64encode(input.get("submission_id"))

        journal = Journal.objects.get(pk=from_global_id(journal_id).id)
        submission = JournalSubmission.objects.selected_related(
            "author_submission__manuscript"
        ).get(pk=from_global_id(submission_id).id)

        abstract_section = submission.author_submission.manuscript.sections.get(
            section__name="abstract"
        )

        abstract = abstract_section.contents
        url = "/peer-review/invite?JID={1}&SID={2}".format(journal_id, submission_id)

        from_email = "{1}@pubsgate.com".format(journal.name)
        subject = "Invitation to be a reviewer for {1} journal".format(journal.name)
        text_content = "We are inviting you to review a manuscript"
        to = email_addresses
        html_content = (
            "<div><p> We are inviting you to review a manuscript,"
            "below this message is the abstract click on the link below to accept out invitation</p>"
            "<p>{1}</p><a>{2}</a></div>"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content.format(abstract, url))
        msg.send()

        return InviteReviewerMutation(message="success")


class AcceptReviewerInvitationMutation(graphene.relay.ClientIDMutation):
    """
    Accept invited reviewers
    """

    message = graphene.String()
    submission = graphene.Field(JournalSubmissionNode)

    class Input:
        submission_id = graphene.ID(required=True)
        journal_id = graphene.ID(required=True)

    @classmethod
    @reviewer_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        journal_id = input.get("journal_id")

        reviewer = info.context.user.reviewer

        submission = JournalSubmission.objects.get(
            pk=from_global_id(submission_id).id,
            journal__pk=from_global_id(journal_id).id,
        )

        submission.reviewers.add(reviewer)

        return AcceptReviewerInvitationMutation(
            message="success", submission=submission
        )


class AcceptSubmissionMutation(graphene.relay.ClientIDMutation):
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
    @editor_in_chief_required(True)
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        is_accepted = input.get("is_accepted")
        submission_id = input.get("submission_id")

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)
        submission.is_accepted = timezone.now() if is_accepted else None
        submission.save()

        message = "success" if submission else "failed"

        return AcceptSubmissionMutation(message, submission=submission)


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
    @editor_in_chief_required(True)
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


class UpdateMemberPermissionMutation(graphene.relay.ClientIDMutation):
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
    @has_handling_permission(True)
    @is_editor_journal(True)
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        editorial_member_id = input.get("editorial_member_id")
        journal_id = input.get("journal_id")

        user = info.context.user
        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)
        permissions_qs = JournalPermission.objects.filter(
            journal__pk=from_global_id(journal_id),
            code_name__in=(
                JournalPermissionChoice.GIVE_REPORTS.value,
                JournalPermissionChoice.EDIT_SUBMISSIONS.value,
            ),
        )

        next_member = EditorialMember.objects.selected_releted("editor__user").get(
            pk=from_global_id(editorial_member_id).id,
            journal__pk=from_global_id(journal_id),
        )

        current_member = submission.editorial_members.get(editor__user__pk=user.pk)

        next_member.permissions.add(*permissions_qs)
        current_member.permissions.remove(*permissions_qs)

        next_member_role = next_member.get_role_display()

        submission.stage = "with {0}".format(next_member_role)
        submission.save()

        has_notified_editor.send(
            sender=JournalSubmission, email=next_member.editor.user.email
        )

        return UpdateMemberPermissionMutation(message="success", submission=submission)


class CreateEditorReportMutation(graphene.relay.ClientIDMutation):
    """
    Create Editor reports or comments on a submission
    """

    submission = graphene.Field(JournalSubmissionNode)
    message = graphene.String()

    class Input:
        report = graphene.String(required=True)
        submission_id = graphene.ID(required=True)
        journal_id = graphene.ID(required=True)

    @classmethod
    @has_handling_permission(True)
    @is_editor_journal(True)
    @editor_is_required
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        report = input.get("report")
        editor = info.context.user.editor

        submission = JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

        report_obj = EditorReport.objects.create(
            report=report, editor=editor, journal_submission=submission
        )

        message = "successfully created" if report_obj else "failed operation"

        return CreateEditorReportMutation(message=message, submission=submission)


class CreateReviewerReportMutation(graphene.relay.ClientIDMutation):
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
    @is_assigned_submission(True)
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
                    reponse=section.get("response"),
                    report=report,
                    section=sections_qs[i],
                )
                for i, section in enumerate(report_sections)
            ]
        )

        return CreateReviewerReportMutation(
            message="success", submission=submission, report=report
        )
