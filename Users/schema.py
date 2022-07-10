import graphene

from django.contrib.auth import get_user_model
from graphene_django import DjangoConnectionField
from graphql_jwt.decorators import login_required, staff_member_required
from graphql_relay import from_global_id

from .mutations import UserCreateMutation, UserUpdateMutation
from .nodes import User as UserNode


class Mutation(graphene.ObjectType):
    create_user = UserCreateMutation.Field()
    update_user = UserUpdateMutation.Field()


class Query(graphene.ObjectType):
    users = DjangoConnectionField(UserNode)
    user = graphene.Field(UserNode, id=graphene.ID(required=True))
    logged_in_user = graphene.Field(UserNode)

    @login_required
    def resolve_logged_in_user(root, info):
        return info.context.user

    @login_required
    @staff_member_required
    def resolve_users(root, info, **kwargs):
        return get_user_model().objects.all()

    @login_required
    @staff_member_required
    def resolve_user(root, info, id):
        return get_user_model().objects.get(pk=from_global_id(id).id)
