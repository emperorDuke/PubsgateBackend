import graphene

from .queries import EditorQuery, ReviewerQuery

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


class Query(ReviewerQuery, EditorQuery, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    assign_editors = AssignHandlingEditorsMutation.Field()
    invite_reviewers = InviteReviewerMutation.Field()
    accept_reviewer_invitation = AcceptReviewerInvitation.Field()
    accept_submission = AcceptSubmission.Field()
    transfer_submission = TransferHandlingPermission.Field()
    create_editor_report = CreateEditorReport.Field()
    create_reviewer_report = CreateReviewerReport.Field()
    submit_to_journal = CreateJournalSubmissionMutation.Field()
