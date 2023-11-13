import uuid
from pydantic import BaseModel
from fastapi import Depends
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils

router = fastapi_utils.CustomAPIRouter(prefix="/daily/log", tags=["daily_log"])


class DailyLogGetRequest(BaseModel):
    ...

class DailyGetAndListRequest(BaseModel):
    ...

@router.api_wrapper(
    "GET",
    "/:id",
    error_codes=[],
)
async def daily_log_get(
    id: uuid.UUID,
    q: DailyLogGetRequest = Depends(),
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> list[DailyGetAndListRequest]:
    return 


class DailyLogListRequest(BaseModel):
    ...

@router.api_wrapper(
    "GET",
    "",
    error_codes=[],
)
async def daily_log_list(
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> DailyGetAndListRequest:
    return


class DailyLogPostRequest(BaseModel):
    ...


class DailyLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def daily_log_post(
    q: DailyLogPostRequest,
    auth_info: auth_utils.AuthInfo = Depends(auth_utils.resolve_token),
) -> DailyLogPostResponse:
    ...
