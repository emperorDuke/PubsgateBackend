import graphene
from Cores.models import SubjectDiscipline

from .nodes import SubjectDiscipline as SubjectDisciplineNode


class CoreQueries(graphene.ObjectType):
    subject_disciplines = graphene.List(SubjectDisciplineNode)

    def resolve_subject_disciplines(root, info):
        return SubjectDiscipline.objects.all()
