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
        "SELECT COUNT(DISTINCT order.id) AS order_count, COUNT(return.id) AS return_count,"
        "COUNT(DISTINCT orderitem.product_id) AS ordered_product_count, SUM(orderitem.quantity) AS ordered_item_count, "
        "SUM(`return`.quantity) AS returned_items_count, SUM(DISTINCT O_SUMS.S) AS total_money,"
        "AVG(O_SUMS.S) AS avg_money "
        "FROM customer "
        "LEFT JOIN `order` ON customer.id=`order`.customer_id "
        "LEFT JOIN `return` ON `order`.id=`return`.order_id "
        "LEFT JOIN orderitem ON `order`.id=orderitem.order_id "
        "LEFT JOIN ("
        "   SELECT SUM(orderitem.price*orderitem.quantity) AS S, customer.id as cus_id FROM orderitem AS orderitem "
        "   INNER JOIN `order` ON orderitem.order_id=`order`.id INNER JOIN customer ON customer.id=`order`.customer_id "
        "   GROUP BY orderitem.order_id"
        ") O_SUMS ON O_SUMS.cus_id=customer.id "
        "WHERE customer.id=%s;"
    )
    return await conn.execute_query_dict(query, [customer_id])


@router.get("/categories/{category_id}")
async def categories_statistics(manager: AuthManagerDep, category_id: int):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT COUNT(order.id) AS order_count, COUNT(return.id) AS return_count, "
        "SUM(orderitem.quantity) AS ordered_item_count, SUM(`return`.quantity) AS returned_items_count,"
        "SUM(orderitem.price * orderitem.quantity) AS total_money "
        "FROM category "
        "LEFT JOIN product ON product.category_id=category.id "
        "LEFT JOIN orderitem ON product.id=orderitem.product_id "
        "LEFT JOIN `order` ON orderitem.order_id=`order`.id "
        "LEFT JOIN `return` ON `order`.id=`return`.order_id "
        "WHERE category.id=%s;"
    )
    return await conn.execute_query_dict(query, [category_id])


@router.get("/customers-top")
async def customers_top(manager: AuthManagerDep, count: int = 100):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT customer.id, customer.first_name, customer.last_name, customer.email, customer.phone_number, "
        "COUNT(orderitem.id) AS order_items, SUM(orderitem.price * orderitem.quantity) AS money_spent "
        "FROM customer "
        "INNER JOIN `order` ON customer.id = `order`.customer_id "
        "INNER JOIN orderitem on `order`.id = orderitem.order_id "
        "WHERE `order`.creation_time > `order`.creation_time - INTERVAL 1 YEAR "
        "ORDER BY COUNT(orderitem.id), SUM(orderitem.price*orderitem.quantity) LIMIT %s;"
    )
    return await conn.execute_query_dict(query, [count])


@router.get("/time/year")
async def last_year_statistics(manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT MONTH(`order`.creation_time) as month, COUNT(order.id) AS order_count, "
        "SUM(orderitem.price*orderitem.quantity) AS total_money "
        "FROM `order` "
        "INNER JOIN orderitem ON `order`.id=orderitem.order_id "
        "WHERE `order`.creation_time > `order`.creation_time - INTERVAL 1 YEAR "
        "GROUP BY month ORDER BY month;"
    )
    return await conn.execute_query_dict(query)


@router.get("/time/month")
async def last_year_statistics(manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.READ_STATISTICS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    query = (
        "SELECT DAY(`order`.creation_time) as day, COUNT(order.id) AS order_count, "
        "SUM(orderitem.price*orderitem.quantity) AS total_money "
        "FROM `order` "
        "INNER JOIN orderitem ON `order`.id=orderitem.order_id "
        "WHERE `order`.creation_time > `order`.creation_time - INTERVAL 1 MONTH "
        "GROUP BY day ORDER BY day;"
    )
    return await conn.execute_query_dict(query)
