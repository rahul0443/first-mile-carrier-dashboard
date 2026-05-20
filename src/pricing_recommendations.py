"""
Pricing recommendation module for per-shipper tier adjustments.

Computes realized rates, cost-to-serve trends, and recommends
pricing tier changes for top-20 shippers.

Usage:
    python -m src.pricing_recommendations
"""

import logging

import duckdb
import pandas as pd

from src.config import PRICING_BENCHMARK_MARKUP, REPORTS_DIR, WAREHOUSE_PATH

logger = logging.getLogger(__name__)


def compute_recommendations(con):
    """Compute pricing recommendations for top-20 shippers."""
    logger.info("Computing pricing recommendations...")

    df = con.execute("""
        WITH shipper_metrics AS (
            SELECT
                s.shipper_id,
                s.shipper_name,
                s.vendor_type,
                s.ship_volume_tier,
                COUNT(*) AS shipment_count,
                AVG(f.total_cost_usd) AS avg_cost_per_shipment,
                AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS avg_cpm,
                SUM(f.total_cost_usd) AS total_cost,
                AVG(f.distance_miles) AS avg_distance,
                AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
                AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_rate,
                AVG(CASE WHEN f.dwell_minutes > 0 THEN f.dwell_minutes ELSE NULL END) AS avg_dwell
            FROM fact_shipment f
            JOIN dim_shipper s ON f.shipper_id = s.shipper_id
            GROUP BY s.shipper_id, s.shipper_name, s.vendor_type, s.ship_volume_tier
            ORDER BY shipment_count DESC
            LIMIT 20
        ),
        growth AS (
            SELECT
                f.shipper_id,
                COUNT(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '90 days' THEN 1 END) AS vol_90d,
                COUNT(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '180 days'
                            AND d.date < CURRENT_DATE - INTERVAL '90 days' THEN 1 END) AS vol_prior_90d
            FROM fact_shipment f
            JOIN dim_date d ON f.shipment_date_key = d.date_key
            GROUP BY f.shipper_id
        )
        SELECT
            m.*,
            g.vol_90d,
            g.vol_prior_90d,
            CASE WHEN g.vol_prior_90d > 0
                 THEN (g.vol_90d - g.vol_prior_90d)::DOUBLE / g.vol_prior_90d
                 ELSE 0 END AS growth_rate
        FROM shipper_metrics m
        LEFT JOIN growth g ON m.shipper_id = g.shipper_id
    """).fetchdf()

    recommendations = []
    benchmark_cpm = 2.43

    for _, row in df.iterrows():
        # Revenue estimate: benchmark CPM * avg distance * markup * volume
        est_revenue = benchmark_cpm * PRICING_BENCHMARK_MARKUP * row["avg_distance"] * row["shipment_count"]
        is_profitable = est_revenue > row["total_cost"]

        # Decision logic
        drivers = []
        action = "Hold"
        pct_change = 0.0

        # Check profitability
        if not is_profitable:
            cost_gap = (row["total_cost"] - est_revenue) / est_revenue * 100
            drivers.append(f"Unprofitable: cost exceeds revenue by {cost_gap:.0f}%")
            action = "Renegotiate Up"
            pct_change = min(15, max(3, cost_gap / 2))

        # Check growth
        growth = row.get("growth_rate", 0)
        if growth < -0.20:
            drivers.append(f"Volume declining {growth*100:.0f}% (90d vs prior 90d)")
            if action == "Hold":
                action = "Volume Discount"
                pct_change = -min(8, max(2, abs(growth) * 10))

        # Check service quality
        if row["otd_rate"] < 0.85:
            drivers.append(f"Below-target OTD: {row['otd_rate']*100:.1f}%")
        if row["defect_rate"] > 0.03:
            drivers.append(f"Elevated defect rate: {row['defect_rate']*100:.1f}%")

        # High-performing shippers get volume discounts
        if growth > 0.10 and row["otd_rate"] > 0.92 and action == "Hold":
            drivers.append(f"Strong growth (+{growth*100:.0f}%) with high OTD ({row['otd_rate']*100:.0f}%)")
            action = "Volume Discount"
            pct_change = -min(5, max(2, growth * 20))

        if not drivers:
            drivers.append("Metrics within normal range")

        recommendations.append({
            "shipper_id": int(row["shipper_id"]),
            "shipper_name": row["shipper_name"],
            "vendor_type": row["vendor_type"],
            "shipment_count": int(row["shipment_count"]),
            "avg_cost_per_shipment": round(row["avg_cost_per_shipment"], 2),
            "avg_cpm": round(row["avg_cpm"], 2),
            "otd_rate": round(row["otd_rate"], 4),
            "defect_rate": round(row["defect_rate"], 4),
            "growth_rate": round(growth, 4) if growth else 0,
            "is_profitable": is_profitable,
            "recommendation": action,
            "pct_change": round(pct_change, 1),
            "driver_1": drivers[0] if len(drivers) > 0 else "",
            "driver_2": drivers[1] if len(drivers) > 1 else "",
        })

    result = pd.DataFrame(recommendations)
    result.to_csv(REPORTS_DIR / "pricing_recommendations.csv", index=False)
    logger.info("Pricing recommendations saved for %d shippers", len(result))
    return result


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    compute_recommendations(con)
    con.close()

    logger.info("Pricing recommendations complete.")


if __name__ == "__main__":
    main()
