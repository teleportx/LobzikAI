from typing import Annotated

from fastapi import Header, HTTPException, Depends

from libs.utils.jwt_token import verify_token


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
