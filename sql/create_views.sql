-- ============================================================
-- Supply Chain Analytics — Snowflake Views
-- These views power the Tableau dashboard and Streamlit app
-- ============================================================

USE DATABASE SUPPLY_CHAIN;
USE SCHEMA ANALYTICS;

-- ─────────────────────────────────────────
-- VW_MONTHLY_REVENUE
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_MONTHLY_REVENUE AS
SELECT
    DATE_TRUNC('month', order_date)::DATE           AS month,
    YEAR(order_date)                                AS year,
    MONTH(order_date)                               AS month_num,
    TO_CHAR(order_date, 'Mon YYYY')                 AS month_label,
    COUNT(DISTINCT order_id)                        AS orders,
    ROUND(SUM(revenue), 2)                          AS revenue,
    ROUND(SUM(cogs), 2)                             AS cogs,
    ROUND(SUM(revenue - cogs), 2)                   AS gross_profit,
    ROUND(SUM(revenue - cogs) / NULLIF(SUM(revenue),0) * 100, 2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1, 2, 3, 4;


-- ─────────────────────────────────────────
-- VW_PRODUCT_PERFORMANCE
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_PRODUCT_PERFORMANCE AS
SELECT
    o.product_id,
    o.product_name,
    o.category,
    o.sub_category,
    p.unit_cost,
    p.unit_price,
    COUNT(DISTINCT o.order_id)                      AS orders,
    SUM(o.quantity)                                 AS units_sold,
    ROUND(SUM(o.revenue), 2)                        AS revenue,
    ROUND(SUM(o.cogs), 2)                           AS cogs,
    ROUND(SUM(o.revenue - o.cogs), 2)               AS gross_profit,
    ROUND(SUM(o.revenue - o.cogs) / NULLIF(SUM(o.revenue),0) * 100, 2) AS margin_pct,
    ROUND(AVG(o.discount) * 100, 1)                 AS avg_discount_pct
FROM ORDERS o
JOIN PRODUCTS p ON o.product_id = p.product_id
WHERE o.status = 'Delivered'
GROUP BY 1,2,3,4,5,6;


-- ─────────────────────────────────────────
-- VW_SUPPLIER_SCORECARD
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_SUPPLIER_SCORECARD AS
SELECT
    o.supplier_id,
    o.supplier_name,
    o.supplier_country,
    s.reliability_score,
    s.lead_time_days                                                    AS contracted_lead_days,
    s.category                                                          AS supplier_category,
    COUNT(DISTINCT sh.shipment_id)                                      AS total_shipments,
    SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)                 AS on_time_count,
    ROUND(SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)
          / NULLIF(COUNT(DISTINCT sh.shipment_id), 0) * 100, 2)        AS on_time_rate_pct,
    ROUND(AVG(sh.delay_days), 2)                                        AS avg_delay_days,
    ROUND(SUM(sh.shipment_cost), 2)                                     AS total_shipping_cost,
    ROUND(SUM(o.revenue), 2)                                            AS revenue_handled
FROM ORDERS o
JOIN SHIPMENTS sh ON o.order_id = sh.order_id
JOIN SUPPLIERS s  ON o.supplier_id = s.supplier_id
WHERE o.status = 'Delivered'
GROUP BY 1,2,3,4,5,6;


-- ─────────────────────────────────────────
-- VW_REGIONAL_SUMMARY
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_REGIONAL_SUMMARY AS
SELECT
    region,
    segment,
    COUNT(DISTINCT customer_id)                     AS customers,
    COUNT(DISTINCT order_id)                        AS orders,
    ROUND(SUM(revenue), 2)                          AS revenue,
    ROUND(SUM(cogs), 2)                             AS cogs,
    ROUND(SUM(revenue - cogs), 2)                   AS gross_profit,
    ROUND(SUM(revenue - cogs) / NULLIF(SUM(revenue),0) * 100, 2) AS margin_pct,
    ROUND(AVG(revenue), 2)                          AS avg_order_value
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1,2;


-- ─────────────────────────────────────────
-- VW_CARRIER_PERFORMANCE
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_CARRIER_PERFORMANCE AS
SELECT
    sh.carrier,
    COUNT(*)                                        AS total_shipments,
    SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)  AS on_time_shipments,
    ROUND(SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0) * 100, 2)           AS on_time_pct,
    ROUND(AVG(sh.delay_days), 2)                    AS avg_delay_days,
    ROUND(AVG(sh.shipment_cost), 2)                 AS avg_shipment_cost,
    ROUND(SUM(sh.shipment_cost), 2)                 AS total_shipment_cost
FROM SHIPMENTS sh
JOIN ORDERS o ON sh.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY 1;


-- ─────────────────────────────────────────
-- VW_ORDER_FULFILLMENT
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_ORDER_FULFILLMENT AS
SELECT
    o.order_id,
    o.order_date,
    o.ship_date,
    sh.actual_delivery,
    o.status,
    o.region,
    o.segment,
    o.product_name,
    o.category,
    o.supplier_name,
    sh.carrier,
    sh.on_time,
    sh.delay_days,
    sh.shipment_cost,
    o.quantity,
    o.revenue,
    o.cogs,
    o.revenue - o.cogs                              AS gross_profit,
    DATEDIFF('day', o.order_date, sh.actual_delivery) AS days_to_deliver
FROM ORDERS o
LEFT JOIN SHIPMENTS sh ON o.order_id = sh.order_id;


-- ─────────────────────────────────────────
-- VW_MOM_GROWTH
-- Month-over-month growth for trend analysis
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW VW_MOM_GROWTH AS
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE   AS month,
        SUM(revenue)                            AS revenue,
        SUM(revenue - cogs)                     AS gross_profit,
        COUNT(DISTINCT order_id)                AS orders
    FROM ORDERS
    WHERE status = 'Delivered'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2)       AS revenue,
    ROUND(gross_profit, 2)  AS gross_profit,
    orders,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
          / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2) AS mom_revenue_growth_pct,
    ROUND((orders - LAG(orders) OVER (ORDER BY month))
          / NULLIF(LAG(orders) OVER (ORDER BY month), 0) * 100, 2)  AS mom_orders_growth_pct
FROM monthly;
