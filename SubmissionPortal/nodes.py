import graphene

from graphene_django import DjangoObjectType

from .models import (
    AuthorSubmission,
    SubmissionConditionAgreement,
    SubmissionStatus,
    SubmissionFile,
)


class SubmissionNode(DjangoObjectType):
    """
    Author submission node
    """

    class Meta:
        model = AuthorSubmission
        fields = (
            "id",
            "user",
            "manuscript",
            "agreements",
            "status",
            "files",
            "article_type",
        )
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = False


class SubmissionAgreementNode(DjangoObjectType):
    class Meta:
        model = SubmissionConditionAgreement
        fields = ("id", "statement", "response", "term", "documented_at")
        convert_choices_to_enum = False
        interfaces = (graphene.relay.Node,)


class SubmissionStatusNode(DjangoObjectType):
    class Meta:
        model = SubmissionStatus
        fields = ("id", "stage")


class SubmissionFileNode(DjangoObjectType):
    class Meta:
        model = SubmissionFile
        fields = ("id", "version", "file_type", "file", "created_at")
