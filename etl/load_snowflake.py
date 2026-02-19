"""
Supply Chain Analytics — ETL Pipeline
Loads generated CSV files into Snowflake tables using snowflake-connector-python
"""
import os
import sys
import pandas as pd
import snowflake.connector
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
    "schema":    os.environ.get("SNOWFLAKE_SCHEMA",   "ANALYTICS"),
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
SQL_DIR  = os.path.join(os.path.dirname(__file__), "..", "sql")

TABLE_ORDER = ["suppliers", "products", "customers", "orders", "shipments"]


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_connection():
    print("🔌  Connecting to Snowflake ...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    print(f"✅  Connected → {SNOWFLAKE_CONFIG['account']} / {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
    return conn


def run_sql_file(conn, filepath: str):
    """Execute every statement in a SQL file."""
    with open(filepath, "r") as f:
        raw = f.read()
    statements = [s.strip() for s in raw.split(";") if s.strip()]
    cur = conn.cursor()
    for stmt in statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            print(f"  ⚠️  SQL warning (continuing): {e}")
    cur.close()


def load_table(conn, table_name: str):
    """Load a CSV into a Snowflake table using direct INSERT via executemany."""
    path = os.path.join(DATA_DIR, f"{table_name}.csv")
    if not os.path.exists(path):
        print(f"  ❌  Missing file: {path}")
        return 0

    df = pd.read_csv(path)

    # Replace NaN with None so Snowflake gets NULL
    df = df.where(pd.notnull(df), None)

    # Convert Python bool strings to actual bools
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna()
        if not sample.empty and sample.isin(["True", "False"]).all():
            df[col] = df[col].map({"True": True, "False": False})

    cur = conn.cursor()
    # Truncate first so re-runs are safe
    cur.execute(f"TRUNCATE TABLE IF EXISTS {table_name.upper()}")

    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql   = f"INSERT INTO {table_name.upper()} VALUES ({placeholders})"
    # Convert any remaining float NaN to None for Snowflake NULL
    import math
    def clean(v):
        if v is None: return None
        if isinstance(v, float) and math.isnan(v): return None
        return v
    rows = [tuple(clean(v) for v in r) for r in df.itertuples(index=False, name=None)]

    # Batch in chunks of 1 000 to avoid request-size limits
    chunk = 1000
    for i in range(0, len(rows), chunk):
        cur.executemany(insert_sql, rows[i:i+chunk])

    cur.close()
    print(f"  ✅  {table_name.upper():<15} {len(df):>6,} rows loaded")
    return len(df)


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    conn = get_connection()

    # 1. Create schema + tables
    print("\n📐  Creating schema and tables ...")
    run_sql_file(conn, os.path.join(SQL_DIR, "schema.sql"))
    print("✅  Schema ready")

    # 2. Load each table
    print("\n📤  Loading data ...")
    total_rows = 0
    for table in TABLE_ORDER:
        total_rows += load_table(conn, table)

    # 3. Create analytical views
    views_path = os.path.join(SQL_DIR, "create_views.sql")
    if os.path.exists(views_path):
        print("\n👁️   Creating analytical views ...")
        run_sql_file(conn, views_path)
        print("✅  Views created")

    conn.close()
    print(f"\n🎉  ETL complete — {total_rows:,} total rows loaded into Snowflake")


if __name__ == "__main__":
    main()
