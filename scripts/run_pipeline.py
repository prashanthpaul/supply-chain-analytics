"""
Supply Chain Analytics — One-Command Pipeline Runner
Usage:
    python scripts/run_pipeline.py           # full pipeline
    python scripts/run_pipeline.py --data    # generate data only
    python scripts/run_pipeline.py --etl     # load to Snowflake only
    python scripts/run_pipeline.py --report  # generate AI report only
    python scripts/run_pipeline.py --app     # launch Streamlit app
"""
import argparse
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable


def step(label: str, cmd: list[str]):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"\n❌  Step failed: {label}")
        sys.exit(result.returncode)
    print(f"✅  Done: {label}")


def main():
    parser = argparse.ArgumentParser(description="Supply Chain Analytics pipeline runner")
    parser.add_argument("--data",   action="store_true", help="Generate synthetic data only")
    parser.add_argument("--etl",    action="store_true", help="Load data to Snowflake only")
    parser.add_argument("--report", action="store_true", help="Generate AI report only")
    parser.add_argument("--app",    action="store_true", help="Launch Streamlit app only")
    args = parser.parse_args()

    run_all = not any([args.data, args.etl, args.report, args.app])

    print("\n🏭  Supply Chain Analytics Pipeline")
    print("=" * 60)

    if args.data or run_all:
        step("Step 1/3 — Generate synthetic data",
             [PYTHON, "data/generate_data.py"])

    if args.etl or run_all:
        step("Step 2/3 — ETL: Load data to Snowflake",
             [PYTHON, "etl/load_snowflake.py"])

    if args.report or run_all:
        step("Step 3/3 — Generate AI report",
             [PYTHON, "ai/report_generator.py", "weekly"])

    if args.app or run_all:
        print("\n🚀  Launching Streamlit dashboard ...")
        print("    Open: http://localhost:8501")
        subprocess.run([PYTHON, "-m", "streamlit", "run", "streamlit/app.py"], cwd=ROOT)

    if run_all:
        print("\n\n🎉  Full pipeline complete!")
        print("    📊 Tableau: open tableau/supply_chain.twb in Tableau Desktop")
        print("    🌐 Streamlit: run `python scripts/run_pipeline.py --app`")
        print("    📋 Reports:  check reports/ directory")


if __name__ == "__main__":
    main()
