-- Query: q30_anomaly_summary_last_14d
-- Business question: What anomalies were flagged in the last 14 days?
-- Returns: Summary of carrier-lane anomalies from the anomaly flag view.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q30_anomaly_summary_last_14d.sql
-- Techniques: VIEW reference, GROUP BY, HAVING

SELECT
    carrier_name,
    carrier_tier,
    lane_label,
    COUNT(*) AS flagged_days,
    ROUND(AVG(daily_otp) * 100, 1) AS avg_otp_pct,
    ROUND(AVG(daily_cpm), 2) AS avg_cpm,
    SUM(daily_volume) AS total_volume
FROM v_anomaly_flags
GROUP BY carrier_name, carrier_tier, lane_label
HAVING AVG(daily_otp) < 0.80
ORDER BY avg_otp_pct ASC
LIMIT 20;
