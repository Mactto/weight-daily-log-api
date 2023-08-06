from __future__ import annotations

import asyncio
import binascii
import hashlib
import os
import time
import uuid
from typing import NamedTuple

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.ctx import AppCtx

from . import fastapi as fastapi_utils

_PBKDF2_HASH_NAME = "SHA256"
_PBKDF2_ITERATIONS = 100_000

_TOKEN_TTL = 7 * 24 * 60 * 60  # 7 days


class AuthInfo(NamedTuple):
    username: str
    account_id: int
    account_login_id: int

    expire_at: int
    issued_at: int
    issuer: str


auth_scheme = HTTPBearer(auto_error=False)


async def generate_hashed_password(password: str) -> str:
    def _inner() -> str:
        pbkdf2_salt = os.urandom(16)
        pw_hash = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,
            password.encode(),
            pbkdf2_salt,
            _PBKDF2_ITERATIONS,
        )

        return "%s:%s" % (
            binascii.hexlify(pbkdf2_salt).decode(),
            binascii.hexlify(pw_hash).decode(),
        )

    return await asyncio.get_running_loop().run_in_executor(None, _inner)


async def validate_hashed_password(password: str, hashed_password: str) -> bool:
    def _inner() -> bool:
        pbkdf2_salt_hex, pw_hash_hex = hashed_password.split(":")

        pw_challenge = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,
            password.encode(),
            binascii.unhexlify(pbkdf2_salt_hex),
            _PBKDF2_ITERATIONS,
        )

        return pw_challenge == binascii.unhexlify(pw_hash_hex)

    return await asyncio.get_running_loop().run_in_executor(None, _inner)


def create_access_token(
    username: str,
    account_id: uuid.UUID,
    account_login_id: uuid.UUID,
) -> str:
    current = time.time()
    return jwt.encode(
        payload={
            "username": username,
            "account_id": str(account_id),
            "account_login_id": str(account_login_id),
            "exp": current + _TOKEN_TTL,
            "iat": current,
            "iss": "elice-backend-api-default-python",
        },
        key=AppCtx.current.settings.SECRET_KEY.get_secret_value(),
        algorithm="HS256",
    )


def resolve_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
) -> AuthInfo:
    if credentials is None:
        raise fastapi_utils.UnauthorizedError()
    try:
        token_info = jwt.decode(
            credentials.credentials,
            key=AppCtx.current.settings.SECRET_KEY.get_secret_value(),
            algorithms=["HS256"],
        )
    except jwt.InvalidIssuerError:
        raise fastapi_utils.AuthError(fastapi_utils.AuthErrorCodeEnum.InvalidIssuer)
    except jwt.InvalidAlgorithmError:
        raise fastapi_utils.AuthError(fastapi_utils.AuthErrorCodeEnum.InvlaidAlgorithm)
    except jwt.ExpiredSignatureError:
        raise fastapi_utils.AuthError(
            fastapi_utils.AuthErrorCodeEnum.ExpiredAccessToken,
        )
    except Exception:
        raise fastapi_utils.AuthError(
            fastapi_utils.AuthErrorCodeEnum.InvalidAccessToken,
        )

    return AuthInfo(
        username=token_info["username"],
        account_id=token_info["account_id"],
        account_login_id=token_info["account_login_id"],
        expire_at=token_info["exp"],
        issued_at=token_info["iat"],
        issuer=token_info["iss"],
    )
