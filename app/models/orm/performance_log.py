import uuid
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, Index
from sqlalchemy.sql import sqltypes
from app.models.orm.daily_log import DailyLog
from app.models.orm.exercise_category import ExerciseCategory

from .base_ import Base


class PerformanceLog(Base):
    __tablename__ = "performance_log"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.uuid_generate_v4(),
    )

    weight: Mapped[int] = mapped_column(
        sqltypes.Integer,
        nullable=False,
        default=0,
    )

    count: Mapped[int] = mapped_column(
        sqltypes.Integer,
        nullable=False,
        default=0,
    )

    exercise_category_id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        ForeignKey("exercise_category.id"),
        nullable=False,
    )
    exercise_category: Mapped[ExerciseCategory] = relationship(
        "ExerciseCategory", uselist=False
    )

    daily_log_id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        ForeignKey("daily_log.id"),
        nullable=False,
    )
    daily_log: Mapped[DailyLog] = relationship("DailyLog", uselist=False)
