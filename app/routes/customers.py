from fastapi import APIRouter

from app.db import database
from app.models.customer import Customer
from app.schemas.customers import CustomerModel

router = APIRouter(prefix="/api/v0/customers")


@router.get("/")
async def get_customers(page: int = 0, limit: int = 50):
    return {"results": await Customer.fetch(limit, page * limit), "count": await Customer.count()}


@router.get("/{category_id}")
async def get_customer(category_id: int):
    return await Customer.get_or_none(category_id)


@router.post("/")
async def create_customer(data: CustomerModel):
    customer = await database.fetch_one("SELECT * FROM customers "
                                        "WHERE first_name=:first_name AND last_name=:last_name AND email=:email "
                                        "AND phone_number=:phone_number;", data.customer_info.model_dump())
    if customer is None:
        customer = await database.fetch_one("INSERT INTO customers (first_name, last_name, email, phone_number) "
                                            "VALUES (:first_name, :last_name, :email, :phone_number)"
                                            "RETURNING customer_id, first_name, last_name, email, phone_number;",
                                            data.customer_info.model_dump())
    return Customer(**customer)


@router.patch("/{customer_id}")
async def update_customer(customer_id: int, data: CustomerModel):
    customer = await Customer.get_or_none(customer_id)
    customer_upd = customer.model_copy(update=data.model_dump())

    if customer == customer_upd:
        return customer

    query = ("UPDATE customers SET first_name=:first_name, last_name=:last_name, email=:email,"
             "phone_number=:phone_number WHERE customer_id=:id;")
    await database.execute(query, customer_upd.model_dump() | {"id": customer_id})

    return customer_upd


@router.delete("/{customer_id}", status_code=204)
async def delete_category(customer_id: int):
    await Customer.delete(customer_id)
