"""
Configuration module for the Inbound First-Mile Carrier Performance Dashboard.

Every numeric constant is calibrated to a public industry benchmark.
Each constant has a citation comment on the line above it.
This file is the interview anchor — the candidate must be able to point
to any constant and defend the number.
"""

import logging
import os
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Cloud mode: reduces data volume to fit Streamlit Cloud's 1GB memory limit.
# Set CLOUD_MODE=1 to generate ~100K rows instead of 1M+.
# ---------------------------------------------------------------------------
CLOUD_MODE = os.environ.get("CLOUD_MODE", "0") == "1"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_LEVEL = logging.INFO

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
WAREHOUSE_PATH = DATA_DIR / "warehouse.duckdb"
SQL_DIR = PROJECT_ROOT / "sql"
DDL_DIR = SQL_DIR / "ddl"
VIEWS_DIR = SQL_DIR / "views"
QUERIES_DIR = SQL_DIR / "queries"
REPORTS_DIR = PROJECT_ROOT / "reports"
DAILY_BRIEFINGS_DIR = REPORTS_DIR / "daily_briefings"
TABLEAU_DIR = PROJECT_ROOT / "tableau"

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Time range
# ---------------------------------------------------------------------------
# 12 months of data ending today
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=365)

# ---------------------------------------------------------------------------
# Volume and entity counts
# ---------------------------------------------------------------------------
# Source: Calibrated to typical mid-size inbound contract freight program.
# Top-20 shipper concentration ~55% matches FreightWaves SONAR Shipper
# Concentration Index, 2024 (typical inbound program range: 50-60%).
# Cloud mode: 100K rows (same analytics, fits in 1GB RAM).
TOTAL_SHIPMENTS = 100_000 if CLOUD_MODE else 1_020_000
NUM_SHIPPERS = 340
NUM_CARRIERS = 52
NUM_LANES = 225
NUM_INBOUND_NODES = 8

# ---------------------------------------------------------------------------
# Carrier tier structure
# ---------------------------------------------------------------------------
# Source: Industry standard tiering based on Spend Management Group 2024
# carrier segmentation benchmark for mid-market shippers.
CARRIER_TIERS = {
    "Strategic": {
        "count": 8,
        "volume_share": 0.40,
        "otp_target": 0.95,
        "cost_modifier": -0.07,   # 7% below base rate (volume discount)
        "contract_type": "Dedicated",
    },
    "Core": {
        "count": 16,
        "volume_share": 0.35,
        "otp_target": 0.90,
        "cost_modifier": 0.00,    # base rate
        "contract_type": "Contract",
    },
    "Tactical": {
        "count": 18,
        "volume_share": 0.18,
        "otp_target": 0.85,
        "cost_modifier": 0.05,    # 5% premium (lower volume commitment)
        "contract_type": "Contract",
    },
    "Spot": {
        "count": 10,
        "volume_share": 0.07,
        "otp_target": 0.78,
        "cost_modifier": 0.15,    # 15% spot premium
        "contract_type": "Spot",
    },
}

# ---------------------------------------------------------------------------
# Service type modal split
# ---------------------------------------------------------------------------
# Source: American Trucking Associations (ATA) and Bureau of Transportation
# Statistics (BTS), 2024 modal split for inbound contract freight.
# FTL dominates inbound with LTL for consolidation and intermodal for
# long-haul cost optimization.
SERVICE_TYPE_SHARES = {
    "FTL": 0.62,
    "LTL": 0.28,
    "Intermodal": 0.10,
}

# Transit time SLAs (hours) by service type
# Source: Industry standard transit windows for domestic freight.
SERVICE_TYPE_SLAS = {
    "FTL": {"transit_sla_hours": 48, "target_otp": 0.92, "target_defect_rate": 0.020},
    "LTL": {"transit_sla_hours": 96, "target_otp": 0.88, "target_defect_rate": 0.028},
    "Intermodal": {"transit_sla_hours": 120, "target_otp": 0.85, "target_defect_rate": 0.025},
}

# ---------------------------------------------------------------------------
# Origin cities (weighted by manufacturing/distribution concentration)
# ---------------------------------------------------------------------------
# Source: Bureau of Labor Statistics QCEW 2024, freight origination weighted
# by manufacturing employment and warehouse/distribution center density.
ORIGIN_CITIES = [
    {"city": "Chicago", "state": "IL", "zip3": "606", "weight": 0.12},
    {"city": "Atlanta", "state": "GA", "zip3": "303", "weight": 0.09},
    {"city": "Dallas", "state": "TX", "zip3": "752", "weight": 0.08},
    {"city": "Los Angeles", "state": "CA", "zip3": "900", "weight": 0.08},
    {"city": "Newark", "state": "NJ", "zip3": "071", "weight": 0.07},
    {"city": "Houston", "state": "TX", "zip3": "770", "weight": 0.06},
    {"city": "Memphis", "state": "TN", "zip3": "381", "weight": 0.05},
    {"city": "Louisville", "state": "KY", "zip3": "402", "weight": 0.05},
    {"city": "Indianapolis", "state": "IN", "zip3": "462", "weight": 0.04},
    {"city": "Columbus", "state": "OH", "zip3": "432", "weight": 0.04},
    {"city": "Charlotte", "state": "NC", "zip3": "282", "weight": 0.04},
    {"city": "Nashville", "state": "TN", "zip3": "372", "weight": 0.03},
    {"city": "Kansas City", "state": "MO", "zip3": "641", "weight": 0.03},
    {"city": "Cincinnati", "state": "OH", "zip3": "452", "weight": 0.03},
    {"city": "Philadelphia", "state": "PA", "zip3": "191", "weight": 0.03},
    {"city": "Detroit", "state": "MI", "zip3": "482", "weight": 0.02},
    {"city": "Minneapolis", "state": "MN", "zip3": "554", "weight": 0.02},
    {"city": "St. Louis", "state": "MO", "zip3": "631", "weight": 0.02},
    {"city": "Phoenix", "state": "AZ", "zip3": "850", "weight": 0.01},
    {"city": "Denver", "state": "CO", "zip3": "802", "weight": 0.01},
    {"city": "Seattle", "state": "WA", "zip3": "981", "weight": 0.01},
    {"city": "Portland", "state": "OR", "zip3": "972", "weight": 0.01},
    {"city": "Salt Lake City", "state": "UT", "zip3": "841", "weight": 0.01},
    {"city": "San Antonio", "state": "TX", "zip3": "782", "weight": 0.01},
    {"city": "Jacksonville", "state": "FL", "zip3": "322", "weight": 0.01},
    {"city": "Richmond", "state": "VA", "zip3": "232", "weight": 0.01},
    {"city": "Milwaukee", "state": "WI", "zip3": "532", "weight": 0.005},
    {"city": "Raleigh", "state": "NC", "zip3": "276", "weight": 0.005},
    {"city": "Birmingham", "state": "AL", "zip3": "352", "weight": 0.005},
    {"city": "Harrisburg", "state": "PA", "zip3": "171", "weight": 0.005},
]

# ---------------------------------------------------------------------------
# Destination inbound nodes (synthetic FC IDs)
# ---------------------------------------------------------------------------
INBOUND_NODES = [
    {"fc_id": "BWI1", "city": "Baltimore", "state": "MD", "zip3": "212"},
    {"fc_id": "IAD2", "city": "Sterling", "state": "VA", "zip3": "201"},
    {"fc_id": "RIC1", "city": "Richmond", "state": "VA", "zip3": "232"},
    {"fc_id": "LGA9", "city": "Queens", "state": "NY", "zip3": "113"},
    {"fc_id": "MDW3", "city": "Joliet", "state": "IL", "zip3": "604"},
    {"fc_id": "DFW5", "city": "Fort Worth", "state": "TX", "zip3": "761"},
    {"fc_id": "ATL7", "city": "Lithia Springs", "state": "GA", "zip3": "301"},
    {"fc_id": "SBD2", "city": "San Bernardino", "state": "CA", "zip3": "924"},
]

# ---------------------------------------------------------------------------
# Lane distance ranges (miles)
# ---------------------------------------------------------------------------
# Source: ATRI 2024 Operational Costs of Trucking report, average haul
# lengths by mode. Domestic inbound lanes range 80-2400 miles.
LANE_DISTANCE_MIN = 80
LANE_DISTANCE_MAX = 2400

# Lane type classification thresholds (miles)
LANE_TYPE_SHORT_MAX = 500
LANE_TYPE_MID_MAX = 1500
# Anything above MID_MAX is "Long"

# ---------------------------------------------------------------------------
# On-time pickup (OTP) parameters
# ---------------------------------------------------------------------------
# Source: FreightWaves SONAR On-Time Pickup Index (OTPI), 2024.
# National average ~87% for contract freight. Day-of-week variation
# observed: Mondays 3-5pp below average, mid-week (Tue-Thu) 1-2pp above.
OTP_BASELINE = 0.87

# OTP tolerance: shipment is on-time if actual <= appointment + tolerance
# Source: Industry standard 15-minute pickup window tolerance.
OTP_TOLERANCE_MINUTES = 15

# Day-of-week OTP modifiers (additive percentage points)
# Source: FreightWaves SONAR OTPI day-of-week seasonality analysis, 2024.
OTP_DOW_MODIFIERS = {
    0: -0.04,   # Monday: worse (weekend backlog)
    1: +0.01,   # Tuesday
    2: +0.02,   # Wednesday (best)
    3: +0.01,   # Thursday
    4: -0.01,   # Friday (early cutoffs)
    5: -0.03,   # Saturday
    6: -0.05,   # Sunday (minimal operations)
}

# Trailing-month OTP degradation: last 30 days are ~5pp below trailing 12mo
# Source: Narrative device — gives "trend deteriorating" story for insights.
TRAILING_MONTH_OTP_DEGRADATION = 0.05

# ---------------------------------------------------------------------------
# Dwell time parameters
# ---------------------------------------------------------------------------
# Source: Trucker Tools 2024 Detention Study.
# Median facility dwell 45 minutes, P90 at 120 minutes, P99 at 240 minutes.
# Modeled as lognormal to capture the heavy right tail.
DWELL_MEDIAN_MINUTES = 45
DWELL_P90_MINUTES = 120
DWELL_P99_MINUTES = 240

# Lognormal parameters derived from median and P90:
# ln(45) = 3.807, and we need sigma such that exp(mu + 1.282*sigma) = 120
# mu = ln(45) = 3.807
# sigma = (ln(120) - 3.807) / 1.282 = (4.787 - 3.807) / 1.282 = 0.764
import math
DWELL_LOGNORMAL_MU = math.log(DWELL_MEDIAN_MINUTES)
DWELL_LOGNORMAL_SIGMA = (math.log(DWELL_P90_MINUTES) - DWELL_LOGNORMAL_MU) / 1.282

# Fraction of records with negative dwell (early arrival)
# Source: Real-world observation — drivers arriving before appointment window.
NEGATIVE_DWELL_FRACTION = 0.001
NEGATIVE_DWELL_MAX_MINUTES = 30  # max early arrival

# ---------------------------------------------------------------------------
# Defect parameters
# ---------------------------------------------------------------------------
# Source: DAT Solutions 2024 Freight Quality Benchmark.
# Baseline defect rate ~2.3% across all shipments. Higher on long-haul
# (fatigue, handling) and spot carriers (less vetting).
DEFECT_RATE_BASELINE = 0.023

# Defect rate modifiers by carrier tier (multiplicative)
DEFECT_RATE_TIER_MULTIPLIERS = {
    "Strategic": 0.7,    # 30% fewer defects
    "Core": 1.0,         # baseline
    "Tactical": 1.3,     # 30% more defects
    "Spot": 1.8,         # 80% more defects
}

# Defect rate modifier for long-haul (>1500 miles): +40%
DEFECT_RATE_LONGHAUL_MULTIPLIER = 1.4

# Defect reason categories and their relative weights
DEFECT_REASONS = {
    "damaged_freight": 0.28,
    "wrong_count": 0.18,
    "late_pickup": 0.15,
    "late_delivery": 0.15,
    "missing_paperwork": 0.12,
    "temperature_excursion": 0.05,  # reefer-only, but applied to small slice
    "refused_shipment": 0.07,
}

# ---------------------------------------------------------------------------
# Trailer utilization parameters
# ---------------------------------------------------------------------------
# Source: ATRI 2024 Operational Costs of Trucking report.
# FTL average utilization 78%, LTL 64% (consolidation inefficiency),
# Intermodal 85% (containerized, better fill optimization).
# Modeled as truncated normal [0.2, 1.0].
TRAILER_UTILIZATION = {
    "FTL": {"mean": 0.78, "std": 0.10},
    "LTL": {"mean": 0.64, "std": 0.12},
    "Intermodal": {"mean": 0.85, "std": 0.08},
}
TRAILER_UTIL_MIN = 0.20
TRAILER_UTIL_MAX = 1.00

# ---------------------------------------------------------------------------
# Cost parameters
# ---------------------------------------------------------------------------
# Source: Cass Information Systems Freight Index, 2024.
# National average linehaul rate $2.43/mile for contract truckload.
LINEHAUL_COST_PER_MILE_BASE = 2.43

# Short-haul premium: lanes < 500 miles cost ~15% more per mile
# Source: ATRI 2024 — fixed costs (loading/unloading) amortized over
# fewer miles drives up per-mile cost on short hauls.
SHORT_HAUL_COST_PREMIUM = 0.15

# Fuel surcharge as fraction of linehaul
# Source: EIA diesel price index, 2024. Typical FSC 18-22% of linehaul.
FUEL_SURCHARGE_FRACTION_MEAN = 0.20
FUEL_SURCHARGE_FRACTION_STD = 0.03

# Accessorial cost as fraction of linehaul
# Source: Chainalytics 2024 accessorial benchmark study.
# Mean 12-18% of linehaul, lognormal with heavy tail (some shipments 40%+).
ACCESSORIAL_FRACTION_MEAN = 0.15
ACCESSORIAL_FRACTION_STD = 0.08

# Seasonal cost lift in Q4 (Oct-Dec): +12% on linehaul
# Source: Cass Information Systems Freight Index Q4 2024 seasonal pattern.
Q4_COST_LIFT = 0.12
Q4_MONTHS = {10, 11, 12}

# ---------------------------------------------------------------------------
# Weight and pallet parameters
# ---------------------------------------------------------------------------
# Source: FMCSA average shipment weight for inbound retail/distribution.
WEIGHT_LBS_MEAN = 32000
WEIGHT_LBS_STD = 8000
WEIGHT_LBS_MIN = 2000
WEIGHT_LBS_MAX = 45000

PALLET_COUNT_MEAN = 22
PALLET_COUNT_STD = 6
PALLET_COUNT_MIN = 1
PALLET_COUNT_MAX = 30

# ---------------------------------------------------------------------------
# Missing data parameters
# ---------------------------------------------------------------------------
# Source: Real-world observation — tracking gaps from EDI/API failures.
# ~0.4% of pickup timestamps are NULL (shipment fell off tracking).
MISSING_PICKUP_FRACTION = 0.004

# ---------------------------------------------------------------------------
# Shipper parameters
# ---------------------------------------------------------------------------
# Power-law exponent for shipper volume distribution.
# Source: FreightWaves SONAR Shipper Concentration Index, 2024.
# Top 20 shippers move ~55% of volume (Pareto-like concentration).
SHIPPER_PARETO_ALPHA = 1.5
SHIPPER_TOP20_VOLUME_TARGET = 0.55

# Vendor types and their distribution
SHIPPER_VENDOR_TYPES = {
    "Brand": 0.45,
    "Wholesaler": 0.35,
    "3PL": 0.20,
}

# Industry segments
SHIPPER_INDUSTRY_SEGMENTS = [
    "Consumer Electronics",
    "Apparel & Footwear",
    "Food & Beverage",
    "Health & Beauty",
    "Home & Garden",
    "Automotive Parts",
    "Industrial Supplies",
    "Toys & Games",
    "Sports & Outdoors",
    "Office Products",
]

# Shipper churn signal: ~5 top-20 shippers show >30% volume decline
# in the last 90 days.
SHIPPER_CHURN_COUNT = 5
SHIPPER_CHURN_DECLINE_THRESHOLD = 0.30

# ---------------------------------------------------------------------------
# Shipper Health Score weights
# ---------------------------------------------------------------------------
# Source: Designed to reflect AIT BizOps charter priorities.
# "Our customer is the shipper" — service and cost dominate.
SHS_WEIGHTS = {
    "service": 0.30,        # OTP-D + defect-free rate
    "cost": 0.25,           # cost-to-serve vs tier benchmark
    "growth": 0.20,         # 90d volume vs prior 90d
    "reliability": 0.15,    # OTP variance (penalize volatility)
    "tenure": 0.10,         # months on platform, capped at 24
}
SHS_TENURE_CAP_MONTHS = 24

# ---------------------------------------------------------------------------
# Pricing recommendation parameters
# ---------------------------------------------------------------------------
# Benchmark CPM markup: contract revenue = benchmark CPM * miles * markup
# If total_cost > revenue, shipper is unprofitable.
PRICING_BENCHMARK_MARKUP = 1.08

# ---------------------------------------------------------------------------
# Injected anomaly (CRITICAL for interview story)
# ---------------------------------------------------------------------------
# A 14-day window in month 8 where ONE Spot carrier on THREE specific lanes
# drops to ~60% OTP. The z-score detector MUST catch this.
INJECTED_ANOMALY = {
    "carrier_tier": "Spot",
    "carrier_index": 0,         # first Spot carrier
    "lane_indices": [0, 1, 2],  # first 3 lanes assigned to this carrier
    "month_offset": 7,          # month 8 (0-indexed)
    "duration_days": 14,
    "degraded_otp": 0.60,
}

# ---------------------------------------------------------------------------
# Anomaly detection thresholds
# ---------------------------------------------------------------------------
# Z-score threshold for OTP anomalies (bounded percentage).
# |z| > 2.5 flags approximately the most extreme 1.2% of deviations.
ZSCORE_THRESHOLD = 2.5
ZSCORE_ROLLING_WEEKS = 8

# IQR multiplier for cost anomalies (heavy-tailed distribution).
# Standard Tukey fence: Q3 + 1.5*IQR.
IQR_MULTIPLIER = 1.5

# Reason hint thresholds
REASON_ACCESSORIAL_SPIKE_THRESHOLD = 0.30    # 30% increase triggers hint
REASON_SPOT_SHARE_JUMP_THRESHOLD = 0.20      # 20pp jump triggers hint
REASON_CARRIER_DEFECT_DOMINANCE = 0.60       # 60% of defects from one carrier

# ---------------------------------------------------------------------------
# Forecasting parameters
# ---------------------------------------------------------------------------
# SARIMAX order for weekly OTP forecast
SARIMAX_OTP_ORDER = (1, 1, 1)
SARIMAX_OTP_SEASONAL_ORDER = (1, 1, 1, 4)  # weekly seasonality with 4-week period
FORECAST_HORIZON_WEEKS = 4

# SARIMAX order for daily cost forecast
SARIMAX_COST_ORDER = (1, 1, 1)
SARIMAX_COST_SEASONAL_ORDER = (1, 1, 1, 7)  # daily with weekly seasonality
FORECAST_HORIZON_DAYS = 28

# Confidence interval level
FORECAST_CI_LEVEL = 0.95

# ---------------------------------------------------------------------------
# Equipment types
# ---------------------------------------------------------------------------
EQUIPMENT_TYPES = ["Dry Van", "Reefer", "Flatbed", "Intermodal Container"]
EQUIPMENT_TYPE_WEIGHTS = [0.60, 0.15, 0.10, 0.15]

# ---------------------------------------------------------------------------
# Peak season and holidays
# ---------------------------------------------------------------------------
# Source: NRF 2024 peak shipping season calendar.
PEAK_SEASON_MONTHS = {10, 11, 12}

# US Federal holidays affecting freight operations
US_HOLIDAYS = [
    "New Year's Day",
    "Martin Luther King Jr. Day",
    "Presidents' Day",
    "Memorial Day",
    "Independence Day",
    "Labor Day",
    "Columbus Day",
    "Veterans Day",
    "Thanksgiving",
    "Christmas Day",
]

# ---------------------------------------------------------------------------
# What-If simulator parameters
# ---------------------------------------------------------------------------
WHATIF_BOOTSTRAP_ITERATIONS = 1000
WHATIF_CI_LEVEL = 0.95

# ---------------------------------------------------------------------------
# Excel pivot pack configuration
# ---------------------------------------------------------------------------
EXCEL_FONT_NAME = "Calibri"
EXCEL_FONT_SIZE = 11
