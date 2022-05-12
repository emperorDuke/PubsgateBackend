import graphene

from graphene_django import DjangoObjectType

from ..models import Editor


class EditorNode(DjangoObjectType):
    class Meta:
        model = Editor
        fields = ["id", "affiliation", "phone_number", "started_at", "user"]
        interfaces = (graphene.relay.Node,)
