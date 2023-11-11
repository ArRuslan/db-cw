from fastapi import APIRouter, HTTPException
from tortoise.expressions import Q

from app.models.category import Category
from app.models.product import Product
from app.schemas.categories import CategoryCreateModel, CategoryUpdateModel, CategoriesBatchLoadModel
from app.utils import Permissions, AuthManagerDep

router = APIRouter(prefix="/api/v0/categories")


@router.get("/")
async def get_categories(page: int=0, limit: int = 50):
    if limit == 0:
        limit = await Category.all().count()
    return {"results": await Category.all().limit(limit).offset(page * limit), "count": await Category.all().count()}


@router.get("/search")
async def search_categories(page: int=0, name: str="", description: str=""):
    q = Category.all().filter(Q(name__istartswith=name) | Q(description__istartswith=description))
    return {"results": await q.limit(50).offset(page * 50), "count": await q.count()}


@router.get("/{category_id}")
async def get_category(category_id: int):
    return await Category.get_or_none(id=category_id)


@router.post("/batch")
async def get_categories_by_ids(data: CategoriesBatchLoadModel):
    return await Category.filter(id__in=data.ids).all()


@router.get("/{category_id}/products")
async def get_category_products(category_id: int, page: int=0, limit: int = 50):
    return await Product.filter(category__id=category_id).limit(limit).offset(page * limit)


@router.post("/")
async def create_category(data: CategoryCreateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CATEGORIES):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    return await Category.create(name=data.name, description=data.description)


@router.patch("/{category_id}")
async def update_category(category_id: int, data: CategoryUpdateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CATEGORIES):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    cat = await Category.get_or_none(id=category_id)
    await cat.update(**data.model_dump(exclude_defaults=True))
    return cat


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CATEGORIES):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    await Category.filter(id=category_id).delete()
