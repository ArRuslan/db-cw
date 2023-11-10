from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.routes import categories, products, orders, managers, customers, auth, characteristics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(managers.router)
app.include_router(customers.router)
app.include_router(auth.router)
app.include_router(characteristics.router)

register_tortoise(
    app,
    db_url="mysql://nure_db_cw:123456789@127.0.0.1/nure_db_cw",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=False,
)
