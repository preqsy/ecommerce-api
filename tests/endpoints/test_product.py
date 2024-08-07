import random
from httpx import AsyncClient
import pytest
from fastapi import status

from schemas.product import ProductReturn
from tests.conftest import get_current_verified_role_override_dependency
from tests.endpoints.test_vendor import create_vendor
from tests.sample_datas.samples import (
    sample_product_create,
    sample_product_create_second,
    sample_product_create_third,
    sample_product_image_update,
    sample_product_review_create,
    sample_product_review_create_invalid_rating,
    sample_product_review_create_nonexistent_product_id,
    sample_product_review_update,
    sample_product_update,
)


async def create_product(
    client: AsyncClient,
    database_override_dependencies,
    get_current_verified_vendor_override_dependency=get_current_verified_role_override_dependency,
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
    get_current_verified_role_override_dependency,
):
    rsp = await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    assert rsp.status_code == status.HTTP_201_CREATED
    ProductReturn(**rsp.json())


@pytest.mark.parametrize(
    "field",
    [
        "product_name",
        "product_images",
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
    get_current_verified_role_override_dependency,
    field,
):
    sample_product_create_json = sample_product_create()
    del sample_product_create_json[field]
    rsp = await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json,
    )
    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_products_and_pagination_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    products = [sample_product_create() for _ in range(random.randint(1, 100))]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products")

    assert rsp.status_code == status.HTTP_200_OK
    print(len(rsp.json()))


@pytest.mark.asyncio
async def test_get_products_search(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    products = [
        sample_product_create(),
        sample_product_create_second(),
        sample_product_create_third(),
    ]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products?search=iphone")

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_products_search_no_product(
    client,
    database_override_dependencies,
):

    rsp = await client.get("/products")

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_vendor_products(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    # TODO: Improve this
    products = [sample_product_create() for _ in range(random.randint(1, 100))]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products/me")

    assert rsp.status_code == status.HTTP_200_OK
    print(len(rsp.json()))


@pytest.mark.asyncio
async def test_get_products_sorted_by_price(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    products = [
        sample_product_create(),
        sample_product_create_second(),
        sample_product_create_third(),
    ]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products/price")

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_products_by_id_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    products = [
        sample_product_create(),
        sample_product_create_second(),
        sample_product_create_third(),
    ]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products/1")

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_products_by_invalid_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    products = [
        sample_product_create(),
        sample_product_create_second(),
        sample_product_create_third(),
    ]
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
        sample_product_create_json=products,
    )
    rsp = await client.get("/products/5")

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_product_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.put("/products/1", json=sample_product_update())

    assert rsp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_product_invalid_product_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.put("/products/5", json=sample_product_update())

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_product_image_invalid_product_image_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.put("/products/image/5", json=sample_product_image_update())

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_product_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.delete("/products/1")

    assert rsp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_product_invalid_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):

    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.delete("/products/10")

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_product_review_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    rsp = await client.post(
        "/products/add-review",
        json=sample_product_review_create(),
    )

    assert rsp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_update_product_review_success(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    await client.post(
        "/products/add-review",
        json=sample_product_review_create(),
    )
    rsp = await client.put(
        "/products/edit-review/1",
        json=sample_product_review_update(),
    )

    assert rsp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_update_product_review_nonexistent_review_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )
    await client.post(
        "/products/add-review",
        json=sample_product_review_create(),
    )
    rsp = await client.put(
        "/products/edit-review/10",
        json=sample_product_review_update(),
    )

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_product_review_nonexistent_product_id(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.post(
        "/products/add-review",
        json=sample_product_review_create_nonexistent_product_id(),
    )

    assert rsp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_product_review_invalid_rating(
    client,
    database_override_dependencies,
    get_current_verified_role_override_dependency,
):
    await create_product(
        client,
        database_override_dependencies,
        get_current_verified_role_override_dependency,
    )

    rsp = await client.post(
        "/products/add-review",
        json=sample_product_review_create_invalid_rating(),
    )

    assert rsp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
