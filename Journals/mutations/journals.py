import graphene

from graphql_jwt.decorators import login_required

from Cores.models import SubjectDiscipline

from Journals.models import Journal
from Journals.nodes import JournalNode


class CreateJournal(graphene.relay.ClientIDMutation):
    journal = graphene.Field(JournalNode)
    message = graphene.String()

    class Input:
        name = graphene.String(required=True)
        issn = graphene.String(required=True)
        is_open_access = graphene.Boolean(required=True)
        subject_discipline = graphene.String(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        subject_discipline = SubjectDiscipline.objects.get(
            name=input.get("subject_discipline")
        )

        input["subject_discipline"] = subject_discipline

        journal = Journal.objects.create(**input)

        return CreateJournal(journal=journal, message="success")
