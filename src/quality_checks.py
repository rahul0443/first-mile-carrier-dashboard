"""
Data quality checks for the warehouse.

Validates FK integrity, cost identity, NULL audits, and row counts.

Usage:
    python -m src.quality_checks
"""

import logging
import sys

import duckdb

from src.config import WAREHOUSE_PATH

logger = logging.getLogger(__name__)


def run_checks():
    """Run all data quality checks. Returns True if all pass."""
    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    passed = True

    # Check 1: Row count >= 1,000,000
    fact_count = con.execute("SELECT COUNT(*) FROM fact_shipment").fetchone()[0]
    if fact_count >= 1_000_000:
        logger.info("PASS: fact_shipment has %d rows (>= 1,000,000)", fact_count)
    else:
        logger.error("FAIL: fact_shipment has %d rows (< 1,000,000)", fact_count)
        passed = False

    # Check 2: Lane count >= 200
    lane_count = con.execute("SELECT COUNT(DISTINCT lane_id) FROM dim_lane").fetchone()[0]
    if lane_count >= 200:
        logger.info("PASS: %d unique lanes (>= 200)", lane_count)
    else:
        logger.error("FAIL: %d unique lanes (< 200)", lane_count)
        passed = False

    # Check 3: FK integrity - no orphan carrier_ids
    orphan_carriers = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_carrier c ON f.carrier_id = c.carrier_id
        WHERE c.carrier_id IS NULL
    """).fetchone()[0]
    if orphan_carriers == 0:
        logger.info("PASS: No orphan carrier_id references")
    else:
        logger.error("FAIL: %d orphan carrier_id references", orphan_carriers)
        passed = False

    # Check 4: FK integrity - no orphan lane_ids
    orphan_lanes = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_lane l ON f.lane_id = l.lane_id
        WHERE l.lane_id IS NULL
    """).fetchone()[0]
    if orphan_lanes == 0:
        logger.info("PASS: No orphan lane_id references")
    else:
        logger.error("FAIL: %d orphan lane_id references", orphan_lanes)
        passed = False

    # Check 5: FK integrity - no orphan shipper_ids
    orphan_shippers = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_shipper s ON f.shipper_id = s.shipper_id
        WHERE s.shipper_id IS NULL
    """).fetchone()[0]
    if orphan_shippers == 0:
        logger.info("PASS: No orphan shipper_id references")
    else:
        logger.error("FAIL: %d orphan shipper_id references", orphan_shippers)
        passed = False

    # Check 6: Cost identity (linehaul + fuel + accessorial == total) EXACT
    cost_mismatches = con.execute("""
        SELECT COUNT(*) FROM fact_shipment
        WHERE linehaul_cost_usd + fuel_surcharge_usd + accessorial_cost_usd != total_cost_usd
    """).fetchone()[0]
    if cost_mismatches == 0:
        logger.info("PASS: Cost identity exact across all rows")
    else:
        logger.error("FAIL: %d rows with cost identity mismatch", cost_mismatches)
        passed = False

    # Check 7: NULL pickup audit
    null_pickups = con.execute(
        "SELECT COUNT(*) FROM fact_shipment WHERE pickup_actual_ts IS NULL"
    ).fetchone()[0]
    null_pct = null_pickups / fact_count * 100
    logger.info("INFO: %d NULL pickup_actual_ts (%.2f%%)", null_pickups, null_pct)

    # Check 8: Negative dwell audit
    neg_dwell = con.execute(
        "SELECT COUNT(*) FROM fact_shipment WHERE dwell_minutes < 0"
    ).fetchone()[0]
    neg_pct = neg_dwell / fact_count * 100
    logger.info("INFO: %d negative dwell records (%.2f%%)", neg_dwell, neg_pct)

    # Check 9: Top-20 shipper concentration >= 50%
    top20_share = con.execute("""
        WITH ranked AS (
            SELECT shipper_id, COUNT(*) AS vol,
                   SUM(COUNT(*)) OVER () AS total_vol
            FROM fact_shipment
            GROUP BY shipper_id
            ORDER BY vol DESC
            LIMIT 20
        )
        SELECT SUM(vol)::DOUBLE / MAX(total_vol) FROM ranked
    """).fetchone()[0]
    if top20_share >= 0.50:
        logger.info("PASS: Top-20 shipper concentration %.1f%% (>= 50%%)", top20_share * 100)
    else:
        logger.error("FAIL: Top-20 shipper concentration %.1f%% (< 50%%)", top20_share * 100)
        passed = False

    con.close()

    if passed:
        logger.info("All quality checks PASSED.")
    else:
        logger.error("Some quality checks FAILED.")

    return passed


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    success = run_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
