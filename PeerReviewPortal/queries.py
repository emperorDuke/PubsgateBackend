import graphene

from graphene_django import DjangoConnectionField
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from Journals.permissions import (
    is_editor_journal,
    editor_is_required,
    is_reviewer_journal,
    reviewer_is_required,
)
from .nodes import JournalSubmissionNode, ReviewerReportNode
from .models import JournalSubmission, ReviewerReport


related_fields = (
    "author_submission__manuscript",
    "author_submission__user",
    "journal",
)


class ReviewerQuery(graphene.ObjectType):
    """
    Reviewers queries
    """

    reviewer_submissions = DjangoConnectionField(
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

    @is_reviewer_journal()
    @reviewer_is_required
    @login_required
    def resolve_reviewer_submissions(self, info, **kwargs):
        journal_id = kwargs.get("journal_id")

        return JournalSubmission.objects.filter(
            journal__pk=from_global_id(journal_id).id,
            reviewers__user__pk=info.context.user.pk,
        ).select_related(*related_fields)

    @is_reviewer_journal()
    @reviewer_is_required
    @login_required
    def resolve_reviewer_submission(self, info, **kwargs):
        submission_id = kwargs.get("submission_id")
        journal_id = kwargs.get("journal_id")

        return JournalSubmission.objects.select_related(*related_fields).get(
            pk=from_global_id(submission_id).id,
            reviewers__user__pk=info.context.user.pk,
            journal__pk=from_global_id(journal_id).id,
        )

    @is_reviewer_journal()
    @reviewer_is_required
    @login_required
    def resolve_reviewer_report(self, info, **kwargs):
        report_id = kwargs.get("report_id")
        journal_id = kwargs.get("journal_id")

        return ReviewerReport.objects.get(
            pk=from_global_id(report_id).id,
            journal_submission__journal__pk=from_global_id(journal_id).id,
            reviewer__user__pk=info.context.user.pk,
        )


class EditorQuery(graphene.ObjectType):
    """
    Editor's queries
    """

    journal_submissions = DjangoConnectionField(
        JournalSubmissionNode, journal_id=graphene.ID(required=True)
    )

    journal_submission = graphene.Field(
        JournalSubmissionNode,
        journal_id=graphene.ID(required=True),
        submission_id=graphene.ID(required=True),
    )

    @is_editor_journal()
    @editor_is_required
    @login_required
    def resolve_journal_submissions(self, info, **kwargs):
        journal_id = kwargs.get("journal_id")

        return JournalSubmission.objects.filter(
            journal__pk=from_global_id(journal_id).id
        ).select_related(*related_fields)

    @is_editor_journal()
    @editor_is_required
    @login_required
    def resolve_journal_submission(self, info, **kwargs):
        submission_id = kwargs.get("submission_id")

        return JournalSubmission.objects.select_related(*related_fields).get(
            pk=from_global_id(submission_id).id
        )
