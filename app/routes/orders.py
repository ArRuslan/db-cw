from fastapi import APIRouter, HTTPException

from app.db import database
from app.models.order import Order
from app.schemas.orders import OrderCreateModel, OrderUpdateModel

router = APIRouter(prefix="/api/v0/orders")


@router.get("/")
async def get_orders(page: int=0, limit: int = 50):
    return {"results": await Order.fetch_full(limit, page * limit), "count": await Order.count()}


@router.post("/")
async def create_order(data: OrderCreateModel):
    customer_id = await database.fetch_one("SELECT customer_id FROM customers "
                                           "WHERE first_name=:first_name AND last_name=:last_name AND email=:email "
                                           "AND phone_number=:phone_number;", data.customer_info.model_dump())
    if customer_id is None:
        customer_id = await database.fetch_one("INSERT INTO customers (first_name, last_name, email, phone_number) "
                                               "VALUES (:first_name, :last_name, :email, :phone_number)"
                                               "RETURNING customer_id;", data.customer_info.model_dump())

    manager_id = await database.fetch_one("SELECT managers.manager_id FROM managers LEFT JOIN orders "
                                          "ON managers.manager_id = orders.manager_id ORDER BY COUNT(orders.order_id)"
                                          "LIMIT 1;")
    if manager_id is None:
        raise HTTPException(status_code=400, detail="No managers found to process this order!")
    else:
        manager_id = manager_id[0]

    query = ("INSERT INTO orders (address, order_type, customer_id, manager_id) "
             "VALUES (:address, :type, :customer_id, :manager_id) RETURNING order_id;")
    order_id = await database.fetch_one(query, {"address": data.address, "type": data.type, "manager_id": manager_id,
                                                "customer_id": customer_id[0]})

    products = []
    ids = ','.join([str(prod.id) for prod in data.products])
    prods = {prod.id: prod for prod in data.products}
    for row in await database.fetch_all(f"SELECT product_id, price FROM products WHERE product_id IN ({ids})"):
        products.append({"order_id": order_id["order_id"], "product_id": row["product_id"],
                         "quantity": prods[row["product_id"]].quantity, "price": row["price"]})

    await database.execute_many("INSERT INTO order_items (order_id, product_id, quantity, price_per_item)"
                                "VALUES (:order_id, :product_id, :quantity, :price);", products)

    return await get_order(order_id["order_id"])


@router.get("/{order_id}")
async def get_order(order_id: int):
    return await Order.get_full(order_id)


@router.patch("/{order_id}")
async def create_order(order_id: int, data: OrderUpdateModel):
    order = await Order.get_or_none(order_id)
    d = {"status": order.status, "address": order.address, "type": order.type} | data.model_dump(exclude_defaults=True)

    await database.execute("UPDATE orders SET order_status=:status, address=:address, order_type=:type "
                           "WHERE order_id=:id", d | {"id": order_id})

    return await get_order(order_id)
