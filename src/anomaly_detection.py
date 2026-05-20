"""
Anomaly detection module with z-score and IQR methods plus daily auto-report.

Detects anomalies in OTP (z-score for bounded percentages) and cost-per-mile
(IQR for heavy-tailed distributions). Produces daily markdown briefings
for ops standup.

Usage:
    python -m src.anomaly_detection
"""

import logging
from datetime import date

import duckdb
import numpy as np
import pandas as pd

from src.config import (
    DAILY_BRIEFINGS_DIR,
    IQR_MULTIPLIER,
    RAW_DIR,
    REASON_ACCESSORIAL_SPIKE_THRESHOLD,
    REASON_CARRIER_DEFECT_DOMINANCE,
    REASON_SPOT_SHARE_JUMP_THRESHOLD,
    WAREHOUSE_PATH,
    ZSCORE_ROLLING_WEEKS,
    ZSCORE_THRESHOLD,
)

logger = logging.getLogger(__name__)


def detect_zscore_anomalies(con):
    """Z-score detector for weekly lane OTP anomalies."""
    logger.info("Running z-score anomaly detection on OTP...")

    df = con.execute("""
        SELECT
            f.lane_id,
            d.year,
            d.week_of_year,
            MIN(d.date) AS week_start,
            AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS weekly_otp,
            COUNT(*) AS volume
        FROM fact_shipment f
        JOIN dim_date d ON f.shipment_date_key = d.date_key
        GROUP BY f.lane_id, d.year, d.week_of_year
        HAVING COUNT(*) >= 5
        ORDER BY f.lane_id, d.year, d.week_of_year
    """).fetchdf()

    anomalies = []
    for lane_id, group in df.groupby("lane_id"):
        group = group.sort_values(["year", "week_of_year"]).reset_index(drop=True)
        if len(group) < ZSCORE_ROLLING_WEEKS + 1:
            continue

        rolling_mean = group["weekly_otp"].rolling(
            ZSCORE_ROLLING_WEEKS, min_periods=ZSCORE_ROLLING_WEEKS
        ).mean()
        rolling_std = group["weekly_otp"].rolling(
            ZSCORE_ROLLING_WEEKS, min_periods=ZSCORE_ROLLING_WEEKS
        ).std()

        for i in range(ZSCORE_ROLLING_WEEKS, len(group)):
            mean_val = rolling_mean.iloc[i - 1]
            std_val = rolling_std.iloc[i - 1]
            if std_val is None or std_val == 0 or pd.isna(std_val):
                continue
            observed = group["weekly_otp"].iloc[i]
            z = (observed - mean_val) / std_val

            if abs(z) > ZSCORE_THRESHOLD:
                severity = "HIGH" if abs(z) > 3.5 else "MEDIUM" if abs(z) > 3.0 else "LOW"
                anomalies.append({
                    "lane_id": int(lane_id),
                    "week_start": group["week_start"].iloc[i],
                    "year": int(group["year"].iloc[i]),
                    "week_of_year": int(group["week_of_year"].iloc[i]),
                    "otp_observed": round(observed, 4),
                    "otp_expected": round(mean_val, 4),
                    "z_score": round(z, 3),
                    "severity": severity,
                    "reason_hint": "",
                })

    result = pd.DataFrame(anomalies)
    if not result.empty:
        result = _enrich_zscore_reasons(con, result)

    result.to_csv(RAW_DIR / "anomalies_zscore.csv", index=False)
    logger.info("Z-score anomalies: %d flagged", len(result))
    return result


def _enrich_zscore_reasons(con, anomalies_df):
    """Add reason hints by inspecting underlying shipments."""
    hints = []
    for _, row in anomalies_df.iterrows():
        lane_id = row["lane_id"]
        week_start = row["week_start"]

        detail = con.execute(f"""
            SELECT
                c.carrier_tier,
                AVG(f.accessorial_cost_usd / NULLIF(f.total_cost_usd, 0)) AS acc_share,
                SUM(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) / COUNT(*) AS defect_rate,
                SUM(CASE WHEN c.carrier_tier = 'Spot' THEN 1.0 ELSE 0.0 END) / COUNT(*) AS spot_share
            FROM fact_shipment f
            JOIN dim_carrier c ON f.carrier_id = c.carrier_id
            JOIN dim_date d ON f.shipment_date_key = d.date_key
            WHERE f.lane_id = {lane_id}
              AND d.date >= '{week_start}'
              AND d.date < '{week_start}'::DATE + INTERVAL '7 days'
            GROUP BY c.carrier_tier
        """).fetchdf()

        hint_parts = []
        if not detail.empty:
            avg_acc = detail["acc_share"].mean()
            if avg_acc > REASON_ACCESSORIAL_SPIKE_THRESHOLD:
                hint_parts.append("Spike in detention accessorials")
            spot_row = detail[detail["carrier_tier"] == "Spot"]
            if not spot_row.empty and spot_row["spot_share"].iloc[0] > REASON_SPOT_SHARE_JUMP_THRESHOLD:
                hint_parts.append("Spot-tier reliance surge")
            max_defect = detail["defect_rate"].max()
            if max_defect > REASON_CARRIER_DEFECT_DOMINANCE:
                hint_parts.append("Carrier-specific defect cluster")

        if not hint_parts:
            if row["z_score"] < 0:
                hint_parts.append("OTP collapse on weekday lanes")
            else:
                hint_parts.append("Unusual OTP improvement")

        hints.append("; ".join(hint_parts))

    anomalies_df["reason_hint"] = hints
    return anomalies_df


def detect_iqr_anomalies(con):
    """IQR detector for daily carrier cost-per-mile anomalies."""
    logger.info("Running IQR anomaly detection on cost-per-mile...")

    df = con.execute("""
        SELECT
            f.carrier_id,
            c.carrier_name,
            l.lane_type,
            d.date,
            AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS daily_cpm,
            COUNT(*) AS volume
        FROM fact_shipment f
        JOIN dim_carrier c ON f.carrier_id = c.carrier_id
        JOIN dim_lane l ON f.lane_id = l.lane_id
        JOIN dim_date d ON f.shipment_date_key = d.date_key
        WHERE f.distance_miles > 0
        GROUP BY f.carrier_id, c.carrier_name, l.lane_type, d.date
        HAVING COUNT(*) >= 3
    """).fetchdf()

    anomalies = []
    for lane_type, group in df.groupby("lane_type"):
        q1 = group["daily_cpm"].quantile(0.25)
        q3 = group["daily_cpm"].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + IQR_MULTIPLIER * iqr

        flagged = group[group["daily_cpm"] > upper]
        for _, row in flagged.iterrows():
            anomalies.append({
                "carrier_id": int(row["carrier_id"]),
                "carrier_name": row["carrier_name"],
                "lane_type": lane_type,
                "date": row["date"],
                "daily_cpm": round(row["daily_cpm"], 2),
                "upper_fence": round(upper, 2),
                "excess_pct": round((row["daily_cpm"] - upper) / upper * 100, 1),
                "volume": int(row["volume"]),
            })

    result = pd.DataFrame(anomalies)
    result.to_csv(RAW_DIR / "anomalies_iqr.csv", index=False)
    logger.info("IQR anomalies: %d flagged", len(result))
    return result


def generate_daily_briefing(con, zscore_df, iqr_df):
    """Generate a dated markdown daily briefing for ops standup."""
    today = date.today()
    DAILY_BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Network headline
    headline = con.execute("""
        SELECT
            ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
            ROUND(AVG(f.total_cost_usd), 0) AS avg_cost
        FROM fact_shipment f
        JOIN dim_date d ON f.shipment_date_key = d.date_key
        WHERE d.date >= CURRENT_DATE - INTERVAL '7 days'
    """).fetchdf()

    otp_7d = headline["otp_pct"].iloc[0] if not headline.empty else 0
    cost_7d = headline["avg_cost"].iloc[0] if not headline.empty else 0

    # Recent anomalies
    recent_zs = zscore_df.tail(10) if not zscore_df.empty else pd.DataFrame()
    recent_iqr = iqr_df.tail(5) if not iqr_df.empty else pd.DataFrame()

    total_anomalies = len(recent_zs) + len(recent_iqr)

    lines = [
        f"# Daily First-Mile Briefing -- {today.isoformat()}",
        "",
        "## Headline",
        f"Network OTP (7d): {otp_7d}% (target 90%). "
        f"Avg cost per shipment (7d): ${cost_7d:,.0f}.",
        "",
        f"## Anomalies flagged ({total_anomalies})",
    ]

    if not recent_zs.empty:
        for idx, (_, row) in enumerate(recent_zs.iterrows(), 1):
            lane_info = con.execute(f"""
                SELECT origin_city || ' -> ' || dest_fc_id AS lane
                FROM dim_lane WHERE lane_id = {row['lane_id']}
            """).fetchone()
            lane_label = lane_info[0] if lane_info else f"Lane {row['lane_id']}"
            lines.append(
                f"{idx}. **Z-score** Lane {lane_label}: "
                f"OTP {row['otp_observed']*100:.1f}% (z = {row['z_score']:.1f}). "
                f"Reason: {row.get('reason_hint', 'Under review')}."
            )
    else:
        lines.append("No z-score anomalies in recent period.")

    if not recent_iqr.empty:
        lines.append("")
        for _, row in recent_iqr.iterrows():
            lines.append(
                f"- **IQR** Carrier {row['carrier_name']} ({row['lane_type']}): "
                f"CPM ${row['daily_cpm']:.2f} (fence ${row['upper_fence']:.2f}, "
                f"+{row['excess_pct']:.0f}% above)."
            )

    lines.extend([
        "",
        "## Recommendations",
        "- Review flagged carriers in Anomaly Center dashboard.",
        "- Hold sourcing review for carriers with z-score below -3.0.",
        "- Investigate accessorial drivers on high-CPM lanes.",
        "",
        f"*Generated {today.isoformat()} by anomaly_detection.py*",
    ])

    filepath = DAILY_BRIEFINGS_DIR / f"{today.isoformat()}.md"
    filepath.write_text("\n".join(lines))
    logger.info("Daily briefing written to %s", filepath)
    return filepath


def main():
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    zscore_df = detect_zscore_anomalies(con)
    iqr_df = detect_iqr_anomalies(con)
    generate_daily_briefing(con, zscore_df, iqr_df)
    con.close()

    logger.info("Anomaly detection complete.")


if __name__ == "__main__":
    main()
