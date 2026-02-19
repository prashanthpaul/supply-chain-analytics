# Supply Chain Analytics

An end-to-end data analytics project that combines **Python ETL**, **Snowflake**, **SQL**, **Claude AI**, **Streamlit**, and **Tableau** to deliver supply chain intelligence reporting.

> **Live Demo:** [Streamlit App](http://localhost:8501) &nbsp;|&nbsp; **Dashboard:** `tableau/supply_chain.twb`

---

## Project Overview

This project simulates a real-world supply chain analytics pipeline for a mid-size distributor. It covers 10,000 orders spanning 2022–2024, across 12 global suppliers, 20 product categories, and 30 enterprise customers — and turns that raw data into actionable business intelligence.

**Core Questions Answered:**
- Which products and categories drive the most margin?
- Which suppliers are creating delivery risk?
- Which regions and customer segments are most valuable?
- Is month-over-month revenue growing or declining?
- What are the strategic recommendations for the business?

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Data Generation | Python (pandas, numpy) |
| Cloud Warehouse | Snowflake |
| Transformation | SQL (CTEs, Window Functions, Views) |
| AI Reporting | Claude API (claude-sonnet-4-6) |
| Interactive App | Streamlit + Plotly |
| BI Dashboard | Tableau Desktop (.twb) |
| Orchestration | Python pipeline runner |

---

## Architecture

```
data/generate_data.py
        │
        ▼ 10K rows (CSV)
etl/load_snowflake.py
        │
        ▼ Snowflake: SUPPLY_CHAIN.ANALYTICS
sql/schema.sql         → 5 core tables
sql/create_views.sql   → 6 analytical views
sql/analysis_queries.sql → KPI queries
        │
        ├──► streamlit/app.py   (interactive reporting)
        ├──► tableau/supply_chain.twb  (BI dashboard)
        └──► ai/report_generator.py   (Claude AI reports)
```

---

## Project Structure

```
supply-chain-analytics/
├── data/
│   ├── generate_data.py        # Synthetic data generator (10K orders)
│   └── raw/                    # Generated CSVs (gitignored)
├── sql/
│   ├── schema.sql              # Snowflake DDL (5 tables)
│   ├── create_views.sql        # 6 analytical views
│   └── analysis_queries.sql   # Business intelligence queries
├── etl/
│   └── load_snowflake.py       # ETL: CSV → Snowflake
├── ai/
│   └── report_generator.py     # Claude AI weekly report generator
├── streamlit/
│   └── app.py                  # Streamlit reporting dashboard
├── tableau/
│   └── supply_chain.twb        # Tableau workbook (open in Tableau Desktop)
├── scripts/
│   └── run_pipeline.py         # One-command pipeline orchestrator
├── reports/                    # Auto-generated AI reports (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/prashanthpaul/supply-chain-analytics.git
cd supply-chain-analytics

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Snowflake credentials and Anthropic API key
```

### 3. Run Full Pipeline

```bash
python scripts/run_pipeline.py
```

This will:
1. Generate 10,000 rows of synthetic supply chain data
2. Load all data into Snowflake and create analytical views
3. Generate a Claude AI weekly intelligence report
4. Launch the Streamlit dashboard at http://localhost:8501

### 4. Open Tableau Dashboard

1. Open Tableau Desktop
2. File → Open → `tableau/supply_chain.twb`
3. Update data source connection (enter your Snowflake credentials)
4. Click "Connect" — all 5 dashboards will auto-populate

---

## SQL Highlights

The project demonstrates production-grade SQL patterns:

```sql
-- Month-over-month growth using LAG window function
WITH monthly AS (
    SELECT DATE_TRUNC('month', order_date) AS month,
           SUM(revenue) AS revenue
    FROM ORDERS WHERE status = 'Delivered'
    GROUP BY 1
)
SELECT month, revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2) AS mom_growth_pct
FROM monthly;
```

```sql
-- Supplier risk scorecard with on-time rate calculation
SELECT supplier_name,
       ROUND(SUM(CASE WHEN sh.on_time THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0) * 100, 2) AS on_time_rate_pct,
       ROUND(AVG(sh.delay_days), 2) AS avg_delay_days
FROM ORDERS o
JOIN SHIPMENTS sh ON o.order_id = sh.order_id
WHERE o.status = 'Delivered'
GROUP BY 1
ORDER BY on_time_rate_pct;
```

---

## Tableau Dashboard Pages

| Sheet | Visualization | Data Source |
|-------|---------------|-------------|
| Revenue Trend | Bar chart (monthly) | VW_MONTHLY_REVENUE |
| Top Products | Horizontal bar | VW_PRODUCT_PERFORMANCE |
| Supplier On-Time Rate | Color-coded bar | VW_SUPPLIER_SCORECARD |
| Regional Revenue | Stacked bar by segment | VW_REGIONAL_SUMMARY |
| Carrier Performance | Scatter (cost vs reliability) | VW_CARRIER_PERFORMANCE |
| Revenue vs Margin | Bubble chart | VW_PRODUCT_PERFORMANCE |

---

## AI Report Sample

The Claude AI module generates executive-level reports like:

> **Strategic Recommendations:**
> 1. **Diversify away from GreatWall Manufacturing** — 76% on-time rate is the lowest in the supplier base and is creating compounding delays in the Heavy Equipment category
> 2. **Double down on Electronics** — highest margin category at 48%+ with growing demand signals
> 3. **Renegotiate with Kuehne+Nagel** — 22% cost premium over average with no reliability advantage vs DHL

---

## Key Metrics (Sample Data)

| Metric | Value |
|--------|-------|
| Total Orders | 10,000 |
| Delivered Orders | ~6,700 |
| Gross Revenue | ~$42M |
| Gross Margin | ~43% |
| Suppliers | 12 |
| Products | 20 |
| Customers | 30 |
| Date Range | Jan 2022 – Dec 2024 |

---

## Author

**Prashanth Paul**
- LinkedIn: [linkedin.com/in/prashanthpaul12](https://www.linkedin.com/in/prashanthpaul12/)
- GitHub: [github.com/prashanthpaul](https://github.com/prashanthpaul)
