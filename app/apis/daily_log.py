import datetime
import uuid
from pydantic import BaseModel
from fastapi import Depends
import sqlalchemy.exc
from app.ctx import AppCtx
from sqlalchemy.sql import expression as sa_exp
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils
from app.models import orm as m

router = fastapi_utils.CustomAPIRouter(prefix="/daily/log", tags=["daily_log"])


class DailyGetAndListResponse(BaseModel):
    id: uuid.UUID
    date: datetime.date


@router.api_wrapper(
    "GET",
    "",
    error_codes=[],
)
async def daily_log_list() -> list[DailyGetAndListResponse]:
    daily_log_list = (
        (await AppCtx.current.db.session.execute(sa_exp.select(m.DailyLog)))
        .scalars()
        .all()
    )

    return [
        DailyGetAndListResponse(
            id=daily_log.id,
            date=daily_log.date,
        )
        for daily_log in daily_log_list
    ]


class DailyLogTodayResponse(BaseModel):
    id: uuid.UUID | None


@router.api_wrapper("GET", "/today", error_codes=[])
async def daily_log_today_get() -> DailyLogTodayResponse:
    today_date = datetime.datetime.now().date()

    today_daily_log_id = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.DailyLog.id).where(m.DailyLog.date == today_date)
        )
    ).scalar()

    return DailyLogTodayResponse(id=today_daily_log_id)


class DailyLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def daily_log_post() -> DailyLogPostResponse:
    today_date = datetime.datetime.now().date()

    is_already_logged = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(sa_exp.exists().where(m.DailyLog.date == today_date))
        )
    ).scalar()

    if is_already_logged:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.AlreadyLogged
        )

    daily_log = m.DailyLog(date=today_date)

    AppCtx.current.db.session.add(daily_log)

    try:
        await AppCtx.current.db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise fastapi_utils.LogicError(
            code=fastapi_utils.LogicErrorCodeEnum.RaceCondition
        )

    return DailyLogPostResponse(id=daily_log.id)
