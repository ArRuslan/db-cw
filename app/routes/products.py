from fastapi import APIRouter, HTTPException
from tortoise.expressions import Q

from app.models import Characteristic, ProductCharacteristic
from app.models.product import Product
from app.schemas import SearchData
from app.schemas.products import ProductCreateModel, ProductUpdateModel, PutCharacteristic
from app.utils import AuthManagerDep, Permissions, search

router = APIRouter(prefix="/api/v0/products")


@router.get("/")
async def get_products(page: int=0, limit: int = 50):
    return {"results": await Product.all().limit(limit).offset(page * limit), "count": await Product.all().count()}


@router.post("/search")
async def search_products_post(data: SearchData):
    query, countQuery = search(Product, data)
    return {"results": await query, "count": await countQuery.count()}


@router.get("/search")
async def search_products(page: int=0, anything: str=""):
    q = Product.all().filter(Q(model__contains=anything) | Q(manufacturer__istartswith=anything))
    return {"results": await q.limit(50).offset(page * 50), "count": await q.count()}


@router.get("/{product_id}")
async def get_product(product_id: int):
    return await Product.get_or_none(id=product_id)


@router.get("/{product_id}/chars")
async def get_product_characteristics(product_id: int):
    if (product := await Product.get_or_none(id=product_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown product!")

    resp = {}
    for char in await product.characteristics.all().select_related("productcharacteristics"):
        resp[char.name] = {"id": char.id, "value": char.productcharacteristics.value, "unit": char.measurement_unit}

    return resp


@router.put("/{product_id}/chars/{char_id}")
async def set_product_characteristic(product_id: int, char_id: int, data: PutCharacteristic, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (product := await Product.get_or_none(id=product_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown product!")
    if (char := await Characteristic.get_or_none(id=char_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown characteristic!")

    await ProductCharacteristic.update_or_create({"value": data.value}, product=product, characteristic=char)
    return {"id": char.id, "value": data.value, "unit": char.measurement_unit}


@router.delete("/{product_id}/chars/{char_id}", status_code=204)
async def delete_product_characteristic(product_id: int, char_id: int, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (product := await Product.get_or_none(id=product_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown product!")
    if (char := await Characteristic.get_or_none(id=char_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown characteristic!")

    await ProductCharacteristic.filter(product=product, characteristic=char).delete()


@router.post("/")
async def create_product(data: ProductCreateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    return await Product.create(**data.model_dump())


@router.patch("/{product_id}")
async def update_product(product_id: int, data: ProductUpdateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (product := await Product.get_or_none(id=product_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown product!")

    await product.update(**data.model_dump(exclude_defaults=True))
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    await Product.filter(id=product_id).delete()
