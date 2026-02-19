"""
Supply Chain Analytics — Command Center
Warm amber/teal dark theme · Sankey · Waterfall · Calendar heatmap ·
Parallel coordinates · Asymmetric masonry layout
"""
import os, sys, json
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
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CSS — Warm Dark / Amber-Teal theme
# (nothing like the BI Copilot blue/grey)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }

/* ── Base ── */
.stApp                { background: #111010; color: #e8e0d5; }
#MainMenu, footer, header { visibility: hidden; }
.block-container      { padding: 0 0 3rem 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Top ticker strip ── */
.ticker-strip {
  background: #1a1612;
  border-bottom: 1px solid #2e2820;
  padding: 0 32px;
  height: 38px;
  display: flex; align-items: center; gap: 40px;
  overflow: hidden; white-space: nowrap;
}
.ticker-item { font-size: 12px; color: #7a6e62; font-family: 'DM Mono', monospace; }
.ticker-item span { color: #f0a500; font-weight: 600; }
.ticker-up   { color: #2ec4a9 !important; }
.ticker-down { color: #e05c4b !important; }

/* ── Page header ── */
.page-header {
  background: linear-gradient(180deg, #1a1612 0%, #111010 100%);
  padding: 28px 40px 24px;
  border-bottom: 1px solid #2e2820;
  display: flex; align-items: flex-end; justify-content: space-between;
}
.page-title { font-size: 28px; font-weight: 700; color: #f0e6d3; letter-spacing: -.5px; line-height: 1; }
.page-title em { font-style: normal; color: #f0a500; }
.page-meta  { font-size: 13px; color: #7a6e62; margin-top: 6px; }
.live-dot   { display: inline-flex; align-items: center; gap: 6px; font-size: 12px;
              color: #7a6e62; background: #1f1b16; border: 1px solid #2e2820;
              border-radius: 20px; padding: 5px 14px; }
.live-dot::before { content: ''; width: 8px; height: 8px; background: #2ec4a9;
                    border-radius: 50%; display: inline-block;
                    box-shadow: 0 0 6px #2ec4a9; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #1a1612 !important;
  border-bottom: 1px solid #2e2820 !important;
  padding: 0 40px !important; gap: 0 !important;
  margin-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  color: #7a6e62 !important; background: transparent !important;
  border: none !important; border-bottom: 2px solid transparent !important;
  padding: 16px 24px !important; font-size: 13px !important; font-weight: 500 !important;
  margin-bottom: -1px !important; letter-spacing: .2px;
}
.stTabs [aria-selected="true"] {
  color: #f0e6d3 !important;
  border-bottom-color: #f0a500 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #f0e6d3 !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }

/* ── Section padding ── */
.tab-body { padding: 32px 40px; }

/* ── KPI strip ── */
.kpi-strip { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 32px; }
.kpi-tile  {
  background: #1a1612; border: 1px solid #2e2820; border-radius: 14px;
  padding: 22px 24px 18px; position: relative; overflow: hidden;
  cursor: default;
}
.kpi-tile::after {
  content: ''; position: absolute; inset: 0; border-radius: 14px;
  background: radial-gradient(ellipse at top left, rgba(240,165,0,.06) 0%, transparent 60%);
  pointer-events: none;
}
.kpi-tile-label  { font-size: 11px; font-weight: 600; text-transform: uppercase;
                   letter-spacing: 1px; color: #7a6e62; margin-bottom: 10px; }
.kpi-tile-value  { font-size: 30px; font-weight: 700; color: #f0e6d3; letter-spacing: -1px; line-height: 1; }
.kpi-tile-sub    { font-size: 12px; color: #7a6e62; margin-top: 8px; }
.kpi-amber { color: #f0a500 !important; }
.kpi-teal  { color: #2ec4a9 !important; }
.kpi-red   { color: #e05c4b !important; }
.kpi-bar   { height: 3px; background: #2e2820; border-radius: 2px; margin-top: 14px; overflow: hidden; }
.kpi-bar-fill { height: 100%; border-radius: 2px; }
.fill-amber  { background: linear-gradient(90deg, #f0a500, #c97f00); }
.fill-teal   { background: linear-gradient(90deg, #2ec4a9, #1a9a87); }
.fill-red    { background: linear-gradient(90deg, #e05c4b, #b8432f); }
.fill-purple { background: linear-gradient(90deg, #9b6dff, #7040d6); }
.fill-blue   { background: linear-gradient(90deg, #4e9eff, #2575d0); }

/* ── Section headings ── */
.sh {
  font-size: 13px; font-weight: 600; color: #f0e6d3;
  text-transform: uppercase; letter-spacing: 1.2px;
  display: flex; align-items: center; gap: 8px;
  margin: 0 0 16px 0;
}
.sh::before { content: ''; width: 14px; height: 2px;
              background: #f0a500; display: inline-block; }

/* ── Chart card ── */
.cc {
  background: #1a1612; border: 1px solid #2e2820; border-radius: 14px;
  padding: 22px 20px; margin-bottom: 20px;
}
.cc-title { font-size: 13px; font-weight: 600; color: #c4b8aa; margin-bottom: 2px; }
.cc-sub   { font-size: 11px; color: #7a6e62; margin-bottom: 14px; }

/* ── Supplier progress bars ── */
.sup-row { margin-bottom: 16px; }
.sup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.sup-name  { font-size: 13px; color: #c4b8aa; font-family: 'DM Mono', monospace; }
.sup-badge {
  font-size: 11px; font-weight: 600; border-radius: 4px;
  padding: 2px 9px; letter-spacing: .3px;
}
.badge-high   { background: #2d0f0c; color: #e05c4b; border: 1px solid rgba(224,92,75,.3); }
.badge-medium { background: #251d09; color: #f0a500; border: 1px solid rgba(240,165,0,.3); }
.badge-low    { background: #0c2018; color: #2ec4a9; border: 1px solid rgba(46,196,169,.3); }
.sup-track { height: 6px; background: #2e2820; border-radius: 10px; overflow: hidden; }
.sup-fill  { height: 100%; border-radius: 10px; transition: width .4s ease; }

/* ── Alert cards ── */
.alert-card {
  background: #1a1612; border-radius: 10px; padding: 14px 18px;
  margin-bottom: 10px; border-left: 3px solid #f0a500;
  border: 1px solid #2e2820; border-left-width: 3px;
}
.alert-card.danger { border-left-color: #e05c4b; }
.alert-card.good   { border-left-color: #2ec4a9; }
.alert-hdr { font-size: 13px; font-weight: 600; color: #f0e6d3; margin-bottom: 3px; }
.alert-txt { font-size: 12px; color: #7a6e62; }

/* ── Report output ── */
.rpt { background: #1a1612; border: 1px solid #2e2820; border-radius: 14px;
       padding: 32px 36px; line-height: 1.85; color: #c4b8aa; }
.rpt h2 { font-size: 16px; color: #f0a500; border-bottom: 1px solid #2e2820;
           padding-bottom: 8px; margin-top: 28px; text-transform: uppercase; letter-spacing: .8px; }
.rpt h3 { font-size: 14px; color: #f0e6d3; margin-top: 16px; }
.rpt li  { margin-bottom: 6px; }
.rpt strong { color: #f0e6d3; }

/* ── Button ── */
.stButton > button {
  background: linear-gradient(135deg, #f0a500, #c97f00) !important;
  color: #111010 !important; border: none !important; border-radius: 8px !important;
  font-weight: 700 !important; padding: 10px 26px !important;
  font-size: 13px !important; letter-spacing: .3px;
}
.stButton > button:hover { opacity: .88 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: #1f1b16 !important; border-color: #2e2820 !important; color: #e8e0d5 !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SNOWFLAKE
# ─────────────────────────────────────────
@st.cache_resource
def get_conn():
    import snowflake.connector
    return snowflake.connector.connect(
        account   = os.environ["SNOWFLAKE_ACCOUNT"],
        user      = os.environ["SNOWFLAKE_USER"],
        password  = os.environ["SNOWFLAKE_PASSWORD"],
        warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database  = os.environ.get("SNOWFLAKE_DATABASE", "SUPPLY_CHAIN"),
        schema    = os.environ.get("SNOWFLAKE_SCHEMA",   "ANALYTICS"),
    )

@st.cache_data(ttl=300)
def q(sql):
    cur = get_conn().cursor()
    cur.execute(sql)
    cols = [d[0].lower() for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)


# ─────────────────────────────────────────
# CHART THEME  (amber/teal — not blue/grey)
# ─────────────────────────────────────────
BG   = "rgba(0,0,0,0)"
GRID = "#2e2820"
T    = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(family="DM Sans", color="#7a6e62", size=12),
    colorway=["#f0a500","#2ec4a9","#e05c4b","#9b6dff","#4e9eff","#f06b00","#79d4c4"],
    margin=dict(l=0, r=0, t=28, b=0),
    legend=dict(bgcolor=BG, font=dict(color="#7a6e62"), orientation="h", y=-0.15),
    hoverlabel=dict(bgcolor="#1f1b16", font_color="#f0e6d3", bordercolor="#2e2820"),
)
AXIS = dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID)

def th(fig, h=None):
    fig.update_layout(**T)
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    if h: fig.update_layout(height=h)
    return fig


# ─────────────────────────────────────────
# GLOBAL DATA (fetched once for ticker)
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def global_kpis():
    return q("""
        SELECT ROUND(SUM(revenue)/1e6,2) AS rev_m,
               ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) AS margin,
               COUNT(DISTINCT order_id) AS orders,
               (SELECT ROUND(AVG(on_time_rate_pct),1) FROM VW_SUPPLIER_SCORECARD) AS otr,
               (SELECT ROUND(AVG(on_time_pct),1) FROM VW_CARRIER_PERFORMANCE) AS carrier_otr
        FROM ORDERS WHERE status='Delivered'
    """).iloc[0]

gk = global_kpis()

# ─────────────────────────────────────────
# TICKER + HEADER
# ─────────────────────────────────────────
st.markdown(f"""
<div class="ticker-strip">
  <span class="ticker-item">REVENUE &nbsp;<span>${gk['rev_m']}M</span></span>
  <span class="ticker-item">MARGIN &nbsp;<span class="ticker-up">{gk['margin']}%</span></span>
  <span class="ticker-item">ORDERS &nbsp;<span>{int(gk['orders']):,}</span></span>
  <span class="ticker-item">SUPPLIER OTR &nbsp;<span class="{'ticker-up' if gk['otr']>=90 else 'ticker-down'}">{gk['otr']}%</span></span>
  <span class="ticker-item">CARRIER OTR &nbsp;<span class="{'ticker-up' if gk['carrier_otr']>=90 else 'ticker-down'}">{gk['carrier_otr']}%</span></span>
  <span class="ticker-item">DATE &nbsp;<span>{date.today()}</span></span>
</div>
<div class="page-header">
  <div>
    <div class="page-title">Supply Chain <em>Command Center</em></div>
    <div class="page-meta">SUPPLY_CHAIN.ANALYTICS &nbsp;·&nbsp; Jan 2022 – Dec 2024 &nbsp;·&nbsp; 10,000 orders</div>
  </div>
  <div class="live-dot">Live · Snowflake</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "  Overview  ", "  Products  ", "  Suppliers  ", "  Logistics  ", "  AI Report  "
])


# ══════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════
with t1:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)

    # ── KPI tiles ──
    k = q("""
        SELECT ROUND(SUM(revenue),2) r, ROUND(SUM(cogs),2) c,
               ROUND(SUM(revenue-cogs),2) p,
               ROUND(SUM(revenue-cogs)/NULLIF(SUM(revenue),0)*100,2) m,
               COUNT(DISTINCT order_id) o, ROUND(AVG(revenue),2) aov
        FROM ORDERS WHERE status='Delivered'
    """).iloc[0]

    cancelled = int(q("SELECT COUNT(*) n FROM ORDERS WHERE status='Cancelled'").iloc[0,0])

    st.markdown(f"""
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-tile-label">Gross Revenue</div>
        <div class="kpi-tile-value">${k['r']/1e6:.1f}<span style="font-size:16px;color:#7a6e62">M</span></div>
        <div class="kpi-tile-sub">Delivered orders</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-amber" style="width:100%"></div></div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-label">Gross Profit</div>
        <div class="kpi-tile-value">${k['p']/1e6:.1f}<span style="font-size:16px;color:#7a6e62">M</span></div>
        <div class="kpi-tile-sub"><span class="kpi-teal">{k['m']}%</span> margin</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-teal" style="width:{k['m']}%"></div></div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-label">Delivered Orders</div>
        <div class="kpi-tile-value">{int(k['o']):,}</div>
        <div class="kpi-tile-sub">of 10,000 placed</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-purple" style="width:{int(k['o'])/100}%"></div></div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-label">Avg Order Value</div>
        <div class="kpi-tile-value">${k['aov']:,.0f}</div>
        <div class="kpi-tile-sub">Per delivered order</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-blue" style="width:65%"></div></div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-label">Cancelled Orders</div>
        <div class="kpi-tile-value kpi-red">{cancelled:,}</div>
        <div class="kpi-tile-sub">{cancelled/100:.1f}% of total</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-red" style="width:{cancelled/100:.1f}%"></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Waterfall: Revenue → Profit breakdown ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<p class="sh">Revenue Waterfall — Cost Breakdown</p>', unsafe_allow_html=True)
        wf = q("""
            SELECT category,
                   ROUND(SUM(revenue),0) AS revenue,
                   ROUND(SUM(cogs),0) AS cogs,
                   ROUND(SUM(revenue-cogs),0) AS profit
            FROM ORDERS WHERE status='Delivered'
            GROUP BY 1 ORDER BY revenue DESC
        """)
        # Horizontal grouped bar as a waterfall proxy
        fig = go.Figure()
        fig.add_trace(go.Bar(name="COGS",        y=wf["category"], x=wf["cogs"],
                              orientation="h", marker_color="#2e2820",
                              marker_line_width=0))
        fig.add_trace(go.Bar(name="Gross Profit", y=wf["category"], x=wf["profit"],
                              orientation="h", marker_color="#f0a500",
                              marker_line_width=0,
                              text=[f"${v/1000:.0f}K" for v in wf["profit"]],
                              textposition="outside",
                              textfont=dict(size=11, color="#7a6e62")))
        fig.update_layout(**T, height=360, barmode="stack",
            yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(tickprefix="$", tickformat=",.0f"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<p class="sh">Order Pipeline — Funnel</p>', unsafe_allow_html=True)
        funnel_df = q("""
            SELECT status, COUNT(*) AS n FROM ORDERS GROUP BY 1
            ORDER BY CASE status
              WHEN 'Delivered' THEN 1 WHEN 'Shipped' THEN 2
              WHEN 'Processing' THEN 3 WHEN 'Cancelled' THEN 4 END
        """)
        fig2 = go.Figure(go.Funnel(
            y=funnel_df["status"],
            x=funnel_df["n"],
            marker=dict(color=["#2ec4a9","#4e9eff","#f0a500","#e05c4b"],
                        line=dict(width=0)),
            textinfo="value+percent initial",
            textfont=dict(size=13, color="#f0e6d3"),
            connector=dict(line=dict(color=GRID, width=1)),
        ))
        fig2.update_layout(**T, height=360)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Monthly trend — Candlestick-style (OHLC monthly) ──
    st.markdown('<p class="sh" style="margin-top:8px">Monthly Revenue — Open / High / Low / Close (Quarterly Candles)</p>', unsafe_allow_html=True)
    monthly = q("SELECT month, revenue, gross_profit, orders FROM VW_MONTHLY_REVENUE ORDER BY month")
    monthly["month"] = pd.to_datetime(monthly["month"])

    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["revenue"],
        fill="tozeroy", fillcolor="rgba(240,165,0,0.08)",
        line=dict(color="#f0a500", width=2.5), name="Revenue",
        hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig3.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["gross_profit"],
        line=dict(color="#2ec4a9", width=1.5, dash="dot"), name="Gross Profit",
        hovertemplate="<b>%{x|%b %Y}</b><br>Profit: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig3.add_trace(go.Bar(
        x=monthly["month"], y=monthly["orders"],
        marker_color="rgba(155,109,255,0.2)", name="Orders",
    ), secondary_y=True)

    fig3.update_layout(**T, height=280,
        yaxis =dict(tickprefix="$", gridcolor=GRID),
        yaxis2=dict(gridcolor="rgba(0,0,0,0)", overlaying="y", side="right"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Calendar heatmap (daily orders density) ──
    st.markdown('<p class="sh">Daily Order Volume — Calendar Heatmap</p>', unsafe_allow_html=True)
    daily = q("""
        SELECT order_date, COUNT(*) AS orders, ROUND(SUM(revenue),0) AS revenue
        FROM ORDERS GROUP BY 1 ORDER BY 1
    """)
    daily["order_date"] = pd.to_datetime(daily["order_date"])
    daily["dow"] = daily["order_date"].dt.dayofweek
    daily["week"] = daily["order_date"].dt.isocalendar().week.astype(int)
    daily["year"] = daily["order_date"].dt.year

    # Show just 2024 for visual clarity
    d24 = daily[daily["year"] == 2024].copy()
    if not d24.empty:
        pivot = d24.pivot_table(index="dow", columns="week", values="orders", aggfunc="sum").fillna(0)
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        fig4 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(w) for w in pivot.columns],
            y=[days[i] for i in pivot.index],
            colorscale=[[0,"#1a1612"],[0.3,"#3d2800"],[0.7,"#8a5a00"],[1,"#f0a500"]],
            showscale=False,
            hovertemplate="Week %{x} · %{y}<br>Orders: %{z:.0f}<extra></extra>",
            xgap=2, ygap=3,
        ))
        th(fig4, h=200)
        fig4.update_layout(margin=dict(l=0,r=0,t=10,b=0))
        fig4.update_xaxes(showgrid=False, showticklabels=False, linecolor="rgba(0,0,0,0)")
        fig4.update_yaxes(showgrid=False, linecolor="rgba(0,0,0,0)", tickfont=dict(size=10))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════
with t2:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)

    prod = q("""
        SELECT product_name, category, sub_category, orders,
               units_sold, revenue, gross_profit, margin_pct, avg_discount_pct
        FROM VW_PRODUCT_PERFORMANCE ORDER BY revenue DESC
    """)

    cats = ["All"] + sorted(prod["category"].unique().tolist())
    sel  = st.selectbox("Filter", cats, label_visibility="collapsed")
    if sel != "All": prod = prod[prod["category"] == sel]

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<p class="sh">Top Products — Revenue vs Profit Overlay</p>', unsafe_allow_html=True)
        top = prod.head(12)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top["product_name"], x=top["revenue"],
            orientation="h", name="Revenue",
            marker=dict(color="rgba(240,165,0,0.18)", line=dict(color="#f0a500", width=1.5)),
            hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            y=top["product_name"], x=top["gross_profit"],
            orientation="h", name="Gross Profit",
            marker=dict(color="#2ec4a9"),
            hovertemplate="%{y}<br>Profit: $%{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**T, height=420, barmode="overlay",
            yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(tickprefix="$"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="sh">Category Treemap</p>', unsafe_allow_html=True)
        cat_agg = q("""
            SELECT category, sub_category,
                   ROUND(SUM(revenue),0) revenue, ROUND(SUM(gross_profit),0) profit
            FROM VW_PRODUCT_PERFORMANCE GROUP BY 1,2
        """)
        fig2 = px.treemap(cat_agg, path=["category","sub_category"],
                           values="revenue", color="profit",
                           color_continuous_scale=[[0,"#1a1612"],[0.5,"#8a5a00"],[1,"#f0a500"]])
        fig2.update_traces(
            texttemplate="<b>%{label}</b><br>$%{value:,.0f}",
            textfont=dict(size=11, color="#f0e6d3"),
            marker_line_width=2, marker_line_color="#111010",
        )
        fig2.update_layout(**T, height=420, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Parallel coordinates — multi-dim product view
    st.markdown('<p class="sh">Multi-Dimensional Product Analysis — Parallel Coordinates</p>', unsafe_allow_html=True)
    fig3 = go.Figure(go.Parcoords(
        line=dict(
            color=prod["margin_pct"],
            colorscale=[[0,"#e05c4b"],[0.5,"#f0a500"],[1,"#2ec4a9"]],
            showscale=True,
            colorbar=dict(title="Margin %", tickfont=dict(color="#7a6e62"),
                          titlefont=dict(color="#7a6e62"), bgcolor=BG,
                          outlinecolor=GRID),
        ),
        dimensions=[
            dict(label="Revenue",      values=prod["revenue"],       tickformat="$,.0f"),
            dict(label="Gross Profit", values=prod["gross_profit"],   tickformat="$,.0f"),
            dict(label="Units Sold",   values=prod["units_sold"]),
            dict(label="Orders",       values=prod["orders"]),
            dict(label="Margin %",     values=prod["margin_pct"],    range=[0,100]),
            dict(label="Discount %",   values=prod["avg_discount_pct"], range=[0,20]),
        ],
    ))
    th(fig3, h=320)
    fig3.update_traces(
        unselected_line_color="rgba(46,196,169,0.1)",
        labelangle=0,
        labelfont=dict(color="#c4b8aa", size=11),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 3 — SUPPLIERS
# ══════════════════════════════════════════
with t3:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)

    sup = q("""
        SELECT supplier_name, supplier_country, supplier_category,
               on_time_rate_pct, avg_delay_days, total_shipments,
               total_shipping_cost, revenue_handled, reliability_score
        FROM VW_SUPPLIER_SCORECARD ORDER BY on_time_rate_pct
    """)
    sup["risk"] = sup["on_time_rate_pct"].apply(
        lambda v: "HIGH" if v < 85 else ("MEDIUM" if v < 92 else "LOW"))

    # KPI row
    k1,k2,k3,k4 = st.columns(4)
    avg_otr = sup["on_time_rate_pct"].mean()
    high    = (sup["risk"]=="HIGH").sum()
    st.markdown(f"""
    <div class="kpi-strip" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi-tile"><div class="kpi-tile-label">Suppliers</div>
        <div class="kpi-tile-value">{len(sup)}</div>
        <div class="kpi-tile-sub">{sup['supplier_country'].nunique()} countries</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-amber" style="width:100%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">Avg On-Time Rate</div>
        <div class="kpi-tile-value {'kpi-teal' if avg_otr>=90 else 'kpi-red'}">{avg_otr:.1f}<span style="font-size:16px">%</span></div>
        <div class="kpi-tile-sub">Target: 92%</div>
        <div class="kpi-bar"><div class="kpi-bar-fill {'fill-teal' if avg_otr>=90 else 'fill-red'}" style="width:{avg_otr}%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">High Risk</div>
        <div class="kpi-tile-value {'kpi-red' if high else 'kpi-teal'}">{high}</div>
        <div class="kpi-tile-sub">OTR &lt; 85%</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-red" style="width:{high/len(sup)*100:.0f}%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">Total Shipping Cost</div>
        <div class="kpi-tile-value">${sup['total_shipping_cost'].sum()/1e6:.2f}<span style="font-size:16px;color:#7a6e62">M</span></div>
        <div class="kpi-tile-sub">All shipments</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-purple" style="width:100%"></div></div></div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<p class="sh">On-Time Rate Scorecard</p>', unsafe_allow_html=True)
        for _, r in sup.sort_values("on_time_rate_pct").iterrows():
            pct = r["on_time_rate_pct"]
            bclass = f"badge-{r['risk'].lower()}"
            fcolor = "fill-red" if pct<85 else "fill-amber" if pct<92 else "fill-teal"
            st.markdown(f"""
            <div class="sup-row">
              <div class="sup-header">
                <span class="sup-name">{r['supplier_name']}</span>
                <span class="sup-badge {bclass}">{r['risk']} &nbsp;{pct:.1f}%</span>
              </div>
              <div class="sup-track">
                <div class="sup-fill {fcolor}" style="width:{pct}%"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown('<p class="sh">Delay vs Revenue Handled — Bubble</p>', unsafe_allow_html=True)
        fig = px.scatter(sup, x="avg_delay_days", y="on_time_rate_pct",
                          size="revenue_handled", color="risk",
                          hover_name="supplier_name",
                          size_max=55, text="supplier_name",
                          color_discrete_map={"HIGH":"#e05c4b","MEDIUM":"#f0a500","LOW":"#2ec4a9"},
                          labels={"avg_delay_days":"Avg Delay (days)","on_time_rate_pct":"On-Time Rate %"})
        fig.update_traces(textposition="top center",
                           textfont=dict(size=9, color="#c4b8aa"),
                           marker=dict(line=dict(width=1.5, color="#111010")))
        fig.add_hline(y=92, line_dash="dot", line_color="#2e2820",
                       annotation_text="  92% target", annotation_font_color="#7a6e62")
        fig.update_layout(**T, height=420, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # Sankey: Supplier → Category → Revenue
    st.markdown('<p class="sh">Supply Chain Flow — Sankey Diagram</p>', unsafe_allow_html=True)
    flow = q("""
        SELECT o.supplier_name, o.category,
               ROUND(SUM(o.revenue),0) AS revenue
        FROM ORDERS o WHERE o.status='Delivered'
        GROUP BY 1,2
        HAVING SUM(o.revenue) > 100000
        ORDER BY revenue DESC
        LIMIT 30
    """)

    suppliers = list(flow["supplier_name"].unique())
    categories = list(flow["category"].unique())
    all_nodes  = suppliers + categories
    node_idx   = {n: i for i, n in enumerate(all_nodes)}

    node_colors = (["rgba(240,165,0,0.8)"] * len(suppliers) +
                   ["rgba(46,196,169,0.8)"]  * len(categories))

    fig_s = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20, thickness=18, line=dict(color="#111010", width=1),
            label=all_nodes, color=node_colors,
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=[node_idx[s] for s in flow["supplier_name"]],
            target=[node_idx[c] for c in flow["category"]],
            value=flow["revenue"].tolist(),
            color=["rgba(240,165,0,0.12)"] * len(flow),
            hovertemplate="$%{value:,.0f}<extra></extra>",
        ),
    ))
    th(fig_s, h=380)
    fig_s.update_layout(font=dict(size=11, color="#c4b8aa"))
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 4 — LOGISTICS
# ══════════════════════════════════════════
with t4:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)

    carrier = q("SELECT * FROM VW_CARRIER_PERFORMANCE ORDER BY on_time_pct DESC")
    fulfill = q("""
        SELECT region,
               ROUND(AVG(days_to_deliver),1) avg_days,
               ROUND(AVG(delay_days),2) avg_delay,
               ROUND(AVG(shipment_cost),2) avg_cost,
               COUNT(*) shipments
        FROM VW_ORDER_FULFILLMENT WHERE status='Delivered'
        GROUP BY region ORDER BY avg_days DESC
    """)

    best = carrier.loc[carrier["on_time_pct"].idxmax()]
    worst = carrier.loc[carrier["on_time_pct"].idxmin()]

    st.markdown(f"""
    <div class="kpi-strip" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi-tile"><div class="kpi-tile-label">Best Carrier</div>
        <div class="kpi-tile-value" style="font-size:22px">{best['carrier']}</div>
        <div class="kpi-tile-sub"><span class="kpi-teal">{best['on_time_pct']:.1f}%</span> on-time</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-teal" style="width:{best['on_time_pct']}%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">Needs Attention</div>
        <div class="kpi-tile-value" style="font-size:22px">{worst['carrier']}</div>
        <div class="kpi-tile-sub"><span class="kpi-red">{worst['on_time_pct']:.1f}%</span> on-time</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-red" style="width:{worst['on_time_pct']}%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">Avg Shipment Cost</div>
        <div class="kpi-tile-value">${carrier['avg_shipment_cost'].mean():.2f}</div>
        <div class="kpi-tile-sub">All carriers</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-amber" style="width:70%"></div></div></div>
      <div class="kpi-tile"><div class="kpi-tile-label">Total Logistics Spend</div>
        <div class="kpi-tile-value">${carrier['total_shipment_cost'].sum()/1e6:.2f}<span style="font-size:16px;color:#7a6e62">M</span></div>
        <div class="kpi-tile-sub">All shipments</div>
        <div class="kpi-bar"><div class="kpi-bar-fill fill-purple" style="width:100%"></div></div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="sh">Carrier — On-Time Rate Lollipop</p>', unsafe_allow_html=True)
        srt = carrier.sort_values("on_time_pct")
        fig = go.Figure()
        # Stems
        for _, r in srt.iterrows():
            fig.add_shape(type="line",
                x0=0, x1=r["on_time_pct"], y0=r["carrier"], y1=r["carrier"],
                line=dict(color=GRID, width=1.5))
        # Dots
        color = ["#e05c4b" if v<90 else "#f0a500" if v<95 else "#2ec4a9"
                 for v in srt["on_time_pct"]]
        fig.add_trace(go.Scatter(
            x=srt["on_time_pct"], y=srt["carrier"],
            mode="markers+text",
            marker=dict(size=18, color=color, line=dict(width=2, color="#111010")),
            text=[f"{v:.1f}%" for v in srt["on_time_pct"]],
            textposition="middle right",
            textfont=dict(size=11, color="#c4b8aa"),
            hovertemplate="%{y}<br>On-Time: %{x:.1f}%<extra></extra>",
        ))
        fig.add_vline(x=92, line_dash="dot", line_color="#2e2820",
                       annotation_text="Target 92%", annotation_font_color="#7a6e62",
                       annotation_position="top right")
        fig.update_layout(**T, height=340, showlegend=False,
            xaxis=dict(range=[80,100], ticksuffix="%"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="sh">Avg Days to Deliver by Region</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            y=fulfill["region"], x=fulfill["avg_days"],
            orientation="h", name="Total Days",
            marker=dict(
                color=fulfill["avg_delay"],
                colorscale=[[0,"#0c2018"],[0.5,"#3d2800"],[1,"#5c1a12"]],
                showscale=False, line=dict(width=0),
            ),
            text=[f"{d:.1f}d" for d in fulfill["avg_days"]],
            textposition="outside", textfont=dict(size=11, color="#7a6e62"),
        ))
        fig2.update_layout(**T, height=340,
            yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="Days"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Alert cards
    st.markdown('<p class="sh" style="margin-top:8px">Carrier Alerts</p>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    below = carrier[carrier["on_time_pct"] < 92]
    with ac1:
        for _, r in below.iterrows():
            cls = "danger" if r["on_time_pct"] < 85 else ""
            st.markdown(f"""
            <div class="alert-card {cls}">
              <div class="alert-hdr">⚠️ {r['carrier']} — Below Target</div>
              <div class="alert-txt">{r['on_time_pct']:.1f}% on-time &nbsp;·&nbsp;
                avg delay {r['avg_delay_days']:.1f}d &nbsp;·&nbsp;
                avg cost ${r['avg_shipment_cost']:.2f}</div>
            </div>""", unsafe_allow_html=True)
    with ac2:
        st.markdown(f"""
        <div class="alert-card good">
          <div class="alert-hdr">✅ Top Performer: {best['carrier']}</div>
          <div class="alert-txt">{best['on_time_pct']:.1f}% on-time &nbsp;·&nbsp;
            ${best['avg_shipment_cost']:.2f} avg cost &nbsp;·&nbsp;
            {int(best['total_shipments']):,} shipments</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 5 — AI REPORT
# ══════════════════════════════════════════
with t5:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:28px">
      <div style="font-size:22px;font-weight:700;color:#f0e6d3;margin-bottom:6px">
        AI Intelligence Report
      </div>
      <div style="font-size:14px;color:#7a6e62">
        Pull live KPIs from Snowflake · Generate executive briefing via <span style="color:#f0a500;font-weight:600">claude-sonnet-4-6</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    r_col, b_col = st.columns([2, 1])
    with r_col:
        rtype = st.radio("Report type", ["Weekly Summary", "Anomaly Alert"], horizontal=True,
                          label_visibility="collapsed")
    with b_col:
        run_btn = st.button("Generate Report  ✦", type="primary")

    st.markdown('<hr style="border-color:#2e2820;margin:20px 0">', unsafe_allow_html=True)

    if run_btn:
        import anthropic as _ant
        from ai.report_generator import fetch_kpi_snapshot, generate_report, generate_anomaly_alert
        with st.spinner("Querying Snowflake · Generating report with Claude AI …"):
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
                data   = fetch_kpi_snapshot(conn); conn.close()
                client = _ant.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
                report = generate_anomaly_alert(data, client) if "Anomaly" in rtype \
                         else generate_report(data, client)

                st.markdown(f"""
                <div style="display:flex;gap:12px;align-items:center;margin-bottom:20px">
                  <div style="background:#0c2018;border:1px solid rgba(46,196,169,.3);
                              border-radius:6px;padding:5px 14px;font-size:12px;
                              color:#2ec4a9;font-weight:600">✓ Generated {date.today()}</div>
                  <div style="font-size:12px;color:#7a6e62;font-family:'DM Mono',monospace">
                    claude-sonnet-4-6</div>
                </div>
                <div class="rpt">{report.replace(chr(10),'<br>')}</div>
                """, unsafe_allow_html=True)

                st.download_button("Download .md", report,
                                    f"sc_report_{date.today()}.md", "text/markdown")
            except Exception as e:
                st.markdown(f"""
                <div class="alert-card danger">
                  <div class="alert-hdr">Error generating report</div>
                  <div class="alert-txt">{e}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card" style="border-left-color:#2e2820;margin-bottom:24px">
          <div class="alert-hdr" style="color:#7a6e62">Configure ANTHROPIC_API_KEY in .env to enable live reports</div>
          <div class="alert-txt">Sample output shown below</div>
        </div>
        <div class="rpt">
          <h2>Executive Summary</h2>
          <ul>
            <li>Gross revenue of <strong>$42.3M</strong> with a <strong>43.1% gross margin</strong> across 6,700+ delivered orders</li>
            <li><strong>North America</strong> leads all regions at 34% of total revenue — Middle East underperforming at 12%</li>
            <li><strong>2 suppliers flagged HIGH RISK</strong> — on-time rates below 85%, causing compounding delays</li>
          </ul>
          <h2>Strategic Recommendations</h2>
          <ul>
            <li><strong>Diversify from GreatWall Manufacturing</strong> — 76% OTR is lowest in the base; renegotiate SLA or qualify alternate</li>
            <li><strong>Double down on Electronics</strong> — 48%+ margin with growing demand; consider safety stock increase</li>
            <li><strong>Renegotiate Kuehne+Nagel contract</strong> — 22% cost premium with no reliability advantage vs DHL</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
