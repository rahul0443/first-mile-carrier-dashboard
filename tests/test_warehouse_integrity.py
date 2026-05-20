"""Tests for warehouse integrity."""

import duckdb
import pytest

from src.config import WAREHOUSE_PATH


@pytest.fixture(scope="module")
def con():
    connection = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    yield connection
    connection.close()


def test_cost_identity_exact(con):
    """linehaul + fuel + accessorial must exactly equal total for all rows."""
    mismatches = con.execute("""
        SELECT COUNT(*) FROM fact_shipment
        WHERE linehaul_cost_usd + fuel_surcharge_usd + accessorial_cost_usd != total_cost_usd
    """).fetchone()[0]
    assert mismatches == 0, f"{mismatches} rows with cost identity mismatch"


def test_dimension_row_counts(con):
    """Dimension tables have expected row counts."""
    assert con.execute("SELECT COUNT(*) FROM dim_carrier").fetchone()[0] == 52
    assert con.execute("SELECT COUNT(*) FROM dim_lane").fetchone()[0] == 225
    assert con.execute("SELECT COUNT(*) FROM dim_shipper").fetchone()[0] == 340
    assert con.execute("SELECT COUNT(*) FROM dim_service_type").fetchone()[0] == 3
    assert con.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0] >= 365


def test_service_types_correct(con):
    """Service types should be FTL, LTL, Intermodal."""
    types = con.execute(
        "SELECT service_name FROM dim_service_type ORDER BY service_name"
    ).fetchall()
    names = [t[0] for t in types]
    assert "FTL" in names
    assert "LTL" in names
    assert "Intermodal" in names


def test_carrier_tiers_correct(con):
    """All four carrier tiers present."""
    tiers = con.execute(
        "SELECT DISTINCT carrier_tier FROM dim_carrier ORDER BY 1"
    ).fetchall()
    tier_names = {t[0] for t in tiers}
    assert tier_names == {"Strategic", "Core", "Tactical", "Spot"}


def test_null_pickup_exists(con):
    """Some pickup_actual_ts should be NULL (tracking gaps)."""
    nulls = con.execute(
        "SELECT COUNT(*) FROM fact_shipment WHERE pickup_actual_ts IS NULL"
    ).fetchone()[0]
    assert nulls > 0, "Expected some NULL pickups"


def test_negative_dwell_exists(con):
    """Some dwell values should be negative (early arrivals)."""
    negs = con.execute(
        "SELECT COUNT(*) FROM fact_shipment WHERE dwell_minutes < 0"
    ).fetchone()[0]
    assert negs > 0, "Expected some negative dwell records"
