"""
Supply Chain Analytics — Executive Dashboard
Dark professional theme, tab-based nav, custom KPI cards,
gauge charts, treemaps, heatmaps — powered by Snowflake + Claude AI
"""
import os
import sys
import json
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Command Center",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CUSTOM CSS — Dark Executive Theme
# ─────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Background */
  .stApp { background: #0d1117; color: #e6edf3; }

  /* Hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 2rem 2rem 2rem; max-width: 100%; }

  /* Top header bar */
  .dash-header {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border-bottom: 1px solid #30363d;
    padding: 18px 32px;
    margin: -1rem -2rem 2rem -2rem;
    display: flex; align-items: center; justify-content: space-between;
  }
  .dash-title { font-size: 22px; font-weight: 700; color: #e6edf3; letter-spacing: -0.3px; }
  .dash-subtitle { font-size: 13px; color: #8b949e; margin-top: 2px; }
  .dash-badge {
    background: #21262d; border: 1px solid #30363d; border-radius: 20px;
    padding: 6px 14px; font-size: 12px; color: #8b949e;
  }
  .dash-badge span { color: #3fb950; font-weight: 600; }

  /* KPI card */
  .kpi-card {
    background: #161b22; border: 1px solid #21262d; border-radius: 12px;
    padding: 20px 24px; position: relative; overflow: hidden;
    transition: border-color .2s;
  }
  .kpi-card:hover { border-color: #388bfd; }
  .kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  }
  .kpi-card.green::before  { background: linear-gradient(90deg, #3fb950, #26a641); }
  .kpi-card.blue::before   { background: linear-gradient(90deg, #388bfd, #1f6feb); }
  .kpi-card.yellow::before { background: linear-gradient(90deg, #d29922, #b08800); }
  .kpi-card.purple::before { background: linear-gradient(90deg, #a371f7, #8957e5); }
  .kpi-card.red::before    { background: linear-gradient(90deg, #f85149, #da3633); }

  .kpi-label { font-size: 12px; font-weight: 500; color: #8b949e; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 8px; }
  .kpi-value { font-size: 32px; font-weight: 700; color: #e6edf3; letter-spacing: -1px; line-height: 1; }
  .kpi-sub   { font-size: 12px; color: #8b949e; margin-top: 6px; }
  .kpi-trend-up   { color: #3fb950; font-weight: 600; }
  .kpi-trend-down { color: #f85149; font-weight: 600; }

  /* Section heading */
  .section-heading {
    font-size: 16px; font-weight: 600; color: #e6edf3;
    border-left: 3px solid #388bfd; padding-left: 10px;
    margin: 28px 0 16px 0;
  }

  /* Risk badge */
  .risk-high   { background: #3d1a1a; color: #f85149; border: 1px solid #f8514940; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
  .risk-medium { background: #2d2200; color: #d29922; border: 1px solid #d2992240; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
  .risk-low    { background: #122112; color: #3fb950; border: 1px solid #3fb95040; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }

  /* Alert box */
  .alert-box {
    background: #1c2333; border: 1px solid #30363d; border-radius: 10px;
    padding: 16px 20px; margin-bottom: 12px;
    border-left: 4px solid #388bfd;
  }
  .alert-box.warn { border-left-color: #d29922; }
  .alert-box.danger { border-left-color: #f85149; }
  .alert-title { font-size: 14px; font-weight: 600; color: #e6edf3; margin-bottom: 4px; }
  .alert-body  { font-size: 13px; color: #8b949e; }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] {
    background: #161b22; border-bottom: 1px solid #21262d;
    padding: 0; gap: 0; margin-bottom: 24px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #8b949e; background: transparent; border: none;
    padding: 14px 22px; font-size: 14px; font-weight: 500;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
  }
  .stTabs [aria-selected="true"] {
    color: #e6edf3 !important; border-bottom-color: #388bfd !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab"]:hover { color: #e6edf3; background: #21262d; }

  /* Chart container */
  .chart-box {
    background: #161b22; border: 1px solid #21262d; border-radius: 12px;
    padding: 20px; margin-bottom: 16px;
  }
  .chart-title { font-size: 14px; font-weight: 600; color: #e6edf3; margin-bottom: 4px; }
  .chart-sub   { font-size: 12px; color: #8b949e; margin-bottom: 14px; }

  /* Table */
  .stDataFrame { background: #161b22; }
  .stDataFrame thead th { background: #21262d !important; color: #8b949e !important; }

  /* Selectbox / radio */
  .stSelectbox > div > div { background: #21262d; border-color: #30363d; color: #e6edf3; }
  .stRadio label { color: #8b949e; font-size: 13px; }

  /* Progress bars */
  .prog-wrap { margin-bottom: 14px; }
  .prog-header { display: flex; justify-content: space-between; margin-bottom: 5px; }
  .prog-name { font-size: 13px; color: #c9d1d9; }
  .prog-val  { font-size: 13px; font-weight: 600; color: #e6edf3; }
  .prog-bar  { height: 8px; background: #21262d; border-radius: 10px; overflow: hidden; }
  .prog-fill { height: 100%; border-radius: 10px; }
  .fill-green  { background: linear-gradient(90deg, #3fb950, #26a641); }
  .fill-yellow { background: linear-gradient(90deg, #d29922, #b08800); }
  .fill-red    { background: linear-gradient(90deg, #f85149, #da3633); }
  .fill-blue   { background: linear-gradient(90deg, #388bfd, #1f6feb); }
  .fill-purple { background: linear-gradient(90deg, #a371f7, #8957e5); }

  /* Report output */
  .report-body {
    background: #161b22; border: 1px solid #21262d; border-radius: 12px;
    padding: 28px 32px; line-height: 1.8; color: #c9d1d9;
  }
  .report-body h2 { color: #388bfd; font-size: 18px; border-bottom: 1px solid #21262d; padding-bottom: 8px; margin-top: 28px; }
  .report-body h3 { color: #e6edf3; font-size: 15px; margin-top: 18px; }
  .report-body li { margin-bottom: 6px; }
  .report-body strong { color: #e6edf3; }

  /* Spinner */
  .stSpinner > div { border-top-color: #388bfd !important; }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #388bfd, #1f6feb);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; padding: 10px 24px; font-size: 14px;
    transition: opacity .2s;
  }
  .stButton > button:hover { opacity: .85; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SNOWFLAKE CONNECTION
# ─────────────────────────────────────────
@st.cache_resource
def get_conn():
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
def q(sql: str) -> pd.DataFrame:
    cur = get_conn().cursor()
    cur.execute(sql)
    cols = [d[0].lower() for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)


# ─────────────────────────────────────────
# CHART THEME
# ─────────────────────────────────────────
THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8b949e", size=12),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
    colorway=["#388bfd","#3fb950","#d29922","#a371f7","#f85149","#06b6d4","#fb923c"],
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e")),
    hoverlabel=dict(bgcolor="#21262d", font_color="#e6edf3", bordercolor="#30363d"),
)

def apply_theme(fig):
    fig.update_layout(**THEME)
    return fig


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-title">🏭 Supply Chain Command Center</div>
    <div class="dash-subtitle">2022 – 2024 &nbsp;·&nbsp; SUPPLY_CHAIN.ANALYTICS &nbsp;·&nbsp; 10,000 orders</div>
  </div>
  <div class="dash-badge">Live &nbsp;<span>●</span>&nbsp; Snowflake</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  📊  Overview  ",
    "  📦  Products  ",
    "  🏭  Suppliers  ",
    "  🚚  Logistics  ",
    "  🤖  AI Report  ",
])


# ═══════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════
with tab1:

    # ── KPIs ──
    kpi = q("""
        SELECT ROUND(SUM(revenue),2) AS revenue,
               ROUND(SUM(cogs),2) AS cogs,
               ROUND(SUM(revenue-cogs),2) AS profit,
               ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) AS margin,
               COUNT(DISTINCT order_id) AS orders,
               ROUND(AVG(revenue),2) AS aov
        FROM ORDERS WHERE status='Delivered'
    """).iloc[0]

    status_ct = q("SELECT status, COUNT(*) AS n FROM ORDERS GROUP BY 1")
    cancelled = int(status_ct.loc[status_ct.status=='Cancelled','n'].values[0]) if 'Cancelled' in status_ct.status.values else 0
    delivered = int(status_ct.loc[status_ct.status=='Delivered','n'].values[0]) if 'Delivered' in status_ct.status.values else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-label">Gross Revenue</div>
          <div class="kpi-value">${kpi['revenue']/1e6:.1f}M</div>
          <div class="kpi-sub">Delivered orders only</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-label">Gross Profit</div>
          <div class="kpi-value">${kpi['profit']/1e6:.1f}M</div>
          <div class="kpi-sub"><span class="kpi-trend-up">↑ {kpi['margin']}%</span> margin</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card purple">
          <div class="kpi-label">Total Orders</div>
          <div class="kpi-value">{int(kpi['orders']):,}</div>
          <div class="kpi-sub">10,000 total placed</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card yellow">
          <div class="kpi-label">Avg Order Value</div>
          <div class="kpi-value">${kpi['aov']:,.0f}</div>
          <div class="kpi-sub">Per delivered order</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        fill_pct = round(cancelled/100*10, 1)
        st.markdown(f"""
        <div class="kpi-card red">
          <div class="kpi-label">Cancelled Orders</div>
          <div class="kpi-value">{cancelled:,}</div>
          <div class="kpi-sub"><span class="kpi-trend-down">~{fill_pct}%</span> of total</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revenue trend + Status donut ──
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown('<div class="section-heading">Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
        monthly = q("SELECT month, revenue, gross_profit, orders FROM VW_MONTHLY_REVENUE ORDER BY month")
        monthly["month"] = pd.to_datetime(monthly["month"])

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["revenue"],
            fill="tozeroy", fillcolor="rgba(56,139,253,0.12)",
            line=dict(color="#388bfd", width=2), name="Revenue",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["gross_profit"],
            line=dict(color="#3fb950", width=2, dash="dot"), name="Gross Profit",
        ), secondary_y=False)
        fig.add_trace(go.Bar(
            x=monthly["month"], y=monthly["orders"],
            marker_color="rgba(163,113,247,0.25)", name="Orders",
            yaxis="y2",
        ), secondary_y=True)
        fig.update_layout(**THEME, height=320,
            yaxis=dict(title="", gridcolor="#21262d", tickprefix="$"),
            yaxis2=dict(title="", gridcolor="rgba(0,0,0,0)", overlaying="y", side="right"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-heading">Order Status</div>', unsafe_allow_html=True)
        fig2 = px.pie(status_ct, names="status", values="n",
                      hole=0.65,
                      color="status",
                      color_discrete_map={
                          "Delivered": "#3fb950",
                          "Shipped":   "#388bfd",
                          "Processing":"#d29922",
                          "Cancelled": "#f85149",
                      })
        fig2.update_traces(textinfo="label+percent", textfont_color="#c9d1d9")
        fig2.update_layout(**THEME, height=320,
            annotations=[dict(text=f"{delivered:,}<br><span style='font-size:10px'>Delivered</span>",
                              x=0.5, y=0.5, font_size=18, font_color="#e6edf3",
                              showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True)

    # ── Region heatmap ──
    st.markdown('<div class="section-heading">Revenue Heatmap — Region × Segment</div>', unsafe_allow_html=True)
    reg = q("""
        SELECT region, segment, ROUND(SUM(revenue),0) AS revenue
        FROM VW_REGIONAL_SUMMARY GROUP BY 1,2
    """)
    pivot = reg.pivot(index="region", columns="segment", values="revenue").fillna(0)
    fig3 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0,"#0d1117"],[0.5,"#1f3a5f"],[1,"#388bfd"]],
        text=[[f"${v/1000:.0f}K" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=13, color="white"),
        hovertemplate="Region: %{y}<br>Segment: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
        showscale=False,
    ))
    fig3.update_layout(**THEME, height=240,
        xaxis=dict(side="top", showgrid=False, linecolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=False, linecolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 2 — PRODUCTS
# ═══════════════════════════════════════════
with tab2:
    prod = q("""
        SELECT product_name, category, sub_category, orders,
               units_sold, revenue, gross_profit, margin_pct, avg_discount_pct
        FROM VW_PRODUCT_PERFORMANCE ORDER BY revenue DESC
    """)

    cats = ["All"] + sorted(prod["category"].unique().tolist())
    sel = st.selectbox("Filter category", cats, label_visibility="collapsed")
    if sel != "All":
        prod = prod[prod["category"] == sel]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-heading">Revenue by Category — Treemap</div>', unsafe_allow_html=True)
        cat_agg = q("""
            SELECT category, sub_category,
                   ROUND(SUM(revenue),0) AS revenue,
                   ROUND(SUM(gross_profit),0) AS profit
            FROM VW_PRODUCT_PERFORMANCE GROUP BY 1,2
        """)
        fig = px.treemap(cat_agg, path=["category","sub_category"],
                          values="revenue",
                          color="profit",
                          color_continuous_scale=["#1c2333","#388bfd"],
                          hover_data={"revenue": ":$,.0f", "profit": ":$,.0f"})
        fig.update_traces(textinfo="label+value",
                          texttemplate="<b>%{label}</b><br>$%{value:,.0f}",
                          textfont=dict(size=12))
        fig.update_layout(**THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-heading">Margin % vs Revenue — Bubble</div>', unsafe_allow_html=True)
        fig2 = px.scatter(prod, x="revenue", y="margin_pct",
                           size="units_sold", color="category",
                           hover_name="product_name",
                           size_max=45,
                           labels={"revenue": "Revenue ($)", "margin_pct": "Gross Margin %"},
                           color_discrete_sequence=["#388bfd","#3fb950","#d29922","#a371f7","#f85149","#06b6d4","#fb923c"])
        fig2.add_hline(y=prod["margin_pct"].mean(), line_dash="dot",
                        line_color="#30363d",
                        annotation_text=f"  Avg {prod['margin_pct'].mean():.1f}%",
                        annotation_font_color="#8b949e")
        fig2.update_layout(**THEME, height=380)
        st.plotly_chart(fig2, use_container_width=True)

    # Top products table with inline bars
    st.markdown('<div class="section-heading">Top 10 Products</div>', unsafe_allow_html=True)
    top10 = prod.head(10)[["product_name","category","orders","units_sold","revenue","margin_pct","avg_discount_pct"]].copy()
    top10["revenue_bar"] = top10["revenue"]

    fig3 = go.Figure(data=[
        go.Bar(name="Revenue", y=top10["product_name"], x=top10["revenue"],
               orientation="h", marker_color="#388bfd",
               text=[f"${v/1000:.0f}K" for v in top10["revenue"]],
               textposition="outside", textfont=dict(color="#8b949e", size=11)),
        go.Bar(name="Gross Profit", y=top10["product_name"],
               x=top10["revenue"] * top10["margin_pct"] / 100,
               orientation="h", marker_color="#3fb950",
               text=[f"{v:.0f}%" for v in top10["margin_pct"]],
               textposition="outside", textfont=dict(color="#8b949e", size=11)),
    ])
    fig3.update_layout(**THEME, barmode="overlay", height=380,
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickprefix="$", tickformat=",.0f"),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 3 — SUPPLIERS
# ═══════════════════════════════════════════
with tab3:
    sup = q("""
        SELECT supplier_name, supplier_country, supplier_category,
               reliability_score, on_time_rate_pct, avg_delay_days,
               total_shipments, total_shipping_cost, revenue_handled
        FROM VW_SUPPLIER_SCORECARD ORDER BY on_time_rate_pct
    """)

    def risk(v):
        if v < 85:   return "HIGH"
        if v < 92:   return "MEDIUM"
        return "LOW"
    def fill_color(v):
        if v < 85:   return "fill-red"
        if v < 92:   return "fill-yellow"
        return "fill-green"

    sup["risk"] = sup["on_time_rate_pct"].apply(risk)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-label">Suppliers</div>
          <div class="kpi-value">{len(sup)}</div>
          <div class="kpi-sub">Across {sup['supplier_country'].nunique()} countries</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        avg_otr = sup["on_time_rate_pct"].mean()
        trend_cls = "kpi-trend-up" if avg_otr >= 90 else "kpi-trend-down"
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-label">Avg On-Time Rate</div>
          <div class="kpi-value">{avg_otr:.1f}%</div>
          <div class="kpi-sub"><span class="{trend_cls}">Target: 92%</span></div>
        </div>""", unsafe_allow_html=True)
    with k3:
        high_risk = (sup["risk"] == "HIGH").sum()
        st.markdown(f"""
        <div class="kpi-card {'red' if high_risk else 'green'}">
          <div class="kpi-label">High Risk Suppliers</div>
          <div class="kpi-value">{high_risk}</div>
          <div class="kpi-sub">On-time rate &lt; 85%</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card yellow">
          <div class="kpi-label">Total Shipping Cost</div>
          <div class="kpi-value">${sup['total_shipping_cost'].sum()/1e6:.2f}M</div>
          <div class="kpi-sub">All carriers combined</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="section-heading">On-Time Rate — Gauge per Supplier</div>', unsafe_allow_html=True)
        # Build a grid of mini gauges using subplot
        n = len(sup)
        cols_g = 3
        rows_g = -(-n // cols_g)
        specs = [[{"type": "indicator"}] * cols_g for _ in range(rows_g)]
        titles = list(sup["supplier_name"])
        fig_g = make_subplots(rows=rows_g, cols=cols_g, specs=specs,
                               subplot_titles=[t[:18] for t in titles])
        for idx, row in sup.iterrows():
            r = (list(sup.index).index(idx)) // cols_g + 1
            c = (list(sup.index).index(idx)) % cols_g + 1
            color = "#f85149" if row["on_time_rate_pct"] < 85 else "#d29922" if row["on_time_rate_pct"] < 92 else "#3fb950"
            fig_g.add_trace(go.Indicator(
                mode="gauge+number",
                value=row["on_time_rate_pct"],
                number=dict(suffix="%", font=dict(size=16, color="#e6edf3")),
                gauge=dict(
                    axis=dict(range=[0, 100], tickfont=dict(size=9, color="#30363d"),
                              tickcolor="#30363d", tickwidth=1),
                    bar=dict(color=color, thickness=0.6),
                    bgcolor="#21262d",
                    borderwidth=0,
                    steps=[dict(range=[0,85], color="#1c1c1c"),
                           dict(range=[85,92], color="#1c2410"),
                           dict(range=[92,100], color="#122112")],
                    threshold=dict(line=dict(color="#388bfd", width=2),
                                   thickness=0.75, value=92),
                ),
            ), row=r, col=c)

        fig_g.update_annotations(font=dict(size=11, color="#8b949e"))
        fig_g.update_layout(**THEME, height=rows_g * 150,
                             grid=dict(rows=rows_g, columns=cols_g))
        st.plotly_chart(fig_g, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-heading">Risk Scorecard</div>', unsafe_allow_html=True)

        for _, row in sup.sort_values("on_time_rate_pct").iterrows():
            risk_cls = f"risk-{row['risk'].lower()}"
            fc = fill_color(row["on_time_rate_pct"])
            pct = row["on_time_rate_pct"]
            st.markdown(f"""
            <div class="prog-wrap">
              <div class="prog-header">
                <span class="prog-name">{row['supplier_name']}</span>
                <span>
                  <span class="{risk_cls}">{row['risk']}</span>
                  &nbsp;<span class="prog-val">{pct:.1f}%</span>
                </span>
              </div>
              <div class="prog-bar">
                <div class="prog-fill {fc}" style="width:{pct}%"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Radar: multi-supplier comparison
    st.markdown('<div class="section-heading">Supplier Comparison — Radar</div>', unsafe_allow_html=True)

    sup_norm = sup.copy()
    sup_norm["cost_score"] = 100 - (sup_norm["total_shipping_cost"] / sup_norm["total_shipping_cost"].max() * 100)
    sup_norm["delay_score"] = 100 - (sup_norm["avg_delay_days"] / sup_norm["avg_delay_days"].max() * 100).fillna(100)
    sup_norm["vol_score"]   = sup_norm["total_shipments"] / sup_norm["total_shipments"].max() * 100
    sup_norm["rev_score"]   = sup_norm["revenue_handled"] / sup_norm["revenue_handled"].max() * 100
    categories = ["On-Time Rate", "Cost Efficiency", "Delay Score", "Volume", "Revenue Impact"]

    fig_r = go.Figure()
    colors = ["#388bfd","#3fb950","#d29922","#a371f7","#f85149","#06b6d4"]
    for i, (_, row) in enumerate(sup_norm.iterrows()):
        vals = [row["on_time_rate_pct"],
                row["cost_score"],
                row["delay_score"],
                row["vol_score"],
                row["rev_score"]]
        fig_r.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            name=row["supplier_name"][:14],
            line=dict(color=colors[i % len(colors)], width=1.5),
            fill="toself", fillcolor=colors[i % len(colors)].replace(")", ",0.05)").replace("rgb(","rgba("),
            opacity=0.8,
        ))
    fig_r.update_layout(**THEME, height=380,
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(range=[0,100], gridcolor="#21262d", linecolor="#21262d",
                            tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
        ),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_r, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 4 — LOGISTICS
# ═══════════════════════════════════════════
with tab4:
    carrier = q("SELECT * FROM VW_CARRIER_PERFORMANCE ORDER BY on_time_pct DESC")
    fulfill = q("""
        SELECT region,
               ROUND(AVG(days_to_deliver),1) AS avg_days,
               ROUND(AVG(delay_days),2) AS avg_delay,
               ROUND(AVG(shipment_cost),2) AS avg_cost,
               COUNT(*) AS shipments
        FROM VW_ORDER_FULFILLMENT WHERE status='Delivered'
        GROUP BY region ORDER BY avg_days DESC
    """)

    k1, k2, k3 = st.columns(3)
    with k1:
        best = carrier.loc[carrier["on_time_pct"].idxmax()]
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-label">Best Carrier (On-Time)</div>
          <div class="kpi-value">{best['carrier']}</div>
          <div class="kpi-sub"><span class="kpi-trend-up">{best['on_time_pct']:.1f}%</span> on-time rate</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        avg_cost = carrier["avg_shipment_cost"].mean()
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-label">Avg Shipment Cost</div>
          <div class="kpi-value">${avg_cost:.2f}</div>
          <div class="kpi-sub">Across all carriers</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        total_cost = carrier["total_shipment_cost"].sum()
        st.markdown(f"""
        <div class="kpi-card yellow">
          <div class="kpi-label">Total Logistics Spend</div>
          <div class="kpi-value">${total_cost/1e6:.2f}M</div>
          <div class="kpi-sub">All shipments</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-heading">Carrier: Cost vs Reliability</div>', unsafe_allow_html=True)
        fig = px.scatter(carrier, x="avg_shipment_cost", y="on_time_pct",
                          size="total_shipments", text="carrier",
                          size_max=50,
                          labels={"avg_shipment_cost": "Avg Cost ($)", "on_time_pct": "On-Time %"},
                          color="on_time_pct",
                          color_continuous_scale=["#f85149","#d29922","#3fb950"])
        fig.update_traces(textposition="top center",
                           textfont=dict(size=11, color="#c9d1d9"),
                           marker=dict(line=dict(width=1.5, color="#21262d")))
        fig.add_hline(y=carrier["on_time_pct"].mean(), line_dash="dot", line_color="#388bfd",
                       annotation_text="  Avg", annotation_font_color="#8b949e")
        fig.update_layout(**THEME, height=350, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-heading">Fulfillment Days by Region</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            y=fulfill["region"], x=fulfill["avg_days"],
            orientation="h", name="Avg Days",
            marker=dict(
                color=fulfill["avg_delay"],
                colorscale=[[0,"#122112"],[0.5,"#2d2200"],[1,"#3d1a1a"]],
                showscale=False,
                line=dict(width=0),
            ),
            text=[f"{d:.1f}d  (+{dl:.1f} delay)" for d, dl in zip(fulfill["avg_days"], fulfill["avg_delay"])],
            textposition="outside",
            textfont=dict(size=11, color="#8b949e"),
        ))
        fig2.update_layout(**THEME, height=350,
            xaxis=dict(title="Days", gridcolor="#21262d"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Carrier table
    st.markdown('<div class="section-heading">Carrier Detail</div>', unsafe_allow_html=True)
    display = carrier.copy()
    display.columns = ["Carrier","Total Shipments","On-Time","On-Time %","Avg Delay","Avg Cost ($)","Total Cost ($)"]

    # Alert boxes
    alert_col1, alert_col2 = st.columns(2)
    low_perf = carrier[carrier["on_time_pct"] < 90]
    if not low_perf.empty:
        with alert_col1:
            for _, r in low_perf.iterrows():
                st.markdown(f"""
                <div class="alert-box warn">
                  <div class="alert-title">⚠️ {r['carrier']} — Below Target</div>
                  <div class="alert-body">{r['on_time_pct']:.1f}% on-time rate · Avg delay {r['avg_delay_days']:.1f} days · Avg cost ${r['avg_shipment_cost']:.2f}</div>
                </div>""", unsafe_allow_html=True)

    best_val = carrier.loc[carrier["on_time_pct"].idxmax()]
    with alert_col2:
        st.markdown(f"""
        <div class="alert-box">
          <div class="alert-title">✅ Best Carrier: {best_val['carrier']}</div>
          <div class="alert-body">{best_val['on_time_pct']:.1f}% on-time · ${best_val['avg_shipment_cost']:.2f} avg cost · {int(best_val['total_shipments']):,} shipments</div>
        </div>""", unsafe_allow_html=True)

    st.dataframe(display.style.format({
        "On-Time %": "{:.1f}%",
        "Avg Delay": "{:.2f} days",
        "Avg Cost ($)": "${:.2f}",
        "Total Cost ($)": "${:,.0f}",
    }).background_gradient(subset=["On-Time %"], cmap="RdYlGn", vmin=80, vmax=100),
    use_container_width=True, height=260)


# ═══════════════════════════════════════════
# TAB 5 — AI REPORT
# ═══════════════════════════════════════════
with tab5:

    st.markdown("""
    <div style="margin-bottom:24px;">
      <div style="font-size:20px;font-weight:700;color:#e6edf3;margin-bottom:6px;">
        🤖 AI-Powered Intelligence Report
      </div>
      <div style="font-size:14px;color:#8b949e;">
        Pull live data from Snowflake and let Claude generate an executive-level report
        with strategic recommendations.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        rtype = st.radio("Report type",
                          ["📋 Weekly Summary", "⚠️ Anomaly Alert"],
                          label_visibility="collapsed")
    with c2:
        generate = st.button("Generate Report  ✨", type="primary")

    st.markdown("---")

    if generate:
        import anthropic as _anthropic
        from ai.report_generator import fetch_kpi_snapshot, generate_report, generate_anomaly_alert

        with st.spinner("Querying Snowflake and generating report with Claude AI..."):
            try:
                import snowflake.connector as _sf
                conn = _sf.connect(
                    account=os.environ["SNOWFLAKE_ACCOUNT"],
                    user=os.environ["SNOWFLAKE_USER"],
                    password=os.environ["SNOWFLAKE_PASSWORD"],
                    warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE","COMPUTE_WH"),
                    database=os.environ.get("SNOWFLAKE_DATABASE","SUPPLY_CHAIN"),
                    schema=os.environ.get("SNOWFLAKE_SCHEMA","ANALYTICS"),
                )
                data = fetch_kpi_snapshot(conn)
                conn.close()

                client = _anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
                is_anomaly = "Anomaly" in rtype
                report = generate_anomaly_alert(data, client) if is_anomaly else generate_report(data, client)

                # Render nicely
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                  <div style="background:#21262d;border:1px solid #30363d;border-radius:8px;
                              padding:6px 14px;font-size:12px;color:#3fb950;font-weight:600;">
                    ✅ Generated {date.today()}
                  </div>
                  <div style="font-size:13px;color:#8b949e;">Powered by claude-sonnet-4-6</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f'<div class="report-body">{report.replace(chr(10), "<br>")}</div>',
                            unsafe_allow_html=True)

                st.download_button(
                    label="Download .md",
                    data=report,
                    file_name=f"sc_report_{date.today()}.md",
                    mime="text/markdown",
                )

            except Exception as e:
                st.markdown(f"""
                <div class="alert-box danger">
                  <div class="alert-title">Error generating report</div>
                  <div class="alert-body">{e}</div>
                </div>""", unsafe_allow_html=True)

    else:
        # Sample preview
        st.markdown("""
        <div class="alert-box">
          <div class="alert-title">Sample Output Preview</div>
          <div class="alert-body">Configure your .env with ANTHROPIC_API_KEY, then click Generate Report to get a live analysis.</div>
        </div>

        <div class="report-body">
          <h2>Executive Summary</h2>
          <ul>
            <li>Gross revenue of <strong>$42.3M</strong> with a <strong>43.1% gross margin</strong> across 6,700+ delivered orders</li>
            <li><strong>North America</strong> leads all regions with 34% of total revenue; Middle East is underperforming at 12%</li>
            <li><strong>2 suppliers flagged as HIGH RISK</strong> — on-time rates below 85%, creating compounding delays</li>
          </ul>
          <h2>Strategic Recommendations</h2>
          <ul>
            <li><strong>Diversify from GreatWall Manufacturing</strong> — 76% on-time rate is the lowest in the supplier base</li>
            <li><strong>Double down on Electronics</strong> — highest margin category at 48%+ with growing demand signals</li>
            <li><strong>Renegotiate Kuehne+Nagel contract</strong> — 22% cost premium over average with no reliability advantage</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
