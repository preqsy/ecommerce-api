from httpx import AsyncClient
import pytest
from fastapi import status

from tests.endpoints.test_auth import login_user
from tests.fixtures.auth_user_samples import (
    sample_auth_user_create_customer,
    sample_auth_user_create_vendor,
    sample_header,
    sample_login_user_vendor,
)
from tests.fixtures.samples import (
    sample_vendor_create,
)


async def create_vendor(
    client: AsyncClient,
    database_override_dependencies,
    sample_vendor_create_details: dict = sample_vendor_create(),
    sample_register_details: dict = sample_auth_user_create_vendor(),
):

    login_rsp = await login_user(
        client,
        sample_register_details=sample_register_details,
        login_details=sample_login_user_vendor(),
    )

    access_token = login_rsp.json()["access_token"]
    headers = sample_header()
    headers["authorization"] = "Bearer {}".format(access_token)

    rsp = await client.post(
        "/vendor/", json=sample_vendor_create_details, headers=headers
    )

    return rsp


@pytest.mark.asyncio
async def test_vendor_create_success(
    client,
    database_override_dependencies,
):
    rsp = await create_vendor(client, database_override_dependencies)

    assert rsp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_vendor_create_with_a_cusomer_as_default_role(
    client,
    database_override_dependencies,
):
    register_details = sample_auth_user_create_customer()
    register_details["email"] = "obbyprecious10@gmail.com"
    rsp = await create_vendor(
        client,
        database_override_dependencies,
        sample_register_details=register_details,
    )

    assert rsp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["first_name", "last_name", "username"])
async def test_vendor_create_short_names(client, database_override_dependencies, field):

    sample_vendor_create_dict = sample_vendor_create()
    # Testing if the endpoint will allow first, last and username to be less than 2 cause it can't be less than 3 characters
    sample_vendor_create_dict[field] = sample_vendor_create_dict[field][0:2]

    rsp = await create_vendor(
        client=client,
        database_override_dependencies=database_override_dependencies,
        sample_vendor_create_details=sample_vendor_create_dict,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "field", ["phone_number", "country", "address", "state", "bio"]
)
@pytest.mark.asyncio
async def test_vendor_create_missing_details(
    client, database_override_dependencies, field
):
    # Testing if the endpoint will allow me to create a vendor account without a phone number, country, address, bio and state
    sample_vendor_create_dict = sample_vendor_create().pop(field)
    rsp = await create_vendor(
        client=client,
        database_override_dependencies=database_override_dependencies,
        sample_vendor_create_details=sample_vendor_create_dict,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
