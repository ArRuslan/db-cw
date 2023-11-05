from fastapi import APIRouter, HTTPException

from app.db import database
from app.schemas.orders import OrderCreateModel


router = APIRouter(prefix="/api/v0/orders")


@router.post("/")
async def create_order(data: OrderCreateModel):
    customer_id = await database.fetch_one("SELECT customer_id FROM customers "
                                           "WHERE first_name=:first_name AND last_name=:last_name AND email=:email "
                                           "AND phone_numer=:phone_number;", data.customer_info.model_dump())
    if customer_id is None:
        customer_id = await database.fetch_one("INSERT INTO customers (first_name, last_name, email, phone_numer) "
                                               "VALUES (:first_name, :last_name, :email, :phone_number)"
                                               "RETURNING customer_id;", data.customer_info.model_dump())

    manager_id = await database.fetch_one("SELECT managers.manager_id FROM managers JOIN orders "
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
    result = await database.fetch_one("SELECT order_id, order_status AS status, order_creation_time AS creation_time,"
                                      "order_type AS type, customers.first_name, orders.customer_id,"
                                      "customers.last_name FROM orders "
                                      "JOIN customers ON orders.customer_id=customers.customer_id "
                                      "WHERE order_id=:order_id", {"order_id": order_id})
    resp = {
        "id": result["order_id"],
        "status": result["status"],
        "creation_time": result["creation_time"],
        "type": result["type"],
        "customer": {
            "id": result["customer_id"],
            "first_name": result["first_name"],
            "last_name": result["last_name"],
        },
        "items": [],
    }

    query = ("SELECT order_items.product_id AS id, order_items.price_per_item AS price, order_items.quantity,"
             "products.model, products.manufacturer, products.image_url, products.warranty_days "
             "FROM order_items JOIN products ON order_items.product_id=products.product_id WHERE order_id=:order_id;")
    for item in await database.fetch_all(query, {"order_id": order_id}):
        resp["items"].append(dict(item))

    return resp
