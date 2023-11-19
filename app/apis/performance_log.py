import uuid
from pydantic import BaseModel
from fastapi import Depends
from app.ctx import AppCtx
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils
from sqlalchemy.sql import expression as sa_exp
from app.models import orm as m

router = fastapi_utils.CustomAPIRouter(
    prefix="/performance/log", tags=["performance_log"]
)


class PerformanceLogGetAndListResponse(BaseModel):
    id: uuid.UUID
    count: int
    weight: int


@router.api_wrapper("GET", "/:id", error_codes=[])
async def performance_log_get(
    id: uuid.UUID,
) -> PerformanceLogGetAndListResponse:
    performance_log = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.PerformanceLog).where(m.PerformanceLog.id == id)
        )
    ).scalar_one_or_none()

    if performance_log is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    return PerformanceLogGetAndListResponse(
        id=performance_log.id,
        count=performance_log.count,
        weight=performance_log.weight,
    )


@router.api_wrapper("GET", "", error_codes=[])
async def performance_log_list() -> list[PerformanceLogGetAndListResponse]:
    performance_log_query = sa_exp.select(m.PerformanceLog)

    performance_log_query = performance_log_query.order_by(
        m.PerformanceLog.created.asc()
    )

    performance_log_list = (
        (await AppCtx.current.db.session.execute(performance_log_query)).scalars().all()
    )

    return [
        PerformanceLogGetAndListResponse(
            id=performance_log.id,
            count=performance_log.count,
            weight=performance_log.weight,
        )
        for performance_log in performance_log_list
    ]


class PerformanceLogPostRequest(BaseModel):
    count: int
    weight: int
    exercise_category_id: uuid.UUID
    daily_log_id: uuid.UUID


class PerformanceLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def performance_log_post(
    q: PerformanceLogPostRequest,
) -> PerformanceLogPostResponse:
    exercise_category = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.ExerciseCategory).where(
                m.ExerciseCategory.id == q.exercise_category_id
            )
        )
    ).scalar_one_or_none()

    if exercise_category is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    daily_log = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.DailyLog).where(m.DailyLog.id == q.daily_log_id)
        )
    ).scalar_one_or_none()

    if daily_log is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    performance_log = m.PerformanceLog(
        count=q.count,
        weight=q.weight,
        exercise_category=exercise_category,
        daily_log=daily_log,
    )

    AppCtx.current.db.session.add(performance_log)

    await AppCtx.current.db.session.commit()

    return PerformanceLogPostResponse(id=performance_log.id)


class PerformanceLogPatchRequest(BaseModel):
    count: int | None
    weight: int | None


class PerformanceLogPatchResponse(BaseModel):
    id: uuid.UUID
    count: int
    weight: int


@router.api_wrapper(
    "PATCH",
    "/:id",
    error_codes=[],
)
async def performance_log_patch(
    id: uuid.UUID,
    q: PerformanceLogPatchRequest,
) -> PerformanceLogPatchResponse:
    performance_log = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.PerformanceLog).where(m.PerformanceLog.id == id)
        )
    ).scalar_one_or_none()

    if performance_log is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    for key, value in q.__dict__.items():
        if value is not None:
            setattr(performance_log, key, value)

    AppCtx.current.db.session.add(performance_log)

    await AppCtx.current.db.session.commit()

    return PerformanceLogPatchResponse(
        id=performance_log.id,
        count=performance_log.count,
        weight=performance_log.weight,
    )


@router.api_wrapper(
    "DELETE",
    "/:id",
    error_codes=[],
)
async def performance_log_delete(
    id: uuid.UUID,
) -> fastapi_utils.DefaultResponse:
    performance_log = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.PerformanceLog).where(m.PerformanceLog.id == id)
        )
    ).scalar_one_or_none()

    if performance_log is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    await AppCtx.current.db.session.delete(performance_log)

    await AppCtx.current.db.session.commit()

    return fastapi_utils.DefaultResponse()
