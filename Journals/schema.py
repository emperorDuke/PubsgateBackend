import graphene

from .mutations import (
    AcceptEditorMutation,
    AdminCreateEditorMutation,
    CreateEditorMutation,
    CreateJournalMutation,
    EditJournalInformationMutation,
    EditJournalMutation,
    JournalSubjectAreaMutation,
    TransferJournalManagementMutation,
)
from .queries import EditorQuery, JournalQuery


class Mutation(graphene.ObjectType):
    ### editor mutations
    create_editor = CreateEditorMutation.Field()
    admin_create_editor = AdminCreateEditorMutation.Field()
    accept_editor = AcceptEditorMutation.Field()
    ## journal mutations
    create_journal = CreateJournalMutation.Field()
    transfer_management = TransferJournalManagementMutation.Field()
    edit_journal = EditJournalMutation.Field()
    journal_subject_area = JournalSubjectAreaMutation.Field()
    edit_journal_information = EditJournalInformationMutation.Field()


class Query(JournalQuery, EditorQuery, graphene.ObjectType):
    pass
