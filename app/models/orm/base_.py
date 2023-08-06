from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy import types as sa_types
from sqlalchemy.dialects import postgresql as pg_dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.schema import Computed, Index

if TYPE_CHECKING:
    from sqlalchemy.sql.schema import ColumnCollectionConstraint, Table


class Base(DeclarativeBase):
    __abstract__ = True

    ern_prefix: ClassVar[str] = "ern:library::"

    tags: Mapped[dict[str, Any]] = mapped_column(
        pg_dialect.JSONB(none_as_null=True),
        default={},
        nullable=False,
    )

    condition: Mapped[dict[str, Any]] = mapped_column(
        pg_dialect.JSONB(none_as_null=True),
        nullable=False,
        default={},
    )

    created: Mapped[datetime.datetime] = mapped_column(
        sa_types.TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    modified: Mapped[datetime.datetime | None] = mapped_column(
        sa_types.TIMESTAMP(timezone=True),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    @declared_attr
    def effective_erns(cls) -> Mapped[list[str]]:
        return mapped_column(
            pg_dialect.ARRAY(sa_types.Text),
            Computed(
                f"""
                ARRAY[
                    (\'{cls.ern_prefix}{cls.__tablename__}/\' || id::text),
                    \'{cls.ern_prefix}/*\'
                ]::text[]
                """
            ),
            nullable=False,
            index=True,
        )

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        return (
            Index(
                None,
                cls.tags,  # type: ignore
                postgresql_using="gin",
                postgresql_ops={"tags": "jsonb_path_ops"},
            ),
            Index(
                None,
                cls.condition,  # type: ignore
                postgresql_using="gin",
                postgresql_ops={"condition": "jsonb_path_ops"},
            ),
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
