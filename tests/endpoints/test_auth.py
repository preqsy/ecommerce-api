from typing import Dict, List, Union

import pytest
from fastapi import status
from unittest.mock import patch
from httpx import AsyncClient

from core.errors import InvalidRequest
from core.tokens import get_current_auth_user, verify_access_token
from main import app
from models.auth_user import OTP
from tests.conftest import database_override_dependencies, mock_crud_auth_user
from tests.mock_dependencies import mock_crud_otp
from schemas import OTPType, RegisterAuthUserResponse
from tests.sample_datas.auth_user_samples import (
    sample_auth_user_create_customer,
    sample_auth_user_invalid_password,
    sample_auth_user_wrong_email,
    sample_header,
    sample_login_user_customer,
    sample_login_user_wrong_email,
    sample_verify_auth_user,
)


crud_otp_verify_path = "endpoints.auth.crud_otp.verify_otp"
auth_endpoint_path = "endpoints.auth"
verify_password_path = "utils.password_utils.verify_password"


async def register_user(
    client: AsyncClient,
    sample_register_details: dict = sample_auth_user_create_customer(),
):
    response = await client.post(
        "/auth/register",
        json=sample_register_details,
        headers=sample_header(),
    )

    return response


async def register_and_verify_email(
    client,
    database_override_dependencies=database_override_dependencies,
    sample_register_details: dict = sample_auth_user_create_customer(),
):
    mock_crud_otp.verify_otp.reset_mock()
    register_rsp = await register_user(
        client, sample_register_details=sample_register_details
    )
    mock_crud_otp.verify_otp.return_value = True
    verify_auth_user = sample_verify_auth_user()
    verify_auth_user["auth_id"] = register_rsp.json()["auth_user"]["id"]

    rsp = await client.post("/auth/verify", json=verify_auth_user)

    mock_crud_otp.verify_otp.assert_called_once()

    assert rsp.json() == {"verified": True}
    assert rsp.status_code == 200
    return register_rsp


async def login_user(
    client: AsyncClient,
    sample_register_details: Union[List, Dict] = sample_auth_user_create_customer(),
    login_details: Union[List, Dict] = sample_login_user_customer(),
):

    response = []
    if isinstance(sample_register_details, dict) and isinstance(login_details, dict):
        register_rsp = await register_and_verify_email(
            client, sample_register_details=sample_register_details
        )
        access_token = register_rsp.json()["tokens"]["access_token"]
        headers = sample_header()
        headers["authorization"] = "Bearer {}".format(access_token)
        rsp = await client.post("/auth/login", data=login_details, headers=headers)

        return rsp
    login_iter = iter(login_details)
    for sample_user in sample_register_details:
        login = next(login_iter)
        register_rsp = await register_and_verify_email(
            client, sample_register_details=sample_user
        )
        access_token = register_rsp.json()["tokens"]["access_token"]
        headers = sample_header()
        headers["authorization"] = "Bearer {}".format(access_token)

        rsp = await client.post("/auth/login", data=login, headers=headers)
        new_data = rsp.json()
        new_data.update({"default_role": sample_user["default_role"]})
        response.append(new_data)

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
        client,
        sample_register_details=sample_auth_user_wrong_email(),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


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

    mock_crud_otp.verify_otp.return_value = True

    rsp = await client.post("/auth/verify", json=sample_verify_auth_user())

    mock_crud_otp.verify_otp.assert_called_once_with(
        auth_id=1,
        token="930287",
        otp_type=OTPType.EMAIL,
    )
    mock_crud_otp.verify_otp.reset_mock()
    assert rsp.json() == {"verified": True}
    assert rsp.status_code == 200


@pytest.mark.asyncio
async def test_verify_email_token_wrong_token(client, database_override_dependencies):

    await register_user(client)

    mock_crud_otp.verify_otp.return_value = None

    rsp = await client.post("/auth/verify", json=sample_verify_auth_user())

    mock_crud_otp.verify_otp.assert_called_once_with(
        auth_id=1,
        token="930287",
        otp_type=OTPType.EMAIL,
    )

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_login_success(client, database_override_dependencies):
    response = await login_user(client)
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]
    access_token = response.json().get("access_token")
    verify_access_token(token=access_token)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_login_nonexistent_user(client, database_override_dependencies):
    await register_user(client)

    response = await client.post(
        "/auth/login", data=sample_login_user_wrong_email(), headers=sample_header()
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_login_wrong_password(client, database_override_dependencies):

    response = await login_user(
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
    login_rsp = await login_user(client)
    access_token = login_rsp.json().get("access_token")
    app.dependency_overrides[get_current_auth_user] = lambda: mock_crud_auth_user
    mock_crud_auth_user.id = 1
    with patch("api.endpoints.auth.deactivate_token") as mock_deactivate_token:
        rsp = await client.post("/auth/logout", json={"access_token": access_token})
        mock_deactivate_token.assert_called_once()

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_logout_user_invalid_token(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):

    with patch("api.endpoints.auth.deactivate_token") as mock_deactivate_token:
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

    mock_crud_otp.check_number_of_trials.return_value = OTP(
        no_of_tries=1, auth_id=1, otp_type=OTPType.EMAIL, otp="019203"
    )
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

    mock_crud_otp.check_number_of_trials.return_value = OTP(
        no_of_tries=4, auth_id=1, otp_type=OTPType.EMAIL, otp="019203"
    )
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


@pytest.mark.asyncio
async def test_change_password_success(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):
    await register_user(client)
    rsp = await client.put(
        "/auth/change-password",
        json={"old_password": "2Strong", "new_password": "2Strongg"},
    )

    assert rsp.json() == {"password_changed": True}
    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_password_wrong_old_password(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):
    await register_user(client)
    rsp = await client.put(
        "/auth/change-password",
        json={"old_password": "2Strongg", "new_password": "2Strongg"},
    )

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_change_password_new_password_same_as_old_password(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):
    await register_user(client)
    rsp = await client.put(
        "/auth/change-password",
        json={"old_password": "2Strong", "new_password": "2Strong"},
    )
    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_change_password_wrong_new_password_format(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):

    await register_user(client)

    rsp = await client.put(
        "/auth/change-password",
        json={"old_password": "2Strong", "new_password": "2Str"},
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_refresh_token_success(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):

    register_rsp = await register_user(client)
    refresh_token = register_rsp.json()["tokens"]["refresh_token"]

    headers = sample_header()
    with patch(
        "core.tokens.crud_refresh_token.check_if_refresh_token_exist"
    ) as mock_crud_refresh_token:
        mock_crud_refresh_token.return_value = True
        rsp = await client.post(
            "/auth/refresh-token",
            json={"refresh_token": refresh_token},
            headers=headers,
        )
        assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token_wrong_token(
    client, database_override_dependencies, get_current_auth_user_override_dependency
):

    await register_user(client)

    headers = sample_header()
    rsp = await client.post(
        "/auth/refresh-token",
        json={"refresh_token": "refresh_token"},
        headers=headers,
    )
    assert rsp.status_code == status.HTTP_404_NOT_FOUND
