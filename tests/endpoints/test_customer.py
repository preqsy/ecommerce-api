from unittest.mock import MagicMock, patch
from httpx import AsyncClient
import pytest
from fastapi import status

from tests.fixtures.auth_user_samples import sample_auth_user_create
from tests.fixtures.customer_samples import sample_customer_create
from tests.mock_dependencies import mock_crud_auth_user


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


@pytest.mark.asyncio
async def test_customer_create_success(
    client,
    database_override_dependencies,
    get_current_auth_user_override_dependency,
):

    await register_user(client)

    rsp = await client.post("/customer/", json=sample_customer_create())

    assert rsp.status_code == status.HTTP_201_CREATED
