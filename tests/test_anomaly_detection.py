"""Tests for anomaly detection module."""

import pandas as pd
import pytest

from src.config import RAW_DIR


def test_zscore_csv_exists():
    """Z-score anomaly CSV should exist and be non-empty."""
    path = RAW_DIR / "anomalies_zscore.csv"
    assert path.exists(), "anomalies_zscore.csv not found"
    df = pd.read_csv(path)
    assert len(df) > 0, "anomalies_zscore.csv is empty"


def test_iqr_csv_exists():
    """IQR anomaly CSV should exist and be non-empty."""
    path = RAW_DIR / "anomalies_iqr.csv"
    assert path.exists(), "anomalies_iqr.csv not found"
    df = pd.read_csv(path)
    assert len(df) > 0, "anomalies_iqr.csv is empty"


def test_zscore_has_required_columns():
    """Z-score CSV should have required columns."""
    df = pd.read_csv(RAW_DIR / "anomalies_zscore.csv")
    required = {"lane_id", "z_score", "severity", "reason_hint"}
    assert required.issubset(set(df.columns)), f"Missing columns: {required - set(df.columns)}"


def test_zscore_reason_hints_populated():
    """Reason hints should be populated for flagged anomalies."""
    df = pd.read_csv(RAW_DIR / "anomalies_zscore.csv")
    non_empty = df["reason_hint"].notna().sum()
    assert non_empty > 0, "No reason hints populated"


def test_daily_briefing_exists():
    """At least one daily briefing markdown should exist."""
    from src.config import DAILY_BRIEFINGS_DIR
    briefings = list(DAILY_BRIEFINGS_DIR.glob("*.md"))
    assert len(briefings) > 0, "No daily briefings found"
