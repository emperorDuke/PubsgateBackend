from django.shortcuts import get_object_or_404
import graphene
from graphene_file_upload.scalars import Upload

from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required

from Cores.models import Discipline
from ..inputTypes.journals import (
    Action,
    JournalInformationInput,
    JournalSubjectAreaInput,
)

from Journals.models import Journal, Editor
from ..models.journals import JournalInformation, JournalSubjectArea
from Journals.models.roles import EditorialMember
from Journals.nodes import Journal as JournalType
from Journals.permissions import editor_in_chief_required


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

    class Arguments:
        journal_id = graphene.ID(required=True)
        informations = graphene.List(JournalInformationInput, required=True)

    @editor_in_chief_required()
    @login_required
    def mutate(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
        informations = {
            info["heading_id"]: info["content"] for info in kwargs.get("informations")
        }

        journal_informations = JournalInformation.objects.filter(
            journal__pk=journal_id
        ).select_related("heading")

        for infoModel in journal_informations:
            heading_id = infoModel.heading.pk

            if heading_id in informations:
                infoModel.content = informations[heading_id]
                infoModel.save()

        return EditJournalInformationMutation(message="success")


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
            raise GraphQLError("Manager is not an editor")

        journal = Journal.objects.get(pk=journal_id)

        journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        return TransferJournalManagementMutation(message="success")
