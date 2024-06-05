import pytest
from fastapi import status
from tests.endpoints.test_auth import register_user
from tests.fixtures.customer_samples import sample_customer_create
from tests.mock_dependencies import mock_crud_customer


@pytest.mark.asyncio
async def test_customer_create_success(
    client,
    database_override_dependencies,
    get_current_auth_user_override_dependency,
    get_crud_customer_override_dependency,
):

    await register_user(client)
    rsp = await client.post("/customer/", json=sample_customer_create())
    assert rsp.status_code == status.HTTP_201_CREATED
