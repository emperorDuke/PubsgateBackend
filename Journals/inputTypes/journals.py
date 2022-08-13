import graphene


class Action(graphene.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class JournalInformationInput(graphene.InputObjectType):
    heading_id = graphene.ID(required=True)
    content = graphene.JSONString(required=True)


class JournalSubjectAreaInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String(required=True)
    action = Action(required=True)
