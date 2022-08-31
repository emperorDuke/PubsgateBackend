import graphene
from Cores.models import Discipline, InformationHeading

from .nodes import (
    Discipline as SubjectDisciplineType,
    InformationHeading as InformationHeadingType,
)


class CoreQueries(graphene.ObjectType):
    disciplines = graphene.List(SubjectDisciplineType)
    information_headings = graphene.List(InformationHeadingType)

    def resolve_disciplines(root, info):
        return Discipline.objects.all()

    def resolve_information_headings(root, info):
        return InformationHeading.objects.all()
