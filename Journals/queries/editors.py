import graphene
from django.db.models import F
from graphql_jwt.decorators import login_required

from ..models import Editor
from ..nodes import Editor as EditorType
from ..nodes import Journal as JournalType
from ..permissions import editor_is_required


class EditorQuery(graphene.ObjectType):
    editor = graphene.Field(EditorType, id=graphene.ID(required=True))
    editor_journals = graphene.List(JournalType)

    @login_required
    def resolve_editor(root, info, **kwargs):
        id = kwargs.get("id")

        return Editor.objects.get(pk=id)

    @editor_is_required
    @login_required
    def resolve_editor_journals(root, info, **kwargs):
        editor = info.context.user.editor

        return editor.journals.annotate(
            editor_last_login=F("editor_activities__last_login")
        ).all()
