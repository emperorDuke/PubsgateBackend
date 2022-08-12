import graphene

from ..models.journals import Journal, JournalInformation, JournalSubjectArea
from ..nodes import (
    JournalInformation as JournalInformationType,
    Journal as JournalType,
    JournalSubjectArea as JournalSubjectAreaType,
)


class JournalQuery(graphene.ObjectType):
    journal_information = graphene.Field(
        JournalInformationType, journal_id=graphene.ID(required=True)
    )

    journal = graphene.Field(JournalType, id=graphene.ID(required=True))
    subject_area = graphene.List(
        JournalSubjectAreaType, journal_id=graphene.ID(required=True)
    )

    def resolve_journal_information(root, info, journal_id):
        return JournalInformation.objects.filter(journal__pk=journal_id).first()

    def resolve_journal(root, info, id):
        return Journal.objects.get(pk=id)

    def resolve_subject_area(root, info, id):
        return JournalSubjectArea.objects.filter(journal__pk=id).first()
