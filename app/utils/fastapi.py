from __future__ import annotations

import dataclasses
import enum
import json
import logging
from typing import TYPE_CHECKING, Any, Callable, Literal, get_type_hints

import anyio
from fastapi import APIRouter, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.types import DecoratedCallable
from pydantic import BaseModel

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)


class AuthErrorCodeEnum(str, enum.Enum):
    InvalidIssuer = "invalid_issuer"
    InvalidPayload = "invalid_payload"
    InvalidAccessToken = "invalid_access_token"
    ExpiredAccessToken = "expired_access_token"
    InvlaidAlgorithm = "invalid_algorithm"

    @property
    def desc(self) -> str:
        return {
            self.InvalidAccessToken: "Failed to decode your access token",
            self.InvalidIssuer: "This token is not issued on this server",
            self.InvalidPayload: "This token's payload is invalid",
            self.ExpiredAccessToken: "Your token has expired",
            self.InvlaidAlgorithm: "Your token has invalid algorithm",
        }[self]


class LogicErrorCodeEnum(str, enum.Enum):
    DuplicatedUsername = "duplicated_username"

    ModelNotFound = "model_not_found"

    RaceCondition = "race_condition"

    WrongPassword = "wrong_password"

    @property
    def desc(self) -> str:
        return {
            self.DuplicatedUsername: "This username already exist.",
            self.ModelNotFound: (
                "Failed to find target model." "Check specific information in detail."
            ),
            self.RaceCondition: "Race condition occurred. try again.",
            self.WrongPassword: "Failed to login with incorrect password.",
        }[self]


@dataclasses.dataclass
class _ManagedError(Exception):
    code: AuthErrorCodeEnum | LogicErrorCodeEnum
    detail: dict[str, Any] | None = None


class AuthError(_ManagedError):
    pass


class LogicError(_ManagedError):
    pass


class UnauthorizedError(Exception):
    pass


class _ErrorResponseModel(BaseModel):
    code: str
    message: str
    detail: dict[str, Any] | None

    @staticmethod
    def from_exc(exc: _ManagedError) -> _ErrorResponseModel:
        return _ErrorResponseModel(
            code=exc.code,
            message=exc.code.desc,
            detail=exc.detail,
        )


class UnauthorizedErrorModel(_ErrorResponseModel):
    code = "Unauthorized"
    message = "Not authenticated"


class AuthErrorModel(_ErrorResponseModel):
    code: AuthErrorCodeEnum = AuthErrorCodeEnum.InvalidAccessToken
    message = AuthErrorCodeEnum.InvalidAccessToken.desc


class LogicErrorModel(_ErrorResponseModel):
    code: LogicErrorCodeEnum = LogicErrorCodeEnum.DuplicatedUsername
    message = LogicErrorCodeEnum.DuplicatedUsername.desc


class UnprocessableEntityErrorModel(_ErrorResponseModel):
    code = "unprocessable_entity"
    message = (
        "1 validation error for Request\nbody -> login_id\n"
        "value is not a valid email address (type=value_error.email)"
    )


class ServerErrorModel(_ErrorResponseModel):
    code = "server_error"
    message = "unexpected server error"


FASTAPI_RESPONSES: dict[int | str, dict[str, Any]] = {
    403: {
        "description": "Auth Error",
        "model": _ErrorResponseModel,
    },
    409: {
        "description": "Logical Error",
        "model": _ErrorResponseModel,
    },
    500: {
        "description": "Server Error",
        "model": _ErrorResponseModel,
    },
}


class ErrorReportAndForgetMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def _send(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True

            await send(message)

        try:
            await self.app(scope, receive, _send)
            return

        except anyio.BrokenResourceError:
            # Client has been disconenction, so nothing to do
            return

        except UnauthorizedError:
            err_response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=UnauthorizedErrorModel().dict(),
            )

        except AuthError as err:
            err_response = JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=_ErrorResponseModel.from_exc(err).dict(),
            )
        except LogicError as err:
            err_response = JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=_ErrorResponseModel.from_exc(err).dict(),
            )
        except Exception:
            logger.exception("Internal server error")

            err_response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ServerErrorModel().dict(),
            )

        if not response_started:
            await err_response(scope, receive, send)


def _build_desc(
    error_codes: list[AuthErrorCodeEnum | LogicErrorCodeEnum],
    desc: str | None = None,
) -> str:
    if not error_codes:
        return desc or ""

    return "\n".join(
        [
            desc or "",
            "### Error codes",
            *[
                f"- **{error_code.value}**:{error_code.desc}"
                for error_code in error_codes
            ],
        ]
    )


async def validation_error_hadler(
    _: Request, err: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=UnprocessableEntityErrorModel(
            message=str(err),
            detail=json.loads(err.json()),
        ).dict(),
    )


class DefaultResponse(BaseModel):
    pass


class CustomAPIRouter(APIRouter):
    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        if kwargs.get("response_model") is None:
            kwargs["response_model"] = get_type_hints(endpoint).get("return")

        return super().add_api_route(path, endpoint, **kwargs)

    def api_wrapper(
        self,
        method: Literal["DELETE", "GET", "PATCH", "POST", "PUT"],
        path: str,
        *,
        error_codes: list[AuthErrorCodeEnum | LogicErrorCodeEnum] | None = None,
        **kwargs: Any,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        kwargs["description"] = _build_desc(
            error_codes or [],
            kwargs.get("description"),
        )
        return {  # type: ignore
            "DELETE": self.delete(path, **kwargs),
            "GET": self.get(path, **kwargs),
            "PATCH": self.patch(path, **kwargs),
            "POST": self.post(path, **kwargs),
            "PUT": self.put(path, **kwargs),
        }[method]


def get_client_ip(request: Request) -> str:
    x_forwarded_for: str | None = request.headers.get("X-FORWARDED-FOR")
    return (
        (x_forwarded_for.split(",")[0]).split(":")[0]
        if x_forwarded_for is not None
        else request.client.host  # type: ignore
    )
