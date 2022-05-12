from datetime import datetime
from graphql_jwt.settings import jwt_settings

# JWT payload for Hasura


def jwt_payload(user, context=None):
    jwt_datetime = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
    jwt_expires = int(jwt_datetime.timestamp())

    payload = {}

    payload["email"] = str(user.email)
    payload["first_name"] = user.first_name
    payload["last_name"] = user.last_name
    payload["exp"] = jwt_expires
    return payload
