from typing import Any

import pytest
from fastapi import status
from unittest.mock import patch
from httpx import AsyncClient

from core.errors import InvalidRequest
from core.tokens import get_current_auth_user, verify_access_token
from crud.auth import get_crud_auth_user
from main import app
from tests.conftest import mock_crud_auth_user
from models.auth_user import AuthUser
from schemas.otp import OTPType
from tests.fixtures.auth_user_samples import (
    sample_auth_user_create,
    sample_auth_user_invalid_password,
    sample_auth_user_query_result_first,
    sample_auth_user_query_result_unverfied_email,
    sample_auth_user_wrong_email,
    sample_header,
    sample_login_user,
    sample_login_user_wrong_email,
    sample_verify_auth_user,
)
from schemas.auth import ForgotPassword, RegisterAuthUserResponse


crud_otp_verify_path = "endpoints.auth.crud_otp.verify_otp"
auth_endpoint_path = "endpoints.auth"
verify_password_path = "utils.password_utils.verify_password"


async def register_user(
    client: AsyncClient,
    sample_register_details: dict = sample_auth_user_create(),
):

    response = await client.post(
        "/auth/register",
        json=sample_register_details,
        headers={"user_agent": "testing"},
    )

    return response


async def login_user_success(
    client: AsyncClient,
    sample_user_return_value: dict[str, Any] = sample_auth_user_query_result_first(),
    login_details: dict[str, str] = sample_login_user(),
):
    await register_user(client)

    app.dependency_overrides[get_crud_auth_user] = lambda: mock_crud_auth_user

    sample_user = AuthUser(**sample_user_return_value)
    mock_crud_auth_user.get_by_email.return_value = sample_user

    with patch(verify_password_path) as mock_verify_password:
        mock_verify_password.return_value = True
        response = await client.post(
            "/auth/token", data=login_details, headers=sample_header()
        )

    app.dependency_overrides = {}
    return response


@pytest.mark.asyncio
@pytest.mark.freeze_time("2024-07-23 08:45:00.650334")
async def test_register_success(client, database_override_dependencies):

    response = await register_user(client)

    new_user = RegisterAuthUserResponse(**response.json())
    assert response.json() == new_user.model_dump()
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_register_wrong_email_format(client, database_override_dependencies):
    response = await register_user(
        client=client, sample_register_details=sample_auth_user_wrong_email()
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_register_wrong_password_format(client, database_override_dependencies):
    response = await client.post(
        "/auth/register",
        json=sample_auth_user_invalid_password(),
        headers=sample_header(),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_verify_token_email_success(client, database_override_dependencies):

    await register_user(client)

    with patch(crud_otp_verify_path) as mock_crud_otp:

        mock_crud_otp.return_value = True

        rsp = await client.post("/auth/verify", json=sample_verify_auth_user())

        mock_crud_otp.assert_called_once_with(
            auth_id=1,
            token="930287",
            otp_type=OTPType.EMAIL,
        )

        assert rsp.status_code == 200


@pytest.mark.asyncio
async def test_verify_email_token_wrong_token(client, database_override_dependencies):

    await register_user(client)

    with patch(crud_otp_verify_path) as mock_crud_otp:

        mock_crud_otp.return_value = None

        rsp = await client.post("/auth/verify", json=sample_verify_auth_user())

        mock_crud_otp.assert_called_once_with(
            auth_id=1,
            token="930287",
            otp_type=OTPType.EMAIL,
        )

        assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_login_success(client, database_override_dependencies):
    response = await login_user_success(client)
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]
    access_token = response.json().get("access_token")
    verify_access_token(token=access_token)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_login_unverified_email(client, database_override_dependencies):
    response = await login_user_success(
        client=client,
        sample_user_return_value=sample_auth_user_query_result_unverfied_email(),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_login_nonexistent_user(client, database_override_dependencies):
    await register_user(client)

    response = await client.post(
        "/auth/token", data=sample_login_user_wrong_email(), headers=sample_header()
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_login_wrong_password(client, database_override_dependencies):

    response = await login_user_success(
        client=client,
        login_details={
            "username": "obbyprecious12@gmail.com",
            "password": "wrongemail",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_logout_user_success(
    client,
    database_override_dependencies,
):
    login_rsp = await login_user_success(client)
    access_token = login_rsp.json().get("access_token")
    app.dependency_overrides[get_current_auth_user] = lambda: mock_crud_auth_user
    mock_crud_auth_user.id = 1
    with patch("endpoints.auth.deactivate_token") as mock_deactivate_token:
        rsp = await client.post("/auth/logout", json={"access_token": access_token})
        mock_deactivate_token.assert_called_once()

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_logout_user_invalid_token(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):

    with patch("endpoints.auth.deactivate_token") as mock_deactivate_token:
        mock_deactivate_token.side_effect = InvalidRequest("Invalid token")
        rsp = await client.post(
            "/auth/logout",
            json={"access_token": "banana"},
        )
        mock_deactivate_token.assert_called_once()

        assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_success(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):
    rsp = await client.get("/auth/me")

    assert rsp.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_forget_password_success(client, database_override_dependencies):
    await register_user(client)

    rsp = await client.post(
        "/auth/forget-password",
        json={"email": "obbyprecious12@gmail.com"},
        headers=sample_header(),
    )
    assert rsp.status_code == status.HTTP_200_OK
    assert rsp.json() == {
        "reset_password_link_sent": True,
    }


@pytest.mark.asyncio
async def test_forget_password_many_requests(client, database_override_dependencies):
    await register_user(client)
    for _ in range(2):
        rsp = await client.post(
            "/auth/forget-password",
            json={"email": "obbyprecious12@gmail.com"},
            headers=sample_header(),
        )
        assert rsp.status_code == status.HTTP_200_OK
    rsp = await client.post(
        "/auth/forget-password",
        json={"email": "obbyprecious12@gmail.com"},
        headers=sample_header(),
    )
    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_forget_password_wrong_email(client, database_override_dependencies):

    rsp = await client.post(
        "/auth/forget-password",
        json={"email": "obbyprecious12@gmail.com"},
        headers=sample_header(),
    )
    assert rsp.status_code == status.HTTP_404_NOT_FOUND
