import uuid
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, Index
from sqlalchemy.sql import sqltypes
from app.models.orm.daily_log import DailyLog

from .base_ import Base


class ExerciseLog(Base):
    __tablename__ = "exercise_log"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.uuid_generate_v4(),
    )

    exercise_type: Mapped[str] = mapped_column(sqltypes.String, nullable=False)

    daily_log_id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        ForeignKey("daily_log.id"),
        nullable=False,
    )
    daily_log: Mapped[DailyLog] = relationship("DailyLog", uselist=False)


Index(ExerciseLog.daily_log_id, ExerciseLog.exercise_type)
