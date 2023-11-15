from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from pytz import UTC
from tortoise.functions import Count, Sum

from app.models import Product, Customer, Order, Category
from app.models.order import OrderPd
from app.models.order_item import OrderItemPd
from app.models.product import ProductPd
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/reports")


@router.get("/products/{product_id}")
async def customer_statistics(manager: AuthManagerDep, product_id: int):
    if not Permissions.check(manager, Permissions.READ_REPORTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    product = await Product.get_or_none(id=product_id).select_related("category") \
        .annotate(order_count=Count("orderitems"), orderitem_count=Sum("orderitems__quantity"))

    result = {
        "id": product.id,
        "model": product.model,
        "manufacturer": product.manufacturer,
        "price": product.price,
        "quantity": product.quantity,
        "per_order_limit": product.per_order_limit,
        "image_url": product.image_url,
        "warranty_days": product.warranty_days,
        "category_name": product.category.name,
        "order_count": product.order_count,
        "order_item_count": product.orderitem_count,
    }

    return result


@router.get("/customers/{customer_id}")
async def customer_statistics(manager: AuthManagerDep, customer_id: int):
    if not Permissions.check(manager, Permissions.READ_REPORTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    customer = await Customer.get_or_none(id=customer_id).annotate(order_count=Count("orders"))

    result = {
        "id": customer.id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone_number": customer.phone_number,
        "order_count": customer.order_count,
        "orders": [],
        "total": 0,
        "averages": {}
    }

    orders = await Order.filter(customer=customer).all()
    for order in orders:
        result["orders"].append((await OrderPd.from_tortoise_orm(order)).model_dump())
        result["orders"][-1]["items"] = []

        order_total = 0
        orderitems = await order.items.all().select_related("orderitems")
        for prod in orderitems:
            result["orders"][-1]["items"].append(
                (await ProductPd.from_tortoise_orm(prod)).model_dump() |
                (await OrderItemPd.from_tortoise_orm(prod.orderitems)).model_dump(exclude={"id"})
            )
            order_total = prod.orderitems.quantity * prod.orderitems.price

        result["orders"][-1]["total"] = order_total
        result["total"] += order_total

        if order.creation_time > (datetime.now() - timedelta(days=365)).replace(tzinfo=UTC):
            date = f"{order.creation_time.month}.{order.creation_time.year}"
            if date not in result["averages"]:
                result["averages"][date] = 0

            if orderitems:
                result["averages"][date] += order_total / len(orderitems)

    return result


@router.get("/categories/{category_id}")
async def customer_statistics(manager: AuthManagerDep, category_id: int):
    if not Permissions.check(manager, Permissions.READ_REPORTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    category = await Category.get_or_none(id=category_id)

    result = {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "product_count": 0,
        "order_count": 0,
        "product_quantity": 0,
        "product_average_price": 0,
    }

    products = await Product.filter(category=category).all()
    result["product_count"] = len(products)
    for product in products:
        result["product_quantity"] += product.quantity
        result["product_average_price"] += product.price

    result["order_count"] = await Order.filter(orderitems__product__id__in=[prod.id for prod in products]).count()
    result["product_average_price"] /= result["product_count"]

    return result
