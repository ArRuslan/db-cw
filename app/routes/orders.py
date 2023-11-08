from fastapi import APIRouter, HTTPException
from tortoise.functions import Count

from app.db import database
from app.models import Customer, Manager, Product
from app.models.customer import CustomerPd
from app.models.order import Order, OrderPd
from app.models.order_item import OrderItemPd, OrderItem
from app.models.product import ProductPd
from app.schemas.orders import OrderCreateModel, OrderUpdateModel

router = APIRouter(prefix="/api/v0/orders")


@router.get("/")
async def get_orders(page: int=0, limit: int = 50):
    return {"results": await Order.all().limit(limit).offset(page * limit), "count": await Order.all().count()}


@router.post("/")
async def create_order(data: OrderCreateModel):
    inf = data.customer_info
    customer = await Customer.get_or_none(**inf.model_dump()) or await Customer.create(**inf.model_dump())
    manager = await Manager.annotate(c=Count("orders")).order_by("c").limit(1)
    if not manager:
        raise HTTPException(status_code=400, detail="No managers found to process this order!")
    else:
        manager = manager[0]

    order = await Order.create(status="processing", address=data.address, type=data.type, customer=customer,
                               manager=manager)

    q = {prod.id: prod.quantity for prod in data.products}
    print(q)
    for prod in await Product.filter(id__in=[prod.id for prod in data.products]).all():
        print(prod.id, q[prod.id])
        await OrderItem.create(order=order, product=prod, quantity=q[prod.id], price=prod.price)

    return await get_order(order.id)


@router.get("/{order_id}")
async def get_order(order_id: int):
    order = await Order.get_or_none(id=order_id).select_related("customer")
    resp = (await OrderPd.from_tortoise_orm(order)).model_dump()
    resp["customer"] = (await CustomerPd.from_tortoise_orm(order.customer)).model_dump()
    resp["items"] = []
    for prod in await order.items.all().select_related("orderitems"):
        resp["items"].append((await ProductPd.from_tortoise_orm(prod)).model_dump() |
                             (await OrderItemPd.from_tortoise_orm(prod.orderitems)).model_dump(exclude={"id"}))

    return resp


@router.patch("/{order_id}")
async def update_order(order_id: int, data: OrderUpdateModel):
    order = await Order.get_or_none(id=order_id)
    await order.update(**data.model_dump(exclude_defaults=True))
    return await get_order(order_id)
