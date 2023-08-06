import asyncio
import hashlib
import random
import time
import uuid
from typing import Any

import asyncpg
from sqlalchemy import func as sa_func
from sqlalchemy import types as sa_types
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import expression as sa_exp

from app.ctx import AppCtx


async def _asyncpg_prepare(  # type: ignore
    self,
    query,
    *,
    name=None,
    timeout=None,
    record_class=None,
):
    return await self._prepare(
        query,
        name=str(uuid.uuid1()) if name is None else name,  # hotfix
        timeout=timeout,
        use_cache=False,
        record_class=record_class,
    )


class SqlaEngineAndSession:
    def __init__(self, db_uri: str, db_options: dict[str, Any]) -> None:
        self.engine: AsyncEngine = create_async_engine(
            db_uri,
            connect_args={
                # to disable SQLA's statement cache for `.prepare()`
                "prepared_statement_cache_size": 0,
                # to disable asyncpg's statement cache for `.execute()`
                "statement_cache_size": 0,
            },
            **db_options,
        )

        # hotfix for `https://github.com/sqlalchemy/sqlalchemy/issues/6467`
        asyncpg.Connection.prepare = _asyncpg_prepare

        self._scoped_session = async_scoped_session(
            async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            ),
            # NOTE : we cannot use `asyncio.current_task` because starlette
            #        schedules HTTPMiddleware and routing function in different
            #        tasks.
            scopefunc=lambda: AppCtx.current.ctx_id,
        )

    @property
    def session(self) -> AsyncSession:
        return self._scoped_session()

    async def clear_scoped_session(self) -> None:
        await self._scoped_session.remove()


async def obtain_advisory_lock(ident: str, timeout: float = 5.0) -> None:
    ident_hashed = int.from_bytes(
        hashlib.sha256(ident.encode()).digest()[:8],
        byteorder="little",
        signed=True,
    )

    lock_query = sa_exp.select(
        sa_func.pg_try_advisory_xact_lock(
            sa_exp.cast(ident_hashed, sa_types.BigInteger)
        )
    )

    deadline = time.monotonic() + timeout

    while deadline >= time.monotonic():
        is_lock_obtained = (
            await AppCtx.current.db.session.execute(lock_query)
        ).scalar()

        if is_lock_obtained:
            break

        await asyncio.sleep(random.uniform(0.1, 0.2))

    else:
        raise RuntimeError(f"failed to obtain the advisory lock (ident: {ident})")
