from typing import Any

from pydantic import AnyUrl, BaseSettings, Field, HttpUrl, SecretStr


class AppSettings(BaseSettings):
    LOGGING_DEBUG_LEVEL: bool = Field(
        default=True,
        description=(
            "If True, the application logging level is set to DEBUG, "
            "which is otherwise INFO."
        ),
    )
    LOGGING_SLACK_URL: HttpUrl | None = Field(
        default=None,
        description=(
            "If set, send slack notifications when ERROR " "or above logs are catched."
        ),
    )
    LOGGING_SENTRY_DSN: HttpUrl | None = Field(
        default=None,
        description=(
            "If set, send sentry reports when ERROR " "or above logs are catched."
        ),
    )

    DEBUG_ALLOW_CORS_ALL_ORIGIN: bool = Field(
        default=True,
        description="If True, allow origins for CORS requests.",
    )

    SECRET_KEY: SecretStr = Field(
        default=SecretStr("default_unsafe_secret_key"),
        description="Secret key to validate auth JWT.",
    )

    DB_URI: AnyUrl = Field(
        default=AnyUrl(
            url=("postgresql+asyncpg://" "sample:password@127.0.0.1:25000/example"),
            scheme="postgresql+asyncpg",
        ),
        description="DB connection URI.",
    )

    DB_OPTIONS: dict[str, Any] = Field(
        default={"pool_recycle": 15 * 60},
        description="PosstgreSQL option to create a connection.",
    )

    class Config:
        env_file = ".env"
        env_prefix = "app_"
