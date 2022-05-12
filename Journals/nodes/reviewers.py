import graphene
from graphene_django import DjangoObjectType

from ..models import Reviewer


class ReviewerNode(DjangoObjectType):
    class Meta:
        model = Reviewer
        fields = ("id", "is_anonymous", "affiliation", "journals", "started_at", "user")
        interfaces = (graphene.relay.Node,)
