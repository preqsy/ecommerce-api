from unittest.mock import MagicMock, patch
from httpx import AsyncClient
from core.db import get_db
from crud.auth import CRUDAuthUser
from crud.otp import CRUDOtp
from main import app
import pytest
from fastapi import BackgroundTasks, status
from sqlalchemy.orm import Session

from schemas.otp import OTPType
from tests.fixtures.auth_user_samples import sample_auth_user_create
from tests.fixtures.testdb import mock_get_db, client

from schemas.auth import RegisterAuthUserResponse


# app.dependency_overrides[get_db] = mock_get_db


# @pytest.mark.asyncio
# # @pytest.mark.anyio
# @pytest.mark.freeze_time("2024-07-23 08:45:00.650334")
# async def test_register_success(client):
#     response = await client.post(
#         "/auth/register",
#         json=sample_auth_user_create(),
#         headers={"user_agent": "testing"},
#     )
#     new_user = RegisterAuthUserResponse(**response.json())
#     assert response.json() == new_user.model_dump()
#     assert response.status_code == status.HTTP_201_CREATED


# @pytest.mark.asyncio
# async def test_register_failure(client):
#     response = await client.post(
#         "/auth/register",
#         json=sample_auth_user_create(),
#         headers={"user_agent": "testing"},
#     )

#     assert response.status_code == status.HTTP_409_CONFLICT


# @pytest.mark.asyncio
# async def verify_token(client: AsyncClient):
#     rsp = client.post("/auth/verify")


@pytest.fixture
async def client():
    client = AsyncClient(app=app, base_url="http://127.0.0.1")
    yield client


@pytest.fixture
def db_session():
    db = MagicMock(spec=Session)
    yield db


@pytest.fixture
def crud_otp():
    mock = MagicMock(spec=CRUDOtp)
    yield mock


@pytest.fixture
def crud_auth_user():
    mock = MagicMock(spec=CRUDAuthUser)
    yield mock


@pytest.fixture
def background_task():
    mock = MagicMock(spec=BackgroundTasks)
    yield mock


@pytest.mark.asyncio
async def test_register_user(
    client, db_session, crud_auth_user, crud_otp, background_task
):
    with patch("core.db.get_db", return_value=db_session), patch(
        "crud.auth.get_crud_auth_user", return_value=crud_auth_user
    ), patch("crud.otp.crud_otp", return_value=crud_otp), patch(
        "fastapi.BackgroundTasks", return_value=background_task
    ):
        crud_auth_user.get_by_email.return_value == "obbyprecious@gmail.com"
        crud_auth_user.create.return_value = MagicMock(sample_auth_user_create())
        crud_otp.create.return_value = MagicMock(auth_id=1, otp_type=OTPType.EMAIL)

        response = await client.post(
            "/auth/register",
            json=sample_auth_user_create(),
            headers={"user-agent": "test-agent"},
        )

        assert response.status_code == 201
