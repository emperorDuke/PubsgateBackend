import graphene
from graphene_django import DjangoConnectionField

from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from Journals.permissions import (
    is_editor_journal,
    editor_is_required,
    is_reviewer_journal,
)

from .mutations import (
    AcceptReviewerInvitation,
    AssignHandlingEditorsMutation,
    CreateJournalSubmissionMutation,
    AcceptSubmission,
    TransferHandlingPermission,
    CreateEditorReport,
    InviteReviewerMutation,
    CreateReviewerReport,
)
from .nodes import JournalSubmissionNode, ReviewerReportNode
from .models import JournalSubmission, ReviewerReport
from .permissions import is_assigned_submission


class Mutation(graphene.ObjectType):
    assign_editors = AssignHandlingEditorsMutation.Field()
    invite_reviewers = InviteReviewerMutation.Field()
    accept_reviewer_invitation = AcceptReviewerInvitation.Field()
    accept_submission = AcceptSubmission.Field()
    transfer_submission = TransferHandlingPermission.Field()
    create_editor_report = CreateEditorReport.Field()
    create_reviewer_report = CreateReviewerReport.Field()
    submit_to_journal = CreateJournalSubmissionMutation.Field()


class Query(graphene.ObjectType):
    journal_submissions = DjangoConnectionField(
        JournalSubmissionNode, journal_id=graphene.ID(required=True)
    )

    journal_submission = graphene.Field(
        JournalSubmissionNode,
        journal_id=graphene.ID(required=True),
        submission_id=graphene.ID(required=True),
    )

    reviewer_submissions = graphene.Field(
        JournalSubmissionNode,
        journal_id=graphene.ID(required=True),
    )

    reviewer_submission = graphene.Field(
        JournalSubmissionNode,
        journal_id=graphene.ID(required=True),
        submission_id=graphene.ID(required=True),
    )

    reviewer_report = graphene.Field(
        ReviewerReportNode,
        journal_id=graphene.ID(required=True),
        report_id=graphene.ID(required=True),
    )

    @is_editor_journal()
    @editor_is_required
    @login_required
    def resolve_journal_submissions(self, info, **kwargs):
        journal_id = kwargs.get("journal_id")

        return JournalSubmission.objects.filter(
            journal__pk=from_global_id(journal_id).id
        ).select_related(
            "author_submission__manuscript",
            "author_submission__user",
            "author_submission__manuscript__journal",
        )

    @is_editor_journal()
    @editor_is_required
    @login_required
    def resolve_journal_submission(self, info, **kwargs):
        submission_id = kwargs.get("submission_id")

        return JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

    @is_reviewer_journal()
    @login_required
    def resolve_review_submissions(self, info, **kwargs):
        journal_id = kwargs.get("journal_id")

        return JournalSubmission.objects.filter(
            journal__pk=from_global_id(journal_id).id,
            reviewers__pk=info.context.user.reviewer.pk,
        )

    @is_reviewer_journal()
    @is_assigned_submission()
    @login_required
    def resolve_review_submission(self, info, **kwargs):
        submission_id = kwargs.get("submission_id")

        return JournalSubmission.objects.get(pk=from_global_id(submission_id).id)

    @is_reviewer_journal()
    @is_assigned_submission()
    @login_required
    def resolve_review_reporter(self, info, **kwargs):
        report_id = kwargs.get("report_id")

        return ReviewerReport.objects.get(pk=from_global_id(report_id).id)
