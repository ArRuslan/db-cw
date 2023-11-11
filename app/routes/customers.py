from fastapi import APIRouter, HTTPException
from tortoise.expressions import Q

from app.models.customer import Customer
from app.schemas.customers import CustomerModel
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/customers")


@router.get("/")
async def get_customers(manager: AuthManagerDep, page: int = 0, limit: int = 50):
    return {"results": await Customer.all().limit(limit).offset(page * limit), "count": await Customer.all().count()}


@router.get("/search")
async def search_customers(page: int=0, anything: str=""):
    q = Customer.all().filter(Q(first_name__istartswith=anything) | Q(first_name__istartswith=anything) |
                              Q(email__istartswith=anything))
    return {"results": await q.limit(50).offset(page * 50), "count": await q.count()}


@router.get("/{category_id}")
async def get_customer(category_id: int, manager: AuthManagerDep):
    return await Customer.get_or_none(id=category_id)


@router.post("/")
async def create_customer(data: CustomerModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CUSTOMERS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (customer := await Customer.get_or_none(**data.model_dump())) is not None:
        return customer
    return await Customer.create(**data.model_dump())


@router.patch("/{customer_id}")
async def update_customer(customer_id: int, data: CustomerModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CUSTOMERS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    customer = await Customer.get_or_none(id=customer_id)
    await customer.update(**data.model_dump())
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_category(customer_id: int, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_CUSTOMERS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    await Customer.filter(id=customer_id).delete()
