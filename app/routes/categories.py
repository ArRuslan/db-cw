from fastapi import APIRouter

from app.db import database
from app.schemas.categories import CategoryCreateModel, CategoryUpdateModel

router = APIRouter(prefix="/api/v0/categories")


@router.get("/")
async def get_categories(page: int=0, limit: int = 50):
    return await database.fetch_all("SELECT * FROM categories LIMIT :limit OFFSET :offset", {
        "limit": limit, "offset": page * limit
    })


@router.get("/{category_id}")
async def get_category(category_id: int):
    return await database.fetch_one("SELECT * FROM categories WHERE category_id=:id;", {"id": category_id})


@router.get("/{category_id}/products")
async def get_category_products(category_id: int, page: int=0, limit: int = 50):
    return await database.fetch_all("SELECT * FROM products WHERE category_id=:cat LIMIT :limit OFFSET :offset", {
        "cat": category_id, "limit": limit, "offset": page * limit
    })


@router.post("/")
async def create_category(data: CategoryCreateModel):
    query = ("INSERT INTO categories (name, description) VALUES (:name, :description) "
             "RETURNING category_id, name, description;")
    return await database.fetch_one(query, {
        "name": data.name, "description": data.description
    })


@router.patch("/{category_id}")
async def update_category(category_id: int, data: CategoryUpdateModel):
    category = await database.fetch_one("SELECT * FROM categories WHERE category_id=:id;", {"id": category_id})
    if (not data.name and not data.description) or \
            (data.name == category["name"] and data.description == category["description"]):
        return category

    query = "UPDATE categories SET name=:name, description=:description WHERE category_id=:id;"
    await database.execute(query, {
        "id": category_id,
        "name": data.name if data.name else category["name"],
        "description": data.description if data.description else category["description"]
    })
    return await database.fetch_one("SELECT * FROM categories WHERE category_id=:id;", {"id": category_id})


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int):
    await database.execute("DELETE FROM categories WHERE category_id=:id;", {"id": category_id})
