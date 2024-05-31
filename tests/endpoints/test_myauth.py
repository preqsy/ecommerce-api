from unittest.mock import patch
from core.db import get_db
from main import app
import pytest
from fastapi import status

from schemas.otp import OTPType
from tests.fixtures.auth_user_samples import (
    sample_auth_user_create,
    sample_auth_user_invalid_password,
    sample_auth_user_wrong_email,
    sample_header,
    sample_login_user,
    sample_verify_auth_user,
)

from tests.fixtures.testdb import mock_get_db, client

from schemas.auth import RegisterAuthUserResponse


app.dependency_overrides[get_db] = mock_get_db


async def register_user(client):

    response = await client.post(
        "/auth/register",
        json=sample_auth_user_create(),
        headers={"user_agent": "testing"},
    )

    return response


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-07-23 08:45:00.650334")
async def test_register_success(client):
    response = await register_user(client)
    new_user = RegisterAuthUserResponse(**response.json())
    assert response.json() == new_user.model_dump()
    assert response.status_code == status.HTTP_201_CREATED
    return response


@pytest.mark.asyncio
async def test_register_failure(client):
    response = await register_user(client)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_register_wrong_email_format(client):
    response = await client.post(
        "/auth/register",
        json=sample_auth_user_wrong_email(),
        headers={"user_agent": "testing"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_register_wrong_password_format(client):
    response = await client.post(
        "/auth/register",
        json=sample_auth_user_invalid_password(),
        headers={"user_agent": "testing"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_verify_token(client):
    # Register a new user
    await register_user(client)

    # Mock the dependencies
    with patch("endpoints.auth.crud_otp.verify_otp") as mock_crud_otp:

        # Set return values for the mocked methods
        mock_crud_otp.return_value = True

        # Perform the verify request
        rsp = await client.post("/auth/verify", json=sample_verify_auth_user())

        # Assert the expected calls
        mock_crud_otp.assert_called_once_with(
            auth_id=1,
            token="930287",
            otp_type=OTPType.EMAIL,
        )

        assert rsp.status_code == 200


@pytest.mark.asyncio
async def test_login(client):
    register_rsp = await register_user(client)
    user_deets: dict = register_rsp.json()

    response = await client.post(
        "/auth/token", data=sample_login_user(), headers=sample_header()
    )
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED
