import graphene

from ..nodes import JournalDetailNode


class Query(graphene.ObjectType):
    journal_details = graphene.Field(
        JournalDetailNode, journal_id=graphene.ID(required=True)
    )
