import graphene

from graphql.error import GraphQLError
from graphql_relay import from_global_id
from graphql_jwt.decorators import login_required

from ..models import Editor
from ..nodes import EditorNode

from Journals.models.journals import Journal


class CreateEditorMutation(graphene.relay.ClientIDMutation):
    editor = graphene.Field(EditorNode)
    message = graphene.String()

    class Input:
        affiliation = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        journal_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        user = info.context.user
        affiliation = input.get("affiliation")
        phone_number = input.get("phone_number")
        editor = None

        journal = Journal.objects.get(pk=from_global_id(input.get("journal_id")).id)

        editor_exist = journal.editors.filter(user__pk=user.pk).exists()
        reviewer_exist = journal.reviewers.filter(user__pk=user.pk).exists()

        if editor_exist:
            raise GraphQLError("user already exists as an editor on this journal")

        if reviewer_exist:
            raise GraphQLError("user already exists as a reviewer on this journal")

        editor = Editor.objects.create(
            affiliation=affiliation,
            phone_number=phone_number,
            user=user,
        )

        editor.journals.add(journal)

        message = "successfully created" if editor else "failed operation"

        return CreateEditorMutation(editor=editor, message=message)
