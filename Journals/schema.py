import graphene
from graphql_jwt.decorators import login_required
from Journals.models.editors import Editor

from Journals.mutations import CreateEditorMutation
from Journals.mutations.editors import AcceptEditorMutation, AdminCreateEditorMutation
from Journals.mutations.journals import (
    CreateJournalMutation,
    TransferJournalManagementMutation,
)
from Journals.nodes import Editor as EditorNode


class Mutation(graphene.ObjectType):
    create_editor = CreateEditorMutation.Field()
    create_journal = CreateJournalMutation.Field()
    transfer_management = TransferJournalManagementMutation.Field()
    admin_create_editor = AdminCreateEditorMutation.Field()
    accept_editor = AcceptEditorMutation.Field()


class Query(graphene.ObjectType):  #
    editor = graphene.Field(EditorNode, id=graphene.ID(required=True))

    @login_required
    def resolve_editor(root, info, **kwargs):
        id = kwargs.get("id")
        editor = Editor.objects.get(pk=id)

        return editor
