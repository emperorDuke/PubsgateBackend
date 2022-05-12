import graphene
import graphql_jwt

import SubmissionPortal.schema as SubmissionPortalSchema
import Users.schema as UserSchema
import PeerReviewPortal.schema as PeerReviewSchema
import Journals.schema as EditorsSchema


class Mutation(
    EditorsSchema.Mutation,
    PeerReviewSchema.Mutation,
    SubmissionPortalSchema.Mutation,
    UserSchema.Mutation,
    graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Query(
    EditorsSchema.Query,
    PeerReviewSchema.Query,
    SubmissionPortalSchema.Query,
    UserSchema.Query,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
