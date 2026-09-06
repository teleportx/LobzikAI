from typing import Annotated

import jwt



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


def generate_token(typ: str, payload: dict, expiration_time: int, jwt_secret: str) -> tuple[uuid.UUID, str]:
    """
    Generate JWT token.

    :param typ: Type of token.
    :param payload: Additional payload to token
    :param expiration_time: Time to expire token in seconds.
    :param jwt_secret: JWT secret.

    :returns: Tuple of JTI and token value
    """

    result_payload = generate_token_payload(typ, payload, expiration_time)
    token = jwt.encode(result_payload, jwt_secret)

    return result_payload['jti'], token


def verify_token(token: str, jwt_secret: str) -> dict | None:
    """
    Validating JWT token.

    :param token: JWT token.
    :param jwt_secret: JWT secret.

    :returns: None if token not valid or expire. Token payload if token valid.
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload

    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return None
