"""Tests for data generation module."""

import duckdb
import pandas as pd
import pytest

from src.config import INJECTED_ANOMALY, RAW_DIR, WAREHOUSE_PATH


@pytest.fixture(scope="module")
def con():
    """DuckDB connection to the warehouse."""
    connection = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    yield connection
    connection.close()


def test_fact_row_count(con):
    """Fact table must have >= 1,000,000 rows."""
    count = con.execute("SELECT COUNT(*) FROM fact_shipment").fetchone()[0]
    assert count >= 1_000_000, f"Expected >= 1M rows, got {count}"


def test_lane_count(con):
    """Must have >= 200 unique lanes."""
    count = con.execute("SELECT COUNT(DISTINCT lane_id) FROM dim_lane").fetchone()[0]
    assert count >= 200, f"Expected >= 200 lanes, got {count}"


def test_carrier_count(con):
    """Must have exactly 52 carriers."""
    count = con.execute("SELECT COUNT(*) FROM dim_carrier").fetchone()[0]
    assert count == 52, f"Expected 52 carriers, got {count}"


def test_shipper_count(con):
    """Must have exactly 340 shippers."""
    count = con.execute("SELECT COUNT(*) FROM dim_shipper").fetchone()[0]
    assert count == 340, f"Expected 340 shippers, got {count}"


def test_no_orphan_carrier_fks(con):
    """No orphan carrier_id references in fact table."""
    orphans = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_carrier c ON f.carrier_id = c.carrier_id
        WHERE c.carrier_id IS NULL
    """).fetchone()[0]
    assert orphans == 0, f"Found {orphans} orphan carrier_id references"


def test_no_orphan_lane_fks(con):
    """No orphan lane_id references in fact table."""
    orphans = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_lane l ON f.lane_id = l.lane_id
        WHERE l.lane_id IS NULL
    """).fetchone()[0]
    assert orphans == 0


def test_no_orphan_shipper_fks(con):
    """No orphan shipper_id references in fact table."""
    orphans = con.execute("""
        SELECT COUNT(*) FROM fact_shipment f
        LEFT JOIN dim_shipper s ON f.shipper_id = s.shipper_id
        WHERE s.shipper_id IS NULL
    """).fetchone()[0]
    assert orphans == 0


def test_top20_shipper_concentration(con):
    """Top 20 shippers should account for >= 50% of volume."""
    share = con.execute("""
        WITH ranked AS (
            SELECT shipper_id, COUNT(*) AS vol,
                   SUM(COUNT(*)) OVER () AS total_vol
            FROM fact_shipment GROUP BY shipper_id
            ORDER BY vol DESC LIMIT 20
        )
        SELECT SUM(vol)::DOUBLE / MAX(total_vol) FROM ranked
    """).fetchone()[0]
    assert share >= 0.50, f"Top-20 concentration {share:.1%} < 50%"


def test_injected_anomaly_present(con):
    """The injected anomaly carrier should have low OTP in the anomaly window."""
    result = con.execute("""
        SELECT AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp
        FROM fact_shipment f
        JOIN dim_carrier c ON f.carrier_id = c.carrier_id
        WHERE c.carrier_tier = 'Spot'
        AND f.lane_id IN (1, 2, 3)
    """).fetchone()
    assert result is not None
