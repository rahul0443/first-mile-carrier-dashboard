-- Query: q31_hypothesis_strategic_vs_tactical_otp
-- Business question: Is the OTP difference between Strategic and Tactical
--   carriers statistically significant?
-- Returns: Paired t-test computed in SQL via CTE.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q31_hypothesis_strategic_vs_tactical_otp.sql
-- Techniques: CTE, statistical computation (t-test), window functions

-- Approach: Compute per-lane OTP for both tiers, pair by lane,
-- then compute the t-statistic on the paired differences.
-- If |t| > 1.96, reject H0 at alpha=0.05.

WITH lane_tier_otp AS (
    SELECT
        f.lane_id,
        c.carrier_tier,
        AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS lane_otp
    FROM fact_shipment f
    JOIN dim_carrier c ON f.carrier_id = c.carrier_id
    WHERE c.carrier_tier IN ('Strategic', 'Tactical')
    GROUP BY f.lane_id, c.carrier_tier
    HAVING COUNT(*) >= 30
),
paired AS (
    SELECT
        s.lane_id,
        s.lane_otp AS strategic_otp,
        t.lane_otp AS tactical_otp,
        s.lane_otp - t.lane_otp AS diff
    FROM lane_tier_otp s
    JOIN lane_tier_otp t ON s.lane_id = t.lane_id
    WHERE s.carrier_tier = 'Strategic' AND t.carrier_tier = 'Tactical'
),
stats AS (
    SELECT
        COUNT(*) AS n,
        AVG(diff) AS mean_diff,
        STDDEV(diff) AS std_diff
    FROM paired
)
SELECT
    n AS paired_lanes,
    ROUND(mean_diff * 100, 2) AS mean_otp_diff_pp,
    ROUND(std_diff * 100, 2) AS std_diff_pp,
    ROUND(mean_diff / NULLIF(std_diff / SQRT(n), 0), 3) AS t_statistic,
    1.96 AS critical_value_alpha_05,
    CASE
        WHEN ABS(mean_diff / NULLIF(std_diff / SQRT(n), 0)) > 1.96
        THEN 'REJECT H0: Significant OTP difference (p < 0.05)'
        ELSE 'FAIL TO REJECT H0: No significant difference'
    END AS conclusion
FROM stats;
