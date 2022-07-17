import graphene

from Cores.queries import CoreQueries


class Query(CoreQueries, graphene.ObjectType):
    pass
