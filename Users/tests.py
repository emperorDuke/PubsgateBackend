import json

from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from graphql_relay import to_global_id
from graphene.utils.str_converters import to_snake_case

from Users.nodes import UserNode


class UsersTests(GraphQLTestCase):

    GRAPHQL_URL = "http://localhost/graphql"

    @classmethod
    def setUpTestData(cls):
        cls.userInfo = {
            "firstName": "duke",
            "lastName": "effiom",
            "email": "effiomduke@gmail.com",
            "password": "finestduke12",
            "country": "nigeria",
            "state": "lagos",
        }

    def test_create_user(self):
        response = self.query(
            """
            mutation CreateAuthorAndLogin($input: UserCreateMutationInput!) {
                createUser(input: $input) {
                    user {
                        firstName
                        lastName
                        email
                        country
                        state
                    }
                    accessToken
                    refreshToken
                }
            }
            """,
            operation_name="CreateAuthorAndLogin",
            variables={"input": self.userInfo},
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]["user"]

        self.assertEqual(content["firstName"], self.userInfo["firstName"])
        self.assertEqual(content["lastName"], self.userInfo["lastName"])
        self.assertEqual(content["email"], self.userInfo["email"])
        self.assertEqual(content["country"], self.userInfo["country"])
        self.assertEqual(content["state"], self.userInfo["state"])

    def test_update_user(self):
        user = get_user_model().objects.create_user(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        update_info = {"firstName": "John", "lastName": "Doe"}

        token = get_token(user)

        response = self.query(
            """
            mutation UpdateAuthorDetails($input: UserUpdateMutationInput!) {
                updateUser(input: $input) {
                    user {
                        firstName
                        lastName
                        email
                        country
                        state
                    }
                }
            }
            """,
            operation_name="UpdateAuthorDetails",
            variables={"input": update_info},
            headers={"HTTP_AUTHORIZATION": f"Bearer {token}"},
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["updateUser"]["user"]

        self.assertEqual(update_info["firstName"], content["firstName"])
        self.assertEqual(update_info["lastName"], content["lastName"])

    def test_retrieve_users(self):
        user = get_user_model().objects.create_superuser(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"}

        response = self.query(
            """
            query GetAllUsers {
                users {
                    edges {
                        node {
                            firstName
                            lastName
                            email
                            country
                            state
                        }
                    }
                }
            }
            """,
            operation_name="GetAllUsers",
            headers=headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertEqual(len(content["data"]["users"]["edges"]), 1)

    def test_retrieve_a_user(self):
        user = get_user_model().objects.create_superuser(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"}

        response = self.query(
            """
            query GetUser($id: ID!) {
                user(id: $id) {
                    firstName
                    lastName
                    email
                    country
                    state
                }
            }
            """,
            operation_name="GetUser",
            variables={"id": to_global_id(UserNode, user.pk)},
            headers=headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["user"]

        self.assertEqual(content["firstName"], self.userInfo["firstName"])
        self.assertEqual(content["lastName"], self.userInfo["lastName"])
        self.assertEqual(content["email"], self.userInfo["email"])
        self.assertEqual(content["country"], self.userInfo["country"])
        self.assertEqual(content["state"], self.userInfo["state"])

    def test_unauthorized_user_to_retrieve_users(self):
        user = get_user_model().objects.create_user(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"}

        response = self.query(
            """
            query GetAllUsers {
                users {
                    edges {
                        node {
                            firstName
                            lastName
                            email
                            country
                            state
                        }
                    }
                }
            }
            """,
            operation_name="GetAllUsers",
            headers=headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_unauthorized_user_to_retrieve_a_user(self):
        user = get_user_model().objects.create_user(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"}

        response = self.query(
            """
            query GetUser($id: ID!) {
                user(id: $id) {
                    firstName
                    lastName
                    email
                    country
                    state
                }
            }
            """,
            operation_name="GetUser",
            variables={"id": to_global_id(UserNode._meta.name, user.pk)},
            headers=headers,
        )

        self.assertResponseHasErrors(response)

        content = json.loads(response.content)

        self.assertEqual(
            content["errors"][0]["message"],
            "You do not have permission to perform this action",
        )

    def test_retrieve_the_auth_user(self):
        user = get_user_model().objects.create_user(
            **{to_snake_case(k): v for k, v in self.userInfo.items()}
        )

        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"}

        response = self.query(
            """
            query GetAuthUser {
                loggedInUser {
                    firstName
                    lastName
                    email
                    country
                    state
                }
            }
            """,
            operation_name="GetAuthUser",
            headers=headers,
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["loggedInUser"]

        self.assertEqual(content["firstName"], self.userInfo["firstName"])
        self.assertEqual(content["lastName"], self.userInfo["lastName"])
        self.assertEqual(content["email"], self.userInfo["email"])
        self.assertEqual(content["country"], self.userInfo["country"])
        self.assertEqual(content["state"], self.userInfo["state"])
