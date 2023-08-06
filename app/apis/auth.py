from __future__ import annotations

import logging

import sqlalchemy.exc
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.sql import expression as sa_exp

from app.constants import USERNAME_REGEX
from app.ctx import AppCtx
from app.models import orm as m
from app.utils import auth as auth_utils
from app.utils import fastapi as fastapi_utils

logger = logging.getLogger(__name__)

router = fastapi_utils.CustomAPIRouter(prefix="/auth", tags=["auth"])


class SignupPostRequest(BaseModel):
    username: str = Field(description="Account's username", regex=USERNAME_REGEX)
    password: SecretStr = Field(description="Account's password", min_length=8)

    fullname: str = Field(description="Account's fullname")


class SignupPostResponse(BaseModel):
    pass


@router.api_wrapper(
    "POST",
    "/signup",
    error_codes=[
        fastapi_utils.LogicErrorCodeEnum.DuplicatedUsername,
        fastapi_utils.LogicErrorCodeEnum.RaceCondition,
    ],
)
async def _(q: SignupPostRequest) -> SignupPostResponse:
    is_username_conflict = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(sa_exp.exists().where(m.Account.username == q.username))
        )
    ).scalar()

    if is_username_conflict:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.DuplicatedUsername
        )

    account = m.Account(
        username=q.username,
        password=(
            await auth_utils.generate_hashed_password(
                q.password.get_secret_value(),
            )
        ),
        fullname=q.fullname,
    )

    AppCtx.current.db.session.add(account)

    try:
        await AppCtx.current.db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.RaceCondition
        )

    return SignupPostResponse()


class LoginPostResponse(BaseModel):
    access_token: str = Field(description="Access token for the session")


@router.api_wrapper(
    "POST",
    "/login",
    error_codes=[
        fastapi_utils.LogicErrorCodeEnum.DuplicatedUsername,
        fastapi_utils.LogicErrorCodeEnum.WrongPassword,
    ],
)
async def _(
    request: Request,
    q: OAuth2PasswordRequestForm = Depends(),
) -> LoginPostResponse:
    account: m.Account | None = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.Account).where(m.Account.username == q.username)
        )
    ).scalar_one_or_none()

    if account is None:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.ModelNotFound
        )

    if not (
        await auth_utils.validate_hashed_password(
            q.password,
            account.password,
        )
    ):
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.WrongPassword
        )

    account_login = m.AccountLogin(
        ipaddr=fastapi_utils.get_client_ip(request),
        account_id=account.id,
    )

    AppCtx.current.db.session.add(account_login)

    await AppCtx.current.db.session.commit()

    return LoginPostResponse(
        access_token=auth_utils.create_access_token(
            account.username,
            account.id,
            account_login.id,
        ),
    )
