import graphene

from graphene_django import DjangoObjectType
from Journals.models.roles import EditorialMember

from PeerReviewPortal.models import (
    EditorReport,
    JournalSubmission,
    JournalSubmissionEditorialTeam,
    ReviewerReport,
    ReviewerReportSection,
)


class JournalSubmissionEditorialTeamNode(DjangoObjectType):
    class Meta:
        model = JournalSubmissionEditorialTeam
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False
        fields = [
            "id",
            "role",
            "permissions",
            "editor",
            "journal_submission",
            "created_at",
        ]


class JournalSubmissionNode(DjangoObjectType):
    class Meta:
        model = JournalSubmission
        interfaces = (graphene.relay.Node,)
        fields = [
            "id",
            "author_submission",
            "reviewers",
            "stage",
            "is_accepted",
            "journal",
            "editorial_members",
            "created_at",
            "editors_reports",
        ]


class EditorialMemberNode(DjangoObjectType):
    class Meta:
        model = EditorialMember
        interfaces = (graphene.relay.Node,)
        fields = ("id", "role")


class EditorReportNode(DjangoObjectType):
    class Meta:
        model = EditorReport
        fields = ["id", "detail", "created_at", "editor"]
        interfaces = (graphene.relay.Node,)


class ReviewerReportNode(DjangoObjectType):
    class Meta:
        model = ReviewerReport
        fields = ["id", "reviewer", "journal_submission", "sections", "created_at"]
        interfaces = (graphene.relay.Node,)


class ReviewerReportSectionNode(DjangoObjectType):
    class Meta:
        model = ReviewerReportSection
        fields = ["id", "response", "section", "report"]
        interfaces = (graphene.relay.Node,)
