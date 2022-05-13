import json

from mixer.backend.django import mixer
from Journals.models.journals import JournalPermission
from Journals.permissions.journals import JournalPermissionChoice

from SubmissionPortal.models import AuthorSubmission
from Cores.models import ArticleType, ArticleTypeSection, SubjectDiscipline

from django.contrib.auth import get_user_model, models
from django.core.signing import Signer
from django.utils import timezone

from graphene.utils.str_converters import to_snake_case
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from graphql_relay import to_global_id

from Journals.models import Journal, Editor, EditorialMember, Reviewer
from Journals.nodes import JournalNode, EditorNode, ReviewerNode

from PeerReviewPortal.models import JournalSubmission
from PeerReviewPortal.nodes import JournalSubmissionNode
from SubmissionPortal.nodes import SubmissionNode

from Contents.models import Manuscript, ManuscriptSection


def dependencies(cls):
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

    cls.auth_token = get_token(cls.user)
    cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
    cls.journal = journal

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


# Create your tests here.
class AssignHandlingEditorsTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

    def test_assign_editors(self):
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


class CreateJournalSubmissionTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

    def test_create_submission(self):
        author_submission = mixer.blend(AuthorSubmission, user=self.user)

        data = {
            "authorSubmissionId": to_global_id(SubmissionNode, author_submission.pk)
        }

        response = self.query(
            """
            mutation CreateSubmission($input: CreateJournalSubmissionMutationInput!) {
                submitToJournal(input: $input) {
                    message
                    submission {
                        id
                        isAccepted
                        authorSubmission {
                            articleType
                        }
                    }
                }
            }
            """,
            operation_name="CreateSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["submitToJournal"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(JournalSubmission.objects.count(), 1)
        self.assertEqual(
            content["submission"]["authorSubmission"]["articleType"],
            author_submission.article_type,
        )


class InviteReviewerMutationTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)
        cls.article_types_qs = mixer.cycle().blend(ArticleType)
        cls.sections_qs = mixer.cycle(5).blend(
            ArticleTypeSection,
            article_type=mixer.sequence(*cls.article_types_qs),
            name=mixer.sequence(
                *[
                    "abstract",
                    "introduction",
                    "materials_and_methods",
                    "results_and_discussions",
                    "conclusion",
                ]
            ),
        )

        manuscript = mixer.blend(Manuscript)

        mixer.cycle(3).blend(
            ManuscriptSection,
            manuscript=manuscript,
            section=mixer.sequence(*cls.sections_qs),
        )

        author_submission = mixer.blend(
            AuthorSubmission,
            user=cls.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
            manuscript=manuscript,
        )

        cls.submission = JournalSubmission.objects.create(
            stage="with line editor",
            author_submission=author_submission,
            journal=cls.journal,
        )

        cls.editor = Editor.objects.create(
            affiliation="bayero university, kano",
            phone_number="+2347037606119",
            user=cls.user,
        )

    def test_invite_reviewer(self):

        ## assign editor to the journal ##
        self.editor.journals.add(self.journal)
        self.journal.add_editorial_member(self.editor, EditorialMember.Role.LINE)

        ## journal specific permissions
        permissions_qs = JournalPermission.objects.filter(
            journal__pk=self.journal.pk,
            code_name__in=(
                JournalPermissionChoice.GIVE_REPORTS.value,
                JournalPermissionChoice.EDIT_SUBMISSIONS.value,
            ),
        )

        ## get the Line editor role/position assigned to this submission
        member = self.submission.editorial_members.filter(
            role=EditorialMember.Role.LINE
        ).first()

        ## change the role/position editor
        member.editor = self.editor
        member.save()

        ## grant the editor submission handling permission
        member.permissions.add(*permissions_qs)

        data = {
            "submissionId": to_global_id(JournalSubmissionNode, self.submission.pk),
            "journalId": to_global_id(JournalNode, self.journal.pk),
            "emailAddresses": [
                "reviewer1@gmail.com",
                "reviewer2@gmail.com",
                "reviewer3@gmail.com",
            ],
        }

        response = self.query(
            """
            mutation SendMail($input: InviteReviewerMutationInput!) {
                inviteReviewers(input: $input) {
                    message
                }
            }
            """,
            operation_name="SendMail",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["inviteReviewers"]

        self.assertEqual(content["message"], "success")


class AcceptReviewerInvitationMutationTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

    def test_accept_invitation(self):
        signer = Signer()

        author_submission = mixer.blend(
            AuthorSubmission,
            user=self.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
        )

        submission = JournalSubmission.objects.create(
            stage="with line editor",
            author_submission=author_submission,
            journal=self.journal,
        )

        mixer.blend(Reviewer, user=self.user)

        data = signer.sign_object(
            {"journal_id": self.journal.pk, "submission_id": submission.pk}
        )

        response = self.query(
            """
            mutation SendMail($input: AcceptReviewerInvitationMutationInput!) {
                reviewerAcceptInvitation(input: $input) {
                    message
                    submission {
                        stage
                        journal {
                            name
                        }
                    }
                }
            }
            """,
            operation_name="SendMail",
            variables={"input": {"jsid": data}},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["reviewerAcceptInvitation"]

        self.assertEqual(content["submission"]["stage"], submission.stage)
        self.assertEqual(content["submission"]["journal"]["name"], self.journal.name)


class AcceptSubmissionTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

    def test_accept_submission(self):
        submission = mixer.blend(
            JournalSubmission, is_accepted=None, journal=self.journal
        )

        editor = mixer.blend(Editor, user=self.user)

        editor.journals.add(self.journal)
        self.journal.add_editorial_member(editor, EditorialMember.Role.CHIEF)

        data = {
            "isAccepted": True,
            "journalId": to_global_id(JournalNode, self.journal.pk),
            "submissionId": to_global_id(SubmissionNode, submission.pk),
        }

        response = self.query(
            """
            mutation acceptSubmission($input: AcceptSubmissionMutationInput!) {
                acceptSubmission(input: $input) {
                    message
                    submission {
                        stage
                        isAccepted
                        journal {
                            name
                        }
                    }
                }
            }
            """,
            operation_name="acceptSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["acceptSubmission"]

        self.assertIsNotNone(content["submission"]["isAccepted"])


class UpdateMemberPermissionMutation(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)


class QueryTest(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

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
                for _ in range(len(self.users))
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
