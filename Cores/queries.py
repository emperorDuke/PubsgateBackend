import graphene
from Cores.models import Discipline

from .nodes import Discipline as SubjectDisciplineNode


class CoreQueries(graphene.ObjectType):
    disciplines = graphene.List(SubjectDisciplineNode)

    def resolve_disciplines(root, info):
        return Discipline.objects.all()
