from flask import current_app, request
from werkzeug.exceptions import Unauthorized
from jwt import encode, decode
from datetime import timedelta, datetime


def create_access_token(identity, expiration: timedelta):
    return encode(
        {"sub": identity, "exp": (datetime.now() + expiration).timestamp()},
        current_app.secret_key,
        "HS256",
    )


def get_token_from_headers():
    if not request.authorization:
        return None

    if request.authorization.type != "bearer" or not request.authorization.token:
        return None

    return request.authorization.token


def get_identity():
    token = get_token_from_headers()
    if not token:
        raise Unauthorized("Invalid/missing token")

    payload = validate(token)
    return payload["sub"]


def validate(token):
    return decode(token, current_app.secret_key, ["HS256"])
