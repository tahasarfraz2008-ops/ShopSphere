-- =============================================================================
-- ShopSphere — E-Commerce Management System
-- PHASE 1: Database Schema (MySQL / XAMPP)
-- =============================================================================
-- Run this in phpMyAdmin's SQL tab, or:
--   mysql -u root -p < 01_schema.sql
--
-- This file is a standalone reference matching the assignment's table names
-- exactly (Users, Products, Categories, Orders, Order_Items, Payments,
-- Reviews). The live application uses Django's ORM/migrations to create an
-- equivalent schema automatically (see store/models.py) — the two are the
-- same design expressed two ways. Use this file to inspect, present, or run
-- the design independently of Django.
-- =============================================================================

DROP DATABASE IF EXISTS shopsphere_db;
CREATE DATABASE shopsphere_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE shopsphere_db;

-- -----------------------------------------------------------------------------
-- Users
-- -----------------------------------------------------------------------------
CREATE TABLE Users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(150) NOT NULL UNIQUE,
    email           VARCHAR(254) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL DEFAULT '',
    last_name       VARCHAR(100) NOT NULL DEFAULT '',
    phone           VARCHAR(20)  NOT NULL DEFAULT '',
    address         VARCHAR(255) NOT NULL DEFAULT '',
    city            VARCHAR(100) NOT NULL DEFAULT '',
    country         VARCHAR(100) NOT NULL DEFAULT '',
    is_verified     TINYINT(1)   NOT NULL DEFAULT 0,
    is_active       TINYINT(1)   NOT NULL DEFAULT 1,
    date_joined     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_email_format CHECK (email LIKE '%_@__%.__%')
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Categories
-- -----------------------------------------------------------------------------
CREATE TABLE Categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Products
-- -----------------------------------------------------------------------------
CREATE TABLE Products (
    product_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    description     TEXT NULL,
    price           DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (price >= 0),
    stock_quantity  INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    category_id     INT NULL,
    image_url       VARCHAR(500) NOT NULL DEFAULT '',
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Orders
-- -----------------------------------------------------------------------------
CREATE TABLE Orders (
    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    order_date      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('Pending','Processing','Shipped','Delivered','Cancelled')
                        NOT NULL DEFAULT 'Pending',
    total_amount    DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    shipping_address VARCHAR(255) NOT NULL DEFAULT '',
    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Order_Items
-- -----------------------------------------------------------------------------
CREATE TABLE Order_Items (
    order_item_id   INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    CONSTRAINT fk_orderitems_order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_orderitems_product
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Payments
-- -----------------------------------------------------------------------------
CREATE TABLE Payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    payment_date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount          DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    payment_method  ENUM('Credit Card','Debit Card','PayPal','Cash on Delivery','Bank Transfer')
                        NOT NULL DEFAULT 'Credit Card',
    status          ENUM('Pending','Completed','Failed','Refunded')
                        NOT NULL DEFAULT 'Completed',
    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Reviews
-- -----------------------------------------------------------------------------
CREATE TABLE Reviews (
    review_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    product_id      INT NOT NULL,
    rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reviews_product
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_review_per_user_product UNIQUE (user_id, product_id)
) ENGINE=InnoDB;
