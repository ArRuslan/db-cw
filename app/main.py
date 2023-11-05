from fastapi import FastAPI

from app.db import database
from app.routes import categories, products, orders, managers

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(products.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(managers.router)
