from asyncio import get_event_loop

import pytest as pt
from fastapi.testclient import TestClient

from app.db import database
from app.main import app
from tests.utils import create_category, create_product, cleanup_db


@pt.fixture(autouse=True, scope="function")
def clean_db():
    get_event_loop().run_until_complete(cleanup_db(database))
    yield
    get_event_loop().run_until_complete(cleanup_db(database))


def test_create_products():
    with TestClient(app) as client:
        cat = create_category(client, name="test")

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"])
        assert prod["model"] == "test"
        assert prod["manufacturer"] == "m"
        assert prod["price"] == 100
        assert prod["category_id"] == cat["category_id"]
        assert prod["quantity"] == 0
        assert prod["warranty_days"] == 14

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"],
                              quantity=5, warranty_days=7)
        assert prod["quantity"] == 5
        assert prod["warranty_days"] == 7


def test_get_products():
    with TestClient(app) as client:
        cat = create_category(client, name="test")
        cat2 = create_category(client, name="test2")

        resp = client.get("/api/v0/products")
        assert resp.status_code == 200
        assert resp.json() == []

        resp = client.get(f"/api/v0/categories/{cat['category_id']}/products")
        assert resp.status_code == 200
        assert resp.json() == []

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"])

        resp = client.get("/api/v0/products")
        assert resp.status_code == 200
        assert resp.json() == [prod]

        resp = client.get(f"/api/v0/categories/{cat['category_id']}/products")
        assert resp.status_code == 200
        assert resp.json() == [prod]

        resp = client.get(f"/api/v0/categories/{cat2['category_id']}/products")
        assert resp.status_code == 200
        assert resp.json() == []


def test_get_product():
    with TestClient(app) as client:
        cat = create_category(client, name="test")

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"])

        resp = client.get(f"/api/v0/products/{prod['product_id']}")
        assert resp.status_code == 200
        assert resp.json() == prod


def test_update_product():
    with TestClient(app) as client:
        cat = create_category(client, name="test")

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"])

        resp = client.patch(f"/api/v0/products/{prod['product_id']}",
                            json={"image_url": "https://example.com/img.png"})
        assert resp.status_code == 200

        resp = client.get(f"/api/v0/products/{prod['product_id']}")
        assert resp.status_code == 200
        assert resp.json() == prod | {"image_url": "https://example.com/img.png"}


def test_delete_category():
    with TestClient(app) as client:
        cat = create_category(client, name="test")

        resp = client.get("/api/v0/products")
        assert resp.status_code == 200
        assert resp.json() == []

        prod = create_product(client, model="test", manufacturer="m", price=100, category_id=cat["category_id"])

        resp = client.get("/api/v0/products")
        assert resp.status_code == 200
        assert resp.json() == [prod]

        resp = client.delete(f"/api/v0/products/{prod['product_id']}")
        assert resp.status_code == 204

        resp = client.get("/api/v0/products")
        assert resp.status_code == 200
        assert resp.json() == []
