import graphene
from graphene_django import DjangoConnectionField
from graphql_jwt.decorators import login_required

from Journals.mutations import CreateEditorMutation
from Journals.mutations.journals import (
    CreateJournalMutation,
    TransferJournalManagementMutation,
)
from Journals.nodes import EditorNode


class Mutation(graphene.ObjectType):
    create_editor = CreateEditorMutation.Field()
    create_journal = CreateJournalMutation.Field()
    transfer_management = TransferJournalManagementMutation.Field()


class Query(graphene.ObjectType):
    editors = DjangoConnectionField(EditorNode, journal_id=graphene.ID(required=True))

    @login_required
    def resolve_editors(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
