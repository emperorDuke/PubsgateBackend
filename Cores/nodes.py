import graphene
from graphene_django import DjangoObjectType

from .models import ArticleTypeSection, Discipline, TermOfService, ArticleType


class Discipline(DjangoObjectType):
    class Meta:
        model = Discipline
        fields = ("id", "name", "slug")


class TermOfServiceNode(DjangoObjectType):
    class Meta:
        model = TermOfService
        fields = "__all__"
        interfaces = (graphene.relay.Node,)


class ArticleTypeNode(DjangoObjectType):
    class Meta:
        model = ArticleType
        fields = "__all__"
        interfaces = (graphene.relay.Node,)


class ArticleTypeSectionNode(DjangoObjectType):
    class Meta:
        model = ArticleTypeSection
        fields = "__all__"
        interfaces = (graphene.relay.Node,)
