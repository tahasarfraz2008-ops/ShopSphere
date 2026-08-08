-- =============================================================================
-- PHASE 3: CRUD Operations
-- =============================================================================
USE shopsphere_db;

-- 1. Add a new user
INSERT INTO Users (username, email, password_hash, first_name, last_name, phone, city, country)
VALUES ('sara.iqbal99', 'sara.iqbal99@example.com', 'pbkdf2_sha256$...hash...',
        'Sara', 'Iqbal', '+92-321-4455667', 'Multan', 'Pakistan');

-- 2. Add a new product
INSERT INTO Products (name, description, price, stock_quantity, category_id)
VALUES ('Ultra Mechanical Keyboard', 'Hot-swappable switches, RGB backlight.', 129.99, 80, 1);

-- 3. Update a product's price
UPDATE Products
SET price = 109.99
WHERE product_id = 1;

-- 4. Update a user's details (address change)
UPDATE Users
SET address = '45 Model Town, Multan', city = 'Multan', phone = '+92-300-7654321'
WHERE user_id = 1;

-- 5. Delete a review
DELETE FROM Reviews
WHERE review_id = 2;

-- 6. Display all products
SELECT product_id, name, price, stock_quantity, category_id
FROM Products
ORDER BY name;

-- 7. Display all orders of a specific customer (by user_id)
SELECT o.order_id, o.order_date, o.status, o.total_amount
FROM Orders o
WHERE o.user_id = 1
ORDER BY o.order_date DESC;
