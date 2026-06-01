-- ==========================================
-- SHOPEY DATABASE (PostgreSQL Version)
-- ==========================================

CREATE SCHEMA IF NOT EXISTS shopey;

-- Customers
CREATE TABLE shopey.customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories
CREATE TABLE shopey.categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Vendors
CREATE TABLE shopey.vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(255)
);

-- Products
CREATE TABLE shopey.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT REFERENCES shopey.categories(category_id),
    vendor_id INT REFERENCES shopey.vendors(vendor_id),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    stock_qty INT DEFAULT 0
);

-- Orders
CREATE TABLE shopey.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES shopey.customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20)
        CHECK (status IN ('Pending','Confirmed','Shipped','Delivered','Cancelled'))
        DEFAULT 'Pending'
);

-- Order Lines
CREATE TABLE shopey.order_lines (
    line_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES shopey.orders(order_id),
    product_id INT NOT NULL REFERENCES shopey.products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL
);

-- Payments
CREATE TABLE shopey.payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT UNIQUE NOT NULL REFERENCES shopey.orders(order_id),
    payment_date TIMESTAMP,
    method VARCHAR(50)
        CHECK (method IN ('Card','PayPal','Bank Transfer','Wallet')),
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(20)
        CHECK (status IN ('Pending','Paid','Failed','Refunded'))
        DEFAULT 'Pending'
);

SELECT
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(ol.quantity * ol.unit_price) AS total_spent,
    RANK() OVER (
        ORDER BY SUM(ol.quantity * ol.unit_price) DESC
    ) AS customer_rank
FROM shopey.customers c
JOIN shopey.orders o
    ON c.customer_id = o.customer_id
JOIN shopey.order_lines ol
    ON o.order_id = ol.order_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY customer_rank;
