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
    sample_customer_create,
    sample_vendor_create,
)


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


@pytest.mark.asyncio
async def test_add_to_cart(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency,
):
    await create_customer(client, database_override_dependencies)
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_vendor_override_dependency,
    )

    rsp = await client.post("/cart/add", json=sample_add_to_cart())
    assert rsp.status_code == status.HTTP_201_CREATED
