import json

from Cores.models import Discipline
from django.contrib.auth import get_user_model, models
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from Journals.models import Journal
from mixer.backend.django import mixer
from Journals.models.journals import RecruitmentApplication

from Journals.models.roles import EditorialMember
from ..models import Reviewer, Editor

# Create your tests here.


class EditorTestcase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        cls.user = mixer.blend(get_user_model())
        cls.auth_token: str = get_token(cls.user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.journal = mixer.blend(Journal, subject_discipline=mixer.blend(Discipline))

        cls.admin_user = mixer.blend(get_user_model(), is_staff=True)
        cls.admin_auth_token: str = get_token(cls.admin_user)
        cls.admin_headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.admin_auth_token}"}

        models.Group.objects.create(name="editors")
        models.Group.objects.create(name="reviewers")

        RecruitmentApplication.objects.create(
            user=cls.user,
            journal=cls.journal,
            status=RecruitmentApplication.Status.ACCEPTED,
            role=RecruitmentApplication.Role.EDITOR,
        )

        cls.mutation_query = """
            mutation AddEditor($affiliation: String!, $phoneNumber: String!, $specialisation: String!, $journalId: ID!) {
                createEditor(affiliation: $affiliation, phoneNumber: $phoneNumber, specialisation: $specialisation, journalId: $journalId) {
                    message
                    editor {
                        id
                        affiliation
                        phoneNumber
                        user {
                            firstName
                            lastName
                        }
                    }
                }
            }
            """

        cls.admin_mutation_query = """
            mutation AddEditor($email: String !, $affiliation: String, $phoneNumber: String, $specialisation: String, $journalId: ID!) {
                adminCreateEditor(email: $email, affiliation: $affiliation, phoneNumber: $phoneNumber, specialisation: $specialisation, journalId: $journalId) {
                    message
                    editor {
                        id
                        affiliation
                        phoneNumber
                        user {
                            firstName
                            lastName
                        }
                    }
                }
            }
            """

        cls.data = {
            "affiliation": "bayero university, kano",
            "phoneNumber": "+2347037606119",
            "specialisation": "enviromental biologist",
            "journalId": cls.journal.pk,
        }

    def test_accept_editor_application(self):
        user = mixer.blend(get_user_model())

        editor = mixer.blend(Editor, user=self.user)

        editor.journals.add(self.journal)
        self.journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        data = {"email": user.email, "journalId": self.journal.pk}

        response = self.query(
            """
            mutation AcceptEditor($email: String!, $journalId: ID !) {
                acceptEditor(email: $email, journalId: $journalId) {
                    message
                }
            }
            """,
            operation_name="AcceptEditor",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["acceptEditor"]

        self.assertEqual(content["message"], "success")

    def test_register_editor(self):
        response = self.query(
            self.mutation_query,
            operation_name="AddEditor",
            variables=self.data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createEditor"]

        self.assertEqual(content["message"], "successfully created")
        self.assertEqual(content["editor"]["affiliation"], self.data["affiliation"])
        self.assertEqual(content["editor"]["user"]["firstName"], self.user.first_name)

    def test_raise_editor_exists(self):
        editor = mixer.blend(Editor, user=self.user)
        editor.journals.add(self.journal)

        response = self.query(
            self.mutation_query,
            operation_name="AddEditor",
            variables=self.data,
            headers=self.headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "user already exists as an editor on this journal",
        )

    def test_raise_reviewer_exists(self):
        reviewer = mixer.blend(Reviewer, user=self.user)
        reviewer.journals.add(self.journal)

        response = self.query(
            self.mutation_query,
            operation_name="AddEditor",
            variables=self.data,
            headers=self.headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "user already exists as a reviewer on this journal",
        )

    def test_create_editor_by_admin_user(self):
        user = mixer.blend(get_user_model())

        data = {
            "affiliation": "",
            "phoneNumber": None,
            "specialisation": None,
            "journalId": self.journal.pk,
            "email": user.email,
        }

        response = self.query(
            self.admin_mutation_query,
            operation_name="AddEditor",
            variables=data,
            headers=self.admin_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["adminCreateEditor"]

        self.assertEqual(content["message"], "successfully created")
        self.assertEqual(content["editor"]["affiliation"], "")
        self.assertEqual(content["editor"]["user"]["firstName"], user.first_name)
        self.assertTrue(Editor.objects.filter(user__email=user.email).exists())

    def test_create_editor_by_non_admin_will_throw_error(self):
        user = mixer.blend(get_user_model())
        self.data.update({"email": user.email})

        response = self.query(
            self.admin_mutation_query,
            operation_name="AddEditor",
            variables=self.data,
            headers=self.headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_get_an_editor(self):
        editors = mixer.cycle(6).blend(Editor)
        data = {
            "id": str(editors[0].pk),
        }

        response = self.query(
            """
            query GetEditor($id: ID !) {
                editor(id: $id) {
                    id
                    affiliation
                    user {
                        firstName
                        lastName
                        email
                    }
                }
            }
        """,
            operation_name="GetEditor",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["editor"]

        self.assertEqual(content["id"], str(editors[0].pk))
        self.assertEqual(content["user"]["firstName"], editors[0].user.first_name)
        self.assertEqual(content["user"]["lastName"], editors[0].user.last_name)
        self.assertEqual(content["user"]["email"], editors[0].user.email)
