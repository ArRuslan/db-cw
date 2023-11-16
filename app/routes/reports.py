from datetime import timedelta, datetime
from io import BytesIO
from typing import Literal

from fastapi import APIRouter, HTTPException, Response
from openpyxl.workbook import Workbook
from pytz import UTC
from tortoise.functions import Count, Sum

from app.models import Product, Customer, Order, Category
from app.models.order import OrderPd
from app.models.order_item import OrderItemPd
from app.models.product import ProductPd
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/reports")


@router.get("/products/{product_id}")
async def customer_statistics(manager: AuthManagerDep, product_id: int, fmt: Literal["json", "excel"]="json"):
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

    if fmt == "excel":
        wb = Workbook()
        ws = wb.active
        ws.append({"A": "Product Id:", "B": product.id})
        ws.append({"A": "Product Manufacturer:", "B": product.manufacturer})
        ws.append({"A": "Product Model:", "B": product.model})
        ws.append({"A": "Product Price:", "B": product.price})
        ws.append({"A": "Product Quantity:", "B": product.quantity})
        ws.append({"A": "Limit per order:", "B": product.per_order_limit})
        ws.append({"A": "Warranty days:", "B": product.warranty_days})
        ws.append({"A": "Category:", "B": product.category.name})
        if product.image_url:
            ws.append({"A": "Image url:", "B": product.image_url})
        ws.append({"A": "Order count:", "B": product.order_count})
        ws.append({"A": "Order item count:", "B": product.orderitem_count})
        fp = BytesIO()
        setattr(fp, "name", f"product-{product.id}-report.xlsx")
        wb.save(fp)
        return Response(content=fp.getvalue(), media_type="application/vnd.ms-excel")

    return result


@router.get("/customers/{customer_id}")
async def customer_statistics(manager: AuthManagerDep, customer_id: int, fmt: Literal["json", "excel"]="json"):
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
            order_total += prod.orderitems.quantity * prod.orderitems.price

        result["orders"][-1]["total"] = order_total
        result["total"] += order_total

        if order.creation_time > (datetime.now() - timedelta(days=365)).replace(tzinfo=UTC):
            date = f"{order.creation_time.month}.{order.creation_time.year}"
            if date not in result["averages"]:
                result["averages"][date] = 0

            if orderitems:
                result["averages"][date] += order_total / len(orderitems)

    if fmt == "excel":
        wb = Workbook()
        ws = wb.active
        ws.append({"A": "Customer Id", "B": customer.id})
        ws.append({"A": "Customer First Name", "B": customer.first_name})
        ws.append({"A": "Customer Last Name", "B": customer.last_name})
        ws.append({"A": "Customer Email", "B": customer.email})
        ws.append({"A": "Customer Phone Number", "B": str(customer.phone_number)})
        ws.append({"A": "Order count", "B": customer.order_count})
        ws.append({"A": "Total", "B": result["total"]})
        ws.append({})
        ws.append({"A": "Average per month:"})
        for month, money in result["averages"].items():
            ws.append({"A": datetime.strptime(month, "%m.%Y"), "B": money})
        ws.append({})
        ws.append({"A": "Orders:"})
        for order in result["orders"]:
            ws.append({"A": "Status", "B": order["status"]})
            ws.append({"A": "Creation Time", "B": order["creation_time"].replace(tzinfo=None)})
            ws.append({"A": "Address", "B": order["address"]})
            ws.append({"A": "Type", "B": order["type"]})
            ws.append({"A": "Total", "B": order["total"]})
            ws.append({"A": "Item Name", "B": "Price", "C": "Quantity"})
            for item in order["items"]:
                ws.append({"A": f"{item['manufacturer']} {item['model']}", "B": item["price"],
                           "C": item["quantity"]})
            ws.append({})
        fp = BytesIO()
        setattr(fp, "name", f"customer-{customer.id}-report.xlsx")
        wb.save(fp)
        return Response(content=fp.getvalue(), media_type="application/vnd.ms-excel")

    return result


@router.get("/categories/{category_id}")
async def customer_statistics(manager: AuthManagerDep, category_id: int, fmt: Literal["json", "excel"]="json"):
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
        "products": [],
    }

    products = await Product.filter(category=category).all()
    result["product_count"] = len(products)
    for product in products:
        result["product_quantity"] += product.quantity
        result["product_average_price"] += product.price
        result["products"].append((await ProductPd.from_tortoise_orm(product)).model_dump())

    result["order_count"] = await Order.filter(orderitems__product__id__in=[prod.id for prod in products]).count()
    result["product_average_price"] /= result["product_count"]

    if fmt == "excel":
        wb = Workbook()
        ws = wb.active
        ws.append({"A": "Category Id:", "B": category_id})
        ws.append({"A": "Category Name:", "B": category.name})
        ws.append({"A": "Category Description:", "B": category.description})
        ws.append({})
        ws.append({"A": "Product count:", "B": result["product_count"]})
        ws.append({"A": "Order count:", "B": result["order_count"]})
        ws.append({"A": "Product quantity:", "B": result["product_quantity"]})
        ws.append({"A": "Product average price:", "B": result["product_average_price"]})
        ws.append({})
        ws.append({"A": "PRODUCTS:"})
        ws.append({})
        ws.append({"A": "model", "B": "manufacturer", "C": "price", "D": "quantity", "E": "per_order_limit",
                   "F": "warranty_days"})
        for prod in result["products"]:
            ws.append({"A": prod["model"], "B": prod["manufacturer"], "C": prod["price"], "D": prod["quantity"],
                       "E": prod["per_order_limit"], "F": prod["warranty_days"]})

        fp = BytesIO()
        setattr(fp, "name", f"category-{category.id}-report.xlsx")
        wb.save(fp)
        return Response(content=fp.getvalue(), media_type="application/vnd.ms-excel")

    return result
