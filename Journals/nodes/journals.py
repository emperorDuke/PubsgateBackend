import graphene

from graphene_django import DjangoObjectType

from Cores.nodes import Discipline as SubjectDisciplineNode
from ..models.journals import (
    JournalInformation,
    JournalPermission,
    JournalReportQuestion,
    JournalSubjectArea,
    Journal,
)


class JournalNode(DjangoObjectType):
    discipline = graphene.Field(SubjectDisciplineNode)

    class Meta:
        model = Journal
        fields = ("id", "name")

    def resolve_discipline(self, info):
        return self.subject_discipline


class JournalInformationNode(DjangoObjectType):
    class Meta:
        model = JournalInformation
        fields = ("id", "content", "header", "created_at", "journal")


class JournalSubjectAreaNode(DjangoObjectType):
    class Meta:
        model = JournalSubjectArea
        fields = ("id", "name")


class JournalPermissionNode(DjangoObjectType):
    class Meta:
        model = JournalPermission
        fields = ["id", "code_name", "label", "journal"]
        interfaces = (graphene.relay.Node,)


class JournalReportQuestionNode(DjangoObjectType):
    class Meta:
        model = JournalReportQuestion
        fields = ("id", "question", "hint", "has_long_answer", "options", "journal")
        interfaces = (graphene.relay.Node,)
