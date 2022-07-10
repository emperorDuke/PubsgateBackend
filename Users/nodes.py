import graphene

from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class User(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "country",
            "state",
            "is_active",
            "date_joined",
        )
        interfaces = (graphene.relay.Node,)
