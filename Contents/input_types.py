import graphene


class KeyWordTagsInputType(graphene.InputObjectType):
    tag = graphene.String()
