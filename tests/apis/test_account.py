from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from tests.helper import ensure_fresh_env, with_app_ctx

if TYPE_CHECKING:
    from httpx import AsyncClient

    from app.settings import AppSettings


@pytest.mark.asyncio
class TestApisAccount:
    @pytest_asyncio.fixture(autouse=True, scope="class")
    async def _init(self, app_settings: AppSettings) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()

            # do DB mocking here
            pass

    @pytest_asyncio.fixture(autouse=True, scope="class")
    async def _init_account(self, app_client: AsyncClient) -> None:
        r = await app_client.post(
            "/auth/signup",
            json={
                "username": "testaccount1",
                "password": "asdfqwer1234",
                "fullname": "test account",
            },
        )
        assert r.status_code == 200

        for _ in range(10):
            r = await app_client.post(
                "/auth/login",
                data={
                    "username": "testaccount1",
                    "password": "asdfqwer1234",
                },
            )
            assert r.status_code == 200

        r = await app_client.post(
            "/auth/signup",
            json={
                "username": "testaccount2",
                "password": "1234qwerasdf",
                "fullname": "test account",
            },
        )
        assert r.status_code == 200

    @pytest_asyncio.fixture(scope="class")
    async def account1_access_token(self, app_client: AsyncClient) -> str:
        r = await app_client.post(
            "/auth/login",
            data={"username": "testaccount1", "password": "asdfqwer1234"},
        )
        assert r.status_code == 200

        return r.json()["access_token"]  # type: ignore

    @pytest_asyncio.fixture(scope="class")
    async def account2_access_token(self, app_client: AsyncClient) -> str:
        r = await app_client.post(
            "/auth/login",
            data={"username": "testaccount2", "password": "1234qwerasdf"},
        )
        assert r.status_code == 200

        return r.json()["access_token"]  # type: ignore

    async def test_get_routing(
        self,
        app_client: AsyncClient,
        account1_access_token: str,
        account2_access_token: str,
    ) -> None:
        ...
        # Case : return the  for the current session

        r = await app_client.get(
            "/account",
        )
        assert r.status_code == 401

        r = await app_client.get(
            "/account", headers={"Authorization": f"Bearer {account1_access_token}"}
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount1"
        test1_id = r.json()["id"]

        r = await app_client.get(
            "/account", headers={"Authorization": f"Bearer {account2_access_token}"}
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount2"

        # Case : return the  for given id

        r = await app_client.get(
            "/account",
            params={"id": "cdf87aab1c38404c93f0d19157d67e55"},
            headers={"Authorization": f"Bearer {account2_access_token}"},
        )
        assert r.status_code == 409
        assert r.json()["code"] == "model_not_found"

        r = await app_client.get(
            "/account",
            params={"id": test1_id},
            headers={"Authorization": f"Bearer {account2_access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount1"

    async def test_by_username_get_routing(
        self,
        app_client: AsyncClient,
        account1_access_token: str,
        account2_access_token: str,
    ) -> None:
        # Case : return the  for the current session

        r = await app_client.get(
            "/account/by_username",
        )
        assert r.status_code == 401

        r = await app_client.get(
            "/account/by_username",
            headers={"Authorization": f"Bearer {account1_access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount1"

        r = await app_client.get(
            "/account/by_username",
            headers={"Authorization": f"Bearer {account2_access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount2"

        # Case : return the  for given username

        r = await app_client.get(
            "/account/by_username",
            params={"username": "fakeaccount"},
            headers={"Authorization": f"Bearer {account2_access_token}"},
        )
        assert r.status_code == 409
        assert r.json()["code"] == "model_not_found"

        r = await app_client.get(
            "/account/by_username",
            params={"username": "testaccount1"},
            headers={"Authorization": f"Bearer {account2_access_token}"},
        )
        assert r.status_code == 200
        assert r.json()["username"] == "testaccount1"

    async def test_patch_routing(self, app_client: AsyncClient) -> None:
        pass

    async def test_logins_get_routing(self, app_client: AsyncClient) -> None:
        pass
