from datetime import timedelta
import pytest

from fastapi import status
from httpx import AsyncClient

from api.routers.auth import create_token

USER_ID = "c603ef4f-08f9-4130-a770-3a34defa44b3"
FAKE_USER_ID = "00000000-08f9-4130-a770-3a34defa44b3"


class TestAuth:
    form = {"grant_type": "", "client_id": "", "client_secret": "", "username": "admin", "password": "pass"}

    @pytest.mark.asyncio
    async def test_incorrect_password(self, client: AsyncClient):
        # Try using an incorrect password
        form = {**self.form, "password": "incorrect"}

        # It should reply with a 401 error
        response = await client.post("/auth/token", data=form)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_garbage_token(self, client: AsyncClient):
        # Craft an invalid token
        headers = {"Authorization": "Bearer craftedtoken"}

        # It should return a 401 error
        response = await client.get("/user/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_missing_user(self, client: AsyncClient):
        # Create a valid access token with a invalid user.
        headers = {"Authorization": "Bearer " + create_token(sub=FAKE_USER_ID, typ="session")}

        # Since the user doesn't exists anymore, it should return a 401 error.
        response = await client.get("/user/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_expired_token(self, client: AsyncClient):
        # Create a valid but expired access token.
        headers = {
            "Authorization": "Bearer " + create_token(sub=USER_ID, typ="session", expires_delta=timedelta(minutes=-1))
        }

        # Since it's not valid anymore, it should return a 401 error.
        response = await client.get("/user/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def _validate_token_response(self, res, client: AsyncClient):
        assert res.status_code == status.HTTP_200_OK
        assert res.json().get("access_token")
        assert res.json().get("refresh_token")
        assert res.json().get("token_type") == "bearer"

        headers = {"Authorization": "Bearer " + res.json()["access_token"]}

        # Check that the given token is working
        response = await client.get("/user/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_correct_token(self, client: AsyncClient):
        # Try using the correct password
        response = await client.post("/auth/token", data=self.form)

        await self._validate_token_response(response, client)

    @pytest.mark.asyncio
    async def test_refresh(self, client: AsyncClient):
        response = await client.post("/auth/token", data=self.form)

        refresh_body = dict(token=response.json().get("refresh_token"))
        response = await client.post("/auth/refresh", json=refresh_body)

        await self._validate_token_response(response, client)
