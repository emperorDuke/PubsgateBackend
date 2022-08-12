from django.shortcuts import get_object_or_404
import graphene
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required

from ..models import Editor, Journal, RecruitmentApplication
from ..nodes import Editor as EditorNode
from ..permissions.editors import editor_in_chief_required


class AcceptEditorMutation(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        journal_id = graphene.ID(required=True)

    @editor_in_chief_required()
    @login_required
    def mutate(root, info, **kwargs):
        journal_id = kwargs.get("journal_id")
        email = kwargs.get("email")

        user = get_user_model().objects.get(email=email)
        journal = Journal.objects.get(pk=journal_id)

        RecruitmentApplication.objects.create(
            user=user,
            journal=journal,
            status=RecruitmentApplication.Status.ACCEPTED,
            role=RecruitmentApplication.Role.EDITOR,
        )

        url = "/editor/application?JID={0}".format(journal_id)

        from_email = "{0}@pubsgate.com".format(journal.name)
        subject = "Invitation to be a reviewer for {0} journal".format(journal.name)
        text_content = "Application is accepted"
        to = [email]
        html_content = (
            "<div><h3> Your application for the role of editor has been accepted"
            "click on the link below to confirm acceptance of the role and fill out the necessary information</h3>"
            "<a>{0}</a></div>"
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content.format(url), "text/html")
        msg.send()

        return AcceptEditorMutation(message="success")


class CreateEditorMutation(graphene.Mutation):
    editor = graphene.Field(EditorNode)
    message = graphene.String()

    class Arguments:
        affiliation = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        journal_id = graphene.ID(required=True)
        specialisation = graphene.String(required=True)

    @login_required
    def mutate(root, info, **kwargs):
        user = info.context.user
        affiliation = kwargs.get("affiliation")
        phone_number = kwargs.get("phone_number")
        specialisation = kwargs.get("specialisation")

        journal = Journal.objects.get(pk=kwargs.get("journal_id"))

        application = RecruitmentApplication.objects.filter(
            user=user,
            status=RecruitmentApplication.Status.ACCEPTED,
            role=RecruitmentApplication.Role.EDITOR,
            journal=journal,
        ).first()

        if not application:
            raise GraphQLError("application does not exist")

        ## A user cannot be a reviewer and editor in the same journal
        editor_exist = journal.editors.filter(user__pk=user.pk).exists()

        if editor_exist:
            raise GraphQLError("user already exists as an editor on this journal")

        reviewer_exist = journal.reviewers.filter(user__pk=user.pk).exists()

        if reviewer_exist:
            raise GraphQLError("user already exists as a reviewer on this journal")

        editor = Editor.objects.create(
            affiliation=affiliation,
            phone_number=phone_number,
            specialisation=specialisation,
            user=user,
        )

        editor.journals.add(journal)

        application.status = RecruitmentApplication.Status.COMPLETED
        application.save()

        message = "successfully created" if editor else "failed operation"

        return CreateEditorMutation(editor=editor, message=message)


class AdminCreateEditorMutation(graphene.Mutation):
    """
    Admin portal for creation of a new editor
    """

    editor = graphene.Field(EditorNode)
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        affiliation = graphene.String()
        phone_number = graphene.String()
        journal_id = graphene.ID(required=True)
        specialisation = graphene.String()

    @staff_member_required
    @login_required
    def mutate(root, info, **kwargs):
        affiliation = kwargs.get("affiliation", None)
        phone_number = kwargs.get("phone_number", None)
        specialisation = kwargs.get("specialisation", None)
        email = kwargs.get("email")
        journal_id = kwargs.get("journal_id")

        user = get_object_or_404(get_user_model(), email=email)
        journal = get_object_or_404(Journal, pk=journal_id)

        editor_exist = journal.editors.filter(user__pk=user.pk).exists()
        reviewer_exist = journal.reviewers.filter(user__pk=user.pk).exists()

        ## A user cannot be a reviewer and editor in the same journal
        if editor_exist:
            raise GraphQLError("user already exists as an editor on this journal")

        if reviewer_exist:
            raise GraphQLError("user already exists as a reviewer on this journal")

        editor = Editor.objects.create(
            affiliation=affiliation,
            phone_number=phone_number,
            specialisation=specialisation,
            user=user,
        )

        editor.journals.add(journal)

        message = "successfully created" if editor else "failed operation"

        return AdminCreateEditorMutation(editor=editor, message=message)
