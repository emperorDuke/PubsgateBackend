import graphene
from Cores.models import Discipline

from .nodes import Discipline as SubjectDisciplineNode


class CoreQueries(graphene.ObjectType):
    subject_disciplines = graphene.List(SubjectDisciplineNode)

    def resolve_subject_disciplines(root, info):
        return Discipline.objects.all()
