import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from graphene_django.utils.testing import GraphQLTestCase
from graphene_file_upload.django.testing import GraphQLFileUploadTestMixin
from graphql_jwt.shortcuts import get_token
from graphql_relay import to_global_id

from mixer.backend.django import mixer

from Cores.models import SubjectDiscipline
from Journals.models.roles import EditorialMember
from Journals.nodes.journals import JournalNode
from ..models.journals import Journal
from ..models.editors import Editor


class JournalTestcase(GraphQLFileUploadTestMixin, GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="editors")
        Group.objects.create(name="reviewers")

        cls.user = mixer.blend(get_user_model(), is_staff=True)
        cls.auth_token: str = get_token(cls.user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.dicipline = SubjectDiscipline.objects.create(name="life sciences")

    def test_staff_create_journal(self):

        input = {
            "name": "biofuel",
            "issn": "455ab5567j7",
            "subjectDiscipline": self.dicipline.name,
        }

        response = self.query(
            """
            mutation CreateJournal($name: String!, $issn: String!, $subjectDiscipline: String !) {
                createJournal(name: $name, issn: $issn, subjectDiscipline: $subjectDiscipline) {
                    message
                }
            }
            """,
            operation_name="CreateJournal",
            variables=input,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createJournal"]

        self.assertEqual(content["message"], "success")

    def test_unauthorized_personnel_create_journal(self):
        user = mixer.blend(get_user_model())
        auth_token = get_token(user)

        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {auth_token}",
        }

        input = {
            "name": "biofuel",
            "issn": "455ab5567j7",
            "subjectDiscipline": self.dicipline.name,
        }

        response = self.query(
            """
            mutation CreateJournal( $name: String!, $issn: String!, $subjectDiscipline: String !) {
                createJournal(name: $name, issn: $issn, subjectDiscipline: $subjectDiscipline) {
                    message
                }
            }
            """,
            operation_name="CreateJournal",
            variables=input,
            headers=headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_transfer_of_journal_management(self):
        editor = mixer.blend(Editor)
        journal = mixer.blend(Journal)

        input = {
            "email": editor.user.email,
            "journalId": to_global_id(JournalNode, journal.pk),
        }

        response = self.query(
            """
            mutation TransferJournalManagement($email: String !, $journalId: ID !) {
                transferManagement(email: $email, journalId: $journalId) {
                    message
                }
            }
            """,
            operation_name="TransferJournalManagement",
            variables=input,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertEqual(content["transferManagement"]["message"], "success")
        self.assertEqual(
            journal.editorial_members.get(
                role=EditorialMember.Role.CHIEF.value
            ).editor.user.first_name,
            editor.user.first_name,
        )
