import json

from mixer.backend.django import mixer

from SubmissionPortal.models import AuthorSubmission
from Cores.models import SubjectDiscipline

from django.contrib.auth import get_user_model, models
from django.utils import timezone

from graphene.utils.str_converters import to_snake_case
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from graphql_relay import to_global_id

from Journals.models import Journal, Editor, EditorialMember, Reviewer
from Journals.nodes import JournalNode, EditorNode, ReviewerNode

from PeerReviewPortal.models import JournalSubmission
from PeerReviewPortal.nodes import JournalSubmissionNode


# Create your tests here.
class JournalSubmissionTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        models.Group.objects.create(name="editors")
        models.Group.objects.create(name="reviewers")

        cls.userInfo = {
            "firstName": "duke",
            "lastName": "effiom",
            "email": "effiomduke@gmail.com",
            "password": "finestduke12",
            "country": "nigeria",
            "state": "lagos",
        }

        users = [
            {
                "first_name": "duke",
                "last_name": "rice",
                "email": "riceduke@gmail.com",
                "password": "finestduke12",
                "country": "nigeria",
                "state": "lagos",
            },
            {
                "first_name": "john",
                "last_name": "doe",
                "email": "johndoe@gmail.com",
                "password": "finestduke12",
                "country": "nigeria",
                "state": "abuja",
            },
            {
                "first_name": "james",
                "last_name": "downey",
                "email": "jamesdowneygmail.com",
                "password": "finestduke12",
                "country": "nigeria",
                "state": "abia",
            },
            {
                "first_name": "rico",
                "last_name": "beans",
                "email": "ricobeans@gmail.com",
                "password": "finestduke12",
                "country": "nigeria",
                "state": "kano",
            },
        ]

        editors = [
            {
                "affiliation": "university of lagos, lagos",
                "phone_number": "+2347037606116",
            },
            {
                "affiliation": "university of abuja, abuja",
                "phone_number": "+2347037606117",
            },
            {
                "affiliation": "abia state university, abia",
                "phone_number": "+2347037606118",
            },
            {
                "affiliation": "bayero university, kano",
                "phone_number": "+2347037606119",
            },
        ]

        reviewers = [
            {"is_anonymous": True, "affiliation": "university of lagos, lagos"},
            {"is_anonymous": False, "affiliation": "university of lagos, lagos"},
            {"is_anonymous": False, "affiliation": "university of lagos, lagos"},
            {"is_anonymous": False, "affiliation": "university of lagos, lagos"},
        ]

        cls.users = get_user_model().objects.bulk_create(
            [get_user_model()(**user) for user in users]
        )

        cls.editors = Editor.objects.bulk_create(
            [
                Editor(**{**editor, **{"user": cls.users[i]}})
                for i, editor in enumerate(editors)
            ]
        )

        cls.reviewers = Reviewer.objects.bulk_create(
            [
                Reviewer(**{**reviewer, **{"user": cls.users[i]}})
                for i, reviewer in enumerate(reviewers)
            ]
        )

        cls.user = get_user_model().objects.create(
            **{to_snake_case(k): v for k, v in cls.userInfo.items()}
        )

        dicipline = SubjectDiscipline.objects.create(name="life sciences")
        journal = Journal.objects.create(name="biolife", subject_dicipline=dicipline)

        journal.editors.set(cls.editors)
        journal.reviewers.set(cls.reviewers)

        cls.auth_token: str = get_token(cls.user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.journal: Journal = journal

        cls.data = {
            "isAccepted": True,
            "journalId": to_global_id(JournalNode, cls.journal.pk),
            "editors": [
                {
                    "editorId": to_global_id(EditorNode, cls.editors[0].pk),
                    "role": EditorialMember.Role.COPY.name,
                },
                {
                    "editorId": to_global_id(EditorNode, cls.editors[1].pk),
                    "role": EditorialMember.Role.LINE.name,
                },
                {
                    "editorId": to_global_id(EditorNode, cls.editors[2].pk),
                    "role": EditorialMember.Role.SECTION.name,
                },
            ],
            "reviewers": [
                {"reviewerId": to_global_id(ReviewerNode, cls.reviewers[0].pk)},
                {"reviewerId": to_global_id(ReviewerNode, cls.reviewers[1].pk)},
                {"reviewerId": to_global_id(ReviewerNode, cls.reviewers[2].pk)},
                {"reviewerId": to_global_id(ReviewerNode, cls.reviewers[3].pk)},
            ],
        }

    def test_updating_submission(self):
        submission = JournalSubmission.objects.create(
            stage="with line editor",
            author_submission=mixer.blend(
                AuthorSubmission,
                user=self.user,
                article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
            ),
            journal=self.journal,
        )
        editor = Editor.objects.create(
            **{
                "affiliation": "bayero university, kano",
                "phone_number": "+2347037606119",
                "user": self.user,
            }
        )

        editor.journals.add(self.journal)
        self.journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        data = {
            "submissionId": to_global_id(JournalSubmissionNode, submission.pk),
            "journalId": self.data["journalId"],
            "editors": self.data["editors"],
        }

        response = self.query(
            """
            mutation updateSubmission($input: AssignHandlingEditorsMutationInput!) {
                assignEditors(input: $input) {
                    message
                    submission {
                        id
                        isAccepted
                    }
                }
            }
            """,
            operation_name="updateSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["assignEditors"]

        self.assertEqual(content["message"], "success")
        self.assertIsNone(content["submission"]["isAccepted"])
        self.assertEqual(submission.editorial_members.count(), len(data["editors"]))
        self.assertTrue(
            submission.editorial_members.filter(
                role=EditorialMember.Role.COPY, editor__pk=self.editors[0].pk
            ).exists()
        )

    def test_unauthorized_editor_update_submission(self):
        submission = JournalSubmission.objects.create(
            stage="with line editor",
            journal=self.journal,
            author_submission=mixer.blend(
                AuthorSubmission,
                user=self.user,
                article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
            ),
        )
        editor = Editor.objects.create(
            **{
                "affiliation": "bayero university, kano",
                "phone_number": "+2347037606119",
                "user": self.user,
            }
        )

        editor.journals.add(self.journal)
        self.journal.assign_editor_role(editor, EditorialMember.Role.LINE)

        data = {
            "submissionId": to_global_id(JournalSubmissionNode, submission.pk),
            "journalId": self.data["journalId"],
            "editors": self.data["editors"],
        }

        response = self.query(
            """
            mutation updateSubmission($input: AssignHandlingEditorsMutationInput!) {
                assignEditors(input: $input) {
                    message
                    submission {
                        id
                        isAccepted
                    }
                }
            }
            """,
            operation_name="updateSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_query_all_submissions(self):
        JournalSubmission.objects.bulk_create(
            [
                JournalSubmission(
                    **{
                        "stage": "with line editor",
                        "author_submission": mixer.blend(
                            AuthorSubmission,
                            user=self.user,
                            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
                        ),
                        "journal": self.journal,
                    }
                )
                for user in self.users
            ]
        )

        editor = Editor.objects.create(
            **{
                "affiliation": "bayero university, kano",
                "phone_number": "+2347037606119",
                "user": self.user,
            }
        )

        editor.journals.add(self.journal)
        self.journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        data = {"journalId": to_global_id(JournalNode, self.journal.pk)}

        response = self.query(
            """
            query GetSubmissions($journalId: ID!) {
                journalSubmissions(journalId: $journalId) {
                    edges {
                        node {
                            id
                            isAccepted
                            createdAt
                            authorSubmission {
                                id,
                                articleType
                            }
                        }
                    }
                }
            }
            """,
            operation_name="GetSubmissions",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertIsNone(
            content["journalSubmissions"]["edges"][0]["node"]["isAccepted"]
        )

    def test_query_a_submission(self):
        submission = JournalSubmission.objects.create(
            **{
                "stage": "with line editor",
                "author_submission": mixer.blend(
                    AuthorSubmission,
                    user=self.users[0],
                    article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
                ),
                "journal": self.journal,
                "is_accepted": timezone.now(),
            }
        )

        submission.reviewers.add(*self.reviewers)
        members = submission.editorial_members.all()

        for i, member in enumerate(members):
            member.editor = self.editors[i]
            member.save()

        editor = Editor.objects.create(
            **{
                "affiliation": "bayero university, kano",
                "phone_number": "+2347037606119",
                "user": self.user,
            }
        )

        editor.journals.add(self.journal)
        self.journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        data = {
            "journalId": to_global_id(JournalNode, self.journal.pk),
            "submissionId": to_global_id(JournalSubmissionNode, submission.pk),
        }

        response = self.query(
            """
            query GetSubmission($journalId: ID!, $submissionId: ID!) {
                journalSubmission(journalId: $journalId, submissionId: $submissionId) {
                    id
                    isAccepted
                    createdAt
                    authorSubmission {
                        id
                        user {
                            firstName
                            lastName
                        }
                    }
                    editorialMembers {
                        edges {
                            node {
                                id
                                role
                                createdAt
                                editor {
                                    id
                                    affiliation
                                    user {
                                        firstName
                                        lastName
                                    }
                                }
                            }
                        }
                    }
                    reviewers {
                        edges {
                            node {
                                id
                                isAnonymous
                                affiliation
                                user {
                                    firstName
                                    lastName
                                }
                            }
                        }
                    }
                }
            }
            """,
            operation_name="GetSubmission",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["journalSubmission"]

        self.assertIsNotNone(content["isAccepted"])
        self.assertEqual(len(content["reviewers"]["edges"]), len(self.reviewers))
        self.assertEqual(
            len(content["editorialMembers"]["edges"]), len(self.editors) - 1
        )
        self.assertEqual(
            content["authorSubmission"]["user"]["firstName"],
            self.users[0].first_name,
        )
