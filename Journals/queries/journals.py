import graphene

from ..models.journals import Journal, JournalInformation, JournalSubjectArea
from ..nodes import (
    JournalInformation as JournalInformationType,
    Journal as JournalType,
    JournalSubjectArea as JournalSubjectAreaType,
)


class JournalQuery(graphene.ObjectType):
    journal_information = graphene.List(
        JournalInformationType, journal_id=graphene.ID(required=True)
    )
    journal = graphene.Field(JournalType, id=graphene.ID(required=True))
    subject_areas = graphene.List(
        JournalSubjectAreaType, journal_id=graphene.ID(required=True)
    )

    def resolve_journal_information(root, info, journal_id):
        return JournalInformation.objects.filter(journal__pk=journal_id).select_related(
            "heading", "journal"
        )

    def resolve_journal(root, info, id):
        return Journal.objects.select_related("discipline").get(pk=id)

    def resolve_subject_areas(root, info, journal_id):
        return JournalSubjectArea.objects.filter(journal__pk=journal_id).select_related(
            "journal"
        )
