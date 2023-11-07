CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL,
    description TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(256),
    manufacturer VARCHAR(256),
    price DOUBLE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    per_order_limit INTEGER DEFAULT NULL,
    image_url TEXT DEFAULT NULL,
    warranty_days INTEGER DEFAULT 14,
    category_id INTEGER REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS characteristics (
    characteristics_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL,
    measurement_unit VARCHAR(256) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS product_characteristics (
    productcharacteristic_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    product_id INTEGER REFERENCES products(product_id),
    characteristics_id INTEGER REFERENCES characteristics(characteristics_id),
    value VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    email TEXT NOT NULL,
    phone_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS managers (
    manager_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    permissions INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    order_status VARCHAR(256) NOT NULL DEFAULT 'processing',
    order_creation_time DATETIME NOT NULL DEFAULT NOW(),
    address TEXT NOT NULL,
    order_type VARCHAR(256) NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    manager_id INTEGER REFERENCES managers(manager_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    orderitem_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    price_per_item INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS returns (
    return_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    return_status VARCHAR(256) NOT NULL DEFAULT 'processing',
    return_creation_time DATETIME NOT NULL DEFAULT NOW(),
    return_quantity INTEGER NOT NULL,
    return_reason TEXT DEFAULT NULL,
    orderitem_id INTEGER REFERENCES order_items(orderitem_id)
)