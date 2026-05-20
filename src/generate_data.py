"""
Synthetic data generator for the Inbound First-Mile Carrier Performance Dashboard.

Generates 1,020,000 shipment records across 340 shippers, 52 carriers, and 225 lanes
with industry-calibrated distributions. Every parameter traces back to a public
benchmark cited in config.py.

Usage:
    python -m src.generate_data
"""

import logging
import math
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd

from src.config import (
    ACCESSORIAL_FRACTION_MEAN,
    ACCESSORIAL_FRACTION_STD,
    CARRIER_TIERS,
    DAILY_BRIEFINGS_DIR,
    DEFECT_RATE_BASELINE,
    DEFECT_RATE_LONGHAUL_MULTIPLIER,
    DEFECT_RATE_TIER_MULTIPLIERS,
    DEFECT_REASONS,
    DWELL_LOGNORMAL_MU,
    DWELL_LOGNORMAL_SIGMA,
    END_DATE,
    EQUIPMENT_TYPES,
    EQUIPMENT_TYPE_WEIGHTS,
    FUEL_SURCHARGE_FRACTION_MEAN,
    FUEL_SURCHARGE_FRACTION_STD,
    INBOUND_NODES,
    INJECTED_ANOMALY,
    LANE_DISTANCE_MAX,
    LANE_DISTANCE_MIN,
    LANE_TYPE_MID_MAX,
    LANE_TYPE_SHORT_MAX,
    LINEHAUL_COST_PER_MILE_BASE,
    MISSING_PICKUP_FRACTION,
    NEGATIVE_DWELL_FRACTION,
    NEGATIVE_DWELL_MAX_MINUTES,
    NUM_CARRIERS,
    NUM_LANES,
    NUM_SHIPPERS,
    ORIGIN_CITIES,
    OTP_BASELINE,
    OTP_DOW_MODIFIERS,
    OTP_TOLERANCE_MINUTES,
    PALLET_COUNT_MAX,
    PALLET_COUNT_MEAN,
    PALLET_COUNT_MIN,
    PALLET_COUNT_STD,
    Q4_COST_LIFT,
    Q4_MONTHS,
    RANDOM_SEED,
    RAW_DIR,
    SERVICE_TYPE_SHARES,
    SERVICE_TYPE_SLAS,
    SHIPPER_CHURN_COUNT,
    SHIPPER_CHURN_DECLINE_THRESHOLD,
    SHIPPER_INDUSTRY_SEGMENTS,
    SHIPPER_PARETO_ALPHA,
    SHIPPER_VENDOR_TYPES,
    SHORT_HAUL_COST_PREMIUM,
    START_DATE,
    TOTAL_SHIPMENTS,
    TRAILER_UTIL_MAX,
    TRAILER_UTIL_MIN,
    TRAILER_UTILIZATION,
    TRAILING_MONTH_OTP_DEGRADATION,
    WEIGHT_LBS_MAX,
    WEIGHT_LBS_MEAN,
    WEIGHT_LBS_MIN,
    WEIGHT_LBS_STD,
)

logger = logging.getLogger(__name__)


def _quantize(value: float) -> Decimal:
    """Round a float to two decimal places using Decimal for exact currency."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_dim_date(start_date, end_date, rng):
    """Generate date dimension covering the full time range."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    records = []
    for d in dates:
        date_key = int(d.strftime("%Y%m%d"))
        records.append({
            "date_key": date_key,
            "date": d.date(),
            "year": d.year,
            "quarter": (d.month - 1) // 3 + 1,
            "month": d.month,
            "week_of_year": d.isocalendar()[1],
            "day_of_week": d.dayofweek,
            "is_weekend": d.dayofweek >= 5,
            "is_holiday": False,
            "is_peak_season": d.month in {10, 11, 12},
        })
    return pd.DataFrame(records)


def generate_dim_carrier(rng):
    """Generate carrier dimension with tiered structure."""
    carriers = []
    carrier_id = 1
    for tier_name, tier_cfg in CARRIER_TIERS.items():
        for i in range(tier_cfg["count"]):
            prefix = tier_name[:3].upper()
            equipment = rng.choice(EQUIPMENT_TYPES, p=EQUIPMENT_TYPE_WEIGHTS)
            regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
            region = rng.choice(regions)
            start_year = rng.integers(2015, 2024)
            start_month = rng.integers(1, 13)
            carriers.append({
                "carrier_id": carrier_id,
                "carrier_name": f"{prefix}-{i + 1:02d}",
                "carrier_tier": tier_name,
                "equipment_type": equipment,
                "region_primary": region,
                "partnership_start_date": f"{start_year}-{start_month:02d}-01",
                "target_otp_pct": tier_cfg["otp_target"],
                "contract_type": tier_cfg["contract_type"],
            })
            carrier_id += 1
    return pd.DataFrame(carriers)


def generate_dim_lane(rng):
    """Generate lane dimension with origin-destination pairs."""
    origin_cities = ORIGIN_CITIES.copy()
    origin_weights = np.array([c["weight"] for c in origin_cities])
    origin_weights = origin_weights / origin_weights.sum()

    lanes = []
    lane_set = set()
    lane_id = 1

    while len(lanes) < NUM_LANES:
        origin_idx = rng.choice(len(origin_cities), p=origin_weights)
        origin = origin_cities[origin_idx]
        dest = rng.choice(INBOUND_NODES)
        key = (origin["zip3"], dest["zip3"])
        if key in lane_set:
            continue
        lane_set.add(key)

        distance = rng.uniform(LANE_DISTANCE_MIN, LANE_DISTANCE_MAX)
        distance = round(distance, 1)

        if distance <= LANE_TYPE_SHORT_MAX:
            lane_type = "Short"
        elif distance <= LANE_TYPE_MID_MAX:
            lane_type = "Mid"
        else:
            lane_type = "Long"

        lanes.append({
            "lane_id": lane_id,
            "origin_city": origin["city"],
            "origin_state": origin["state"],
            "origin_zip3": origin["zip3"],
            "dest_city": dest["city"],
            "dest_state": dest["state"],
            "dest_zip3": dest["zip3"],
            "dest_fc_id": dest["fc_id"],
            "distance_miles": distance,
            "lane_type": lane_type,
        })
        lane_id += 1

    return pd.DataFrame(lanes)


def generate_dim_shipper(rng):
    """Generate shipper dimension with power-law volume distribution."""
    vendor_types = list(SHIPPER_VENDOR_TYPES.keys())
    vendor_weights = list(SHIPPER_VENDOR_TYPES.values())

    shippers = []
    for i in range(1, NUM_SHIPPERS + 1):
        vendor_type = rng.choice(vendor_types, p=vendor_weights)
        segment = rng.choice(SHIPPER_INDUSTRY_SEGMENTS)
        start_year = rng.integers(2018, 2025)
        start_month = rng.integers(1, 13)

        if i <= 20:
            volume_tier = "Top20"
        elif i <= 100:
            volume_tier = "Mid"
        else:
            volume_tier = "LongTail"

        account_managers = [
            "J. Martinez", "S. Patel", "R. Thompson", "A. Chen",
            "M. Williams", "K. Johnson", "D. Lee", "L. Garcia",
        ]

        shippers.append({
            "shipper_id": i,
            "shipper_name": f"Shipper-{i:03d}",
            "vendor_type": vendor_type,
            "ship_volume_tier": volume_tier,
            "onboarding_date": f"{start_year}-{start_month:02d}-01",
            "account_manager": rng.choice(account_managers),
            "industry_segment": segment,
        })

    return pd.DataFrame(shippers)


def generate_dim_service_type():
    """Generate service type dimension."""
    records = []
    for sid, (svc_name, sla) in enumerate(SERVICE_TYPE_SLAS.items(), start=1):
        records.append({
            "service_type_id": sid,
            "service_name": svc_name,
            "transit_time_sla_hours": sla["transit_sla_hours"],
            "target_otp_pct": sla["target_otp"],
            "target_defect_rate_pct": sla["target_defect_rate"],
        })
    return pd.DataFrame(records)


def _assign_shipper_volumes(rng, num_shippers, total_shipments):
    """Power-law distribution ensuring top 20 shippers get ~55% of volume."""
    raw = rng.pareto(SHIPPER_PARETO_ALPHA, size=num_shippers) + 1
    raw = np.sort(raw)[::-1]
    shares = raw / raw.sum()

    # Force top-20 concentration to ~55% if the random draw didn't reach it
    top20_share = shares[:20].sum()
    if top20_share < 0.55:
        deficit = 0.55 - top20_share
        # Redistribute from bottom shippers to top-20
        shares[:20] += deficit / 20
        shares[20:] *= (1 - 0.55) / shares[20:].sum()
        shares = shares / shares.sum()

    volumes = np.round(shares * total_shipments).astype(int)
    diff = total_shipments - volumes.sum()
    if diff != 0:
        volumes[0] += diff
    return volumes


def _build_carrier_lane_map(carriers_df, lanes_df, rng):
    """Assign lanes to carriers. Each lane has a primary carrier."""
    lane_ids = lanes_df["lane_id"].values
    carrier_ids = carriers_df["carrier_id"].values
    tier_map = dict(zip(carriers_df["carrier_id"], carriers_df["carrier_tier"]))

    tier_volume_shares = {t: cfg["volume_share"] for t, cfg in CARRIER_TIERS.items()}
    carrier_weights = []
    for cid in carrier_ids:
        tier = tier_map[cid]
        tier_count = CARRIER_TIERS[tier]["count"]
        carrier_weights.append(tier_volume_shares[tier] / tier_count)
    carrier_weights = np.array(carrier_weights)
    carrier_weights = carrier_weights / carrier_weights.sum()

    primary_carriers = rng.choice(carrier_ids, size=len(lane_ids), p=carrier_weights)
    return dict(zip(lane_ids, primary_carriers))


def generate_fact_shipment(
    dim_date, dim_carrier, dim_lane, dim_shipper, dim_service_type, rng
):
    """Generate the fact table with 1M+ shipment records."""
    logger.info("Generating %d shipment records...", TOTAL_SHIPMENTS)

    # Over-allocate volume for churn shippers to compensate for the ~30% drop
    # in the last 90 days. Roughly 25% of their records fall in the last 90 days
    # (90/365), and 30% of those are dropped, so inflate by ~7.5%.
    target_total = int(TOTAL_SHIPMENTS * 1.02)  # 2% buffer for churn filtering
    shipper_volumes = _assign_shipper_volumes(rng, NUM_SHIPPERS, target_total)
    carrier_lane_map = _build_carrier_lane_map(dim_carrier, dim_lane, rng)

    carrier_tier_map = dict(zip(dim_carrier["carrier_id"], dim_carrier["carrier_tier"]))
    lane_distance_map = dict(zip(dim_lane["lane_id"], dim_lane["distance_miles"]))
    lane_type_map = dict(zip(dim_lane["lane_id"], dim_lane["lane_type"]))

    service_type_ids = dim_service_type["service_type_id"].values
    service_type_names = dim_service_type["service_name"].values
    svc_shares = [SERVICE_TYPE_SHARES[n] for n in service_type_names]
    svc_shares = np.array(svc_shares) / sum(svc_shares)

    all_dates = dim_date["date"].values
    date_keys = dim_date["date_key"].values
    date_dow = dim_date["day_of_week"].values
    date_to_key = dict(zip(all_dates, date_keys))
    date_to_dow = dict(zip(all_dates, date_dow))

    lane_ids = dim_lane["lane_id"].values

    # Identify the injected anomaly window
    anomaly_cfg = INJECTED_ANOMALY
    anomaly_start = pd.Timestamp(START_DATE) + pd.DateOffset(months=anomaly_cfg["month_offset"])
    anomaly_end = anomaly_start + timedelta(days=anomaly_cfg["duration_days"])
    spot_carriers = dim_carrier[dim_carrier["carrier_tier"] == "Spot"]["carrier_id"].values
    anomaly_carrier_id = spot_carriers[anomaly_cfg["carrier_index"]]
    anomaly_lane_ids = set(lane_ids[anomaly_cfg["lane_indices"]].tolist())

    # Identify churn shippers (top-20 tier, last 90 days volume decline)
    churn_shipper_ids = set(range(1, SHIPPER_CHURN_COUNT + 1))
    churn_start = END_DATE - timedelta(days=90)

    # Trailing month boundary
    trailing_month_start = END_DATE - timedelta(days=30)

    logger.info(
        "Anomaly: carrier_id=%d, lanes=%s, window=%s to %s",
        anomaly_carrier_id, anomaly_lane_ids,
        anomaly_start.date(), anomaly_end.date(),
    )

    records = []
    shipment_counter = 0

    for shipper_idx in range(NUM_SHIPPERS):
        shipper_id = shipper_idx + 1
        volume = shipper_volumes[shipper_idx]

        for _ in range(volume):
            shipment_counter += 1

            # Date assignment (uniform across range)
            date_idx = rng.integers(0, len(all_dates))
            ship_date = all_dates[date_idx]
            ship_date_py = pd.Timestamp(ship_date).date()
            date_key = date_keys[date_idx]
            dow = date_dow[date_idx]

            # Churn logic: reduce volume for churn shippers in last 90 days
            if shipper_id in churn_shipper_ids and ship_date_py >= churn_start:
                if rng.random() < SHIPPER_CHURN_DECLINE_THRESHOLD:
                    continue

            # Lane assignment
            lane_id = int(rng.choice(lane_ids))
            distance = lane_distance_map[lane_id]
            lane_type = lane_type_map[lane_id]

            # Carrier assignment (primary carrier for lane, with some variation)
            primary_carrier = carrier_lane_map[lane_id]
            if rng.random() < 0.15:
                carrier_id = int(rng.choice(dim_carrier["carrier_id"].values))
            else:
                carrier_id = int(primary_carrier)
            carrier_tier = carrier_tier_map[carrier_id]

            # Service type
            svc_type_id = int(rng.choice(service_type_ids, p=svc_shares))

            # Pickup appointment timestamp
            hour = rng.integers(6, 20)
            minute = rng.choice([0, 15, 30, 45])
            pickup_appt = datetime(
                ship_date_py.year, ship_date_py.month, ship_date_py.day,
                int(hour), int(minute)
            )

            # OTP computation
            tier_otp = CARRIER_TIERS[carrier_tier]["otp_target"]
            otp_prob = OTP_BASELINE * (tier_otp / 0.90)
            otp_prob += OTP_DOW_MODIFIERS.get(int(dow), 0)

            # Trailing month degradation
            if ship_date_py >= trailing_month_start:
                otp_prob -= TRAILING_MONTH_OTP_DEGRADATION

            # Injected anomaly
            in_anomaly = (
                carrier_id == anomaly_carrier_id
                and lane_id in anomaly_lane_ids
                and anomaly_start.date() <= ship_date_py <= anomaly_end.date()
            )
            if in_anomaly:
                otp_prob = anomaly_cfg["degraded_otp"]

            otp_prob = max(0.1, min(0.99, otp_prob))
            on_time_pickup = bool(rng.random() < otp_prob)

            # Pickup actual timestamp
            pickup_actual = None
            if rng.random() >= MISSING_PICKUP_FRACTION:
                if on_time_pickup:
                    delay_min = rng.integers(-5, OTP_TOLERANCE_MINUTES + 1)
                else:
                    delay_min = rng.integers(OTP_TOLERANCE_MINUTES + 1, 180)
                pickup_actual = pickup_appt + timedelta(minutes=int(delay_min))

            # Dwell time
            dwell = float(rng.lognormal(DWELL_LOGNORMAL_MU, DWELL_LOGNORMAL_SIGMA))
            if rng.random() < NEGATIVE_DWELL_FRACTION:
                dwell = -float(rng.integers(1, NEGATIVE_DWELL_MAX_MINUTES + 1))

            # Delivery timestamps
            sla_hours = SERVICE_TYPE_SLAS[service_type_names[svc_type_id - 1]]["transit_sla_hours"]
            transit_hours = distance / 50.0
            transit_hours = max(transit_hours, sla_hours * 0.5)
            delivery_appt = pickup_appt + timedelta(hours=sla_hours)
            delivery_variation = rng.normal(0, sla_hours * 0.1)
            delivery_actual = pickup_appt + timedelta(
                hours=transit_hours + delivery_variation
            )
            on_time_delivery = delivery_actual <= delivery_appt + timedelta(
                minutes=OTP_TOLERANCE_MINUTES
            )

            # Defect
            defect_rate = DEFECT_RATE_BASELINE
            defect_rate *= DEFECT_RATE_TIER_MULTIPLIERS.get(carrier_tier, 1.0)
            if lane_type == "Long":
                defect_rate *= DEFECT_RATE_LONGHAUL_MULTIPLIER
            defect_flag = bool(rng.random() < defect_rate)
            defect_reason = None
            if defect_flag:
                reasons = list(DEFECT_REASONS.keys())
                reason_weights = list(DEFECT_REASONS.values())
                reason_weights = np.array(reason_weights) / sum(reason_weights)
                defect_reason = rng.choice(reasons, p=reason_weights)

            # Trailer utilization
            svc_name = service_type_names[svc_type_id - 1]
            util_params = TRAILER_UTILIZATION[svc_name]
            util = float(rng.normal(util_params["mean"], util_params["std"]))
            util = max(TRAILER_UTIL_MIN, min(TRAILER_UTIL_MAX, util))

            # Weight and pallets
            weight = float(rng.normal(WEIGHT_LBS_MEAN, WEIGHT_LBS_STD))
            weight = max(WEIGHT_LBS_MIN, min(WEIGHT_LBS_MAX, weight))
            pallets = int(rng.normal(PALLET_COUNT_MEAN, PALLET_COUNT_STD))
            pallets = max(PALLET_COUNT_MIN, min(PALLET_COUNT_MAX, pallets))

            # Cost computation (Decimal for exact arithmetic)
            base_cpm = LINEHAUL_COST_PER_MILE_BASE
            tier_modifier = CARRIER_TIERS[carrier_tier]["cost_modifier"]
            base_cpm *= (1 + tier_modifier)

            if distance <= LANE_TYPE_SHORT_MAX:
                base_cpm *= (1 + SHORT_HAUL_COST_PREMIUM)

            if ship_date_py.month in Q4_MONTHS:
                base_cpm *= (1 + Q4_COST_LIFT)

            linehaul = _quantize(base_cpm * distance)

            fsc_frac = max(0.05, float(rng.normal(
                FUEL_SURCHARGE_FRACTION_MEAN, FUEL_SURCHARGE_FRACTION_STD
            )))
            fuel_surcharge = _quantize(float(linehaul) * fsc_frac)

            acc_frac = max(0.0, float(rng.lognormal(
                math.log(ACCESSORIAL_FRACTION_MEAN), ACCESSORIAL_FRACTION_STD
            )))
            acc_frac = min(acc_frac, 0.60)
            accessorial = _quantize(float(linehaul) * acc_frac)

            total_cost = linehaul + fuel_surcharge + accessorial

            shipment_id = f"SHP-{ship_date_py.strftime('%Y%m%d')}-{shipment_counter:07d}"

            records.append({
                "shipment_id": shipment_id,
                "shipment_date_key": int(date_key),
                "carrier_id": carrier_id,
                "lane_id": lane_id,
                "shipper_id": shipper_id,
                "service_type_id": svc_type_id,
                "pickup_appt_ts": pickup_appt,
                "pickup_actual_ts": pickup_actual,
                "delivery_appt_ts": delivery_appt,
                "delivery_actual_ts": delivery_actual,
                "on_time_pickup": on_time_pickup,
                "on_time_delivery": on_time_delivery,
                "dwell_minutes": round(dwell, 2),
                "defect_flag": defect_flag,
                "defect_reason": defect_reason,
                "trailer_utilization_pct": round(util, 4),
                "distance_miles": distance,
                "weight_lbs": round(weight, 1),
                "pallet_count": pallets,
                "linehaul_cost_usd": str(linehaul),
                "fuel_surcharge_usd": str(fuel_surcharge),
                "accessorial_cost_usd": str(accessorial),
                "total_cost_usd": str(total_cost),
            })

            if shipment_counter % 200_000 == 0:
                logger.info("  Generated %d / %d shipments", shipment_counter, TOTAL_SHIPMENTS)

    df = pd.DataFrame(records)
    logger.info("Generated %d shipment records total.", len(df))
    return df


def main():
    """Main entry point: generate all dimension and fact CSVs."""
    logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(RANDOM_SEED)

    logger.info("Generating dimension tables...")
    dim_date = generate_dim_date(START_DATE, END_DATE, rng)
    dim_carrier = generate_dim_carrier(rng)
    dim_lane = generate_dim_lane(rng)
    dim_shipper = generate_dim_shipper(rng)
    dim_service_type = generate_dim_service_type()

    dim_date.to_csv(RAW_DIR / "dim_date.csv", index=False)
    dim_carrier.to_csv(RAW_DIR / "dim_carrier.csv", index=False)
    dim_lane.to_csv(RAW_DIR / "dim_lane.csv", index=False)
    dim_shipper.to_csv(RAW_DIR / "dim_shipper.csv", index=False)
    dim_service_type.to_csv(RAW_DIR / "dim_service_type.csv", index=False)
    logger.info("Dimension tables saved to %s", RAW_DIR)

    logger.info("Generating fact_shipment...")
    fact = generate_fact_shipment(
        dim_date, dim_carrier, dim_lane, dim_shipper, dim_service_type, rng
    )
    fact.to_csv(RAW_DIR / "fact_shipment.csv", index=False)
    logger.info("fact_shipment.csv saved (%d rows)", len(fact))

    logger.info("Data generation complete.")


if __name__ == "__main__":
    main()
