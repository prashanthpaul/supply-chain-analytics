"""
Supply Chain Analytics — Streamlit Dashboard
Interactive reporting interface powered by Snowflake + Claude AI
"""
import os
import sys
import json
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

# Add project root to path so we can import ai module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# SNOWFLAKE CONNECTION (cached)
# ─────────────────────────────────────────
@st.cache_resource
def get_snowflake_conn():
    import snowflake.connector
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "SUPPLY_CHAIN"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "ANALYTICS"),
    )


@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_snowflake_conn()
    cur = conn.cursor()
    cur.execute(sql)
    cols = [desc[0].lower() for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows, columns=cols)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/supply-chain.png", width=60)
    st.title("Supply Chain\nAnalytics")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Executive Overview", "📦 Products", "🏭 Suppliers", "🚚 Logistics", "🤖 AI Report"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(f"Data: SUPPLY_CHAIN.ANALYTICS")
    st.caption(f"Last refresh: {date.today()}")


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def metric_card(col, label, value, delta=None):
    col.metric(label, value, delta)


ACCENT = "#4f8ef7"


# ─────────────────────────────────────────
# PAGE 1 — EXECUTIVE OVERVIEW
# ─────────────────────────────────────────
if page == "📊 Executive Overview":
    st.title("📊 Executive Overview")
    st.markdown("High-level KPIs, revenue trends, and regional performance across all delivered orders.")

    # KPI row
    kpi = run_query("""
        SELECT
            ROUND(SUM(revenue),2)                                     AS gross_revenue,
            ROUND(SUM(cogs),2)                                        AS cogs,
            ROUND(SUM(revenue-cogs),2)                                AS gross_profit,
            ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2)    AS margin_pct,
            COUNT(DISTINCT order_id)                                  AS total_orders,
            ROUND(AVG(revenue),2)                                     AS avg_order_value
        FROM ORDERS WHERE status='Delivered'
    """).iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Gross Revenue", f"${kpi['gross_revenue']:,.0f}")
    c2.metric("Gross Profit",  f"${kpi['gross_profit']:,.0f}")
    c3.metric("Margin %",      f"{kpi['margin_pct']}%")
    c4.metric("Total Orders",  f"{int(kpi['total_orders']):,}")
    c5.metric("Avg Order Value", f"${kpi['avg_order_value']:,.2f}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # Monthly revenue trend
    with col_left:
        st.subheader("Monthly Revenue Trend")
        monthly = run_query("""
            SELECT month, revenue, gross_profit, margin_pct
            FROM VW_MONTHLY_REVENUE
            ORDER BY month
        """)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly["month"], y=monthly["revenue"],
                              name="Revenue", marker_color=ACCENT))
        fig.add_trace(go.Bar(x=monthly["month"], y=monthly["gross_profit"],
                              name="Gross Profit", marker_color="#34d399"))
        fig.update_layout(barmode="overlay", height=350, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Revenue by region
    with col_right:
        st.subheader("Revenue by Region")
        region = run_query("""
            SELECT region, SUM(revenue) AS revenue
            FROM VW_REGIONAL_SUMMARY
            GROUP BY region ORDER BY revenue DESC
        """)
        fig2 = px.pie(region, names="region", values="revenue",
                      color_discrete_sequence=px.colors.qualitative.Pastel,
                      hole=0.4)
        fig2.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # Order status breakdown
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Order Status Breakdown")
        status_df = run_query("""
            SELECT status, COUNT(*) AS orders
            FROM ORDERS GROUP BY status ORDER BY orders DESC
        """)
        fig3 = px.bar(status_df, x="status", y="orders",
                      color="status", text="orders",
                      color_discrete_sequence=px.colors.qualitative.Safe)
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.subheader("Revenue by Customer Segment")
        seg = run_query("""
            SELECT segment, revenue, margin_pct FROM VW_REGIONAL_SUMMARY
            GROUP BY segment, revenue, margin_pct ORDER BY revenue DESC
        """)
        seg_agg = seg.groupby("segment").agg(revenue=("revenue","sum")).reset_index()
        fig4 = px.bar(seg_agg, x="segment", y="revenue",
                      color="segment", text_auto=".3s",
                      color_discrete_sequence=["#4f8ef7","#f59e0b","#10b981"])
        fig4.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────
# PAGE 2 — PRODUCTS
# ─────────────────────────────────────────
elif page == "📦 Products":
    st.title("📦 Product Performance")

    prod = run_query("""
        SELECT product_name, category, sub_category, orders, units_sold,
               revenue, gross_profit, margin_pct, avg_discount_pct
        FROM VW_PRODUCT_PERFORMANCE
        ORDER BY revenue DESC
    """)

    # Category filter
    cats = ["All"] + sorted(prod["category"].unique().tolist())
    sel_cat = st.selectbox("Filter by Category", cats)
    if sel_cat != "All":
        prod = prod[prod["category"] == sel_cat]

    st.markdown(f"Showing **{len(prod)}** products")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Products by Revenue")
        fig = px.bar(prod.head(15), x="revenue", y="product_name",
                     orientation="h", color="category", text="revenue",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(texttemplate="%{text:$,.0f}", textposition="outside")
        fig.update_layout(height=450, yaxis=dict(autorange="reversed"),
                          margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Margin % by Product")
        fig2 = px.scatter(prod, x="revenue", y="margin_pct",
                          size="units_sold", color="category",
                          hover_name="product_name",
                          labels={"revenue": "Revenue ($)", "margin_pct": "Margin %"},
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.add_hline(y=prod["margin_pct"].mean(), line_dash="dash",
                        annotation_text="Avg Margin")
        fig2.update_layout(height=450, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Full Product Table")
    st.dataframe(
        prod.style.format({
            "revenue": "${:,.0f}", "gross_profit": "${:,.0f}",
            "margin_pct": "{:.1f}%", "avg_discount_pct": "{:.1f}%",
        }),
        use_container_width=True,
        height=350,
    )


# ─────────────────────────────────────────
# PAGE 3 — SUPPLIERS
# ─────────────────────────────────────────
elif page == "🏭 Suppliers":
    st.title("🏭 Supplier Scorecard")

    sup = run_query("""
        SELECT supplier_name, supplier_country, supplier_category,
               reliability_score, contracted_lead_days,
               total_shipments, on_time_rate_pct, avg_delay_days,
               total_shipping_cost, revenue_handled
        FROM VW_SUPPLIER_SCORECARD
        ORDER BY on_time_rate_pct DESC
    """)

    # Risk flags
    def risk_label(pct):
        if pct < 85:   return "🔴 HIGH"
        if pct < 92:   return "🟡 MEDIUM"
        return "🟢 LOW"

    sup["risk"] = sup["on_time_rate_pct"].apply(risk_label)

    c1, c2, c3 = st.columns(3)
    c1.metric("Suppliers", len(sup))
    c2.metric("Avg On-Time Rate", f"{sup['on_time_rate_pct'].mean():.1f}%")
    c3.metric("Total Shipping Cost", f"${sup['total_shipping_cost'].sum():,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("On-Time Delivery Rate by Supplier")
        fig = px.bar(sup.sort_values("on_time_rate_pct"), x="on_time_rate_pct",
                     y="supplier_name", orientation="h",
                     color="on_time_rate_pct",
                     color_continuous_scale=["#ef4444","#f59e0b","#10b981"],
                     labels={"on_time_rate_pct": "On-Time %"})
        fig.add_vline(x=92, line_dash="dot", line_color="gray",
                      annotation_text="92% threshold")
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg Delay Days by Supplier")
        fig2 = px.bar(sup.sort_values("avg_delay_days", ascending=False),
                      x="supplier_name", y="avg_delay_days",
                      color="avg_delay_days",
                      color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                      labels={"avg_delay_days": "Avg Delay (days)"})
        fig2.update_layout(height=400, xaxis_tickangle=-30,
                           margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Supplier Risk Table")
    st.dataframe(
        sup[["supplier_name","supplier_country","on_time_rate_pct",
             "avg_delay_days","total_shipments","risk","revenue_handled"]].style.format({
            "on_time_rate_pct": "{:.1f}%",
            "avg_delay_days": "{:.2f}",
            "revenue_handled": "${:,.0f}",
        }),
        use_container_width=True,
    )


# ─────────────────────────────────────────
# PAGE 4 — LOGISTICS
# ─────────────────────────────────────────
elif page == "🚚 Logistics":
    st.title("🚚 Logistics & Carrier Performance")

    carrier = run_query("SELECT * FROM VW_CARRIER_PERFORMANCE ORDER BY on_time_pct DESC")
    fulfill = run_query("""
        SELECT region,
               ROUND(AVG(days_to_deliver),1)  AS avg_days,
               ROUND(AVG(delay_days),2)        AS avg_delay,
               ROUND(AVG(shipment_cost),2)     AS avg_cost
        FROM VW_ORDER_FULFILLMENT
        WHERE status='Delivered'
        GROUP BY region ORDER BY avg_days DESC
    """)

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg On-Time %",   f"{carrier['on_time_pct'].mean():.1f}%")
    c2.metric("Total Shipment Cost", f"${carrier['total_shipment_cost'].sum():,.0f}")
    c3.metric("Avg Shipment Cost", f"${carrier['avg_shipment_cost'].mean():.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Carrier On-Time Performance")
        fig = px.bar(carrier, x="carrier", y="on_time_pct",
                     color="on_time_pct", text="on_time_pct",
                     color_continuous_scale=["#ef4444","#10b981"],
                     labels={"on_time_pct": "On-Time %"})
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg Shipment Cost by Carrier")
        fig2 = px.bar(carrier, x="carrier", y="avg_shipment_cost",
                      text="avg_shipment_cost",
                      color_discrete_sequence=[ACCENT])
        fig2.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
        fig2.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Fulfillment Time by Region")
    fig3 = px.bar(fulfill, x="region", y="avg_days", color="avg_delay",
                  text="avg_days",
                  color_continuous_scale=["#10b981","#ef4444"],
                  labels={"avg_days": "Avg Days to Deliver", "avg_delay": "Avg Delay"})
    fig3.update_traces(texttemplate="%{text:.1f}d", textposition="outside")
    fig3.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Carrier Detail")
    st.dataframe(carrier.style.format({
        "on_time_pct": "{:.1f}%",
        "avg_delay_days": "{:.2f}",
        "avg_shipment_cost": "${:.2f}",
        "total_shipment_cost": "${:,.0f}",
    }), use_container_width=True)


# ─────────────────────────────────────────
# PAGE 5 — AI REPORT
# ─────────────────────────────────────────
elif page == "🤖 AI Report":
    st.title("🤖 AI-Powered Supply Chain Report")
    st.markdown(
        "Generate an executive-level intelligence report using **Claude AI**. "
        "The report analyses live Snowflake data and provides strategic recommendations."
    )

    report_type = st.radio("Report Type", ["Weekly Summary", "Anomaly Alert"],
                            horizontal=True)

    if st.button("Generate Report ✨", type="primary"):
        import anthropic as _anthropic
        from ai.report_generator import fetch_kpi_snapshot, generate_report, generate_anomaly_alert

        with st.spinner("Fetching data from Snowflake and consulting Claude AI..."):
            try:
                import snowflake.connector
                conn = snowflake.connector.connect(
                    account=os.environ["SNOWFLAKE_ACCOUNT"],
                    user=os.environ["SNOWFLAKE_USER"],
                    password=os.environ["SNOWFLAKE_PASSWORD"],
                    warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
                    database=os.environ.get("SNOWFLAKE_DATABASE", "SUPPLY_CHAIN"),
                    schema=os.environ.get("SNOWFLAKE_SCHEMA", "ANALYTICS"),
                )
                data = fetch_kpi_snapshot(conn)
                conn.close()

                client = _anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

                if report_type == "Anomaly Alert":
                    report = generate_anomaly_alert(data, client)
                else:
                    report = generate_report(data, client)

                st.success("Report generated successfully!")
                st.markdown("---")
                st.markdown(report)

                # Download button
                st.download_button(
                    label="Download Report (.md)",
                    data=report,
                    file_name=f"supply_chain_{report_type.lower().replace(' ','_')}_{date.today()}.md",
                    mime="text/markdown",
                )

            except Exception as e:
                st.error(f"Error generating report: {e}")
                st.info("Make sure ANTHROPIC_API_KEY is set in your .env file.")
    else:
        st.info("Click **Generate Report** to create a fresh AI-powered analysis.")

        # Show a sample preview
        with st.expander("Sample Report Preview"):
            st.markdown("""
## Executive Summary
- Gross revenue of **$42.3M** with a **43.1% gross margin** across 8,247 delivered orders
- **North America** leads all regions with 34% of total revenue
- **2 suppliers** flagged as HIGH RISK due to on-time rates below 85%

## Strategic Recommendations
1. **Diversify from GreatWall Manufacturing** — 76% on-time rate is causing downstream delays
2. **Increase Electronics category allocation** — highest margin at 48.2%
3. **Negotiate with Kuehne+Nagel** — 22% cost premium over average with no service advantage
            """)
