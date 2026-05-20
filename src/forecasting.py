"""
SARIMAX forecasting module for OTP and cost predictions.

Produces 4-week OTP forecasts and 28-day cost forecasts with
confidence intervals.

Usage:
    python -m src.forecasting
"""

import logging
import warnings

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.config import (
    FORECAST_CI_LEVEL,
    FORECAST_HORIZON_DAYS,
    FORECAST_HORIZON_WEEKS,
    REPORTS_DIR,
    SARIMAX_COST_ORDER,
    SARIMAX_COST_SEASONAL_ORDER,
    SARIMAX_OTP_ORDER,
    SARIMAX_OTP_SEASONAL_ORDER,
    WAREHOUSE_PATH,
)

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)


def forecast_otp(con):
    """SARIMAX forecast for weekly network OTP, 4 weeks ahead."""
    logger.info("Forecasting weekly OTP...")

    df = con.execute("""
        SELECT
            d.year, d.week_of_year,
            MIN(d.date) AS week_start,
            AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp
        FROM fact_shipment f
        JOIN dim_date d ON f.shipment_date_key = d.date_key
        GROUP BY d.year, d.week_of_year
        ORDER BY d.year, d.week_of_year
    """).fetchdf()

    df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.set_index("week_start").sort_index()

    # Use a simpler model if data is short
    n = len(df)
    if n < 20:
        logger.warning("Insufficient data for SARIMAX (%d weeks). Skipping.", n)
        return None

    try:
        model = SARIMAX(
            df["otp"],
            order=SARIMAX_OTP_ORDER,
            seasonal_order=SARIMAX_OTP_SEASONAL_ORDER,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False, maxiter=200)
        forecast = fit.get_forecast(steps=FORECAST_HORIZON_WEEKS)
        pred = forecast.predicted_mean
        ci = forecast.conf_int(alpha=1 - FORECAST_CI_LEVEL)
    except Exception as e:
        logger.warning("SARIMAX OTP failed: %s. Falling back to simple model.", e)
        model = SARIMAX(df["otp"], order=(1, 0, 0), enforce_stationarity=False)
        fit = model.fit(disp=False)
        forecast = fit.get_forecast(steps=FORECAST_HORIZON_WEEKS)
        pred = forecast.predicted_mean
        ci = forecast.conf_int(alpha=1 - FORECAST_CI_LEVEL)

    # Save CSV
    fc_df = pd.DataFrame({
        "week": range(1, FORECAST_HORIZON_WEEKS + 1),
        "otp_forecast": pred.values,
        "otp_lower": ci.iloc[:, 0].values,
        "otp_upper": ci.iloc[:, 1].values,
    })
    fc_df.to_csv(REPORTS_DIR / "forecast_otp.csv", index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["otp"] * 100, label="Observed OTP %", color="#2c3e50")

    future_dates = pd.date_range(
        df.index[-1] + pd.Timedelta(weeks=1),
        periods=FORECAST_HORIZON_WEEKS,
        freq="W",
    )
    ax.plot(future_dates, pred.values * 100, "--", label="Forecast", color="#e74c3c")
    ax.fill_between(
        future_dates,
        ci.iloc[:, 0].values * 100,
        ci.iloc[:, 1].values * 100,
        alpha=0.2,
        color="#e74c3c",
        label="95% CI",
    )
    ax.axhline(y=90, color="#95a5a6", linestyle=":", label="Target (90%)")
    ax.set_title("Weekly Network OTP -- 4-Week Forecast")
    ax.set_ylabel("OTP %")
    ax.set_xlabel("Week")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "forecast_otp.png", dpi=150)
    plt.close()

    logger.info("OTP forecast saved. AIC=%.1f, BIC=%.1f", fit.aic, fit.bic)
    return fit


def forecast_cost(con):
    """SARIMAX forecast for daily total cost, 28 days ahead."""
    logger.info("Forecasting daily total cost...")

    df = con.execute("""
        SELECT
            d.date,
            SUM(f.total_cost_usd) AS daily_cost
        FROM fact_shipment f
        JOIN dim_date d ON f.shipment_date_key = d.date_key
        GROUP BY d.date
        ORDER BY d.date
    """).fetchdf()

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    n = len(df)
    if n < 30:
        logger.warning("Insufficient data for cost SARIMAX (%d days). Skipping.", n)
        return None

    try:
        model = SARIMAX(
            df["daily_cost"],
            order=SARIMAX_COST_ORDER,
            seasonal_order=SARIMAX_COST_SEASONAL_ORDER,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False, maxiter=200)
        forecast = fit.get_forecast(steps=FORECAST_HORIZON_DAYS)
        pred = forecast.predicted_mean
        ci = forecast.conf_int(alpha=1 - FORECAST_CI_LEVEL)
    except Exception as e:
        logger.warning("SARIMAX cost failed: %s. Falling back.", e)
        model = SARIMAX(df["daily_cost"], order=(1, 1, 0), enforce_stationarity=False)
        fit = model.fit(disp=False)
        forecast = fit.get_forecast(steps=FORECAST_HORIZON_DAYS)
        pred = forecast.predicted_mean
        ci = forecast.conf_int(alpha=1 - FORECAST_CI_LEVEL)

    # Save
    fc_df = pd.DataFrame({
        "day": range(1, FORECAST_HORIZON_DAYS + 1),
        "cost_forecast": pred.values,
        "cost_lower": ci.iloc[:, 0].values,
        "cost_upper": ci.iloc[:, 1].values,
    })
    fc_df.to_csv(REPORTS_DIR / "forecast_cost.csv", index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    recent = df.tail(60)
    ax.plot(recent.index, recent["daily_cost"], label="Observed", color="#2c3e50")

    future_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=FORECAST_HORIZON_DAYS)
    ax.plot(future_dates, pred.values, "--", label="Forecast", color="#e74c3c")
    ax.fill_between(
        future_dates, ci.iloc[:, 0].values, ci.iloc[:, 1].values,
        alpha=0.2, color="#e74c3c", label="95% CI",
    )
    ax.set_title("Daily Total Cost -- 28-Day Forecast")
    ax.set_ylabel("Total Cost ($)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "forecast_cost.png", dpi=150)
    plt.close()

    logger.info("Cost forecast saved. AIC=%.1f, BIC=%.1f", fit.aic, fit.bic)
    return fit


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    forecast_otp(con)
    forecast_cost(con)
    con.close()

    logger.info("Forecasting complete.")


if __name__ == "__main__":
    main()
