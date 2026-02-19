-- ============================================================
-- Supply Chain Analytics — Key Business Queries
-- Database: SUPPLY_CHAIN | Schema: ANALYTICS
-- ============================================================

USE DATABASE SUPPLY_CHAIN;
USE SCHEMA ANALYTICS;

-- ─────────────────────────────────────────
-- 1. REVENUE & PROFITABILITY KPIs
-- ─────────────────────────────────────────

-- Overall revenue summary
SELECT
    COUNT(DISTINCT order_id)                                AS total_orders,
    SUM(revenue)                                            AS gross_revenue,
    SUM(cogs)                                               AS total_cogs,
    SUM(revenue - cogs)                                     AS gross_profit,
    ROUND(SUM(revenue - cogs) / NULLIF(SUM(revenue),0)*100,2) AS gross_margin_pct,
    ROUND(AVG(revenue),2)                                   AS avg_order_value
FROM ORDERS
WHERE status = 'Delivered';

-- Monthly revenue trend (2022–2024)
SELECT
    DATE_TRUNC('month', order_date)  AS month,
    COUNT(DISTINCT order_id)         AS orders,
    ROUND(SUM(revenue),2)            AS revenue,
    ROUND(SUM(revenue - cogs),2)     AS gross_profit,
    ROUND(SUM(revenue - cogs) / NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1
ORDER BY 1;

-- Revenue by product category
SELECT
    category,
    COUNT(DISTINCT order_id)    AS orders,
    ROUND(SUM(revenue),2)       AS revenue,
    ROUND(SUM(cogs),2)          AS cogs,
    ROUND(SUM(revenue-cogs),2)  AS gross_profit,
    ROUND(SUM(revenue-cogs) / NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1
ORDER BY revenue DESC;


-- ─────────────────────────────────────────
-- 2. TOP PRODUCTS & CUSTOMERS
-- ─────────────────────────────────────────

-- Top 10 products by revenue
SELECT
    product_id,
    product_name,
    category,
    COUNT(DISTINCT order_id)    AS orders,
    SUM(quantity)               AS units_sold,
    ROUND(SUM(revenue),2)       AS revenue,
    ROUND(SUM(revenue-cogs),2)  AS profit,
    ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1,2,3
ORDER BY revenue DESC
LIMIT 10;

-- Top 10 customers by revenue
SELECT
    customer_id,
    customer_name,
    segment,
    region,
    COUNT(DISTINCT order_id)    AS orders,
    ROUND(SUM(revenue),2)       AS lifetime_revenue,
    ROUND(AVG(revenue),2)       AS avg_order_value,
    ROUND(SUM(revenue-cogs),2)  AS lifetime_profit
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1,2,3,4
ORDER BY lifetime_revenue DESC
LIMIT 10;

-- Revenue by customer segment
SELECT
    segment,
    COUNT(DISTINCT customer_id)  AS customers,
    COUNT(DISTINCT order_id)     AS orders,
    ROUND(SUM(revenue),2)        AS total_revenue,
    ROUND(AVG(revenue),2)        AS avg_order_value,
    ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1
ORDER BY total_revenue DESC;


-- ─────────────────────────────────────────
-- 3. SUPPLIER PERFORMANCE
-- ─────────────────────────────────────────

-- Supplier scorecard
SELECT
    o.supplier_id,
    o.supplier_name,
    o.supplier_country,
    s.reliability_score,
    s.lead_time_days                                                AS contracted_lead_days,
    COUNT(DISTINCT sh.shipment_id)                                  AS total_shipments,
    SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)             AS on_time_deliveries,
    ROUND(SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)
          / NULLIF(COUNT(DISTINCT sh.shipment_id),0) * 100, 2)     AS on_time_rate_pct,
    ROUND(AVG(sh.delay_days), 2)                                    AS avg_delay_days,
    ROUND(SUM(sh.shipment_cost), 2)                                 AS total_shipping_cost,
    ROUND(AVG(sh.shipment_cost), 2)                                 AS avg_shipment_cost,
    ROUND(SUM(o.revenue), 2)                                        AS revenue_handled
FROM ORDERS o
JOIN SHIPMENTS sh ON o.order_id = sh.order_id
JOIN SUPPLIERS s  ON o.supplier_id = s.supplier_id
WHERE o.status = 'Delivered'
GROUP BY 1,2,3,4,5
ORDER BY on_time_rate_pct DESC;

-- Supplier delay distribution
SELECT
    o.supplier_name,
    sh.delay_days,
    COUNT(*) AS shipment_count
FROM ORDERS o
JOIN SHIPMENTS sh ON o.order_id = sh.order_id
WHERE o.status = 'Delivered'
  AND sh.delay_days IS NOT NULL
GROUP BY 1,2
ORDER BY 1, 2;


-- ─────────────────────────────────────────
-- 4. SHIPPING & LOGISTICS
-- ─────────────────────────────────────────

-- Carrier performance
SELECT
    sh.carrier,
    COUNT(*) AS shipments,
    SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END) AS on_time,
    ROUND(SUM(CASE WHEN sh.on_time = TRUE THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*),0) * 100, 2)               AS on_time_pct,
    ROUND(AVG(sh.delay_days), 2)                       AS avg_delay_days,
    ROUND(AVG(sh.shipment_cost), 2)                    AS avg_cost,
    ROUND(SUM(sh.shipment_cost), 2)                    AS total_cost
FROM SHIPMENTS sh
JOIN ORDERS o ON sh.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY 1
ORDER BY on_time_pct DESC;

-- Avg days from order to delivery by region
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                                          AS orders,
    ROUND(AVG(DATEDIFF('day', o.order_date, sh.actual_delivery)), 1)    AS avg_fulfillment_days,
    ROUND(AVG(sh.delay_days), 2)                                        AS avg_delay_days,
    ROUND(AVG(sh.shipment_cost), 2)                                     AS avg_shipment_cost
FROM ORDERS o
JOIN SHIPMENTS sh ON o.order_id = sh.order_id
WHERE o.status = 'Delivered'
GROUP BY 1
ORDER BY avg_fulfillment_days DESC;

-- Order status breakdown
SELECT
    status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM ORDERS
GROUP BY 1
ORDER BY order_count DESC;


-- ─────────────────────────────────────────
-- 5. REGIONAL ANALYSIS
-- ─────────────────────────────────────────

-- Revenue by region and segment (pivot-ready)
SELECT
    region,
    segment,
    COUNT(DISTINCT order_id)    AS orders,
    ROUND(SUM(revenue),2)       AS revenue,
    ROUND(SUM(revenue-cogs),2)  AS profit,
    ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY 1,2
ORDER BY revenue DESC;


-- ─────────────────────────────────────────
-- 6. ADVANCED ANALYTICS (Window Functions)
-- ─────────────────────────────────────────

-- Month-over-month revenue growth
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date)  AS month,
        SUM(revenue)                     AS revenue
    FROM ORDERS
    WHERE status = 'Delivered'
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2)    AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2)  AS prev_month_revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
          / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Running total revenue by year
SELECT
    order_date,
    YEAR(order_date)    AS year,
    revenue,
    ROUND(SUM(revenue) OVER (
        PARTITION BY YEAR(order_date)
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ), 2)               AS running_total_ytd
FROM ORDERS
WHERE status = 'Delivered'
ORDER BY order_date;

-- Customer ranking by revenue within each segment (RANK)
WITH customer_revenue AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM ORDERS
    WHERE status = 'Delivered'
    GROUP BY 1,2,3
)
SELECT
    segment,
    customer_name,
    total_revenue,
    RANK() OVER (PARTITION BY segment ORDER BY total_revenue DESC) AS rank_in_segment
FROM customer_revenue
ORDER BY segment, rank_in_segment
LIMIT 30;

-- 30-day rolling average revenue
SELECT
    order_date,
    ROUND(SUM(revenue), 2)  AS daily_revenue,
    ROUND(AVG(SUM(revenue)) OVER (
        ORDER BY order_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2)                   AS rolling_30d_avg
FROM ORDERS
WHERE status = 'Delivered'
GROUP BY order_date
ORDER BY order_date;


-- ─────────────────────────────────────────
-- 7. INVENTORY / DEMAND SIGNAL
-- ─────────────────────────────────────────

-- Product velocity — average units ordered per month
WITH monthly_demand AS (
    SELECT
        product_id,
        product_name,
        DATE_TRUNC('month', order_date) AS month,
        SUM(quantity)                   AS units_ordered
    FROM ORDERS
    WHERE status IN ('Delivered', 'Shipped')
    GROUP BY 1,2,3
)
SELECT
    product_id,
    product_name,
    ROUND(AVG(units_ordered), 1)   AS avg_monthly_units,
    MIN(units_ordered)             AS min_month_units,
    MAX(units_ordered)             AS max_month_units,
    COUNT(DISTINCT month)          AS months_active
FROM monthly_demand
GROUP BY 1,2
ORDER BY avg_monthly_units DESC;
