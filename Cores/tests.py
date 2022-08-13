import json
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer

from Cores.models import Discipline


class CoreTestcase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost/graphql"

    def test_get_all_disciplines(self):
        disciplines = mixer.cycle(5).blend(Discipline)

        response = self.query(
            """
            query GetDisciplines {
                disciplines {
                    id
                    name
                    slug
                }
            }
            """,
            operation_name="GetDisciplines",
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["disciplines"]

        self.assertEqual(len(content), len(disciplines))
        self.assertTrue(content[0]["name"] in [d.name for d in disciplines])
