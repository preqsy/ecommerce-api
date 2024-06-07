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
    # get_crud_auth_user_override_dependency,
):
    # mock_crud_auth_user.get_by_id.return_value = MagicMock(id=1)

    await register_user(client)
    with patch("endpoints.customer.BackgroundTasks") as mock_background_tasks:
        mock_instance = mock_background_tasks.return_value
        rsp = await client.post("/customer/", json=sample_customer_create())

        mock_instance.add_task.assert_any_call()
        assert rsp.status_code == status.HTTP_201_CREATED
