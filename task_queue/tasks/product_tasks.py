from crud import CRUDProductImage
from schemas.product import ProductImageCreate


async def save_product_images(ctx, product_id: int, product_images: ProductImageCreate):
    crud_product_image: CRUDProductImage = ctx["crud_product_image"]
    for image in product_images:
        product_img_obj = ProductImageCreate(
            product_id=product_id, product_image=str(image)
        )
        await crud_product_image.create(product_img_obj)
    return
