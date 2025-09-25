from typing import Annotated

import jwt
from fastapi import Header, HTTPException, Depends

import config


import uuid
from datetime import datetime, timezone


def generate_token_payload(typ: str, payload_add: dict, expiration_time: int) -> dict:
    """
    Generate JWT token payload

    :param typ: Type of token.
    :param payload_add: Additional payload to token
    :param expiration_time: Time to expire token in seconds.

    :returns: dict of token payload
    """

    token_uuid = uuid.uuid4()
    iat = int(datetime.now(timezone.utc).timestamp())

    payload = {
        "jti": str(token_uuid),
        "typ": typ,
        "iat": iat,
        "exp": iat + expiration_time,
    }
    payload.update(**payload_add)

    return payload


def generate_token(typ: str, payload: dict, expiration_time: int) -> tuple[uuid.UUID, str]:
    """
    Generate JWT token.

    :param typ: Type of token.
    :param payload: Additional payload to token
    :param expiration_time: Time to expire token in seconds.

    :returns: Tuple of JTI and token value
    """

    result_payload = generate_token_payload(typ, payload, expiration_time)
    token = jwt.encode(result_payload, config.jwt_secret)

    return result_payload['jti'], token


def verify_token(token: str) -> dict | None:
    """
    Validating JWT token.

    :param token: JWT token.

    :returns: None if token not valid or expire. Token payload if token valid.
    """
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=["HS256"])
        return payload

    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return None


class AuthRawDepend:
    def __init__(self, typ: str | None, *, raise_exception: bool = True):
        self.raise_exception = raise_exception
        self.typ = typ

    def parse_token(self, authorization: str) -> dict | None:
        token_parts = authorization.split()
        if len(token_parts) < 2:
            raise ValueError

        token_type = token_parts[0]
        token = ' '.join(token_parts[1:])

        if token_type != 'Bearer':
            raise ValueError

        payload = verify_token(token)
        if payload is None:
            raise ValueError

        return payload

    async def __call__(self, authorization: Annotated[str, Header()]) -> dict | None:
        try:
            return self.parse_token(authorization)

        except ValueError:
            if self.raise_exception:
                raise HTTPException(401, 'Invalid authorization token')
            return None


def AuthorizeDep(typ: str | None, *, raise_exception: bool = True):
    annotated_type = dict
    if not raise_exception:
        annotated_type = dict | None

    return Annotated[annotated_type, Depends(AuthRawDepend(typ=typ, raise_exception=raise_exception))]
