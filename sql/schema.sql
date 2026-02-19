-- ============================================================
-- Supply Chain Analytics — Snowflake Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS SUPPLY_CHAIN;
USE DATABASE SUPPLY_CHAIN;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
USE SCHEMA ANALYTICS;

-- ─────────────────────────────────────────
-- CORE TABLES
-- ─────────────────────────────────────────

CREATE OR REPLACE TABLE SUPPLIERS (
    supplier_id       VARCHAR(10)   PRIMARY KEY,
    supplier_name     VARCHAR(100)  NOT NULL,
    country           VARCHAR(50),
    lead_time_days    INT,
    reliability_score FLOAT,
    category          VARCHAR(50)
);

CREATE OR REPLACE TABLE PRODUCTS (
    product_id    VARCHAR(10)   PRIMARY KEY,
    product_name  VARCHAR(100)  NOT NULL,
    category      VARCHAR(50),
    sub_category  VARCHAR(50),
    unit_cost     FLOAT,
    unit_price    FLOAT,
    supplier_id   VARCHAR(10)   REFERENCES SUPPLIERS(supplier_id)
);

CREATE OR REPLACE TABLE CUSTOMERS (
    customer_id    VARCHAR(10)  PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    segment        VARCHAR(30),
    region         VARCHAR(50),
    city           VARCHAR(50)
);

CREATE OR REPLACE TABLE ORDERS (
    order_id          VARCHAR(15)  PRIMARY KEY,
    order_date        DATE,
    ship_date         DATE,
    status            VARCHAR(20),
    customer_id       VARCHAR(10)  REFERENCES CUSTOMERS(customer_id),
    customer_name     VARCHAR(100),
    segment           VARCHAR(30),
    region            VARCHAR(50),
    city              VARCHAR(50),
    product_id        VARCHAR(10)  REFERENCES PRODUCTS(product_id),
    product_name      VARCHAR(100),
    category          VARCHAR(50),
    sub_category      VARCHAR(50),
    supplier_id       VARCHAR(10)  REFERENCES SUPPLIERS(supplier_id),
    supplier_name     VARCHAR(100),
    supplier_country  VARCHAR(50),
    quantity          INT,
    unit_cost         FLOAT,
    unit_price        FLOAT,
    discount          FLOAT,
    revenue           FLOAT,
    cogs              FLOAT
);

CREATE OR REPLACE TABLE SHIPMENTS (
    shipment_id         VARCHAR(15)  PRIMARY KEY,
    order_id            VARCHAR(15)  REFERENCES ORDERS(order_id),
    carrier             VARCHAR(50),
    ship_date           DATE,
    estimated_delivery  DATE,
    actual_delivery     DATE,
    on_time             BOOLEAN,
    delay_days          INT,
    shipment_cost       FLOAT
);
