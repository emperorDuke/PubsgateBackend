import graphene

from graphene_django import DjangoObjectType

from Cores.nodes import (
    Discipline as SubjectDisciplineNode,
    InformationHeading as InformationHeadingType,
)
from ..models.journals import (
    JournalInformation as JournalInformationModel,
    JournalPermission,
    JournalReportQuestion,
    JournalSubjectArea as JournalSubjectAreaModel,
    Journal as JournalModel,
)


class Journal(DjangoObjectType):
    discipline = graphene.Field(SubjectDisciplineNode)
    publication_frequency = graphene.String()
    editor_last_login = graphene.DateTime()

    class Meta:
        model = JournalModel
        convert_choices_to_enum = False
        fields = (
            "id",
            "name",
            "slug",
            "publication_start_date",
            "iso_abbreviation",
            "logo",
            "issn",
            "access_options",
            "editor_last_login",
        )

    def resolve_discipline(self, info):
        return self.discipline

    def resolve_publication_frequency(self, info):
        return self.get_publication_frequency_display()

    def resolve_last_login(self, info):
        return self.editor_last_login


class JournalInformation(DjangoObjectType):
    heading = graphene.Field(InformationHeadingType)

    class Meta:
        model = JournalInformationModel
        fields = ("id", "content", "created_at", "journal")

    def resolve_heading(self, info):
        return self.heading


class JournalSubjectArea(DjangoObjectType):
    class Meta:
        model = JournalSubjectAreaModel
        fields = ("id", "name", "journal")


class JournalPermissionNode(DjangoObjectType):
    class Meta:
        model = JournalPermission
        fields = ["id", "code_name", "label", "journal"]


class JournalReportQuestionNode(DjangoObjectType):
    class Meta:
        model = JournalReportQuestion
        fields = ("id", "question", "hint", "has_long_answer", "options", "journal")
        interfaces = (graphene.relay.Node,)
