from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import types as sa_types
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.schema import Index

if TYPE_CHECKING:
    from sqlalchemy.sql.schema import ColumnCollectionConstraint, Table


class Base(DeclarativeBase):
    __abstract__ = True

    created: Mapped[datetime.datetime] = mapped_column(
        sa_types.TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    modified: Mapped[datetime.datetime | None] = mapped_column(
        sa_types.TIMESTAMP(timezone=True),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        return (
            Index(
                None,
                cls.created,  # type:ignore
            ),
        )


def _table_guid_generator(
    constraint: ColumnCollectionConstraint,
    table: Table,
) -> str:
    str_tokens = [table.name] + [col.name for col in constraint.columns]
    if constraint.info is not None and "extra_guid_token" in constraint.info:
        str_tokens.append(constraint.info["extra_guid_token"])
    guid = uuid.uuid5(uuid.NAMESPACE_OID, "_".join(str_tokens))
    return guid.hex


Base.metadata.naming_convention = {
    "guid": _table_guid_generator,  # type: ignore
    "pk": "pk_%(table_name)s",
    "ix": "ix_%(guid)s",
    "uq": "uq_%(guid)s",
    "fk": "fk_%(guid)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}
