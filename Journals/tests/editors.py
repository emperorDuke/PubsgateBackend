import json

from Cores.models import SubjectDiscipline
from django.contrib.auth import get_user_model, models
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from graphql_relay import to_global_id
from Journals.models import Journal
from Journals.nodes import JournalNode
from mixer.backend.django import mixer
from ..models import Reviewer, Editor

# Create your tests here.


class EditorTestcase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        cls.user = mixer.blend(get_user_model())
        cls.auth_token: str = get_token(cls.user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.journal = mixer.blend(
            Journal, subject_dicipline=mixer.blend(SubjectDiscipline)
        )

        models.Group.objects.create(name="editors")
        models.Group.objects.create(name="reviewers")

        cls.data = {
            "affiliation": "bayero university, kano",
            "phoneNumber": "+2347037606119",
            "journalId": to_global_id(JournalNode, cls.journal.pk),
        }

    def test_create_editor(self):
        response = self.query(
            """
            mutation AddEditor($input: CreateEditorMutationInput!) {
                createEditor(input: $input) {
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
            """,
            operation_name="AddEditor",
            variables={"input": self.data},
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
            """
            mutation AddEditor($input: CreateEditorMutationInput!) {
                createEditor(input: $input) {
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
            """,
            operation_name="AddEditor",
            variables={"input": self.data},
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
            """
            mutation AddEditor($input: CreateEditorMutationInput!) {
                createEditor(input: $input) {
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
            """,
            operation_name="AddEditor",
            variables={"input": self.data},
            headers=self.headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "user already exists as a reviewer on this journal",
        )
