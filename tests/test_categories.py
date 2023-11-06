from asyncio import get_event_loop

import pytest as pt
from fastapi.testclient import TestClient

from app.db import database
from app.main import app
from tests.utils import create_category, cleanup_db


@pt.fixture(autouse=True, scope="function")
def clean_db():
    get_event_loop().run_until_complete(cleanup_db(database))
    yield
    get_event_loop().run_until_complete(cleanup_db(database))


def test_create_categories():
    with TestClient(app) as client:
        cat1 = create_category(client, name="test")
        assert cat1["name"] == "test"
        assert cat1["description"] is None

        cat2 = create_category(client, name="test", description="test category")
        assert cat2["name"] == "test"
        assert cat2["description"] == "test category"


def test_get_categories():
    with TestClient(app) as client:
        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json() == {'count': 0, 'results': []}

        cat1 = create_category(client, name="test")

        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1
        assert resp.json()["results"][0] == cat1

        cat2 = create_category(client, name="test", description="test category")

        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json()["count"] == 2
        assert resp.json()["results"] == [cat1, cat2] or resp.json() == [cat2, cat1]

        resp = client.get("/api/v0/categories?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 1

        resp = client.get("/api/v0/categories?limit=1&page=2")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 0


def test_get_category():
    with TestClient(app) as client:
        cat1 = create_category(client, name="test")

        resp = client.get(f"/api/v0/categories/{cat1['id']}")
        assert resp.status_code == 200
        assert resp.json() == cat1


def test_update_category():
    with TestClient(app) as client:
        cat1 = create_category(client, name="test")

        resp = client.patch(f"/api/v0/categories/{cat1['id']}", json={"description": "123"})
        assert resp.status_code == 200
        assert resp.json() == cat1 | {"description": "123"}


def test_delete_category():
    with TestClient(app) as client:
        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json()["results"] == []

        cat1 = create_category(client, name="test")

        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json()["results"] == [cat1]

        resp = client.delete(f"/api/v0/categories/{cat1['id']}")
        assert resp.status_code == 204

        resp = client.get("/api/v0/categories")
        assert resp.status_code == 200
        assert resp.json()["results"] == []
