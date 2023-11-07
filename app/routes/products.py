from fastapi import APIRouter

from app.db import database
from app.models.product import Product
from app.schemas.products import ProductCreateModel, ProductUpdateModel

router = APIRouter(prefix="/api/v0/products")


@router.get("/")
async def get_products(page: int=0, limit: int = 50):
    return {"results": await Product.fetch(limit, page * limit), "count": await Product.count()}


@router.get("/{product_id}")
async def get_product(product_id: int):
    return await Product.get_or_none(product_id)


#@router.get("/{product_id}/chars")
#async def get_product_characteristics(product_id: int):
#    ...


@router.post("/")
async def create_product(data: ProductCreateModel):
    query = ("INSERT INTO "
             "products (model, manufacturer, price, quantity, per_order_limit, image_url, warranty_days, category_id) "
             "VALUES (:model, :manufacturer, :price, :quantity, :per_order_limit, :image_url, :warranty_days, "
             ":category_id) "
             "RETURNING product_id, model, manufacturer, price, quantity, per_order_limit, image_url, warranty_days, "
             "category_id;")
    result = await database.fetch_one(query, data.model_dump())
    return Product(**result)


@router.patch("/{product_id}")
async def update_product(product_id: int, data: ProductUpdateModel):
    product = await database.fetch_one("SELECT * FROM products WHERE product_id=:id;", {"id": product_id})
    product = dict(product)
    changes = product.copy()
    changes |= data.model_dump(exclude_defaults=True)
    if product == changes:
        return product

    query = ("UPDATE products SET model=:model, manufacturer=:manufacturer, price=:price, quantity=:quantity,"
             "per_order_limit=:per_order_limit, image_url=:image_url, warranty_days=:warranty_days,"
             "category_id=:category_id WHERE product_id=:product_id;")
    await database.execute(query, changes)

    return await Product.get_or_none(product_id)


@router.delete("/{product_id}", status_code=204)
async def delete_category(product_id: int):
    await Product.delete(product_id)
