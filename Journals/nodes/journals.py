import graphene

from graphene_django import DjangoObjectType

from Cores.nodes import SubjectDiscipline as SubjectDisciplineNode
from ..models.journals import (
    JournalDetail,
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


class JournalDetailNode(DjangoObjectType):
    class Meta:
        model = JournalDetail
        fields = ("id", "content", "detail_type", "created_at", "journal")


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
