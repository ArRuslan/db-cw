from fastapi import APIRouter, HTTPException
from tortoise import connections
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


@router.get("/price-recommendations")
async def price_recommendations(manager: AuthManagerDep, interval: int = 2):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT product.id, product.price, DAYOFYEAR(`order`.creation_time) AS day, COUNT(orderitem.id) AS items,"
        "SUM(`return`.quantity) AS returns "
        "FROM product "
        "INNER JOIN orderitem ON product.id = orderitem.product_id "
        "INNER JOIN `order` ON orderitem.order_id = `order`.id "
        "LEFT JOIN `return` ON orderitem.id = `return`.id "
        "WHERE `order`.creation_time > `order`.creation_time - INTERVAL %s WEEK "
        "GROUP BY product.id, product.price, day;"
    )

    products = {}
    for res in await conn.execute_query_dict(query, [interval]):
        if res["id"] not in products:
            products[res["id"]] = []
        products[res["id"]].append({"price": res["price"], "day": res["day"], "count": res["items"]})

    total_analyzed = len(products)

    ignored = []
    for product_id in products:
        if len(products[product_id]) < 3:
            ignored.append(product_id)
            continue

        products[product_id].sort(key=lambda prod: prod["day"])

    ignored_count = len(ignored)
    for ig in ignored:
        del products[ig]

    ignored = []
    for product_id in products:
        count = products[product_id][0]["count"]
        changed = False
        for day in products[product_id][1:]:
            if day["count"] != count:
                changed = True
                break
        if not changed:
            ignored.append(product_id)

    ignored_count += len(ignored)
    for ig in ignored:
        del products[ig]

    for product_id in products:
        average = sum([day["count"] for day in products[product_id]]) / len(products[product_id])
        for day in products[product_id]:
            day["delta"] = day["count"] - average

    raw_result = {}
    for product_id in products:
        deltas = sum([day["delta"] for day in products[product_id][:-1]])

        price = products[product_id][0]["price"]
        res = {"price": price}
        if deltas > products[product_id][-1]["delta"]:
            raw_result[product_id] = res | {"action": "down", "recommended_price": round(price * 0.975, 2)}
        else:
            raw_result[product_id] = res | {"action": "up", "recommended_price": round(price * 1.025, 2)}

    result = []
    for prod in await Product.filter(id__in=list(raw_result.keys())).all():
        result.append({
            "id": prod.id,
            "model": prod.model,
            "manufacturer": prod.manufacturer,
            **raw_result[prod.id],
        })

    return {"total_analyzed": total_analyzed, "ignored": ignored_count, "raw_result": raw_result, "result": result}


@router.get("/{product_id}")
async def get_product(product_id: int):
    return await Product.get_or_none(id=product_id)


@router.get("/{product_id}/chars")
async def get_product_characteristics(product_id: int):
    if (product := await Product.get_or_none(id=product_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown product!")

    resp = []
    for char in await product.characteristics.all().select_related("productcharacteristics"):
        resp.append({
            "id": char.id,
            "name": char.name,
            "value": char.productcharacteristics.value,
            "unit": char.measurement_unit
        })

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
    return {"id": char.id, "name": char.name, "value": data.value, "unit": char.measurement_unit}


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
