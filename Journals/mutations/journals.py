import graphene

from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required

from Cores.models import Discipline

from Journals.models import Journal, Editor
from Journals.models.roles import EditorialMember
from Journals.nodes import JournalNode


class CreateJournalMutation(graphene.Mutation):
    journal = graphene.Field(JournalNode)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        issn = graphene.String(required=True)
        subject_discipline = graphene.String(required=True)

    @classmethod
    @staff_member_required
    @login_required
    def mutate(cls, root, info, **kwargs):
        subject_discipline = Discipline.objects.get(
            name=kwargs.pop("subject_discipline")
        )

        journal = Journal.objects.create(
            subject_discipline=subject_discipline, **kwargs
        )

        return CreateJournalMutation(journal=journal, message="success")


class TransferJournalManagementMutation(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        journal_id = graphene.ID(required=True)
        email = graphene.String(required=True)

    @classmethod
    @staff_member_required
    @login_required
    def mutate(cls, root, info, **kwargs):
        email = kwargs.pop("email")
        journal_id = kwargs.pop("journal_id")

        editor = Editor.objects.filter(user__email=email).first()

        if not editor:
            raise GraphQLError("Manager is not an editor")

        journal = Journal.objects.get(pk=journal_id)

        journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        return TransferJournalManagementMutation(message="success")
