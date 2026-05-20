"""Tests for forecasting module."""

import pytest

from src.config import REPORTS_DIR


def test_forecast_otp_csv_exists():
    """OTP forecast CSV should exist."""
    path = REPORTS_DIR / "forecast_otp.csv"
    assert path.exists(), "forecast_otp.csv not found"


def test_forecast_otp_png_exists():
    """OTP forecast plot should exist."""
    path = REPORTS_DIR / "forecast_otp.png"
    assert path.exists(), "forecast_otp.png not found"


def test_forecast_cost_csv_exists():
    """Cost forecast CSV should exist."""
    path = REPORTS_DIR / "forecast_cost.csv"
    assert path.exists(), "forecast_cost.csv not found"


def test_forecast_has_correct_horizon():
    """OTP forecast should have 4-week horizon."""
    import pandas as pd
    df = pd.read_csv(REPORTS_DIR / "forecast_otp.csv")
    assert len(df) == 4, f"Expected 4 forecast rows, got {len(df)}"
    assert "otp_forecast" in df.columns
    assert "otp_lower" in df.columns
    assert "otp_upper" in df.columns


def test_forecast_intervals_valid():
    """Confidence intervals should bracket the point forecast."""
    import pandas as pd
    df = pd.read_csv(REPORTS_DIR / "forecast_otp.csv")
    for _, row in df.iterrows():
        assert row["otp_lower"] <= row["otp_forecast"] <= row["otp_upper"], \
            f"CI not bracketing forecast: {row['otp_lower']} <= {row['otp_forecast']} <= {row['otp_upper']}"
