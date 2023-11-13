from fastapi import APIRouter, HTTPException
from tortoise.functions import Count

from app.models import Customer, Manager, Product
from app.models.customer import CustomerPd
from app.models.order import Order, OrderPd
from app.models.order_item import OrderItemPd, OrderItem
from app.models.product import ProductPd
from app.schemas import SearchData
from app.schemas.orders import OrderCreateModel, OrderUpdateModel
from app.utils import AuthManagerDep, Permissions, search

router = APIRouter(prefix="/api/v0/orders")


@router.get("/")
async def get_orders(page: int=0, limit: int = 50):
    orders = await Order.all().limit(limit).offset(page * limit).select_related("customer")
    return {"results": [await order_to_resp(order) for order in orders], "count": await Order.all().count()}


@router.post("/search")
async def search_order_post(data: SearchData):
    query, countQuery = search(Order, data)
    query = query.select_related("customer")
    return {"results": [await order_to_resp(order) for order in await query], "count": await countQuery.count()}


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
    for prod in await Product.filter(id__in=[prod.id for prod in data.products]).all():
        await OrderItem.create(order=order, product=prod, quantity=q[prod.id], price=prod.price)

    return await get_order(order.id)


async def order_to_resp(order: Order) -> list[dict]:
    resp = (await OrderPd.from_tortoise_orm(order)).model_dump()
    resp["customer"] = (await CustomerPd.from_tortoise_orm(order.customer)).model_dump()
    resp["items"] = []
    for prod in await order.items.all().select_related("orderitems"):
        resp["items"].append((await ProductPd.from_tortoise_orm(prod)).model_dump() |
                             (await OrderItemPd.from_tortoise_orm(prod.orderitems)).model_dump(exclude={"id"}))

    return resp


@router.get("/{order_id}")
async def get_order(order_id: int):
    q = {"id": order_id}

    if (order := await Order.get_or_none(**q).select_related("customer")) is None:
        raise HTTPException(status_code=404, detail="Unknown order!")

    return await order_to_resp(order)


@router.patch("/{order_id}")
async def update_order(order_id: int, data: OrderUpdateModel, manager: AuthManagerDep):
    q = {"id": order_id}
    if not Permissions.check(manager, Permissions.MANAGE_ORDERS):
        q["manager"] = manager

    if (order := await Order.get_or_none(**q)) is None:
        raise HTTPException(status_code=404, detail="Unknown order!")

    await order.update(**data.model_dump(exclude_defaults=True))
    return await get_order(order_id)
