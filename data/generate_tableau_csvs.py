"""
Generates pre-aggregated CSVs for Tableau Public.
Replicates the 5 Snowflake analytical views using only raw CSVs.
Output goes to data/tableau/
"""
import os
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "raw")
OUT = os.path.join(os.path.dirname(__file__), "tableau")
os.makedirs(OUT, exist_ok=True)

# ── Load raw tables ──────────────────────────────────────────
# orders is already fully denormalized (has product/customer/supplier info)
orders    = pd.read_csv(f"{RAW}/orders.csv", parse_dates=["order_date"])
shipments = pd.read_csv(f"{RAW}/shipments.csv")
suppliers = pd.read_csv(f"{RAW}/suppliers.csv")

# Derived columns
orders["gross_profit"] = orders["revenue"] - orders["cogs"]
orders["discount_pct"] = (orders["discount"] * 100).round(2)
orders["month"]        = orders["order_date"].dt.to_period("M").dt.to_timestamp()
orders["year"]         = orders["order_date"].dt.year
orders["month_num"]    = orders["order_date"].dt.month
orders["month_label"]  = orders["order_date"].dt.strftime("%b %Y")

# Delivered orders only (for revenue/profit views)
delivered = orders[orders["status"] == "Delivered"]

# ── VW_MONTHLY_REVENUE ───────────────────────────────────────
monthly = (
    delivered
    .groupby(["month", "year", "month_num", "month_label"], as_index=False)
    .agg(
        orders       = ("order_id",     "count"),
        revenue      = ("revenue",      "sum"),
        cogs         = ("cogs",         "sum"),
        gross_profit = ("gross_profit", "sum"),
    )
    .sort_values("month")
)
monthly["margin_pct"] = (monthly["gross_profit"] / monthly["revenue"] * 100).round(2)
monthly["month"]      = monthly["month"].dt.strftime("%Y-%m-%d")
monthly.to_csv(f"{OUT}/vw_monthly_revenue.csv", index=False)
print(f"  ✅  vw_monthly_revenue      {len(monthly):>4} rows")

# ── VW_PRODUCT_PERFORMANCE ───────────────────────────────────
prod_perf = (
    delivered
    .groupby(["product_id", "product_name", "category", "sub_category"], as_index=False)
    .agg(
        orders          = ("order_id",     "count"),
        units_sold      = ("quantity",     "sum"),
        revenue         = ("revenue",      "sum"),
        gross_profit    = ("gross_profit", "sum"),
        avg_discount_pct= ("discount_pct", "mean"),
    )
)
prod_perf["margin_pct"]       = (prod_perf["gross_profit"] / prod_perf["revenue"] * 100).round(2)
prod_perf["avg_discount_pct"] = prod_perf["avg_discount_pct"].round(2)
prod_perf.to_csv(f"{OUT}/vw_product_performance.csv", index=False)
print(f"  ✅  vw_product_performance  {len(prod_perf):>4} rows")

# ── VW_SUPPLIER_SCORECARD ─────────────────────────────────────
# Join shipments → orders (for revenue_handled & supplier info)
ship = shipments.copy()
ship["on_time"]    = ship["on_time"].map({"True": 1, "False": 0, True: 1, False: 0}).astype("Int64")
ship["delay_days"] = pd.to_numeric(ship["delay_days"], errors="coerce").fillna(0)

# Only completed shipments (have on_time value)
ship_done = ship[ship["on_time"].notna()]
ship_ord  = ship_done.merge(
    orders[["order_id", "supplier_id", "supplier_name", "supplier_country", "revenue"]]
    .drop_duplicates("order_id"),
    on="order_id", how="left"
)
# suppliers.csv uses column names: country, lead_time_days, category
suppliers_slim = suppliers.rename(columns={
    "country":        "supplier_country2",
    "lead_time_days": "contracted_lead_days",
    "category":       "supplier_category",
})
ship_sup = ship_ord.merge(
    suppliers_slim[["supplier_id", "contracted_lead_days", "reliability_score", "supplier_category"]],
    on="supplier_id", how="left"
)

scorecard = (
    ship_sup.groupby(
        ["supplier_id", "supplier_name", "supplier_country",
         "contracted_lead_days", "reliability_score", "supplier_category"],
        as_index=False
    ).agg(
        total_shipments    = ("shipment_id",   "count"),
        on_time_count      = ("on_time",       "sum"),
        avg_delay_days     = ("delay_days",    "mean"),
        total_shipping_cost= ("shipment_cost", "sum"),
        revenue_handled    = ("revenue",       "sum"),
    )
)
scorecard["on_time_rate_pct"] = (scorecard["on_time_count"] / scorecard["total_shipments"] * 100).round(2)
scorecard["avg_delay_days"]   = scorecard["avg_delay_days"].round(2)
scorecard.to_csv(f"{OUT}/vw_supplier_scorecard.csv", index=False)
print(f"  ✅  vw_supplier_scorecard   {len(scorecard):>4} rows")

# ── VW_REGIONAL_SUMMARY ──────────────────────────────────────
regional = (
    delivered
    .groupby(["region", "segment"], as_index=False)
    .agg(
        customers      = ("customer_id",  "nunique"),
        orders         = ("order_id",     "count"),
        revenue        = ("revenue",      "sum"),
        gross_profit   = ("gross_profit", "sum"),
        avg_order_value= ("revenue",      "mean"),
    )
)
regional["margin_pct"]      = (regional["gross_profit"] / regional["revenue"] * 100).round(2)
regional["avg_order_value"] = regional["avg_order_value"].round(2)
regional.to_csv(f"{OUT}/vw_regional_summary.csv", index=False)
print(f"  ✅  vw_regional_summary     {len(regional):>4} rows")

# ── VW_CARRIER_PERFORMANCE ───────────────────────────────────
carrier_perf = (
    ship_done.groupby("carrier", as_index=False)
    .agg(
        total_shipments    = ("shipment_id",   "count"),
        on_time_count      = ("on_time",       "sum"),
        avg_delay_days     = ("delay_days",    "mean"),
        avg_shipment_cost  = ("shipment_cost", "mean"),
        total_shipment_cost= ("shipment_cost", "sum"),
    )
)
carrier_perf["on_time_pct"]       = (carrier_perf["on_time_count"] / carrier_perf["total_shipments"] * 100).round(2)
carrier_perf["avg_delay_days"]    = carrier_perf["avg_delay_days"].round(2)
carrier_perf["avg_shipment_cost"] = carrier_perf["avg_shipment_cost"].round(2)
carrier_perf.to_csv(f"{OUT}/vw_carrier_performance.csv", index=False)
print(f"  ✅  vw_carrier_performance  {len(carrier_perf):>4} rows")

print(f"\n🎉  Done — all Tableau CSVs in  {OUT}/")
