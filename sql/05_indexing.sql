-- =============================================================================
-- PHASE 5: Indexing
-- =============================================================================
-- Run this AFTER the database has been seeded (100 users / 200 products /
-- 500 orders / etc.) so the before/after comparison is meaningful — on a
-- handful of rows MySQL will table-scan either way and the timings won't
-- show a difference.
--
-- Method: run each "BEFORE" query, note the time / EXPLAIN output, add the
-- index, then re-run the same query as "AFTER" and compare.
-- =============================================================================
USE shopsphere_db;

-- -----------------------------------------------------------------------------
-- 1. User email lookup (e.g. login)
-- -----------------------------------------------------------------------------
-- BEFORE: drop the index Django/the schema normally creates, to see the
-- table-scan baseline.
ALTER TABLE Users DROP INDEX email;

EXPLAIN SELECT * FROM Users WHERE email = 'amelia.khan214@example.com';
-- Expect: type = ALL (full table scan), rows ≈ total row count

-- AFTER: add the index back
CREATE UNIQUE INDEX idx_users_email ON Users (email);

EXPLAIN SELECT * FROM Users WHERE email = 'amelia.khan214@example.com';
-- Expect: type = const/ref, rows = 1, key = idx_users_email

-- -----------------------------------------------------------------------------
-- 2. Product name search
-- -----------------------------------------------------------------------------
EXPLAIN SELECT * FROM Products WHERE name LIKE 'Wireless%';
-- BEFORE: type = ALL

CREATE INDEX idx_products_name ON Products (name);

EXPLAIN SELECT * FROM Products WHERE name LIKE 'Wireless%';
-- AFTER: type = range, key = idx_products_name

-- -----------------------------------------------------------------------------
-- 3. Order date range queries (e.g. reporting by month)
-- -----------------------------------------------------------------------------
EXPLAIN SELECT * FROM Orders WHERE order_date BETWEEN '2026-01-01' AND '2026-01-31';
-- BEFORE: type = ALL

CREATE INDEX idx_orders_order_date ON Orders (order_date);

EXPLAIN SELECT * FROM Orders WHERE order_date BETWEEN '2026-01-01' AND '2026-01-31';
-- AFTER: type = range, key = idx_orders_order_date

-- -----------------------------------------------------------------------------
-- Timing comparison (alternative to EXPLAIN — wall-clock proof)
-- -----------------------------------------------------------------------------
SET profiling = 1;

SELECT * FROM Products WHERE name LIKE 'Wireless%';
SHOW PROFILES;              -- note the Duration for the query above

-- (Query already benefits from idx_products_name here; to see the "before"
--  number, run DROP INDEX idx_products_name and repeat, then re-create it.)

-- -----------------------------------------------------------------------------
-- Composite indexes actually shipped in the Django schema (store/models.py)
-- -----------------------------------------------------------------------------
-- Products(category_id, price)   -> speeds up "products in category X sorted
--                                    by price" (a very common storefront query)
-- Products(stock_quantity)       -> speeds up "out of stock" filters
-- Orders(status)                 -> speeds up admin/dashboard status filters
-- Orders(user_id, order_date)    -> speeds up "this customer's order history"
-- Payments(payment_date), (status)
-- Reviews(product_id, rating)    -> speeds up "average rating per product"
