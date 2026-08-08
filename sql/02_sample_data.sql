-- =============================================================================
-- PHASE 2: Sample Data
-- =============================================================================
-- The assignment allows "SQL scripts OR a data generation tool" — this project
-- uses a data generation tool (Faker, driven through Django) because it needs
-- to satisfy real foreign-key relationships (order totals that match their
-- order items, payments that match order totals, one review per user/product,
-- etc.) at volume:
--
--     100 Users · 200 Products · 10 Categories · 500 Orders ·
--     1,000 Order_Items · 500 Payments · 300 Reviews
--
-- Generate it with:
--     python manage.py migrate
--     python manage.py seed_data
--
-- (see store/management/commands/seed_data.py for the full generator)
--
-- Below is the same shape of data expressed as plain INSERT statements, for
-- reference/demonstration against the schema in 01_schema.sql.
-- =============================================================================

USE shopsphere_db;

INSERT INTO Categories (name, description) VALUES
    ('Electronics', 'Phones, audio, computing and smart-home gear.'),
    ('Clothing & Apparel', 'Everyday and seasonal wear for all ages.'),
    ('Home & Kitchen', 'Cookware, small appliances and decor.'),
    ('Books', 'Fiction, non-fiction and reference titles.'),
    ('Sports & Outdoors', 'Fitness gear and outdoor equipment.');

INSERT INTO Users (username, email, password_hash, first_name, last_name, phone, city, country, is_verified) VALUES
    ('amelia.khan214', 'amelia.khan214@example.com', 'pbkdf2_sha256$...hash...', 'Amelia', 'Khan', '+92-300-1234567', 'Multan', 'Pakistan', 1),
    ('daniel.rossi77',  'daniel.rossi77@example.com', 'pbkdf2_sha256$...hash...', 'Daniel', 'Rossi', '+39-345-9876543', 'Milan', 'Italy', 1),
    ('mei.chen501',     'mei.chen501@example.com',    'pbkdf2_sha256$...hash...', 'Mei', 'Chen', '+86-138-0013800', 'Chengdu', 'China', 0);

INSERT INTO Products (name, description, price, stock_quantity, category_id) VALUES
    ('Wireless Headphones Nova', 'Over-ear ANC headphones, 30h battery.', 89.99, 140, 1),
    ('Classic Denim Jacket', 'Mid-wash cotton denim, unisex fit.', 54.50, 0, 2),
    ('Smart Blender Pro', '6-speed blender with pulse mode.', 74.00, 65, 3);

INSERT INTO Orders (user_id, status, total_amount, shipping_address) VALUES
    (1, 'Delivered', 179.98, '221B Cantonment Road, Multan'),
    (2, 'Processing', 74.00, 'Via Roma 12, Milan');

INSERT INTO Order_Items (order_id, product_id, quantity, price) VALUES
    (1, 1, 2, 89.99),
    (2, 3, 1, 74.00);

INSERT INTO Payments (order_id, amount, payment_method, status) VALUES
    (1, 179.98, 'Credit Card', 'Completed'),
    (2, 74.00, 'Cash on Delivery', 'Pending');

INSERT INTO Reviews (user_id, product_id, rating, comment) VALUES
    (1, 1, 5, 'Excellent sound isolation, worth the price.'),
    (2, 3, 4, 'Powerful motor, a bit loud on high speed.');
