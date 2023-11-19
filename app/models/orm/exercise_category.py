import uuid
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import Index
from sqlalchemy.sql import sqltypes
from app.models.orm.daily_log import DailyLog

from .base_ import Base


class ExerciseCategory(Base):
    __tablename__ = "exercise_category"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.uuid_generate_v4(),
    )

    name: Mapped[str] = mapped_column(sqltypes.String, nullable=False)
