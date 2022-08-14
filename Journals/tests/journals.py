import json
import time

from Cores.models import Discipline, InformationHeading
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from graphene_django.utils.testing import GraphQLTestCase
from graphene_file_upload.django.testing import GraphQLFileUploadTestMixin
from graphql_jwt.shortcuts import get_token
from mixer.backend.django import mixer

from ..models.editors import Editor
from ..models.journals import Journal, JournalInformation, JournalSubjectArea
from ..models.roles import EditorialMember


class JournalTestcase(GraphQLFileUploadTestMixin, GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="editors")
        Group.objects.create(name="reviewers")

        cls.user = mixer.blend(get_user_model(), is_staff=True)
        cls.auth_token: str = get_token(cls.user)
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {cls.auth_token}"}
        cls.dicipline = Discipline.objects.create(name="life sciences")

        cls.n_info_heading = 4
        cls.information_headings = mixer.cycle(cls.n_info_heading).blend(
            InformationHeading
        )
        user = mixer.blend(get_user_model())
        cls.editor = mixer.blend(Editor, user=user)
        cls.journal = mixer.blend(Journal)

        auth_token = get_token(user)

        cls.editor.journals.add(cls.journal)
        cls.journal.make_editor_chief(cls.editor)
        cls.editor_headers = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}

        cls.formatted_information = [
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

    def test_staff_create_journal(self):
        """
        Journals are successfully created when accessed by company staff
        """
        input = {
            "name": "biofuel",
            "issn": "455ab5567j7",
            "discipline": self.dicipline.name,
        }

        response = self.query(
            """
            mutation CreateJournal($name: String!, $issn: String!, $discipline: String !) {
                createJournal(name: $name, issn: $issn, discipline: $discipline) {
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
        """
        Creation of journal should fail when created by a user that is not part of company management
        """
        user = mixer.blend(get_user_model())
        auth_token = get_token(user)

        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {auth_token}",
        }

        input = {
            "name": "biofuel",
            "issn": "455ab5567j7",
            "discipline": self.dicipline.name,
        }

        response = self.query(
            """
            mutation CreateJournal( $name: String!, $issn: String!, $discipline: String !) {
                createJournal(name: $name, issn: $issn, discipline: $discipline) {
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

    def test_transfer_of_journal_management_to_editor(self):
        """
        Transfer of Journal management to the editor should be successful when
        handled by publishing company management staff
        """
        editor = mixer.blend(Editor)
        journal = mixer.blend(Journal)

        input = {
            "email": editor.user.email,
            "journalId": journal.pk,
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

    def test_transfer_of_journal_management_to_non_editor(self):
        """
        Transfer of Journal management to a user that is not an should be raise an error when
        handled by publishing company management staff
        """
        user = mixer.blend(get_user_model())
        journal = mixer.blend(Journal)

        input = {
            "email": user.email,
            "journalId": journal.pk,
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

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "manager is not an editor",
        )

    def test_edit_journal(self):
        file = SimpleUploadedFile(name="logo.jpg", content=b"logo.jpg")
        file = {"logo": file}

        data = {
            "journalId": self.journal.pk,
            "publicationStartDate": time.strftime("%Y-%m-%d"),
            "publicationFrequency": Journal.PublicationFrequency.QUARTERLY.name,
            "isoAbbreviation": self.journal.name[0:4],
        }

        response = self.file_query(
            """
            mutation EditJournal(
                $journalId: ID !, 
                $publicationStartDate: Date, 
                $publicationFrequency: PublicationFrequency, 
                $isoAbbreviation: String, 
                $logo: Upload
                ) {
                editJournal(
                    journalId: $journalId, 
                    publicationStartDate: $publicationStartDate, 
                    publicationFrequency: $publicationFrequency,
                    isoAbbreviation: $isoAbbreviation,
                    logo: $logo
                    ) {
                        message
                        journal {
                            id
                            name
                            publicationStartDate
                            publicationFrequency
                            logo
                            isoAbbreviation
                            discipline {
                                name
                            }
                        }
                }
            }
            """,
            op_name="EditJournal",
            variables=data,
            files=file,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertEqual(content["editJournal"]["message"], "success")
        self.assertEqual(content["editJournal"]["journal"]["name"], self.journal.name)
        self.assertEqual(
            content["editJournal"]["journal"]["publicationStartDate"],
            data["publicationStartDate"],
        )
        self.assertEqual(
            content["editJournal"]["journal"]["publicationFrequency"],
            Journal.PublicationFrequency.QUARTERLY.label,
        )

    def test_edit_journal_by_unauthorized_editor(self):
        self.journal.assign_editor_role(self.editor, EditorialMember.Role.LINE)
        file = SimpleUploadedFile(name="logo.jpg", content=b"logo.jpg")
        file = {"logo": file}

        data = {
            "journalId": self.journal.pk,
            "publicationStartDate": time.strftime("%Y-%m-%d"),
            "publicationFrequency": Journal.PublicationFrequency.QUARTERLY.name,
            "isoAbbreviation": self.journal.name[0:4],
        }

        response = self.file_query(
            """
            mutation EditJournal(
                $journalId: ID !, 
                $publicationStartDate: Date, 
                $publicationFrequency: PublicationFrequency, 
                $isoAbbreviation: String, 
                $logo: Upload
                ) {
                editJournal(
                    journalId: $journalId, 
                    publicationStartDate: $publicationStartDate, 
                    publicationFrequency: $publicationFrequency,
                    isoAbbreviation: $isoAbbreviation,
                    logo: $logo
                    ) {
                        message
                        journal {
                            id
                            name
                            publicationStartDate
                            publicationFrequency
                            logo
                            isoAbbreviation
                            discipline {
                                name
                            }
                        }
                }
            }
            """,
            op_name="EditJournal",
            variables=data,
            files=file,
            headers=self.editor_headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_edit_journal_information(self):
        information_headings = InformationHeading.objects.all()

        data = {
            "journalId": self.journal.pk,
            "information": [
                {
                    "headingId": str(heading.pk),
                    "content": json.dumps(self.formatted_information),
                }
                for heading in information_headings
            ],
        }

        response = self.query(
            """
            mutation EditJournalInfo($journalId: ID !, $information: [JournalInformationInput] !) {
                editJournalInformation(journalId: $journalId, information: $information) {
                    message
                    information {
                        content
                        heading {
                            id
                            name
                        }
                    }
                }
            }
            """,
            operation_name="EditJournalInfo",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["editJournalInformation"]

        self.assertEqual(
            content["information"][0]["content"], data["information"][0]["content"]
        )
        self.assertEqual(
            content["information"][1]["heading"]["id"],
            data["information"][1]["headingId"],
        )

    def test_edit_journal_information_by_unauthorized_editor(self):
        information_headings = InformationHeading.objects.all()
        self.journal.assign_editor_role(self.editor, EditorialMember.Role.LINE)

        data = {
            "journalId": self.journal.pk,
            "information": [
                {
                    "headingId": str(heading.pk),
                    "content": json.dumps(self.formatted_information),
                }
                for heading in information_headings
            ],
        }

        response = self.query(
            """
            mutation EditJournalInfo($journalId: ID !, $information: [JournalInformationInput] !) {
                editJournalInformation(journalId: $journalId, information: $information) {
                    message
                    information {
                        content
                        heading {
                            id
                            name
                        }
                    }
                }
            }
            """,
            operation_name="EditJournalInfo",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_journal_subject_area(self):
        subject_areas = mixer.cycle(5).blend(JournalSubjectArea)

        data = {
            "journalId": self.journal.pk,
            "subjectAreas": [
                {"id": str(subject_areas[0].pk), "name": "biofuel", "action": "UPDATE"},
                {"name": "biolife", "action": "CREATE"},
                {"name": "biosensor", "action": "CREATE"},
                {
                    "id": str(subject_areas[4].pk),
                    "name": subject_areas[4].name,
                    "action": "DELETE",
                },
            ],
        }

        response = self.query(
            """
            mutation SubjectArea($journalId: ID !, $subjectAreas: [JournalSubjectAreaInput] !) {
                journalSubjectArea(journalId: $journalId, subjectAreas: $subjectAreas) {
                    message
                }
            }
            """,
            operation_name="SubjectArea",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["journalSubjectArea"]

        self.assertEqual(content["message"], "success")
        self.assertEqual(
            JournalSubjectArea.objects.get(pk=str(subject_areas[0].pk)).name, "biofuel"
        )
        self.assertEqual(JournalSubjectArea.objects.count(), 6)
        with self.assertRaises(JournalSubjectArea.DoesNotExist):
            JournalSubjectArea.objects.get(pk=str(subject_areas[4].pk))

    def test_journal_subject_area_by_unauthorized_editor(self):
        self.journal.assign_editor_role(self.editor, EditorialMember.Role.LINE)
        subject_areas = mixer.cycle(5).blend(JournalSubjectArea)

        data = {
            "journalId": self.journal.pk,
            "subjectAreas": [
                {"id": str(subject_areas[0].pk), "name": "biofuel", "action": "UPDATE"},
                {"name": "biolife", "action": "CREATE"},
                {"name": "biosensor", "action": "CREATE"},
                {
                    "id": str(subject_areas[4].pk),
                    "name": subject_areas[4].name,
                    "action": "DELETE",
                },
            ],
        }

        response = self.query(
            """
            mutation SubjectArea($journalId: ID !, $subjectAreas: [JournalSubjectAreaInput] !) {
                journalSubjectArea(journalId: $journalId, subjectAreas: $subjectAreas) {
                    message
                }
            }
            """,
            operation_name="SubjectArea",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_get_a_journal(self):
        data = {"id": self.journal.pk}

        response = self.query(
            """
            query GetJournal($id: ID !) {
                journal(id: $id) {
                    id
                    name
                    slug
                    publicationStartDate
                    isoAbbreviation
                    logo
                }
            }
            """,
            operation_name="GetJournal",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertEqual(content["journal"]["name"], self.journal.name)
        self.assertEqual(content["journal"]["slug"], self.journal.slug)
        self.assertEqual(
            content["journal"]["publicationStartDate"],
            self.journal.publication_start_date.strftime("%Y-%m-%d"),
        )

    def test_get_journal_information(self):
        JournalInformation.objects.filter(journal=self.journal).update(
            content=self.formatted_information
        )

        data = {
            "journalId": self.journal.pk,
        }

        response = self.query(
            """
            query GetJournalInformation($journalId: ID !) {
                journalInformation(journalId: $journalId) {
                    id
                    content
                    heading {
                        name
                    }
                    journal {
                        id
                    }
                }
            }
            """,
            operation_name="GetJournalInformation",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertEqual(len(content["journalInformation"]), self.n_info_heading)
        self.assertEqual(
            content["journalInformation"][0]["heading"]["name"],
            self.information_headings[0].name,
        )
        self.assertEqual(
            content["journalInformation"][1]["content"],
            json.dumps(self.formatted_information),
        )
        self.assertEqual(
            content["journalInformation"][2]["journal"]["id"], str(self.journal.pk)
        )

    def test_get_a_journal_subject_areas(self):
        n_subject_areas = 10

        mixer.cycle(n_subject_areas).blend(JournalSubjectArea, journal=self.journal)

        subject_areas = JournalSubjectArea.objects.all()

        data = {
            "journalId": self.journal.pk,
        }

        response = self.query(
            """
            query GetJournalSubjectAreas($journalId: ID !) {
                subjectAreas(journalId: $journalId) {
                    id
                    name
                    journal {
                        id
                    }
                }
            }
            """,
            operation_name="GetJournalSubjectAreas",
            variables=data,
            headers=self.editor_headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]

        self.assertEqual(len(content["subjectAreas"]), n_subject_areas)
        self.assertEqual(
            content["subjectAreas"][2]["journal"]["id"], str(self.journal.pk)
        )
        self.assertEqual(content["subjectAreas"][2]["name"], subject_areas[2].name)
        self.assertEqual(content["subjectAreas"][3]["name"], subject_areas[3].name)
        self.assertEqual(content["subjectAreas"][4]["name"], subject_areas[4].name)
        self.assertEqual(content["subjectAreas"][5]["name"], subject_areas[5].name)
