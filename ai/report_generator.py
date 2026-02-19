"""
Supply Chain Analytics — AI Report Generator
Uses Claude to generate natural-language weekly business intelligence reports
from Snowflake data summaries.
"""
import os
import sys
import json
from datetime import date, datetime
from typing import Optional

import anthropic
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SNOWFLAKE_CONFIG = {
    "account":   os.environ["SNOWFLAKE_ACCOUNT"],
    "user":      os.environ["SNOWFLAKE_USER"],
    "password":  os.environ["SNOWFLAKE_PASSWORD"],
    "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database":  os.environ.get("SNOWFLAKE_DATABASE", "SUPPLY_CHAIN"),
    "schema":    os.environ.get("SNOWFLAKE_SCHEMA", "ANALYTICS"),
}

CLAUDE_MODEL = "claude-sonnet-4-6"


# ─────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────
def _run_query(conn, sql: str) -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute(sql)
    cols = [desc[0].lower() for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows, columns=cols)


def fetch_kpi_snapshot(conn) -> dict:
    """Pull the key numbers needed to fill a report context."""

    revenue_sql = """
        SELECT
            ROUND(SUM(revenue),2)                                             AS gross_revenue,
            ROUND(SUM(cogs),2)                                                AS total_cogs,
            ROUND(SUM(revenue-cogs),2)                                        AS gross_profit,
            ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2)            AS margin_pct,
            COUNT(DISTINCT order_id)                                          AS total_orders,
            ROUND(AVG(revenue),2)                                             AS avg_order_value
        FROM ORDERS
        WHERE status='Delivered'
    """

    top_products_sql = """
        SELECT product_name, ROUND(SUM(revenue),2) AS revenue
        FROM ORDERS WHERE status='Delivered'
        GROUP BY 1 ORDER BY revenue DESC LIMIT 5
    """

    top_regions_sql = """
        SELECT region, ROUND(SUM(revenue),2) AS revenue
        FROM ORDERS WHERE status='Delivered'
        GROUP BY 1 ORDER BY revenue DESC
    """

    supplier_sql = """
        SELECT
            o.supplier_name,
            ROUND(AVG(sh.delay_days),2) AS avg_delay,
            ROUND(SUM(CASE WHEN sh.on_time THEN 1 ELSE 0 END)*100.0
                  /NULLIF(COUNT(*),0),1) AS on_time_pct
        FROM ORDERS o
        JOIN SHIPMENTS sh ON o.order_id=sh.order_id
        WHERE o.status='Delivered'
        GROUP BY 1
        ORDER BY on_time_pct ASC
        LIMIT 5
    """

    carrier_sql = """
        SELECT carrier,
               ROUND(SUM(CASE WHEN on_time THEN 1 ELSE 0 END)*100.0
                     /NULLIF(COUNT(*),0),1) AS on_time_pct,
               ROUND(AVG(shipment_cost),2) AS avg_cost
        FROM SHIPMENTS
        WHERE on_time IS NOT NULL
        GROUP BY 1
        ORDER BY on_time_pct DESC
    """

    mom_sql = """
        SELECT month, revenue, mom_revenue_growth_pct
        FROM VW_MOM_GROWTH
        ORDER BY month DESC
        LIMIT 3
    """

    return {
        "kpis":         _run_query(conn, revenue_sql).to_dict(orient="records")[0],
        "top_products": _run_query(conn, top_products_sql).to_dict(orient="records"),
        "top_regions":  _run_query(conn, top_regions_sql).to_dict(orient="records"),
        "suppliers":    _run_query(conn, supplier_sql).to_dict(orient="records"),
        "carriers":     _run_query(conn, carrier_sql).to_dict(orient="records"),
        "mom_trend":    _run_query(conn, mom_sql).to_dict(orient="records"),
    }


# ─────────────────────────────────────────
# CLAUDE REPORT GENERATION
# ─────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior supply chain business intelligence analyst.
Your job is to transform raw KPI data into clear, executive-level reports.
Be specific with numbers, identify risks and opportunities, and keep each section concise.
Use a professional but readable tone. Format output in clean Markdown."""

REPORT_PROMPT_TEMPLATE = """
Based on the following supply chain KPI snapshot, write a comprehensive Weekly Supply Chain Intelligence Report.

DATA SNAPSHOT:
{data}

Structure the report with these sections:

## Executive Summary
2-3 bullet points covering the most important takeaways from this period.

## Revenue & Profitability
Analyze gross revenue, gross profit, margin %, and average order value. Note any trends.

## Top Performing Products
Highlight the top 5 products and what they tell us about demand concentration.

## Regional Performance
Break down revenue by region. Identify the strongest and weakest regions.

## Supplier Risk Assessment
For each supplier listed, assess their on-time rate and average delay.
Flag any suppliers with on-time rates below 85% as HIGH RISK.
Flag suppliers between 85-92% as MEDIUM RISK.

## Logistics & Carrier Analysis
Evaluate carrier performance. Identify which carriers are most reliable and most cost-effective.

## Month-over-Month Trend
Interpret the revenue growth trend. Is growth accelerating or decelerating?

## Strategic Recommendations
Provide 3-5 specific, actionable recommendations based on the data. Be direct.
"""


def generate_report(data: dict, client: anthropic.Anthropic) -> str:
    data_str = json.dumps(data, indent=2, default=str)
    prompt = REPORT_PROMPT_TEMPLATE.format(data=data_str)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_anomaly_alert(data: dict, client: anthropic.Anthropic) -> str:
    """Quick anomaly scan — returns a short alert summary."""
    prompt = f"""
Scan the following supply chain data snapshot for anomalies, risks, or unusual patterns:

{json.dumps(data, indent=2, default=str)}

Return a brief alert summary (max 200 words) in Markdown listing:
- Any suppliers with on-time rate below 80%
- Any carriers with on-time rate below 85%
- Any unusual revenue patterns
- Overall risk level: LOW / MEDIUM / HIGH
"""
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main(report_type: str = "weekly"):
    print("🔌  Connecting to Snowflake ...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)

    print("📊  Fetching KPI snapshot ...")
    data = fetch_kpi_snapshot(conn)
    conn.close()

    print("🤖  Generating AI report with Claude ...")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if report_type == "anomaly":
        report = generate_anomaly_alert(data, client)
        print("\n⚠️  ANOMALY ALERT\n" + "─" * 60)
    else:
        report = generate_report(data, client)
        print(f"\n📋  WEEKLY SUPPLY CHAIN REPORT — {date.today()}\n" + "─" * 60)

    print(report)

    # Save to file
    out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"report_{report_type}_{date.today().isoformat()}.md"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w") as f:
        f.write(f"# Supply Chain {report_type.title()} Report — {date.today()}\n\n")
        f.write(report)
    print(f"\n💾  Saved to: {out_path}")


if __name__ == "__main__":
    rtype = sys.argv[1] if len(sys.argv) > 1 else "weekly"
    main(rtype)
