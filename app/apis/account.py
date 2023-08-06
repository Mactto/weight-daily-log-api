from __future__ import annotations

import datetime
import uuid
from typing import Literal

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.sql import expression as sa_exp

from app.constants import USERNAME_REGEX
from app.ctx import AppCtx
from app.models import orm as m
from app.utils import auth as auth_utils
from app.utils import fastapi as fastapi_utils

router = fastapi_utils.CustomAPIRouter(prefix="/account", tags=["account"])


class GetRequest(BaseModel):
    id: uuid.UUID | None = Field(
        description="Account's id. If omiited, assume the current account's id.",
    )


class ByAccountnameGetRequest(BaseModel):
    username: str | None = Field(
        description=(
            "Account's username. If omiited, assume the current account's username."
        ),
        regex=USERNAME_REGEX,
    )


class GetResponse(BaseModel):
    id: uuid.UUID
    username: str
    fullname: str
    introduction: str
    created: datetime.datetime

    class Config:
        orm_mode = True


@router.api_wrapper(
    "GET",
    "",
    error_codes=[fastapi_utils.LogicErrorCodeEnum.ModelNotFound],
)
async def _(
    q: GetRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> GetResponse:
    return await _get_routing(q.id, None, auth_info)


@router.api_wrapper(
    "GET",
    "/by_username",
    error_codes=[fastapi_utils.LogicErrorCodeEnum.ModelNotFound],
)
async def _(
    q: ByAccountnameGetRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> GetResponse:
    return await _get_routing(None, q.username, auth_info)


async def _get_routing(
    account_id: uuid.UUID | None,
    account_username: str | None,
    auth_info: auth_utils.AuthInfo,
) -> GetResponse:
    if account_id is not None:
        account_ident_filter = m.Account.id == account_id
    elif account_username is not None:
        account_ident_filter = m.Account.username == account_username
    else:
        account_ident_filter = m.Account.id == auth_info.account_id

    account: m.Account | None = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.Account).where(account_ident_filter)
        )
    ).scalar_one_or_none()

    if account is None:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.ModelNotFound,
            detail={"Account": ["id"]},
        )

    return GetResponse.from_orm(account)


class PatchRequest(BaseModel):
    fullname: str | None = Field(default=None, max_length=128)
    introduction: str | None = Field(default=None)


class PatchResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "PATCH",
    "",
    error_codes=[fastapi_utils.LogicErrorCodeEnum.ModelNotFound],
)
async def _(
    q: PatchRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> PatchResponse:
    obj = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.Account).where(m.Account.id == auth_info.account_id)
        )
    ).scalar_one_or_none()

    if obj is None:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.ModelNotFound,
            detail={"Account": ["id"]},
        )

    for field in q.__fields_set__:
        setattr(obj, field, getattr(q, field))

    AppCtx.current.db.session.add(obj)

    await AppCtx.current.db.session.commit()

    return PatchResponse(id=obj.id)


class LoginGetAndListResponse(BaseModel):
    id: uuid.UUID
    ipaddr: str
    created: datetime.datetime


@router.api_wrapper(
    "GET",
    "/login/{account_login_id}",
    error_codes=[fastapi_utils.LogicErrorCodeEnum.ModelNotFound],
)
async def _(
    account_login_id: uuid.UUID,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> LoginGetAndListResponse:
    account_login = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.AccountLogin).where(m.AccountLogin.id == account_login_id)
        )
    ).scalar_one_or_none()

    if account_login is None:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.ModelNotFound,
            detail={"AccountLogin": ["id"]},
        )

    return LoginGetAndListResponse(
        id=account_login.id,
        ipaddr=account_login.ipaddr,
        created=account_login.created,
    )


class LoginListRequest(BaseModel):
    sort_by: Literal["created", "-created"] = Field(
        default="-created",
        description="Sort by a specific field",
    )
    skip: int = Field(
        description="The offset of returned objects",
        ge=0,
        le=1_000,
    )
    count: int = Field(
        description="The maximum number of returned objects",
        ge=1,
        le=100,
    )


@router.api_wrapper(
    "GET",
    "/login",
)
async def _(
    q: LoginListRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> list[LoginGetAndListResponse]:
    order_by_exp = {
        "created": m.AccountLogin.created.asc(),
        "-created": m.AccountLogin.created.desc(),
    }[q.sort_by]

    account_logins = (
        (
            await AppCtx.current.db.session.execute(
                sa_exp.select(m.AccountLogin)
                .where(m.AccountLogin.account_id == auth_info.account_id)
                .order_by(order_by_exp)
                .slice(q.skip, q.skip + q.count)
            )
        )
        .scalars()
        .all()
    )

    return [
        LoginGetAndListResponse(
            id=account_login.id,
            ipaddr=account_login.ipaddr,
            created=account_login.created,
        )
        for account_login in account_logins
    ]
