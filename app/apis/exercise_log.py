import uuid
from pydantic import BaseModel
from fastapi import Depends
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils

router = fastapi_utils.CustomAPIRouter(prefix="/exercise/log", tags=["exercise_log"])


class ExerciseLogGetRequest(BaseModel):
    ...


class ExerciseLogGetAndListResponse(BaseModel):
    ...


@router.api_wrapper(
    "GET",
    "/:id",
    error_codes=[]
)
async def exercise_log_get(
    id: uuid.UUID,
    q: ExerciseLogGetRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> ExerciseLogGetAndListResponse:
    ...


class ExeriseLogListRequest(BaseModel):
    ...

@router.api_wrapper(
    "GET",
    "",
    error_codes=[]
)
async def exercise_log_list(
    q: ExeriseLogListRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> list[ExerciseLogGetAndListResponse]:
    ...


class ExerciseLogPostRequest(BaseModel):
    ...


class ExerciseLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def exercise_log_post(
    q: ExerciseLogPostRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> ExerciseLogPostResponse:
    ...


class ExerciseLogPatchRequest(BaseModel):
    ...


class ExerciseLogPatchResponse(BaseModel):
    ...


@router.api_wrapper(
    "PATCH",
    "/:id",
    error_codes=[],
)
async def exercise_log_patch(
    id: uuid.UUID,
    q: ExerciseLogPatchRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> ExerciseLogPatchResponse:
    ...


@router.api_wrapper(
    "DELETE",
    "/:id",
    error_codes=[],
)
async def exercise_log_delete(
    id: uuid.UUID,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> fastapi_utils.DefaultResponse:
    return fastapi_utils.DefaultResponse()
