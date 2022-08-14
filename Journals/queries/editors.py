import graphene
from graphql_jwt.decorators import login_required
from ..models import Editor
from ..nodes import Editor as EditorType


class EditorQuery(graphene.ObjectType):
    editor = graphene.Field(EditorType, id=graphene.ID(required=True))

    @login_required
    def resolve_editor(root, info, **kwargs):
        id = kwargs.get("id")

        return Editor.objects.get(pk=id)
