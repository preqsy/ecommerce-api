from httpx import AsyncClient
import pytest
from fastapi import status

from tests.endpoints.test_cart import create_add_to_cart
from tests.sample_datas.samples import sample_checkout_data
from tests.mock_dependencies import mock_queue_connection


@pytest.mark.asyncio
async def create_order(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.post("/cart/checkout", json=sample_checkout_data())
    mock_queue_connection.enqueue_job.assert_called()

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_orders(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_order(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.get("/order/")
    print(rsp.json())
    assert rsp.status_code == status.HTTP_200_OK
