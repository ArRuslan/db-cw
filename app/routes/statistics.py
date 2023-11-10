from fastapi import APIRouter, HTTPException
from tortoise import connections

from app.models import Characteristic, ProductCharacteristic
from app.models.product import Product
from app.schemas.products import ProductCreateModel, ProductUpdateModel, PutCharacteristic
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/statistics")


@router.get("/customers/{customer_id}")
async def customer_statistics(manager: AuthManagerDep, customer_id: int):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT COUNT(order.id) AS order_count, COUNT(return.id) AS return_count,"
        "COUNT(DISTINCT orderitem.product_id) AS ordered_product_count, SUM(orderitem.quantity) AS ordered_item_count, "
        "SUM(`return`.quantity) AS returned_items_count, SUM(orderitem.price) AS total_money,"
        "AVG(O_SUMS.S) AS avg_money "
        "FROM customer "
        "INNER JOIN `order` ON customer.id=`order`.customer_id "
        "INNER JOIN `return` ON `order`.id=`return`.order_id "
        "INNER JOIN orderitem ON `order`.id=orderitem.order_id "
        "INNER JOIN ("
        "   SELECT SUM(orderitem.price) AS S, customer.id as cus_id FROM orderitem AS orderitem "
        "   INNER JOIN `order` ON orderitem.order_id=`order`.id INNER JOIN customer ON customer.id=`order`.customer_id "
        "   GROUP BY orderitem.order_id"
        ") O_SUMS ON O_SUMS.cus_id=customer.id "
        "WHERE customer.id=?;"
    )
    return await conn.execute_query_dict(query, [customer_id])


@router.get("/customers/{category_id}")
async def categories_statistics(manager: AuthManagerDep, category_id: int):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT COUNT(order.id) AS order_count, COUNT(return.id) AS return_count, "
        "SUM(orderitem.quantity) AS ordered_item_count, SUM(`return`.quantity) AS returned_items_count,"
        "SUM(orderitem.price) AS total_money "
        "FROM category "
        "INNER JOIN product ON product.category_id=category.id "
        "INNER JOIN orderitem ON product.id=orderitem.product_id "
        "INNER JOIN `order` ON orderitem.order_id=`order`.id "
        "INNER JOIN `return` ON `order`.id=`return`.order_id "
        "WHERE category.id=?;"
    )
    return await conn.execute_query_dict(query, [category_id])


#@router.get("/time/year")
#async def last_year_statistics(manager: AuthManagerDep, category_id: int):
#    if not Permissions.check(manager, Permissions.READ_STATISTICS):
#        raise HTTPException(status_code=403, detail="Insufficient privileges!")
#
#    conn = connections.get("default")
#    query = (
#        "SELECT COUNT(order.id) AS order_count, COUNT(return.id) AS return_count, "
#        "SUM(orderitem.quantity) AS ordered_item_count, SUM(`return`.quantity) AS returned_items_count,"
#        "SUM(orderitem.price) AS total_money "
#        "FROM category "
#        "INNER JOIN product ON product.category_id=category.id "
#        "INNER JOIN orderitem ON product.id=orderitem.product_id "
#        "INNER JOIN `order` ON orderitem.order_id=`order`.id "
#        "INNER JOIN `return` ON `order`.id=`return`.order_id "
#        "WHERE category.id=?;"
#    )
#    return await conn.execute_query_dict(query, [category_id])
