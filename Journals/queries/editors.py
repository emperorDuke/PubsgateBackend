import graphene
from graphql_jwt.decorators import login_required
from ..models import Editor
from ..nodes import Editor as EditorNode


class EditorQuery(graphene.ObjectType):
    editor = graphene.Field(EditorNode, id=graphene.ID(required=True))

    @login_required
    def resolve_editor(root, info, **kwargs):
        id = kwargs.get("id")

        return Editor.objects.get(pk=id)
