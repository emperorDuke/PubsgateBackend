import json
import graphene

from graphql import GraphQLError
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from Contents.models import (
    Manuscript,
    ManuscriptAuthor,
    ManuscriptSection,
)

from Cores.models import ArticleTypeSection, TermOfService
from Journals.models import Journal, JournalSubjectArea

from .nodes import SubmissionNode
from .input_types import (
    AuthorInputType,
    ManuscriptSectionInput,
    StatementInputType,
    UpdateAuthorInput,
    UpdateStatementInput,
)
from .models import AuthorSubmission, SubmissionConditionAgreement, SubmissionFile
from .utils import cast


class CreateSubmissionMutation(graphene.relay.ClientIDMutation):
    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Input:
        title = graphene.String(required=True)
        journal_name = graphene.String(required=True)
        subject_area = graphene.String()
        article_type = graphene.Enum.from_enum(AuthorSubmission.ArticleType)(
            required=True
        )
        word_count = graphene.Int(required=True)
        sections = graphene.List(ManuscriptSectionInput, required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        subject_area = input.get("subject_area")
        journal_name = input.get("journal_name")
        article_type = input.get("article_type")
        word_count = input.get("word_count")
        title = input.get("title")
        sections = input.get("sections")
        subject = None

        if subject_area:
            subject = JournalSubjectArea.objects.get(name=subject_area)

        journal = Journal.objects.get(name=journal_name)

        manuscript = Manuscript.objects.create(
            title=title,
            journal=journal,
            subject_area=subject,
            word_count=word_count,
        )

        get_article_section = lambda id: ArticleTypeSection.objects.get(
            pk=from_global_id(id).id
        )

        ManuscriptSection.objects.bulk_create(
            [
                ManuscriptSection(
                    section=get_article_section(section.get("section_id")),
                    content=json.dumps(
                        [
                            {
                                "type": "paragraph",
                                "children": [{"text": section.get("content")}],
                            }
                        ]
                    ),
                    manuscript=manuscript,
                )
                for section in sections
            ]
        )

        submission = AuthorSubmission.objects.create(
            user=info.context.user,
            article_type=article_type,
            manuscript=manuscript,
        )

        return CreateSubmissionMutation(message="success", submission=submission)


##### second stage of the from ####
class CreateAuthorMutation(graphene.relay.ClientIDMutation):
    submission = graphene.Field(SubmissionNode)
    message = graphene.String()

    class Input:
        submission_id = graphene.ID(required=True)
        authors = graphene.List(AuthorInputType, required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        authors = input.get("authors")

        user = info.context.user
        manuscript = (
            user.submissions.select_related("manuscript")
            .get(pk=from_global_id(submission_id).id)
            .manuscript
        )

        authors = ManuscriptAuthor.objects.bulk_create(
            [ManuscriptAuthor(manuscript=manuscript, **author) for author in authors]
        )

        message = "success" if authors else "failed"
        submission = user.submissions.get(pk=from_global_id(submission_id).id)

        return CreateAuthorMutation(submission=submission, message=message)


class SubmissionUploadMutation(graphene.Mutation):
    """
    Upload Submission files wihch include doc files and manuscripts
    """

    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Arguments:
        submission_id = graphene.ID(required=True)
        file = Upload(required=True)
        type = graphene.Enum.from_enum(SubmissionFile.FileType)(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, **input):
        submission_id = input.get("submission_id")
        file_type = input.get("type")

        user = info.context.user
        submission = user.submissions.get(pk=from_global_id(submission_id).id)

        submission_file = SubmissionFile.objects.create(
            author_submission=submission,
            file_type=file_type,
            file=input.get("file"),
        )

        message = "success" if submission_file else "failed"

        return SubmissionUploadMutation(message=message, submission=submission)


class CreateStatementMutation(graphene.relay.ClientIDMutation):
    """
    Create manuscript submissions statements
    """

    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Input:
        submission_id = graphene.ID(required=True)
        statements = graphene.List(StatementInputType, required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        statements = input.get("statements")

        user = info.context.user
        submission = user.submissions.get(pk=from_global_id(submission_id).id)

        terms_qs = TermOfService.objects.filter(
            pk__in=[from_global_id(statement["term_id"]).id for statement in statements]
        )

        condition = SubmissionConditionAgreement.objects.bulk_create(
            [
                SubmissionConditionAgreement(
                    **{
                        "author_submission": submission,
                        "term": terms_qs[i],
                        "response": cast(statement.get("response")),
                        "statement": statement.get("statement", None),
                    }
                )
                for i, statement in enumerate(statements)
            ]
        )

        message = "success" if condition else "failed"

        return CreateStatementMutation(message=message, submission=submission)


####  EDITING THE SUBMISSION ###


class UpdateAuthorSubmissionMutation(graphene.relay.ClientIDMutation):
    """
    Update manuscript submission informations
    """

    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Input:
        title = graphene.String()
        journal_name = graphene.String()
        subject_area = graphene.String()
        article_type = graphene.Enum.from_enum(AuthorSubmission.ArticleType)()
        word_count = graphene.Int()
        sections = graphene.List(ManuscriptSectionInput)
        submission_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id: str = input.get("submission_id")

        subject_area: str | None = input.get("subject_area", None)
        journal_name: str | None = input.get("journal_name", None)
        article_type: str | None = input.get("article_type", None)
        word_count: int | None = input.get("word_count", None)
        title: str | None = input.get("title", None)
        sections: list | None = input.get("sections", None)

        user = info.context.user
        submission = user.submissions.select_related("manuscript").get(
            pk=from_global_id(submission_id).id
        )
        manuscript: Manuscript = submission.manuscript

        if subject_area:
            subject = JournalSubjectArea.objects.get(name=subject_area)
            manuscript.subject_area = subject

        if article_type:
            submission.article_type = article_type
            submission.save()

            if sections is None:
                raise GraphQLError("manuscript sections are missing")

            manuscript.sections.delete()

            get_article_section = lambda id: ArticleTypeSection.objects.get(
                pk=from_global_id(id).id
            )

            ManuscriptSection.objects.bulk_create(
                [
                    ManuscriptSection(
                        section=get_article_section(section.get("section_id")),
                        content=json.dumps(
                            [
                                {
                                    "type": "paragraph",
                                    "children": [{"text": section.get("content")}],
                                }
                            ]
                        ),
                        manuscript=manuscript,
                    )
                    for section in sections
                ]
            )

        if journal_name:
            journal = Journal.objects.get(name=journal_name)
            manuscript.journal = journal

        if word_count:
            manuscript.word_count = word_count

        if title:
            manuscript.title = title

        manuscript.save()

        if sections:
            sections_qs = manuscript.sections.all()

            for section in sections:
                for section_qs in sections_qs:
                    if section_qs.section.name == section.get("section_name"):
                        section_qs.content = section.get("content")
                        section_qs.save()

        return CreateSubmissionMutation(message="success", submission=submission)


class UpdateAuthorMutation(graphene.relay.ClientIDMutation):
    """
    Update manuscript authors informations
    """

    submission = graphene.Field(SubmissionNode)
    message = graphene.String()

    class Input:
        submission_id = graphene.ID(required=True)
        authors = graphene.List(UpdateAuthorInput)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        authors = input.get("authors", None)

        user = info.context.user
        manuscript = Manuscript.objects.select_related("journal", "subject_area").get(
            author_submission__pk=from_global_id(submission_id).id,
            author_submission__user__pk=user.pk,
        )

        if authors:
            for author in authors:
                if author["action"] == "create":
                    author.pop("action")
                    manuscript.authors.create(manuscript=manuscript, **author)
                elif author["action"] == "update" and "id" in author and author["id"]:
                    author_model = manuscript.authors.get(
                        pk=from_global_id(author["id"]).id
                    )

                    for key, value in author.items():
                        if key not in ("action", "id"):
                            setattr(author_model, key, value)

                    author_model.save()
                else:
                    author_model = manuscript.authors.get(
                        pk=from_global_id(author["id"]).id
                    )
                    author_model.delete()

        submission = AuthorSubmission.objects.get(pk=from_global_id(submission_id).id)

        return CreateAuthorMutation(submission=submission, message="success")


class UpdateStatementMutation(graphene.relay.ClientIDMutation):
    """
    Update manuscript submissions statements
    """

    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Input:
        submission_id = graphene.ID(required=True)
        statements = graphene.List(UpdateStatementInput)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        statements = input.get("statements")

        user = info.context.user
        submission = user.submissions.get(pk=from_global_id(submission_id).id)

        terms_qs = TermOfService.objects.filter(
            pk__in=map(lambda s: from_global_id(s["term_id"]).id, statements)
        )

        conditions_qs = SubmissionConditionAgreement.objects.filter(
            pk__in=map(lambda s: from_global_id(s["id"]).id, statements)
        )

        for i, statement in enumerate(statements):
            instance = conditions_qs[i]

            instance.statement = statement.get("statement", None)
            instance.response = cast(statement.get("response"))
            instance.term = terms_qs[i]

            instance.save()

        return UpdateStatementMutation(message="success", submission=submission)


class DeleteSubmissionFileMutation(graphene.relay.ClientIDMutation):
    """
    Delete a submission file
    """

    message = graphene.String()
    submission = graphene.Field(SubmissionNode)

    class Input:
        submission_id = graphene.ID(required=True)
        submission_file_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")
        submission_file_id = input.get("submission_file_id")

        user = info.context.user
        submission = user.submissions.get(pk=from_global_id(submission_id).id)
        file = submission.files.get(pk=from_global_id(submission_file_id).id)

        file.delete()

        return DeleteSubmissionFileMutation(message="success", submission=submission)


## DELETING THE SUBMISSION ENTRY ###


class DeleteAuthorSubmissionMutation(graphene.relay.ClientIDMutation):
    """Delete the author submission entry."""

    message = graphene.String()

    class Input:
        submission_id = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        submission_id = input.get("submission_id")

        user = info.context.user
        submission = user.submissions.get(pk=from_global_id(submission_id).id)

        submission.delete()

        return DeleteAuthorSubmissionMutation(message="success")
