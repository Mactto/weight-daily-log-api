import functools
import logging
import re

from ebc.log_helper import init_logger as _init_logger
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

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
except LookupError:
    try:
        from ._version import version

        __version__ = version
    except ModuleNotFoundError:
        raise RuntimeError(
            "Cannot determine version: "
            "check whether git repository is initialized "
            "or _version.py file exists."
        )


logger = logging.getLogger(__name__)


def init_logger(app_settings: AppSettings) -> logging.Logger:
    app_logger_level = (
        logging.DEBUG if app_settings.LOGGING_DEBUG_LEVEL else logging.INFO
    )

    return _init_logger(
        f"sample-api@{__version__}",
        __name__,
        app_logger_level=app_logger_level,
        stdout_handler_level=app_logger_level,
        slack_url=app_settings.LOGGING_SLACK_URL,
        sentry_dsn=app_settings.LOGGING_SENTRY_DSN,
        additional_loggers=[],
    )


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
