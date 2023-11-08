from fastapi import APIRouter

from app.db import database
from app.models.customer import Customer
from app.schemas.customers import CustomerModel

router = APIRouter(prefix="/api/v0/customers")


@router.get("/")
async def get_customers(page: int = 0, limit: int = 50):
    return {"results": await Customer.all().limit(limit).offset(page * limit), "count": await Customer.all().count()}


@router.get("/{category_id}")
async def get_customer(category_id: int):
    return await Customer.get_or_none(id=category_id)


@router.post("/")
async def create_customer(data: CustomerModel):
    if (customer := await Customer.get_or_none(**data.model_dump())) is not None:
        return customer
    return await Customer.create(**data.model_dump())


@router.patch("/{customer_id}")
async def update_customer(customer_id: int, data: CustomerModel):
    customer = await Customer.get_or_none(id=customer_id)
    await customer.update(**data.model_dump())
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_category(customer_id: int):
    await Customer.filter(id=customer_id).delete()
