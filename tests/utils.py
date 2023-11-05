from fastapi.testclient import TestClient


def create_category(client: TestClient, **kwargs) -> dict:
    resp = client.post("/api/v0/categories", json=kwargs)
    assert resp.status_code == 200
    return resp.json()


def create_product(client: TestClient, **kwargs) -> dict:
    resp = client.post("/api/v0/products", json=kwargs)
    assert resp.status_code == 200
    return resp.json()


def create_manager(client, **kwargs) -> dict:
    resp = client.post("/api/v0/managers", json=kwargs)
    assert resp.status_code == 200
    return resp.json()


def create_order(client, **kwargs) -> dict:
    resp = client.post("/api/v0/orders", json=kwargs)
    assert resp.status_code == 200
    return resp.json()


async def cleanup_db(database):
    await database.connect()
    await database.execute("DELETE FROM order_items;")
    await database.execute("DELETE FROM orders;")
    await database.execute("DELETE FROM managers;")
    await database.execute("DELETE FROM products;")
    await database.execute("DELETE FROM categories;")
    await database.disconnect()
