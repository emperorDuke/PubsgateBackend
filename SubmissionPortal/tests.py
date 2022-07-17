import json
import os

from mixer.backend.django import mixer

from django.contrib.auth import get_user_model, models
from django.core.files.uploadedfile import SimpleUploadedFile

from graphene_django.utils.testing import GraphQLTestCase
from graphene_file_upload.django.testing import GraphQLFileUploadTestMixin
from graphql_jwt.shortcuts import get_token
from graphql_relay import from_global_id, to_global_id
from graphene.utils.str_converters import to_snake_case

from Cores.models import ArticleType, ArticleTypeSection, SubjectDiscipline
from Cores.models import TermOfService
from Cores.nodes import ArticleTypeSectionNode, TermOfServiceNode

from Journals.models import Journal, JournalSubjectArea

from Contents.models import Manuscript, ManuscriptAuthor, ManuscriptSection
from Contents.nodes import ManuscriptAuthorNode

from SubmissionPortal.models import (
    AuthorSubmission,
    SubmissionConditionAgreement,
    SubmissionFile,
)
from SubmissionPortal.nodes import (
    SubmissionNode,
    SubmissionAgreementNode,
    SubmissionFileNode,
)


class SubmissionsTests(GraphQLFileUploadTestMixin, GraphQLTestCase):

    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):

        models.Group.objects.create(name="reviewers")

        cls.userInfo = {
            "firstName": "duke",
            "lastName": "effiom",
            "email": "effiomduke@gmail.com",
            "password": "finestduke12",
            "country": "nigeria",
            "state": "lagos",
        }

        user = get_user_model().objects.create(
            **{to_snake_case(k): v for k, v in cls.userInfo.items()}
        )

        dicipline = SubjectDiscipline.objects.create(name="life sciences")
        journal = Journal.objects.create(name="biolife", subject_discipline=dicipline)
        subject = JournalSubjectArea.objects.create(
            name="microbiology", journal=journal
        )

        cls.article_types_qs = mixer.cycle().blend(ArticleType)
        cls.sections_qs = mixer.cycle().blend(
            ArticleTypeSection, article_type=mixer.sequence(*cls.article_types_qs)
        )

        cls.auth_token: str = get_token(user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.journal = journal
        cls.subject = subject
        cls.user = user

    def test_create_manuscript(self):
        section_id = to_global_id(ArticleTypeSectionNode, self.sections_qs[1].pk)
        section_name = self.sections_qs[1].name

        input = {
            "journalName": self.journal.name,
            "subjectArea": self.subject.name,
            "articleType": AuthorSubmission.ArticleType.RESEARCH_ARTICLE.name,
            "wordCount": 1000,
            "title": "Suppose further we needed to calculate the standard errors of the state income means",
            "sections": [
                {
                    "sectionId": section_id,
                    "sectionName": section_name,
                    "content": "the arguments to cbind() must be either vectors of any length, or matrices with the same",
                }
            ],
        }

        response = self.query(
            """
            mutation StageOneSubmission($input: CreateSubmissionMutationInput!) {
                createAuthorSubmission(input: $input) {
                    message
                    submission {
                        user {
                            firstName
                        }
                        manuscript {
                            id
                            title
                            journal {
                                name
                            }
                            subjectArea {
                                name
                            }
                        }
                    }
                }
            }
            """,
            operation_name="StageOneSubmission",
            variables={"input": input},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createAuthorSubmission"][
            "submission"
        ]

        self.assertEqual(content["manuscript"]["journal"]["name"], self.journal.name)
        self.assertEqual(
            content["manuscript"]["subjectArea"]["name"], self.subject.name
        )

        self.assertEqual(content["user"]["firstName"], self.userInfo["firstName"])
        self.assertEqual(content["manuscript"]["title"], input["title"])

    def test_create_article_type(self):

        manuscript = Manuscript.objects.create(
            title="Suppose further we needed to calculate the standard errors of the state income means",
            journal=self.journal,
            subject_area=self.subject,
            word_count=2000,
        )

        submission = AuthorSubmission.objects.create(
            user=self.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
            manuscript=manuscript,
        )

        input = {
            "submissionId": to_global_id(SubmissionNode, submission.id),
            "authors": [
                {
                    "firstName": "John",
                    "lastName": "Smith",
                    "email": "johnsmith@gmail.com",
                    "affiliation": "university of Aberdeen",
                    "isCorresponding": True,
                    "rank": 1,
                },
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "johnsdoe@gmail.com",
                    "affiliation": "university of Aberdeen",
                    "isCorresponding": False,
                    "rank": 2,
                },
                {
                    "firstName": "John",
                    "lastName": "Smoke",
                    "email": "johnsmoke@gmail.com",
                    "affiliation": "university of Aberdeen",
                    "isCorresponding": False,
                    "rank": 3,
                },
                {
                    "firstName": "John",
                    "lastName": "Snow",
                    "email": "johnsnow@gmail.com",
                    "isCorresponding": False,
                    "affiliation": "university of Aberdeen",
                    "rank": 4,
                },
            ],
        }

        response = self.query(
            """
            mutation StageTwoSubmission($input: CreateAuthorMutationInput!) {
                addSubmissionAuthors(input: $input) {
                    message
                    submission {
                        manuscript {
                            id
                            title
                            journal {
                                name
                            }
                            subjectArea {
                                name
                            }
                        }
                    }
                }
            }
            """,
            operation_name="StageTwoSubmission",
            variables={"input": input},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["addSubmissionAuthors"][
            "submission"
        ]

        self.assertEqual(content["manuscript"]["journal"]["name"], self.journal.name)
        self.assertEqual(
            content["manuscript"]["subjectArea"]["name"], self.subject.name
        )
        self.assertEqual(ManuscriptAuthor.objects.count(), len(input["authors"]))

    def test_submission_file_upload(self):
        submission = mixer.blend(
            AuthorSubmission,
            user=self.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
        )
        file = SimpleUploadedFile(name="test.docx", content=b"test.docx")

        input = {
            "submissionId": to_global_id(SubmissionNode, submission.pk),
            "type": SubmissionFile.FileType.COVER_LETTER.name,
        }

        file = {"file": file}

        headers = {"content-type": "multipart/form-data"}

        headers.update(self.headers)

        response = self.file_query(
            """
            mutation StageThreeSubmission($submissionId: ID!, $type: FileType!, $file: Upload!) {
                uploadSubmissionFile(submissionId: $submissionId, type: $type, file: $file) {
                    message
                }
            }
            """,
            op_name="StageThreeSubmission",
            variables=input,
            files=file,
            headers=headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["uploadSubmissionFile"]

        self.assertEqual(content["message"], "success")

    def test_statements_response(self):
        submission = mixer.blend(
            AuthorSubmission,
            user=self.user,
            article_type=AuthorSubmission.ArticleType.RESEARCH_ARTICLE,
        )
        terms_qs = mixer.cycle(10).blend(TermOfService)

        statements = {
            "submissionId": to_global_id(SubmissionNode, submission.pk),
            "statements": [
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[0].pk),
                    "response": True,
                    "statement": None,
                },
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[1].pk),
                    "response": True,
                    "statement": "blah blah",
                },
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[2].pk),
                    "response": True,
                    "statement": None,
                },
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[3].pk),
                    "response": True,
                    "statement": None,
                },
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[4].pk),
                    "response": False,
                    "statement": None,
                },
            ],
        }

        response = self.query(
            """
            mutation StageFourSubmission($input: CreateStatementMutationInput!) {
                addSubmissionAgreements(input: $input) {
                    message
                    submission {
                        id
                        user {
                            firstName
                        }
                    }
                }
            }
            """,
            operation_name="StageFourSubmission",
            variables={"input": statements},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["addSubmissionAgreements"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(
            content["submission"]["user"]["firstName"], self.userInfo["firstName"]
        )

    def test_author_submission(self):

        manuscript = mixer.blend(
            Manuscript,
            journal=self.journal,
            subject_area=self.subject,
        )

        mixer.cycle(3).blend(
            ManuscriptSection,
            manuscript=manuscript,
            section=mixer.sequence(*self.sections_qs),
            content=json.dumps([{"type": "paragraph"}]),
        )

        submission = mixer.blend(
            AuthorSubmission, user=self.user, manuscript=manuscript
        )

        section_id = to_global_id(ArticleTypeSectionNode, self.sections_qs[1].pk)
        section_name = self.sections_qs[1].name

        data = {
            "submissionId": to_global_id(SubmissionNode, submission.pk),
            "wordCount": 20000,
            "title": "Boquila trifoliolata mimics leaves of an artificial plastic host plants",
            "sections": [
                {
                    "sectionId": section_id,
                    "sectionName": section_name,
                    "content": (
                        "Upon discovery that the Boquila trifoliolata is capable of flexible leaf mimicry, the question of the"
                        "mechanism behind this ability has been unanswered. Here, we demonstrate that plant vision possibly"
                        "via plant-specific ocelli is a plausible hypothesis. A simple experiment by placing an artificial vine model"
                        "above the living plants has shown that these will attempt to mimic the artificial leaves. The experiment"
                        "has been carried out with multiple plants, and each plant has shown attempts at mimicry. It was observed"
                        "that mimic leaves showed altered leaf areas, perimeters, lengths, and widths compared to non-mimic"
                        "leaves. We have calculated four morphometrical features and observed that mimic leaves showed higher"
                    ),
                }
            ],
        }

        response = self.query(
            """
            mutation StageOneSubmission($input: UpdateAuthorSubmissionMutationInput!) {
                editAuthorSubmission(input: $input) {
                    message
                    submission {
                        id
                        manuscript {
                            id
                            title
                            wordCount
                            sections {
                                edges {
                                    node {
                                        id
                                        content
                                        section {
                                            name
                                        }
                                    }
                                }
                            }
                            journal {
                                name
                            }
                            subjectArea {
                                name
                            }
                        }
                    }
                }
            }
            """,
            operation_name="StageOneSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["editAuthorSubmission"][
            "submission"
        ]

        self.assertEqual(content["manuscript"]["wordCount"], data["wordCount"])
        self.assertEqual(content["manuscript"]["title"], data["title"])
        self.assertEqual(
            content["manuscript"]["sections"]["edges"][1]["node"]["section"]["name"],
            data["sections"][0]["sectionName"],
        )

    def test_edit_authors(self):
        manuscript = mixer.blend(
            Manuscript,
            journal=self.journal,
            subject_area=self.subject,
        )

        authors_qs = mixer.cycle(4).blend(ManuscriptAuthor, manuscript=manuscript)
        submission = mixer.blend(
            AuthorSubmission, user=self.user, manuscript=manuscript
        )

        input = {
            "submissionId": to_global_id(SubmissionNode, submission.id),
            "authors": [
                {
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "email": "janedoe@gmail.com",
                    "affiliation": "university of Aberdeen",
                    "isCorresponding": True,
                    "rank": 1,
                    "action": "update",
                    "id": to_global_id(ManuscriptAuthorNode, authors_qs[0].pk),
                },
                {
                    "firstName": "John",
                    "lastName": "Snow",
                    "email": "johnsnow@gmail.com",
                    "isCorresponding": False,
                    "affiliation": "university of Aberdeen",
                    "rank": 4,
                    "action": "delete",
                    "id": to_global_id(ManuscriptAuthorNode, authors_qs[3].pk),
                },
                {
                    "firstName": "Rico",
                    "lastName": "Rice",
                    "email": "ricorice@gmail.com",
                    "isCorresponding": False,
                    "affiliation": "university of Lagos",
                    "rank": 4,
                    "action": "create",
                },
            ],
        }

        response = self.query(
            """
            mutation StageTwoSubmission($input: UpdateAuthorMutationInput!) {
                editSubmissionAuthors(input: $input) {
                    message
                    submission {
                        manuscript {
                            id
                            title
                            authors {
                                firstName
                                lastName
                                rank
                                email
                            }
                            journal {
                                name
                            }
                            subjectArea {
                                name
                            }
                        }
                    }
                }
            }
            """,
            operation_name="StageTwoSubmission",
            variables={"input": input},
            headers=self.headers,
        )

        content = json.loads(response.content)["data"]["editSubmissionAuthors"][
            "submission"
        ]

        self.assertEqual(len(content["manuscript"]["authors"]), 4)
        self.assertEqual(
            content["manuscript"]["authors"][3]["email"], input["authors"][2]["email"]
        )
        with self.assertRaises(ManuscriptAuthor.DoesNotExist):
            ManuscriptAuthor.objects.get(
                pk=from_global_id(input["authors"][1]["id"]).id
            ),

    def test_edit_submission_statements(self):
        terms_qs = mixer.cycle(10).blend(TermOfService)

        manuscript = mixer.blend(
            Manuscript,
            journal=self.journal,
            subject_area=self.subject,
        )

        submission = mixer.blend(
            AuthorSubmission, user=self.user, manuscript=manuscript
        )

        conditions_qs = mixer.cycle(4).blend(
            SubmissionConditionAgreement,
            author_submission=submission,
            term=mixer.sequence(*terms_qs),
        )

        data = {
            "submissionId": to_global_id(SubmissionNode, submission.id),
            "statements": [
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[1].pk),
                    "statement": "i wanted to go",
                    "response": False,
                    "id": to_global_id(SubmissionAgreementNode, conditions_qs[1].pk),
                },
                {
                    "termId": to_global_id(TermOfServiceNode, terms_qs[2].pk),
                    "statement": "yeah yeah",
                    "response": True,
                    "id": to_global_id(SubmissionAgreementNode, conditions_qs[3].pk),
                },
            ],
        }

        response = self.query(
            """
            mutation StageFourSubmissionEdit($input: UpdateStatementMutationInput!) {
                editSubmissionAgreements(input: $input) {
                    message
                    submission {
                        agreements {
                            edges {
                                node {
                                    id
                                    response
                                    statement
                                    documentedAt
                                    term {
                                        section
                                        question
                                        group
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            operation_name="StageFourSubmissionEdit",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["editSubmissionAgreements"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(len(content["submission"]["agreements"]["edges"]), 4)
        self.assertEqual(
            content["submission"]["agreements"]["edges"][3]["node"]["statement"],
            data["statements"][1]["statement"],
        )
        self.assertEqual(
            content["submission"]["agreements"]["edges"][1]["node"]["statement"],
            data["statements"][0]["statement"],
        )

    def test_delete_submission_file(self):
        submission = mixer.blend(AuthorSubmission, user=self.user)

        file_1 = SimpleUploadedFile(name="test_1.jpg", content=b"test_1.jpg")
        file_2 = SimpleUploadedFile(name="test_2.jpg", content=b"test_2.jpg")

        submission_file_1 = SubmissionFile.objects.create(
            author_submission=submission,
            file_type=SubmissionFile.FileType.COVER_LETTER,
            file=file_1,
        )

        submission_file_2 = SubmissionFile.objects.create(
            author_submission=submission,
            file_type=SubmissionFile.FileType.MANUSCRIPT,
            file=file_2,
        )

        data = {
            "submissionId": to_global_id(SubmissionNode, submission.pk),
            "submissionFileId": to_global_id(SubmissionFileNode, submission_file_1.pk),
        }

        response = self.query(
            """
            mutation DeleteFile($input: DeleteSubmissionFileMutationInput!) {
                deleteSubmissionFile(input: $input) {
                    message
                }
            }
            """,
            operation_name="DeleteFile",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["deleteSubmissionFile"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(SubmissionFile.objects.count(), 1)
        self.assertEqual(
            SubmissionFile.objects.get(pk=submission_file_2.pk), submission_file_2
        )
        with self.assertRaises(SubmissionFile.DoesNotExist):
            SubmissionFile.objects.get(pk=submission_file_1.pk)
        self.assertFalse(os.path.exists(submission_file_1.file.path))

    def test_delete_author_submission(self):
        submissions = mixer.cycle(3).blend(AuthorSubmission, user=self.user)

        data = {
            "submissionId": to_global_id(SubmissionNode, submissions[1].pk),
        }

        response = self.query(
            """
            mutation DeleteAuthorSubmission($input:  DeleteAuthorSubmissionMutationInput!) {
                deleteAuthorSubmission(input: $input) {
                    message
                }
            }
            """,
            operation_name="DeleteAuthorSubmission",
            variables={"input": data},
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["deleteAuthorSubmission"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(AuthorSubmission.objects.count(), 2)
        with self.assertRaises(AuthorSubmission.DoesNotExist):
            AuthorSubmission.objects.get(pk=submissions[1].pk)

    def test_query_all_submissions(self):
        manuscripts = mixer.cycle(3).blend(Manuscript)

        mixer.cycle(3).blend(
            ManuscriptSection,
            manuscript=mixer.sequence(*manuscripts),
            section=mixer.sequence(*self.sections_qs),
            content=json.dumps([{"type": "paragraph"}]),
        )

        submissions = mixer.cycle(3).blend(
            AuthorSubmission, user=self.user, manuscript=mixer.sequence(*manuscripts)
        )

        response = self.query(
            """
            query allUserSubmissions {
                userSubmissions {
                    edges {
                        node {
                            id
                            manuscript {
                                title
                                wordCount
                            }
                        }
                    }
                }
            }
            """,
            operation_name="allUserSubmissions",
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["userSubmissions"]
        submission_node = content["edges"][0]["node"]
        submission = next(
            filter(
                lambda x: str(x.pk) == from_global_id(submission_node["id"]).id,
                submissions,
            )
        )

        self.assertEqual(len(content["edges"]), 3)
        self.assertEqual(
            submission_node["manuscript"]["title"],
            submission.manuscript.title,
        )
        self.assertEqual(
            submission_node["manuscript"]["wordCount"],
            submission.manuscript.word_count,
        )

    def test_query_submission(self):
        manuscript = mixer.blend(Manuscript)

        mixer.cycle(3).blend(
            ManuscriptSection,
            manuscript=manuscript,
            section=mixer.sequence(*self.sections_qs),
            content=json.dumps([{"type": "paragraph"}]),
        )

        submission = mixer.blend(
            AuthorSubmission, user=self.user, manuscript=manuscript
        )

        data = {"submissionId": to_global_id(SubmissionNode, submission.pk)}

        response = self.query(
            """
            query UserSubmission($submissionId: ID!) {
                userSubmission(submissionId: $submissionId) {
                    id
                    manuscript {
                        title
                        sections {
                            edges {
                                node {
                                    id
                                    content
                                    section {
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            operation_name="UserSubmission",
            variables=data,
            headers=self.headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["userSubmission"]
        first_node = content["manuscript"]["sections"]["edges"][0]["node"]
        section = manuscript.sections.get(pk=from_global_id(first_node["id"]).id)

        self.assertEqual(content["manuscript"]["title"], manuscript.title)
        self.assertEqual(
            first_node["section"]["name"],
            section.section.name,
        )
