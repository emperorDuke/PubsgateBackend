import graphene


class AuthorInputType(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    affiliation = graphene.String(required=True)
    rank = graphene.Int(required=True)
    is_corresponding = graphene.Boolean(required=True)


class StatementInputType(graphene.InputObjectType):
    term_id = graphene.ID(required=True)
    response = graphene.Boolean(required=True)
    statement = graphene.String()


class UpdateAuthorInput(AuthorInputType):
    action = graphene.String(required=True)
    id = graphene.ID()


class UpdateStatementInput(StatementInputType):
    id = graphene.ID(required=True)


class ManuscriptSectionInput(graphene.InputObjectType):
    section_id = graphene.ID(required=True)
    section_name = graphene.String(required=True)
    content = graphene.String(required=True)
