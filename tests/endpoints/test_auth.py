from fastapi import BackgroundTasks
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from crud.otp import CRUDOtp
from main import app
from crud.auth import CRUDAuthUser
from utils.password_utils import hash_password

client = TestClient(app)


# Mock dependencies
@pytest.fixture
def db_session():
    db = MagicMock(spec=Session)
    yield db


@pytest.fixture
def crud_auth_user():
    mock = MagicMock(spec=CRUDAuthUser)
    yield mock


@pytest.fixture
def crud_otp():
    mock = MagicMock(spec=CRUDOtp)
    yield mock


@pytest.fixture
def background_tasks():
    mock = MagicMock(spec=BackgroundTasks)
    yield mock


# # Test the register_user endpoint
# def test_register_user(db_session, crud_auth_user, crud_otp, background_tasks):
#     with patch("core.db.get_db", return_value=db_session), patch(
#         "crud.auth.get_crud_auth_user", return_value=crud_auth_user
#     ), patch("crud.otp.get_crud_otp", return_value=crud_otp), patch(
#         "fastapi.BackgroundTasks", return_value=background_tasks
#     ):

#         crud_auth_user.get_by_email.return_value = None
#         crud_auth_user.create.return_value = MagicMock(id=1)
#         crud_otp.create.return_value = MagicMock()

#         response = client.post(
#             "/auth/register",
#             json={
#                 "email": "preqsy1@gmail.com",
#                 "password": "Testpassword1!",
#                 "default_role": "customer",
#             },
#             headers={"user-agent": "test-agent"},
#         )

#         assert response.status_code == 201
#         response_json = response.json()
#         assert response_json["auth_user"]["email"] == "preqsy1@gmail.com"


# Test the verify endpoint
# def test_verify_user(crud_auth_user, crud_otp):
#     with patch("crud.auth.get_crud_auth_user", return_value=crud_auth_user), patch(
#         "crud.otp.get_crud_otp", return_value=crud_otp
#     ):

#         crud_auth_user.get_or_raise_exception.return_value = MagicMock()
#         crud_otp.verify_otp.return_value = MagicMock(otp_type="EMAIL")

#         response = client.post(
#             "/auth/verify", json={"auth_id": 1, "token": "123456", "otp_type": "EMAIL"}
#         )

#         assert response.status_code == 200


# # Test the login_user endpoint
# def test_login_user(db_session, crud_auth_user):
#     with patch("core.db.get_db", return_value=db_session), patch(
#         "crud.auth.get_crud_auth_user", return_value=crud_auth_user
#     ):

#         crud_auth_user.get_by_email.return_value = MagicMock(
#             id=1, password=hash_password("Testpassword1!")
#         )

#         response = client.post(
#             "/auth/token",
#             data={"username": "test@example.com", "password": "Testpassword1!"},
#             headers={
#                 "user-agent": "test-agent",
#                 "Content-Type": "application/x-www-form-urlencoded",
#             },
#         )

#         assert response.status_code == 201
#         response_json = response.json()
#         assert "access_token" in response_json


# # Test the logout_user endpoint
# def test_logout_user(db_session):
#     with patch("core.db.get_db", return_value=db_session), patch(
#         "core.tokens.get_current_auth_user", return_value=MagicMock(id=1)
#     ):

#         response = client.post(
#             "/auth/logout",
#             json={"access_token": "testtoken"},
#             headers={"Authorization": "Bearer testtoken"},
#         )

#         assert response.status_code == 200
#         response_json = response.json()
#         assert response_json["logout"] is True
