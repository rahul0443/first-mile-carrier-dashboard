"""
KPI computation module. Materializes business views for dashboard consumption.

Usage:
    python -m src.compute_kpis
"""

import logging

import duckdb
import pandas as pd

from src.config import REPORTS_DIR, WAREHOUSE_PATH

logger = logging.getLogger(__name__)


def compute_kpis(con):
    """Compute and export key KPI summaries."""
    logger.info("Computing KPIs...")

    # Network-level KPIs
    network = con.execute("""
        SELECT
            COUNT(*) AS total_shipments,
            ROUND(AVG(CASE WHEN on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
            ROUND(AVG(CASE WHEN on_time_delivery THEN 1.0 ELSE 0.0 END) * 100, 1) AS otd_pct,
            ROUND(AVG(CASE WHEN dwell_minutes > 0 THEN dwell_minutes END), 1) AS avg_dwell,
            ROUND(AVG(CASE WHEN defect_flag THEN 1.0 ELSE 0.0 END) * 100, 2) AS defect_rate_pct,
            ROUND(AVG(trailer_utilization_pct) * 100, 1) AS avg_utilization_pct,
            ROUND(AVG(total_cost_usd), 2) AS avg_cost_per_shipment,
            ROUND(AVG(total_cost_usd / NULLIF(distance_miles, 0)), 2) AS avg_cpm,
            ROUND(SUM(total_cost_usd), 0) AS total_cost
        FROM fact_shipment
    """).fetchdf()

    logger.info("Network KPIs: OTP=%.1f%%, Defect=%.2f%%, AvgCost=$%.2f",
                network["otp_pct"].iloc[0],
                network["defect_rate_pct"].iloc[0],
                network["avg_cost_per_shipment"].iloc[0])

    # Export weekly KPIs
    weekly = con.execute("SELECT * FROM v_weekly_kpis").fetchdf()
    weekly.to_csv(REPORTS_DIR / "weekly_kpis.csv", index=False)

    # Export carrier scorecard
    carrier = con.execute("SELECT * FROM v_carrier_scorecard").fetchdf()
    carrier.to_csv(REPORTS_DIR / "carrier_scorecard.csv", index=False)

    # Export lane performance
    lane = con.execute("SELECT * FROM v_lane_performance").fetchdf()
    lane.to_csv(REPORTS_DIR / "lane_performance.csv", index=False)

    # Export shipper health
    shipper = con.execute("SELECT * FROM v_shipper_health").fetchdf()
    shipper.to_csv(REPORTS_DIR / "shipper_health.csv", index=False)

    logger.info("KPI exports saved to %s", REPORTS_DIR)
    return network


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    compute_kpis(con)
    con.close()

    logger.info("KPI computation complete.")


if __name__ == "__main__":
    main()
