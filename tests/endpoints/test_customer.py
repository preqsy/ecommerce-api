from httpx import AsyncClient
import pytest
from fastapi import status

from tests.endpoints.test_auth import login_user
from tests.fixtures.auth_user_samples import (
    sample_auth_user_create_customer,
    sample_auth_user_create_vendor,
    sample_header,
)
from tests.fixtures.samples import (
    sample_customer_create,
)
from tests.mock_dependencies import mock_queue_connection


async def create_customer(
    client: AsyncClient,
    database_override_dependencies,
    sample_customer_create_details: dict = sample_customer_create(),
    sample_register_details: dict = sample_auth_user_create_customer(),
):

    login_rsp = await login_user(
        client, sample_register_details=sample_register_details
    )

    access_token = login_rsp.json()["access_token"]
    headers = sample_header()
    headers["authorization"] = "Bearer {}".format(access_token)

    rsp = await client.post(
        "/customer/", json=sample_customer_create_details, headers=headers
    )
    mock_queue_connection.enqueue_job.assert_called_once()

    return rsp


@pytest.mark.asyncio
async def test_customer_create_success(
    client,
    database_override_dependencies,
):
    rsp = await create_customer(client, database_override_dependencies)

    assert rsp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_customer_create_with_a_vendor_as_default_role(
    client,
    database_override_dependencies,
):
    register_details = sample_auth_user_create_vendor()
    register_details["email"] = "obbyprecious12@gmail.com"

    rsp = await create_customer(
        client,
        database_override_dependencies,
        sample_register_details=register_details,
    )

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["first_name", "last_name", "username"])
async def test_customer_create_short_names(
    client, database_override_dependencies, field
):

    sample_customer_create_dict = sample_customer_create()
    # Testing if the endpoint will allow first, last and username to be less than 2 cause it can't be less than 3 characters
    sample_customer_create_dict[field] = sample_customer_create_dict[field][0:2]

    rsp = await create_customer(
        client=client,
        database_override_dependencies=database_override_dependencies,
        sample_customer_create_details=sample_customer_create_dict,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("field", ["phone_number", "country", "address", "state"])
@pytest.mark.asyncio
async def test_customer_create_missing_details(
    client, database_override_dependencies, field
):
    # Testing if the endpoint will allow me to create a customer account without a phone number, country, address and state
    sample_customer_create_dict = sample_customer_create().pop(field)
    rsp = await create_customer(
        client=client,
        database_override_dependencies=database_override_dependencies,
        sample_customer_create_details=sample_customer_create_dict,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
