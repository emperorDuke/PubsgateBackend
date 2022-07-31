from graphene_django import DjangoObjectType

from ..models import Editor


class Editor(DjangoObjectType):
    class Meta:
        model = Editor
        fields = [
            "id",
            "affiliation",
            "phone_number",
            "started_at",
            "user",
            "specialisation",
        ]
