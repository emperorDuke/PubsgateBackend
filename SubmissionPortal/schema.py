import graphene
from graphene_django import DjangoConnectionField
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .nodes import SubmissionNode
from .mutations import (
    CreateAuthorMutation,
    DeleteAuthorSubmissionMutation,
    SubmissionUploadMutation,
    CreateSubmissionMutation,
    CreateStatementMutation,
    UpdateAuthorMutation,
    UpdateStatementMutation,
    UpdateAuthorSubmissionMutation,
    DeleteSubmissionFileMutation,
)


class Query(graphene.ObjectType):
    user_submissions = DjangoConnectionField(SubmissionNode)
    user_submission = graphene.Field(
        SubmissionNode, submission_id=graphene.ID(required=True)
    )

    @login_required
    def resolve_user_submissions(self, info, **kwargs):
        return info.context.user.submissions

    @login_required
    def resolve_user_submission(self, info, **kwargs):
        submission_id = kwargs.get("submission_id")

        return info.context.user.submissions.get(pk=from_global_id(submission_id).id)


class Mutation(graphene.ObjectType):
    create_author_submission = CreateSubmissionMutation.Field()
    add_submission_authors = CreateAuthorMutation.Field()
    upload_submission_file = SubmissionUploadMutation.Field()
    add_submission_agreements = CreateStatementMutation.Field()
    edit_author_submission = UpdateAuthorSubmissionMutation.Field()
    edit_submission_authors = UpdateAuthorMutation.Field()
    edit_submission_agreements = UpdateStatementMutation.Field()
    delete_submission_file = DeleteSubmissionFileMutation.Field()
    delete_author_submission = DeleteAuthorSubmissionMutation.Field()
