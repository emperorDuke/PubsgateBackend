import graphene
from graphene_django import DjangoObjectType

from Journals.nodes import JournalNode

from .models import (
    Manuscript,
    ManuscriptSection,
    ManuscriptAuthor,
    ManuscriptKeywordTag,
)


class ManuscriptSectionNode(DjangoObjectType):
    class Meta:
        model = ManuscriptSection
        fields = ("id", "section", "content", "created_at")
        interfaces = (graphene.relay.Node,)


class ManuscriptAuthorNode(DjangoObjectType):
    class Meta:
        model = ManuscriptAuthor
        fields = [
            "first_name",
            "last_name",
            "email",
            "affiliation",
            "rank",
            "is_corresponding",
        ]


class ManuscriptKeywordTagNode(DjangoObjectType):
    class Meta:
        model = ManuscriptKeywordTag
        interfaces = (graphene.relay.Node,)
        fields = ("id", "tag")


class ManuscriptNode(DjangoObjectType):

    journal = graphene.Field(JournalNode)

    class Meta:
        model = Manuscript
        fields = (
            "id",
            "word_count",
            "title",
            "author_submission",
            "authors",
            "subject_area",
            "sections",
        )
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "title": ["exact", "icontains", "istartswith"],
        }

    def resolve_journal(self, info):
        return self.journal
