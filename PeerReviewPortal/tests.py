import json

from mixer.backend.django import mixer

from SubmissionPortal.models import AuthorSubmission
from Cores.models import ArticleType, ArticleTypeSection, Discipline

from django.contrib.auth import get_user_model, models
from django.core.signing import Signer
from django.utils import timezone

from graphene.utils.str_converters import to_snake_case
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from graphql_relay import from_global_id, to_global_id

from Journals.models import (
    Journal,
    Editor,
    EditorialMember,
    Reviewer,
    JournalPermission,
    JournalReportQuestion,
)
from Journals.nodes import (
    Journal as JournalType,
    Editor as EditorNode,
    ReviewerNode,
    JournalReportQuestionNode,
)

from PeerReviewPortal.models import (
    JournalSubmission,
    ReviewerReport,
    ReviewerReportSection,
)
from PeerReviewPortal.nodes import (
    EditorialMemberNode,
    JournalSubmissionNode,
    ReviewerReportNode,
)
from PeerReviewPortal.permissions import handling_permissions

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

    dicipline = Discipline.objects.create(name="life sciences")
    journal = Journal.objects.create(name="biolife", discipline=dicipline)

    journal.editors.set(cls.editors)
    journal.reviewers.set(cls.reviewers)

    cls.auth_token = get_token(cls.user)
    cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
    cls.journal = journal

    cls.data = {
        "isAccepted": True,
        "journalId": to_global_id(JournalType, cls.journal.pk),
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


def assign_handling_permissions(cls):
    ## assign editor to the journal ##
    cls.editor.journals.add(cls.journal)

    ## journal specific permissions
    permissions_qs = JournalPermission.objects.filter(
        journal__pk=cls.journal.pk,
        code_name__in=handling_permissions,
    )

    ## get the Line editor role/position assigned to this submission
    cls.member = cls.submission.editorial_members.filter(
        role=EditorialMember.Role.LINE
    ).first()

    ## change the role/position editor
    cls.member.editor = cls.editor
    cls.member.save()

    ## grant the editor submission handling permission
    cls.member.permissions.add(*permissions_qs)


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
        self.journal.make_editor_chief(editor)

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
            content=json.dumps(
                [
                    {
                        "type": "paragraph",
                        "children": [
                            {
                                "text": (
                                    "Upon discovery that the Boquila trifoliolata is capable of flexible leaf mimicry, the question of the"
                                    "mechanism behind this ability has been unanswered. Here, we demonstrate that plant vision possibly"
                                    "via plant-specific ocelli is a plausible hypothesis. A simple experiment by placing an artificial vine model"
                                    "above the living plants has shown that these will attempt to mimic the artificial leaves. The experiment"
                                    "has been carried out with multiple plants, and each plant has shown attempts at mimicry. It was observed"
                                    "that mimic leaves showed altered leaf areas, perimeters, lengths, and widths compared to non-mimic"
                                    "leaves. We have calculated four morphometrical features and observed that mimic leaves showed higher"
                                )
                            }
                        ],
                    }
                ]
            ),
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

        ## journal specific permissions
        permissions_qs = JournalPermission.objects.filter(
            journal__pk=self.journal.pk,
            code_name__in=handling_permissions,
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
            "journalId": to_global_id(JournalType, self.journal.pk),
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
            mutation SendMail($input: AcceptReviewerInvitationInput!) {
                acceptReviewerInvitation(input: $input) {
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

        content = json.loads(response.content)["data"]["acceptReviewerInvitation"]

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
        self.journal.make_editor_chief(editor)

        data = {
            "isAccepted": True,
            "journalId": to_global_id(JournalType, self.journal.pk),
            "submissionId": to_global_id(SubmissionNode, submission.pk),
        }

        response = self.query(
            """
            mutation acceptSubmission($input: AcceptSubmissionInput!) {
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

        author_submission = mixer.blend(
            AuthorSubmission,
            user=cls.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
        )

        cls.next_editor = mixer.blend(Editor)
        cls.next_editor.journals.add(cls.journal)

        cls.journal.assign_editor_role(cls.next_editor, EditorialMember.Role.SECTION)

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

        assign_handling_permissions(cls)

    def test_transfer_submission(self):
        next_handler = self.submission.editorial_members.get(
            role=EditorialMember.Role.SECTION
        )

        current_handler = self.member

        has_handling_perms = lambda m: self.submission.editorial_members.filter(
            pk=m.pk,
            permissions__code_name__in=handling_permissions,
        ).exists()

        data = {
            "journalId": to_global_id(JournalType, self.journal.pk),
            "submissionId": to_global_id(SubmissionNode, self.submission.pk),
            "editorialMemberId": to_global_id(EditorialMemberNode, next_handler.pk),
            "clientMutationId": "d4f4f444",
        }

        response = self.query(
            """
            mutation TransferSubmissions($input: TransferHandlingPermissionInput!) {
                transferSubmission(input: $input) {
                    clientMutationId
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
            operation_name="TransferSubmissions",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["transferSubmission"]

        self.assertEqual(content["message"], "success")
        self.assertTrue(has_handling_perms(next_handler))
        self.assertFalse(has_handling_perms(current_handler))
        self.assertEqual(
            content["submission"]["stage"],
            "with {}".format(next_handler.get_role_display()),
        )


class CreateEditorReport(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)
        author_submission = mixer.blend(
            AuthorSubmission,
            user=cls.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
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

        assign_handling_permissions(cls)

    def test_create_editor_report(self):

        data = {
            "report": "the manuscript is good",
            "journalId": to_global_id(JournalType, self.journal.pk),
            "submissionId": to_global_id(SubmissionNode, self.submission.pk),
        }

        response = self.query(
            """
            mutation CreateSubmissionReport($input: CreateEditorReportInput!) {
                createEditorReport(input: $input) {
                    message
                    report {
                        detail
                    }
                    submission {
                        stage
                        journal {
                            name
                        }
                    }
                }
            }
            """,
            operation_name="CreateSubmissionReport",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createEditorReport"]

        self.assertEqual(content["report"]["detail"], data["report"])


class CreateReviewerReport(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

        author_submission = mixer.blend(
            AuthorSubmission,
            user=cls.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
        )

        cls.submission = JournalSubmission.objects.create(
            stage="with line editor",
            author_submission=author_submission,
            journal=cls.journal,
        )

    def test_create_reviewer_reporter(self):
        reviewer = mixer.blend(Reviewer, user=self.user)
        questions = mixer.cycle(3).blend(JournalReportQuestion, journal=self.journal)

        self.submission.reviewers.add(reviewer)

        data = {
            "submissionId": to_global_id(JournalSubmissionNode, self.submission.pk),
            "journalId": to_global_id(Journal, self.journal.pk),
            "reportSections": [
                {
                    "response": "i feel the manuscript is a work in progress",
                    "questionId": to_global_id(JournalReportQuestionNode, question.pk),
                }
                for question in questions
            ],
        }

        response = self.query(
            """
            mutation CreateSubmissionReport($input: CreateReviewerReportInput!) {
                createReviewerReport(input: $input) {
                    message
                    report {
                        sections {
                            edges {
                                node {
                                    response
                                    section {
                                        question
                                        hint
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            operation_name="CreateSubmissionReport",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createReviewerReport"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(len(content["report"]["sections"]["edges"]), len(questions))
        self.assertEqual(
            content["report"]["sections"]["edges"][0]["node"]["section"]["question"],
            questions[0].question,
        )


class EditorQueryTest(GraphQLTestCase):
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
        self.journal.make_editor_chief(editor)

        data = {"journalId": to_global_id(JournalType, self.journal.pk)}

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
        self.journal.make_editor_chief(editor)

        data = {
            "journalId": to_global_id(JournalType, self.journal.pk),
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


class ReviewerQuery(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        dependencies(cls)

        cls.reviewer_1 = mixer.blend(Reviewer, user=cls.user)
        cls.reviewer_2 = mixer.blend(Reviewer)

        cls.reviewer_1.journals.add(cls.journal)
        cls.reviewer_2.journals.add(cls.journal)

        initial_submission = JournalSubmission.objects.create(
            stage="with line editor",
            author_submission=mixer.blend(
                AuthorSubmission,
                article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
            ),
            journal=cls.journal,
        )

        cls.submissions = JournalSubmission.objects.bulk_create(
            [
                JournalSubmission(
                    **{
                        "stage": "with line editor",
                        "author_submission": mixer.blend(
                            AuthorSubmission,
                            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
                        ),
                        "journal": cls.journal,
                    }
                )
                for _ in range(len(cls.users))
            ]
        )

        initial_submission.reviewers.add(cls.reviewer_2)

        for submission in cls.submissions:
            submission.reviewers.add(cls.reviewer_1)

    def test_query_all_reviewer_submissions(self):
        data = {"journalId": to_global_id(JournalType, self.journal.pk)}

        response = self.query(
            """
            query GetReviewerSubmissions($journalId: ID!) {
                reviewerSubmissions(journalId: $journalId) {
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
            operation_name="GetReviewerSubmissions",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["reviewerSubmissions"]

        self.assertIsNone(content["edges"][0]["node"]["isAccepted"])
        self.assertEqual(len(content["edges"]), len(self.submissions))
        self.assertNotEqual(len(content["edges"]), JournalSubmission.objects.count())

    def test_query_reviewer_submission(self):
        data = {
            "journalId": to_global_id(JournalType, self.journal.pk),
            "submissionId": to_global_id(JournalSubmissionNode, self.submissions[0].pk),
        }

        response = self.query(
            """
            query GetSubmission($journalId: ID!, $submissionId: ID!) {
                reviewerSubmission(journalId: $journalId, submissionId: $submissionId) {
                    id
                    isAccepted
                    createdAt
                    authorSubmission {
                        id
                        articleType
                    }
                }
            }
            """,
            operation_name="GetSubmission",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["reviewerSubmission"]

        self.assertIsNone(content["isAccepted"])
        self.assertEqual(int(from_global_id(content["id"]).id), self.submissions[0].pk)
        self.assertEqual(
            int(from_global_id(content["authorSubmission"]["id"]).id),
            self.submissions[0].author_submission.pk,
        )

    def test_query_reviewer_report(self):
        mixer.cycle(3).blend(ReviewerReport)
        questions = mixer.cycle(3).blend(JournalReportQuestion, journal=self.journal)

        report = mixer.blend(
            ReviewerReport,
            reviewer=self.reviewer_1,
            journal_submission=mixer.blend(JournalSubmission, journal=self.journal),
        )

        report_sections = mixer.cycle(3).blend(
            ReviewerReportSection, report=report, section=mixer.sequence(*questions)
        )

        data = {
            "journalId": to_global_id(JournalType, self.journal.pk),
            "reportId": to_global_id(ReviewerReportNode, report.pk),
        }

        response = self.query(
            """
            query GetSubmissionReport($journalId: ID!, $reportId: ID!) {
                reviewerReport(journalId: $journalId, reportId: $reportId) {
                    id
                    createdAt
                    sections {
                        edges {
                            node {
                                response
                            }
                        }
                    }
                }
            }
            """,
            operation_name="GetSubmissionReport",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["reviewerReport"]

        self.assertEqual((from_global_id(content["id"]).id), str(report.pk))
        self.assertEqual(len(content["sections"]["edges"]), len(report_sections))
        self.assertEqual(ReviewerReport.objects.count(), 4)
        self.assertEqual(
            content["sections"]["edges"][0]["node"]["response"],
            report_sections[0].response,
        )
