-- =============================================================================
-- PHASE 4: SQL Queries
-- =============================================================================
USE shopsphere_db;

-- ---------- BASIC ----------

-- 1. Display all products
SELECT product_id, name, price, stock_quantity
FROM Products
ORDER BY name;

-- 2. Display products in a specific category (e.g. "Electronics")
SELECT p.product_id, p.name, p.price, p.stock_quantity
FROM Products p
JOIN Categories c ON c.category_id = p.category_id
WHERE c.name = 'Electronics'
ORDER BY p.name;

-- 3. Find products that are out of stock
SELECT product_id, name, stock_quantity
FROM Products
WHERE stock_quantity = 0;

-- 4. Show all orders placed by a user (e.g. user_id = 1)
SELECT order_id, order_date, status, total_amount
FROM Orders
WHERE user_id = 1
ORDER BY order_date DESC;

-- 5. Count the total number of users
SELECT COUNT(*) AS total_users
FROM Users;

-- ---------- INTERMEDIATE ----------

-- 1. Find the top 5 best-selling products (by units sold)
SELECT p.product_id, p.name, SUM(oi.quantity) AS units_sold
FROM Order_Items oi
JOIN Products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY units_sold DESC
LIMIT 5;

-- 2. Calculate total sales (sum of completed payments)
SELECT SUM(amount) AS total_sales
FROM Payments
WHERE status = 'Completed';

-- 3. Find the customer who placed the most orders
SELECT u.user_id, u.username, COUNT(o.order_id) AS order_count
FROM Orders o
JOIN Users u ON u.user_id = o.user_id
GROUP BY u.user_id, u.username
ORDER BY order_count DESC
LIMIT 1;

-- 4. Display monthly sales (based on order totals)
SELECT DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
       SUM(total_amount) AS monthly_total,
       COUNT(*) AS orders_placed
FROM Orders
GROUP BY sales_month
ORDER BY sales_month;

-- 5. Show products with an average rating above 4
SELECT p.product_id, p.name, ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(r.review_id) AS review_count
FROM Products p
JOIN Reviews r ON r.product_id = p.product_id
GROUP BY p.product_id, p.name
HAVING AVG(r.rating) > 4
ORDER BY avg_rating DESC;
