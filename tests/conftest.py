from httpx import AsyncClient
import pytest

from core.db import get_db
from core.tokens import get_current_auth_user
from crud.auth import get_crud_auth_user
from crud.customer import get_crud_customer
from main import app
from tests.fixtures.auth_user_samples import sample_auth_user_query_result_first
from tests.fixtures.testdb import engine, mock_get_db
from models import auth_user, product, cart as cartmodel, AuthUser
from .mock_dependencies import mock_crud_auth_user, mock_crud_customer


@pytest.fixture
# @pytest.fixture(scope="module")
def client():
    # Drop Tables
    auth_user.Base.metadata.drop_all(bind=engine)
    product.Base.metadata.drop_all(bind=engine)
    cartmodel.Base.metadata.drop_all(bind=engine)
    # Creat tables
    auth_user.Base.metadata.create_all(bind=engine)
    product.Base.metadata.create_all(bind=engine)
    cartmodel.Base.metadata.create_all(bind=engine)
    client = AsyncClient(app=app, base_url="https://127.0.0.1/")
    yield client


@pytest.fixture
def database_override_dependencies():
    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides = {}


@pytest.fixture
def get_crud_auth_user_override_dependency():
    app.dependency_overrides[get_crud_auth_user] = lambda: mock_crud_auth_user
    yield
    app.dependency_overrides = {}


@pytest.fixture
def get_crud_customer_override_dependency():
    app.dependency_overrides[get_crud_customer] = lambda: mock_crud_customer
    yield
    app.dependency_overrides = {}


@pytest.fixture
def get_current_auth_user_override_dependency():
    app.dependency_overrides[get_current_auth_user] = lambda: AuthUser(
        **sample_auth_user_query_result_first()
    )
    yield
    app.dependency_overrides = {}
