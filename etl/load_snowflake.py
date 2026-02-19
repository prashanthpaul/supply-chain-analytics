"""
Supply Chain Analytics — ETL Pipeline
Loads generated CSV files into Snowflake tables using snowflake-connector-python
"""
import os
import sys
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
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
    """Load a CSV into a Snowflake table using write_pandas."""
    path = os.path.join(DATA_DIR, f"{table_name}.csv")
    if not os.path.exists(path):
        print(f"  ❌  Missing file: {path}")
        return 0

    df = pd.read_csv(path)

    # Snowflake column names must be upper-case for write_pandas
    df.columns = [c.upper() for c in df.columns]

    # Convert boolean columns
    for col in df.select_dtypes(include="object").columns:
        if df[col].dropna().isin(["True", "False"]).all():
            df[col] = df[col].map({"True": True, "False": False})

    success, nchunks, nrows, _ = write_pandas(
        conn,
        df,
        table_name.upper(),
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"],
        overwrite=True,
        quote_identifiers=False,
    )

    status = "✅" if success else "❌"
    print(f"  {status}  {table_name.upper():<15} {nrows:>6,} rows loaded")
    return nrows


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
