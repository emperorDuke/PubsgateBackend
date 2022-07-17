import json
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer

from Cores.models import SubjectDiscipline


class CoreTestcase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    def test_get_all_disciplines(self):
        disciplines = mixer.cycle(5).blend(SubjectDiscipline)

        response = self.query(
            """
            query GetSubjectDisciplines {
                subjectDisciplines {
                    id
                    name
                }
            }
            """,
            operation_name="GetSubjectDisciplines",
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["subjectDisciplines"]

        self.assertEqual(len(content), len(disciplines))
        self.assertTrue(content[0]["name"] in [d.name for d in disciplines])
