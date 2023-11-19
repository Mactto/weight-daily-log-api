import uuid
from pydantic import BaseModel
from fastapi import Depends
from app.ctx import AppCtx
from app.utils import fastapi as fastapi_utils
from app.utils import auth as auth_utils
from sqlalchemy.sql import expression as sa_exp
from app.models import orm as m

router = fastapi_utils.CustomAPIRouter(
    prefix="/exercise/category", tags=["exercise_category"]
)


class ExerciseLogGetAndListResponse(BaseModel):
    id: uuid.UUID
    name: str


@router.api_wrapper("GET", "/:id", error_codes=[])
async def exercise_category_get(
    id: uuid.UUID,
) -> ExerciseLogGetAndListResponse:
    exercise_category = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.ExerciseCategory).where(m.ExerciseCategory.id == id)
        )
    ).scalar_one_or_none()

    if exercise_category is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    return ExerciseLogGetAndListResponse(
        id=exercise_category.id, name=exercise_category.name
    )


@router.api_wrapper("GET", "", error_codes=[])
async def exercise_category_list() -> list[ExerciseLogGetAndListResponse]:
    exercise_category_query = sa_exp.select(m.ExerciseCategory)

    exercise_category_query = exercise_category_query.order_by(
        m.ExerciseCategory.created.desc()
    )

    exercise_category_list = (
        (await AppCtx.current.db.session.execute(exercise_category_query))
        .scalars()
        .all()
    )

    return [
        ExerciseLogGetAndListResponse(
            id=exercise_category.id, name=exercise_category.name
        )
        for exercise_category in exercise_category_list
    ]


class ExerciseLogPostRequest(BaseModel):
    name: str


class ExerciseLogPostResponse(BaseModel):
    id: uuid.UUID


@router.api_wrapper(
    "POST",
    "",
    error_codes=[],
)
async def exercise_category_post(
    q: ExerciseLogPostRequest,
) -> ExerciseLogPostResponse:
    exercise_category = m.ExerciseCategory(
        name=q.name,
    )

    AppCtx.current.db.session.add(exercise_category)

    await AppCtx.current.db.session.commit()

    return ExerciseLogPostResponse(id=exercise_category.id)


class ExerciseLogPatchRequest(BaseModel):
    name: str | None


class ExerciseLogPatchResponse(BaseModel):
    id: uuid.UUID
    name: str


@router.api_wrapper(
    "PATCH",
    "/:id",
    error_codes=[],
)
async def exercise_category_patch(
    id: uuid.UUID,
    q: ExerciseLogPatchRequest,
) -> ExerciseLogPatchResponse:
    exercise_category = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.ExerciseCategory).where(m.ExerciseCategory.id == id)
        )
    ).scalar_one_or_none()

    if exercise_category is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    exercise_category.name = q.name

    AppCtx.current.db.session.add(exercise_category)

    await AppCtx.current.db.session.commit()

    return ExerciseLogPatchResponse(
        id=exercise_category.id, name=exercise_category.name
    )


@router.api_wrapper(
    "DELETE",
    "/:id",
    error_codes=[],
)
async def exercise_category_delete(
    id: uuid.UUID,
) -> fastapi_utils.DefaultResponse:
    exercise_category = (
        await AppCtx.current.db.session.execute(
            sa_exp.select(m.ExerciseCategory).where(m.ExerciseCategory.id == id)
        )
    ).scalar_one_or_none()

    if exercise_category is None:
        raise fastapi_utils.LogicError(fastapi_utils.LogicErrorCodeEnum.ModelNotFound)

    await AppCtx.current.db.session.delete(exercise_category)

    await AppCtx.current.db.session.commit()

    return fastapi_utils.DefaultResponse()
