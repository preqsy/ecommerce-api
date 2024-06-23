from httpx import AsyncClient
import pytest

from core.db import get_db
from core.tokens import get_current_auth_user, get_current_verified_vendor
from crud import get_crud_auth_user, get_crud_customer, get_crud_product_image
from main import app
from task_queue.main import get_queue_connection
from tests.fixtures.auth_user_samples import sample_auth_user_query_result_first
from tests.fixtures.samples import sample_get_verified_vendor
from tests.fixtures.testdb import engine, mock_get_db
from models import auth_user, product, cart as cartmodel, AuthUser
from .mock_dependencies import (
    mock_crud_auth_user,
    mock_crud_customer,
    mock_queue_connection,
    mock_crud_product_image,
)


@pytest.fixture
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
    app.dependency_overrides[get_queue_connection] = lambda: mock_queue_connection
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

    auth_user = AuthUser(**sample_auth_user_query_result_first())
    app.dependency_overrides[get_current_auth_user] = lambda: auth_user
    yield auth_user
    app.dependency_overrides = {}


@pytest.fixture
def get_current_verified_vendor_override_dependency():

    auth_user = AuthUser(**sample_get_verified_vendor())
    app.dependency_overrides[get_current_verified_vendor] = lambda: auth_user
    yield auth_user
    app.dependency_overrides = {}


@pytest.fixture
def get_crud_product_image_override_dependency():
    app.dependency_overrides[get_crud_product_image] = lambda: mock_crud_product_image
    yield
    app.dependency_overrides = {}
