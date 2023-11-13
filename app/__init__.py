import functools
import logging
import re

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .apis import API_ROUTERS
from .ctx import AppCtx, bind_app_ctx, create_app_ctx
from .settings import AppSettings
from .utils.fastapi import (
    FASTAPI_RESPONSES,
    ErrorReportAndForgetMiddleware,
    validation_error_hadler,
)

logger = logging.getLogger(__name__)


def create_app(app_settings: AppSettings) -> FastAPI:
    app = FastAPI(responses=FASTAPI_RESPONSES)

    app.add_middleware(ErrorReportAndForgetMiddleware)

    if app_settings.DEBUG_ALLOW_CORS_ALL_ORIGIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.error("`DEBUG_ALLOW_CORS_ALL_ORIGIN` is on!")

    async def _ctx_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        app_ctx: AppCtx = request.app.extra["_app_ctx"]
        async with bind_app_ctx(app_ctx):
            response = await call_next(request)
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_ctx_middleware)

    app.add_event_handler(
        "startup", functools.partial(_web_app_startup, app, app_settings)
    )

    app.add_event_handler("shutdown", functools.partial(_web_app_shutdown, app))

    app.add_exception_handler(RequestValidationError, validation_error_hadler)

    for api_router in API_ROUTERS:
        app.include_router(api_router)

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = "%s_%s" % (
                re.sub(
                    r"[{}/]",
                    "_",
                    route.path.strip("/"),
                ),
                tuple(route.methods)[0].lower(),
            )

            route.summary = route.operation_id.title().replace("_", " ")

    return app


async def _web_app_startup(app: FastAPI, app_settings: AppSettings) -> None:
    app_ctx = await create_app_ctx(app_settings)
    app.extra["_app_ctx"] = app_ctx


async def _web_app_shutdown(app: FastAPI) -> None:
    app_ctx: AppCtx = app.extra["_app_ctx"]

    try:
        await app_ctx.db.engine.dispose()
    except Exception:
        logger.warning("Failed dispose DB engine", exc_info=True)
