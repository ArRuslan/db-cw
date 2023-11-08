from fastapi import APIRouter

from app.db import database
from app.models.product import Product
from app.schemas.products import ProductCreateModel, ProductUpdateModel

router = APIRouter(prefix="/api/v0/products")


@router.get("/")
async def get_products(page: int=0, limit: int = 50):
    return {"results": await Product.all().limit(limit).offset(page * limit), "count": await Product.all().count()}


@router.get("/{product_id}")
async def get_product(product_id: int):
    return await Product.get_or_none(id=product_id)


#@router.get("/{product_id}/chars")
#async def get_product_characteristics(product_id: int):
#    ...


@router.post("/")
async def create_product(data: ProductCreateModel):
    return await Product.create(**data.model_dump())


@router.patch("/{product_id}")
async def update_product(product_id: int, data: ProductUpdateModel):
    product = await Product.get_or_none(id=product_id)
    await product.update(**data.model_dump(exclude_defaults=True))
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_category(product_id: int):
    await Product.filter(id=product_id).delete()
