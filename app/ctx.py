from __future__ import annotations

import contextlib
import contextvars
import dataclasses
import logging
import uuid
from typing import TYPE_CHECKING, AsyncIterator

if TYPE_CHECKING:
    from .settings import AppSettings
    from .utils.sqla import SqlaEngineAndSession

logger = logging.getLogger(__name__)

_current_app_ctx_var: contextvars.ContextVar[AppCtx] = contextvars.ContextVar(
    "_current_app_ctx_var"
)


class AppCtxMeta(type):
    @property
    def current(self) -> AppCtx:
        return _current_app_ctx_var.get()


@dataclasses.dataclass(frozen=True)
class AppCtx(metaclass=AppCtxMeta):
    settings: AppSettings
    db: SqlaEngineAndSession

    ctx_id: str


async def create_app_ctx(app_settings: AppSettings) -> AppCtx:
    from .utils.sqla import SqlaEngineAndSession

    return AppCtx(
        settings=app_settings,
        db=SqlaEngineAndSession(app_settings.DB_URI, app_settings.DB_OPTIONS),
        ctx_id=str(uuid.uuid4()),
    )


@contextlib.asynccontextmanager
async def bind_app_ctx(app_ctx: AppCtx) -> AsyncIterator[None]:
    var_set_token = _current_app_ctx_var.set(
        dataclasses.replace(app_ctx, ctx_id=str(uuid.uuid4()))
    )
    try:
        yield
    finally:
        try:
            await app_ctx.db.clear_scoped_session()
        except Exception:
            logger.warning("Failed to clear DB scoped session", exc_info=True)

        _current_app_ctx_var.reset(var_set_token)
