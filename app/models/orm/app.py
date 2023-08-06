from __future__ import annotations

import uuid

from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, Index
from sqlalchemy.sql import sqltypes

from .base_ import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.gen_random_uuid(),
    )

    username: Mapped[str] = mapped_column(sqltypes.String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(sqltypes.String, nullable=False)

    fullname: Mapped[str] = mapped_column(sqltypes.String(128), nullable=False)
    introduction: Mapped[str] = mapped_column(sqltypes.Text, nullable=False, default="")


class AccountLogin(Base):
    __tablename__ = "account_login"

    id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa_func.gen_random_uuid(),
    )

    ipaddr: Mapped[str] = mapped_column(sqltypes.String, nullable=False)

    account_id: Mapped[uuid.UUID] = mapped_column(
        pg_dialect.UUID(as_uuid=True),
        ForeignKey("account.id"),
        nullable=False,
    )
    account: Mapped[Account] = relationship("Account", uselist=False)


Index(None, AccountLogin.account_id, AccountLogin.created)
