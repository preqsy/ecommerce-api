from typing import Dict, List, Union
from httpx import AsyncClient
import pytest
from fastapi import status

from tests.endpoints.test_auth import login_user
from tests.endpoints.test_customer import create_customer
from tests.endpoints.test_product import create_product
from tests.sample_datas.auth_user_samples import (
    sample_auth_user_create_customer,
    sample_auth_user_create_vendor,
    sample_header,
    sample_login_user_customer,
    sample_login_user_vendor,
)
from tests.sample_datas.samples import (
    sample_add_to_cart,
    sample_add_to_cart_invalid_id,
    sample_add_to_cart_overquantity,
    sample_checkout_data,
    sample_customer_create,
    sample_vendor_create,
)
from tests.mock_dependencies import mock_queue_connection


async def create_multiple_users(
    client: AsyncClient,
    database_override_dependencies,
    sample_role_create_details: Union[List, Dict] = [
        sample_customer_create(),
        sample_vendor_create(),
    ],
    sample_register_details: Union[List, Dict] = [
        sample_auth_user_create_customer(),
        sample_auth_user_create_vendor(),
    ],
    sample_login_details: Union[List, Dict] = [
        sample_login_user_customer(),
        sample_login_user_vendor(),
    ],
):

    login_rsp = await login_user(
        client,
        sample_register_details=sample_register_details,
        login_details=sample_login_details,
    )
    responses = []
    for num in range(len(login_rsp)):
        access_token = login_rsp[num]["access_token"]
        headers = sample_header()
        headers["authorization"] = "Bearer {}".format(access_token)

        if login_rsp[num]["default_role"] == "vendor":
            vendor_rsp = await client.post(
                "/vendor/", json=sample_role_create_details[num], headers=headers
            )
            assert vendor_rsp.status_code == status.HTTP_201_CREATED
            responses.append(vendor_rsp.json())
        else:
            customer_rsp = await client.post(
                "/customer/", json=sample_role_create_details[num], headers=headers
            )
            assert customer_rsp.status_code == status.HTTP_201_CREATED
            responses.append(customer_rsp.json())

    return responses


async def create_add_to_cart(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
    sample_add_to_cart_json: dict = sample_add_to_cart(),
):
    await create_customer(client, database_override_dependencies)
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.post("/cart/add", json=sample_add_to_cart_json)
    return rsp


@pytest.mark.asyncio
async def test_add_to_cart_success(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    rsp = await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    assert rsp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_add_to_cart_too_many_quantity(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    rsp = await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_add_to_cart_json=sample_add_to_cart_overquantity(),
    )
    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_add_to_cart_nonexistent_product_id(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    rsp = await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_add_to_cart_json=sample_add_to_cart_invalid_id(),
    )
    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_same_product_id_twice(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_customer(client, database_override_dependencies)
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    await client.post("/cart/add", json=sample_add_to_cart())
    second_rsp = await client.post("/cart/add", json=sample_add_to_cart())
    assert second_rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_cart_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.put("/cart/", json={"product_id": 1, "quantity": 10})

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_cart_nonexistent_product_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.put("/cart/", json={"product_id": 10, "quantity": 10})

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_cart_item_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.delete("/cart/1")

    assert rsp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_cart_item_nonexistent_product_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.delete("/cart/56")

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_clear_cart_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.delete("/cart/")

    assert rsp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_cart_summary_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_add_to_cart(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.get("/cart/summary")
    assert rsp.json()["total_items_quantity"]
    assert rsp.json()["total_amount"]
    assert rsp.json()["cart_items"]

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_cart_summary_no_cart_item(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    rsp = await client.get("/cart/summary")

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_checkout_success(
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

    print(rsp.json())
    assert rsp.status_code == status.HTTP_200_OK
