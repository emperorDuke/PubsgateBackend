import graphene

from graphene_django import DjangoObjectType

from Cores.nodes import Discipline as SubjectDisciplineNode
from ..models.journals import (
    JournalInformation as JournalInformationModel,
    JournalPermission,
    JournalReportQuestion,
    JournalSubjectArea as JournalSubjectAreaModel,
    Journal as JournalModel,
)


class Journal(DjangoObjectType):
    discipline = graphene.Field(SubjectDisciplineNode)

    class Meta:
        model = JournalModel
        fields = ("id", "name")

    def resolve_discipline(self, info):
        return self.discipline


class JournalInformation(DjangoObjectType):
    class Meta:
        model = JournalInformationModel
        fields = ("id", "content", "heading", "created_at", "journal")


class JournalSubjectArea(DjangoObjectType):
    class Meta:
        model = JournalSubjectAreaModel
        fields = ("id", "name")


class JournalPermissionNode(DjangoObjectType):
    class Meta:
        model = JournalPermission
        fields = ["id", "code_name", "label", "journal"]


class JournalReportQuestionNode(DjangoObjectType):
    class Meta:
        model = JournalReportQuestion
        fields = ("id", "question", "hint", "has_long_answer", "options", "journal")
        interfaces = (graphene.relay.Node,)
