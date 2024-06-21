from httpx import AsyncClient
import pytest
from fastapi import status

from schemas.product import ProductReturn
from tests.endpoints.test_vendor import create_vendor
from tests.fixtures.customer_samples import (
    sample_product_create,
    sample_product_create_second,
    sample_product_create_third,
)


async def create_product(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency,
    sample_product_create_json: list = [sample_product_create()],
):
    await create_vendor(client, database_override_dependencies)
    for products in sample_product_create_json:
        rsp = await client.post("/products", json=products)

    return rsp


@pytest.mark.asyncio
async def test_create_product(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency,
):
    rsp = await create_product(
        client,
        database_override_dependencies,
        get_current_verified_vendor_override_dependency,
    )

    assert rsp.status_code == status.HTTP_201_CREATED
    ProductReturn(**rsp.json())


@pytest.mark.parametrize(
    "field",
    [
        "product_name",
        "product_image",
        "category",
        "short_description",
        "long_description",
        "stock",
        "price",
    ],
)
@pytest.mark.asyncio
async def test_create_product_missing_important_fields(
    client,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency,
    field,
):
    sample_product_create_json = sample_product_create()
    del sample_product_create_json[field]
    rsp = await create_product(
        client,
        database_override_dependencies,
        get_current_verified_vendor_override_dependency,
        sample_product_create_json,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_products_and_pagination_success(
    client,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency,
):
    products = [sample_product_create() for _ in range(20)]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_vendor_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products")

    assert rsp.status_code == status.HTTP_200_OK


# @pytest.mark.asyncio
# async def test_get_products_search(
#     client,
#     database_override_dependencies,
#     get_current_verified_vendor_override_dependency,
# ):
#     products = [
#         sample_product_create(),
#         sample_product_create_second(),
#         sample_product_create_third(),
#     ]
#     await create_product(
#         client,
#         database_override_dependencies,
#         get_current_verified_vendor_override_dependency,
#         sample_product_create_json=products,
#     )
#     rsp = await client.get("/products?search=Iphone")

#     assert rsp.status_code == status.HTTP_200_OK
