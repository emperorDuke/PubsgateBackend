import graphene
from Cores.models import Discipline
from django.shortcuts import get_object_or_404
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required

from ..inputTypes.journals import (
    Action,
    JournalInformationInput,
    JournalSubjectAreaInput,
)
from ..models import (
    Editor,
    Journal,
    JournalInformation,
    JournalSubjectArea,
)
from ..nodes import Journal as JournalType, JournalInformation as JournalInformationType
from ..permissions import editor_in_chief_required


class CreateJournalMutation(graphene.Mutation):
    journal = graphene.Field(JournalType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        issn = graphene.String(required=True)
        discipline = graphene.String(required=True)

    @staff_member_required
    @login_required
    def mutate(root, info, **kwargs):
        discipline = Discipline.objects.get(name=kwargs.pop("discipline"))

        journal = Journal.objects.create(discipline=discipline, **kwargs)

        return CreateJournalMutation(journal=journal, message="success")


class EditJournalMutation(graphene.Mutation):
    journal = graphene.Field(JournalType)
    message = graphene.String()

    class Arguments:
        journal_id = graphene.ID(required=True)
        publication_start_date = graphene.Date()
        publication_frequency = graphene.Enum.from_enum(Journal.PublicationFrequency)()
        iso_abbreviation = graphene.String()
        logo = Upload()

    @editor_in_chief_required()
    @login_required
    def mutate(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
        journal = get_object_or_404(Journal, pk=journal_id)

        for k, v in kwargs.items():
            setattr(journal, k, v)

        journal.full_clean()
        journal.save()

        return EditJournalMutation(journal=journal, message="success")


class JournalSubjectAreaMutation(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        journal_id = graphene.ID(required=True)
        subject_areas = graphene.List(JournalSubjectAreaInput, required=True)

    @editor_in_chief_required()
    @login_required
    def mutate(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
        subject_areas = kwargs.get("subject_areas")

        journal = get_object_or_404(Journal, pk=journal_id)

        for area in subject_areas:
            if area["action"] == Action.CREATE:
                JournalSubjectArea.objects.create(name=area["name"], journal=journal)
            elif area["action"] == Action.UPDATE and "id" in area and area["id"]:
                JournalSubjectArea.objects.filter(pk=area["id"]).update(
                    name=area["name"]
                )
            else:
                JournalSubjectArea.objects.filter(pk=area["id"]).delete()

        return JournalSubjectAreaMutation(message="success")


class EditJournalInformationMutation(graphene.Mutation):
    message = graphene.String()
    information = graphene.List(JournalInformationType)

    class Arguments:
        journal_id = graphene.ID(required=True)
        information = graphene.List(JournalInformationInput, required=True)

    @editor_in_chief_required()
    @login_required
    def mutate(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
        information = {
            str(info["heading_id"]): info["content"]
            for info in kwargs.get("information")
        }

        journal_information = JournalInformation.objects.filter(
            journal__pk=journal_id
        ).select_related("heading")

        for infoModel in journal_information:
            heading_id = str(infoModel.heading.pk)

            if heading_id in information:
                infoModel.content = information[heading_id]
                infoModel.save()

        return EditJournalInformationMutation(
            message="success", information=journal_information
        )


class TransferJournalManagementMutation(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        journal_id = graphene.ID(required=True)
        email = graphene.String(required=True)

    @staff_member_required
    @login_required
    def mutate(root, info, **kwargs):
        email = kwargs.pop("email")
        journal_id = kwargs.pop("journal_id")

        editor = Editor.objects.filter(user__email=email).first()

        if not editor:
            raise GraphQLError("manager is not an editor")

        journal = Journal.objects.get(pk=journal_id)

        journal.make_editor_chief(editor)

        return TransferJournalManagementMutation(message="success")
