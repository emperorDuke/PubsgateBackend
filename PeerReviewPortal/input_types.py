import graphene

from Journals.models import EditorialMember


class EditorInput(graphene.InputObjectType):
    role = graphene.Enum.from_enum(EditorialMember.Role)(required=True)
    editor_id = graphene.ID(required=True)


class ReportSectionInput(graphene.InputObjectType):
    response = graphene.String(required=True)
    question_id = graphene.ID(required=True)
