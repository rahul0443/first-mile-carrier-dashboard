"""
Build the DuckDB star-schema warehouse from raw CSV files.

Executes DDL scripts, loads dimension and fact tables, creates analytical views,
and runs quality checks.

Usage:
    python -m src.build_warehouse
"""

import logging
from pathlib import Path

import duckdb

from src.config import DDL_DIR, RAW_DIR, VIEWS_DIR, WAREHOUSE_PATH

logger = logging.getLogger(__name__)


def _execute_sql_file(con, filepath: Path):
    """Execute a SQL file against the DuckDB connection."""
    sql = filepath.read_text()
    con.execute(sql)
    logger.info("Executed: %s", filepath.name)


def build():
    """Build the warehouse from raw CSVs."""
    if WAREHOUSE_PATH.exists():
        WAREHOUSE_PATH.unlink()
        logger.info("Removed existing warehouse at %s", WAREHOUSE_PATH)

    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE_PATH))

    # Load dimension tables first (FK targets)
    dim_tables = [
        ("dim_date", "02_dim_carrier.sql"),
        ("dim_carrier", "02_dim_carrier.sql"),
        ("dim_lane", "03_dim_lane.sql"),
        ("dim_shipper", "04_dim_shipper.sql"),
        ("dim_service_type", "06_dim_service_type.sql"),
        ("dim_date", "05_dim_date.sql"),
    ]

    # Execute DDL in order: dimensions first, then fact
    ddl_files = sorted(DDL_DIR.glob("*.sql"))
    # Create dimensions before fact (fact has FK refs)
    dim_ddls = [f for f in ddl_files if "dim_" in f.name]
    fact_ddls = [f for f in ddl_files if "fact_" in f.name]

    for ddl_file in dim_ddls:
        _execute_sql_file(con, ddl_file)

    # Load dimension data
    dim_csv_map = {
        "dim_date": "dim_date.csv",
        "dim_carrier": "dim_carrier.csv",
        "dim_lane": "dim_lane.csv",
        "dim_shipper": "dim_shipper.csv",
        "dim_service_type": "dim_service_type.csv",
    }

    for table_name, csv_name in dim_csv_map.items():
        csv_path = RAW_DIR / csv_name
        con.execute(f"INSERT INTO {table_name} SELECT * FROM read_csv_auto('{csv_path}')")
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info("Loaded %s: %d rows", table_name, count)

    # Create fact table
    for ddl_file in fact_ddls:
        _execute_sql_file(con, ddl_file)

    # Load fact data
    fact_path = RAW_DIR / "fact_shipment.csv"
    con.execute(f"""
        INSERT INTO fact_shipment
        SELECT * FROM read_csv_auto('{fact_path}',
            types={{
                'linehaul_cost_usd': 'DECIMAL(10,2)',
                'fuel_surcharge_usd': 'DECIMAL(10,2)',
                'accessorial_cost_usd': 'DECIMAL(10,2)',
                'total_cost_usd': 'DECIMAL(10,2)'
            }}
        )
    """)
    fact_count = con.execute("SELECT COUNT(*) FROM fact_shipment").fetchone()[0]
    logger.info("Loaded fact_shipment: %d rows", fact_count)

    # Create views
    view_files = sorted(VIEWS_DIR.glob("*.sql"))
    for view_file in view_files:
        _execute_sql_file(con, view_file)

    logger.info("Warehouse build complete at %s", WAREHOUSE_PATH)
    con.close()


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    build()


if __name__ == "__main__":
    main()
