-- =============================================================================
-- PHASE 6: Performance Optimization
-- =============================================================================
USE shopsphere_db;

-- =============================================================================
-- SLOW QUERY #1 — "Best-selling products this year, with category name"
-- =============================================================================

-- --- BEFORE (naive version) ---------------------------------------------
-- Problems:
--   * SELECT * pulls every column, including large TEXT description fields,
--     for rows that are immediately discarded by GROUP BY.
--   * No index on Order_Items.order_id / product_id to drive the join.
--   * Filtering by YEAR(o.order_date) can't use an index on order_date at
--     all, because wrapping the column in a function forces a full scan.
EXPLAIN SELECT *
FROM Order_Items oi
JOIN Orders o   ON o.order_id = oi.order_id
JOIN Products p ON p.product_id = oi.product_id
WHERE YEAR(o.order_date) = 2026
GROUP BY p.product_id
ORDER BY SUM(oi.quantity) DESC
LIMIT 5;

-- --- AFTER (optimized) ----------------------------------------------------
-- Fixes applied:
--   1. Select only the columns actually needed.
--   2. Rewrite the date filter as a sargable range so it CAN use an index
--      on order_date, instead of YEAR(order_date).
--   3. Make sure supporting indexes exist (foreign keys are auto-indexed by
--      InnoDB; order_date is indexed in 05_indexing.sql).
CREATE INDEX idx_orderitems_product ON Order_Items (product_id);
CREATE INDEX idx_orderitems_order   ON Order_Items (order_id);

EXPLAIN SELECT p.product_id, p.name, SUM(oi.quantity) AS units_sold
FROM Order_Items oi
JOIN Orders o   ON o.order_id = oi.order_id
JOIN Products p ON p.product_id = oi.product_id
WHERE o.order_date >= '2026-01-01' AND o.order_date < '2027-01-01'
GROUP BY p.product_id, p.name
ORDER BY units_sold DESC
LIMIT 5;
-- Expect: join now uses key = idx_orderitems_product / PRIMARY on Orders,
-- range scan on order_date instead of a full table scan for every row.

-- =============================================================================
-- SLOW QUERY #2 — "Customers with more than 3 orders and their average
-- order value" (dashboard "loyal customers" widget)
-- =============================================================================

-- --- BEFORE (naive version) ---------------------------------------------
-- Problems:
--   * SELECT * on Users pulls password_hash and every profile column
--     for a report that only needs 3 fields.
--   * A correlated subquery re-scans Orders once per user row instead of
--     a single grouped pass.
EXPLAIN SELECT *,
       (SELECT COUNT(*) FROM Orders WHERE Orders.user_id = Users.user_id) AS order_count
FROM Users
WHERE (SELECT COUNT(*) FROM Orders WHERE Orders.user_id = Users.user_id) > 3;

-- --- AFTER (optimized) ----------------------------------------------------
-- Fixes applied:
--   1. Select only needed columns.
--   2. Replace the correlated subquery with a single GROUP BY + HAVING pass
--      over Orders, joined once to Users.
--   3. Orders(user_id, order_date) composite index (already created in
--      05_indexing.sql / store/models.py) covers the join + grouping.
EXPLAIN SELECT u.user_id, u.username, u.email,
       COUNT(o.order_id) AS order_count,
       ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM Users u
JOIN Orders o ON o.user_id = u.user_id
GROUP BY u.user_id, u.username, u.email
HAVING COUNT(o.order_id) > 3
ORDER BY order_count DESC;
-- Expect: single pass with type = ref/index on the join, no per-row
-- subquery re-execution (Extra no longer shows "Dependent subquery").

-- =============================================================================
-- How to read the EXPLAIN output for both pairs above
-- =============================================================================
-- type:  ALL (full scan, slow) -> ref/range/index (index-assisted, fast)
-- rows:  estimated rows examined — should drop sharply after optimization
-- Extra: "Using filesort" / "Using temporary" are red flags worth revisiting;
--        "Dependent subquery" disappearing confirms fix #2 above worked.
