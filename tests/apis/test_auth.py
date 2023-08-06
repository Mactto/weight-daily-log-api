from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from tests.helper import ensure_fresh_env, with_app_ctx

if TYPE_CHECKING:
    from httpx import AsyncClient

    from app.settings import AppSettings


@pytest.mark.asyncio
class TestApisAuth:
    @pytest_asyncio.fixture(autouse=True, scope="class")
    async def _init_db(self, app_settings: AppSettings) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()

            # do DB mocking here
            pass

    async def test_signup_post_routing(self, app_client: AsyncClient) -> None:
        r = await app_client.post(
            "/auth/signup",
            json={
                "username": "testuser",
                "password": "asdfqwer1234",
                "fullname": "test account",
            },
        )
        assert r.status_code == 200

        r = await app_client.post(
            "/auth/signup",
            json={
                "username": "testuser",
                "password": "1234qwerasdf",
                "fullname": "test account",
            },
        )
        assert r.status_code == 409
        assert r.json()["code"] == "duplicated_username"

    async def test_login_post_routing(self, app_client: AsyncClient) -> None:
        r = await app_client.post(
            "/auth/login",
            data={"username": "testuser2", "password": "asdfqwer1234"},
        )
        assert r.status_code == 409
        assert r.json()["code"] == "model_not_found"

        r = await app_client.post(
            "/auth/login",
            data={"username": "testuser", "password": "1234qwerasdf"},
        )
        assert r.status_code == 409
        assert r.json()["code"] == "wrong_password"

        r = await app_client.post(
            "/auth/login",
            data={"username": "testuser", "password": "asdfqwer1234"},
        )
        assert r.status_code == 200
