import graphene

from ..nodes import JournalInformationNode


class Query(graphene.ObjectType):
    journal_details = graphene.Field(
        JournalInformationNode, journal_id=graphene.ID(required=True)
    )
