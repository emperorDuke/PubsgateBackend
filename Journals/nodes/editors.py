from graphene_django import DjangoObjectType

from ..models import Editor as EditorModel


class Editor(DjangoObjectType):
    class Meta:
        model = EditorModel
        fields = [
            "id",
            "affiliation",
            "phone_number",
            "started_at",
            "user",
            "specialisation",
        ]
