import graphene
from graphene_django import DjangoObjectType

from .models import ArticleTypeSection, SubjectDiscipline, TermOfService, ArticleType


class SubjectDisciplineNode(DjangoObjectType):
    class Meta:
        model = SubjectDiscipline
        fields = ("name",)
        interfaces = (graphene.relay.Node,)


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
