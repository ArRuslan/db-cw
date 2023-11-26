from fastapi import APIRouter, HTTPException

from app.models import Return
from app.models.customer import CustomerPd
from app.models.order import Order
from app.models.order_item import OrderItemPd
from app.models.product import ProductPd
from app.schemas import SearchData
from app.schemas.returns import ReturnCreateModel, ReturnUpdateModel
from app.utils import AuthManagerDep, Permissions, search

router = APIRouter(prefix="/api/v0/returns")


@router.post("/search")
async def search_return(data: SearchData):
    query, countQuery = search(Return, data)
    return {"results": [await return_to_resp(ret) for ret in await query], "count": await countQuery.count()}


@router.post("/")
async def create_return(data: ReturnCreateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_ORDERS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (order := await Order.get_or_none(id=data.order_id).select_related("customer")) is None:
        raise HTTPException(status_code=404, detail="Unknown order!")
    if (product := await order.items.filter().get_or_none(id=data.product_id).select_related("orderitems")) is None:
        raise HTTPException(status_code=404, detail="Unknown item!")

    if data.quantity > product.orderitems.quantity:
        raise HTTPException(status_code=400, detail="Return quantity cannot be bigger than order quantity!")

    ret = await Return.create(quantity=data.quantity, reason=data.reason, order=order, order_item=product.orderitems)
    return await return_to_resp(ret)


async def return_to_resp(return_: Return) -> dict:
    await return_.fetch_related("order", "order__customer", "order_item", "order_item__product")

    return {
        "id": return_.id,
        "customer": (await CustomerPd.from_tortoise_orm(return_.order.customer)).model_dump(),
        "order_id": return_.order.id,
        "item": (await ProductPd.from_tortoise_orm(return_.order_item.product)).model_dump() |
                (await OrderItemPd.from_tortoise_orm(return_.order_item)).model_dump(exclude={"id"}),
        "status": return_.status,
        "creation_time": return_.creation_time,
        "quantity": return_.quantity,
        "reason": return_.reason,
    }


@router.get("/{return_id}")
async def get_return(return_id: int):
    if (ret := await Return.get_or_none(id=return_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown return!")

    return await return_to_resp(ret)


@router.patch("/{return_id}")
async def update_return(return_id: int, data: ReturnUpdateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_ORDERS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (ret := await Return.get_or_none(id=return_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown return!")

    await ret.update(**data.model_dump(exclude_defaults=True))
    return await return_to_resp(ret)
