import os
from typing import Dict, List

import requests
from fastapi import Depends, HTTPException
from starlette.config import Config
from starlette.status import HTTP_403_FORBIDDEN

from app.api.auth.jwt_bearer import JWKS, JWTAuthorizationCredentials, JWTBearer

JWK = Dict[str, str]

config = Config(".env")
COGNITO_REGION = config("COGNITO_REGION", cast=str)
COGNITO_POOL_ID = config("COGNITO_POOL_ID", cast=str)

jwks = JWKS.parse_obj(
    requests.get(
        f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
        f"{COGNITO_POOL_ID}/.well-known/jwks.json"
    ).json()
)

auth = JWTBearer(jwks)

async def get_current_user(
    credentials: JWTAuthorizationCredentials = Depends(auth)
) -> str:
    try:
        return credentials.claims["username"]
    except KeyError:
        HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")