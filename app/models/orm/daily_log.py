import datetime
import uuid
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes

from .base_ import Base


class DailyLog(Base):
    __tablename__ = "daily_log"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.uuid_generate_v4(),
    )

    date: Mapped[datetime.date] = mapped_column(
        sqltypes.Date, nullable=False, index=True
    )
