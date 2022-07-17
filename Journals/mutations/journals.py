import graphene

from django.contrib.auth import get_user_model

from graphql_jwt.decorators import login_required, staff_member_required
from graphql_relay import from_global_id

from Cores.models import SubjectDiscipline

from Journals.models import Journal
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
        subject_discipline = SubjectDiscipline.objects.get(
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
    @login_required
    def mutate(cls, root, info, **kwargs):
        email = kwargs.pop("email")
        journal_id = kwargs.pop("journal_id")
        editor = get_user_model().objects.get(email=email).editor
        journal = Journal.objects.get(pk=from_global_id(journal_id).id)

        editor.journals.add(journal)

        journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        return TransferJournalManagementMutation(message="success")
