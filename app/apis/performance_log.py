import uuid
from pydantic import BaseModel
from fastapi import Depends
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils

router = fastapi_utils.CustomAPIRouter(prefix="/performance/log", tags=["performance_log"])


class PerformanceLogGetRequest(BaseModel):
    ...


class PerformanceLogGetAndListResponse(BaseModel):
    ...


@router.api_wrapper(
    "GET",
    "/:id",
    error_codes=[]
)
async def performance_log_get(
    id: uuid.UUID,
    q: PerformanceLogGetRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> PerformanceLogGetAndListResponse:
    ...


class PerformanceLogListRequest(BaseModel):
    ...

@router.api_wrapper(
    "GET",
    "",
    error_codes=[]
)
async def performance_log_list(
    q: PerformanceLogListRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> list[PerformanceLogGetAndListResponse]:
    ...


class PerformanceLogPostRequest(BaseModel):
    ...


class PerformanceLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def performance_log_post(
    q: PerformanceLogPostRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> PerformanceLogPostResponse:
    ...


class PerformanceLogPatchRequest(BaseModel):
    ...


class PerformanceLogPatchResponse(BaseModel):
    ...


@router.api_wrapper(
    "PATCH",
    "/:id",
    error_codes=[],
)
async def performance_log_patch(
    id: uuid.UUID,
    q: PerformanceLogPatchRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> PerformanceLogPatchResponse:
    ...


@router.api_wrapper(
    "DELETE",
    "/:id",
    error_codes=[],
)
async def performance_log_delete(
    id: uuid.UUID,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> fastapi_utils.DefaultResponse:
    return fastapi_utils.DefaultResponse()
