from fastapi import APIRouter

from app.models.category import Category
from app.models.product import Product
from app.schemas.categories import CategoryCreateModel, CategoryUpdateModel

router = APIRouter(prefix="/api/v0/categories")


@router.get("/")
async def get_categories(page: int=0, limit: int = 50):
    return {"results": await Category.all().limit(limit).offset(page * limit), "count": await Category.all().count()}


@router.get("/{category_id}")
async def get_category(category_id: int):
    return await Category.get_or_none(id=category_id)


@router.get("/{category_id}/products")
async def get_category_products(category_id: int, page: int=0, limit: int = 50):
    return await Product.filter(category__id=category_id).limit(limit).offset(page * limit)


@router.post("/")
async def create_category(data: CategoryCreateModel):
    return await Category.create(name=data.name, description=data.description)


@router.patch("/{category_id}")
async def update_category(category_id: int, data: CategoryUpdateModel):
    cat = await Category.get_or_none(id=category_id)
    await cat.update(**data.model_dump(exclude_defaults=True))

    return cat


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int):
    await Category.filter(id=category_id).delete()
