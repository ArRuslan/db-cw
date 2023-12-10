from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from tortoise import connections

from app.schemas.sql import ExecuteSql
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/sql")


def get_js_type(value: Any) -> str:
    if isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, (datetime, date)):
        return "date"
    return "string"


@router.post("/")
async def execute_sql(data: ExecuteSql, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.ADMIN):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    conn = connections.get("default")
    result = await conn.execute_query_dict(data.query)
    columns = []
    if result:
        for key in result[0]:
            columns.append({"name": key, "type": get_js_type(result[0][key])})

    return {"result": result, "columns": columns}


"""

create table category (
    category_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL
);

create table characteristic (
    characteristic_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(255) NOT NULL UNIQUE,
    measurement_unit VARCHAR(32) NULL
);

create table customer (
    customer_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(128) NOT NULL,
    last_name    VARCHAR(128) NOT NULL,
    email        VARCHAR(256) NOT NULL,
    phone_number BIGINT NOT NULL
);

create table manager (
    manager_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(128) NOT NULL,
    last_name   VARCHAR(128) NOT NULL,
    email       VARCHAR(256) NOT NULL,
    password    VARCHAR(256) NOT NULL,
    permissions INT default 2 NOT NULL
);

create table `order` (
    order_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    status        VARCHAR(64) NOT NULL,
    creation_time DATETIME NOT NULL,
    address       TEXT NOT NULL,
    type          VARCHAR(64) NOT NULL,
    customer_id   BIGINT NOT NULL,
    manager_id    BIGINT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES manager (manager_id) ON DELETE CASCADE
);

create table orderitem (
    orderitem_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    quantity   INT NOT NULL,
    price      DOUBLE NOT NULL,
    order_id   BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order` (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

create table product (
    product_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    model           VARCHAR(128) NOT NULL,
    manufacturer    VARCHAR(128) NOT NULL,
    price           DOUBLE DEFAULT 0 NOT NULL,
    quantity        INT DEFAULT 0 NOT NULL,
    per_order_limit INT DEFAULT 0 NOT NULL,
    image_url       TEXT DEFAULT NULL,
    warranty_days   INT DEFAULT 0 NOT NULL,
    category_id     BIGINT DEFAULT NULL,
    FOREIGN KEY (category_id) REFERENCES category (category_id) ON DELETE CASCADE 
);

create table productcharacteristic (
    productcharacteristic_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    value             TEXT NOT NULL,
    characteristic_id BIGINT NOT NULL,
    product_id        BIGINT NOT NULL,
    FOREIGN KEY (characteristic_id) REFERENCES characteristic (characteristic_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

create table `return` (
    return_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    status        VARCHAR(128) default 'processing' NOT NULL,
    creation_time DATETIME NOT NULL,
    quantity      INT NOT NULL,
    reason        TEXT DEFAULT NULL,
    order_id      BIGINT NOT NULL,
    order_item_id BIGINT NOT NULL UNIQUE,
    FOREIGN KEY (order_id) REFERENCES `order` (order_id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES orderitem (orderitem_id) ON DELETE CASCADE
);



"""
