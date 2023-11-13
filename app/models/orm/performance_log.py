import uuid
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, Index
from sqlalchemy.sql import sqltypes
from app.models.orm.exercise_log import ExerciseLog

from .base_ import Base


class PerformanceLog(Base):
    __tablename__ = "performance_log"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.uuid_generate_v4(),
    )

    performance_count: Mapped[int] = mapped_column(
        sqltypes.Integer,
        nullable=False,
        default=0,
    )

    exercise_log_id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        ForeignKey("exercise_log.id"),
        nullable=False,
    )
    exercise_log: Mapped[ExerciseLog] = relationship("ExerciseLog", uselist=False)
