from asyncio import get_event_loop

import pytest as pt
from fastapi.testclient import TestClient

from app.db import database
from app.main import app
from tests.utils import create_category, create_product, cleanup_db, create_manager, create_order


@pt.fixture(autouse=True, scope="function")
def clean_db():
    get_event_loop().run_until_complete(cleanup_db(database))
    yield
    get_event_loop().run_until_complete(cleanup_db(database))


def test_create_order():
    with TestClient(app) as client:
        cat = create_category(client, name="test")
        create_manager(client, first_name="First test", last_name="Last test", email="first.last@test.nure.ua",
                       password="123456789")

        prod1 = create_product(client, model="test1", manufacturer="m", price=100, category_id=cat["id"])
        prod2 = create_product(client, model="test2", manufacturer="m", price=150, category_id=cat["id"])
        prod3 = create_product(client, model="test3", manufacturer="m", price=200, category_id=cat["id"])

        cust = {"first_name": "test", "last_name": "test", "email": "test.test@test.nure.ua", "phone_number": 123}
        prods = [{"id": prod1["id"], "quantity": 1},
                 {"id": prod2["id"], "quantity": 2},
                 {"id": prod3["id"], "quantity": 3},
                 {"id": prod3["id"]*2, "quantity": 4}]
        ord1 = create_order(client, customer_info=cust, address="test", type="test", products=prods)
        ord2 = create_order(client, customer_info=cust, address="test", type="test", products=prods)
        ord3 = create_order(client, customer_info=cust | {"phone_number": 456}, address="test", type="test",
                            products=prods)
        assert ord1["customer"]["first_name"] == ord1["customer"]["last_name"] == "test"
        assert ord1["customer"] == ord2["customer"]
        assert ord1["customer"] != ord3["customer"]
        assert len(ord1["items"]) == 3
        assert ord1["items"] == ord2["items"] == ord3["items"]
