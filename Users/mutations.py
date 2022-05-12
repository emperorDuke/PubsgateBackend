import graphene

from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import create_refresh_token, get_token

from Users.models import User

from .nodes import UserNode


class UserCreateMutation(graphene.relay.ClientIDMutation):
    user = graphene.Field(UserNode)
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Input:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        country = graphene.String(required=True)
        state = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info: dict, input: dict):
        email = input.pop('email')
        password = input.pop('password')

        user: User = get_user_model().objects.create_user(
            email=email,
            password=password,
            **input
        )

        token = get_token(user)
        refresh_token = create_refresh_token(user)

        return UserCreateMutation(
            user=user,
            access_token=token,
            refresh_token=refresh_token
        )


class UserUpdateMutation(graphene.relay.ClientIDMutation):
    user = graphene.Field(UserNode)

    class Input:
        email = graphene.String(required=False)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        password = graphene.String(required=False)
        email = graphene.String(required=False)
        country = graphene.String(required=False)
        state = graphene.String(required=False)

    @classmethod
    @login_required
    def mutate(cls, root, info: dict, input: dict):
        user: User = info.context.user

        for k, v in input.items():
            if (k == 'password') and (v is not None):
                user.set_password(input.password)
            else:
                setattr(user, k, v)

        user.full_clean()
        user.save()

        return UserUpdateMutation(user=user)
