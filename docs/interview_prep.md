# Interview Prep -- Carrier Performance Dashboard

## "Walk me through this project."

I built an end-to-end analytics stack for inbound first-mile transportation. The problem: how do you monitor and optimize a network of 52 carriers moving 85K shipments/month across 225 lanes from 340 shippers? I generated a million-row synthetic dataset calibrated to public freight benchmarks, built a DuckDB star schema, wrote 35 SQL queries for operational deep-dives, implemented anomaly detection and SARIMAX forecasting, and delivered dashboards in Streamlit and Tableau. The top finding: Monday pickups run 5pp below mid-week OTP, and Spot carriers on long-haul lanes create 80% more defects.

## "Where did the data come from?"

Synthetic, calibrated to public benchmarks. Every constant in `src/config.py` (line 40+) has a citation comment: FreightWaves SONAR for OTP, Trucker Tools for dwell, ATRI for utilization, Cass for cost-per-mile. The data is reproducible (fixed seed) and passes quality checks: exact cost identity across 1M+ rows, FK integrity, and a seeded anomaly that the detector catches.

## "Why DuckDB?"

Three reasons: (1) zero-config -- a recruiter clones and runs `make all` without installing a database; (2) columnar OLAP -- analytically optimized for the aggregation-heavy queries in this project; (3) full SQL support including window functions, CTEs, and percentiles. In production, I'd use Redshift or BigQuery.

## "Walk me through your SQL."

Pick 3:
- **q07** (rolling 4-week OTP trend): Uses a CTE to compute weekly OTP, then a window function `AVG() OVER (ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)` for the rolling average. Good for trend detection.
- **q31** (paired t-test): Pairs Strategic and Tactical carriers by lane, computes the mean difference and standard deviation, then calculates the t-statistic in SQL. Demonstrates that the OTP gap isn't just noise.
- **q21** (modal mismatch): Finds LTL shipments with FTL-like utilization (>70% fill, >30K lbs) -- candidates for mode conversion and cost savings.

## "How did you detect anomalies?"

Two methods: z-score for bounded percentages (OTP) and IQR for heavy-tailed costs (CPM). The z-score detector computes an 8-week rolling mean and std per lane, flags weeks where |z| > 2.5. Validated with an injected anomaly: I seeded a 14-day OTP collapse on 3 lanes in month 8. The detector caught it within 3 days at z = -3.1. Test in `tests/test_anomaly_detection.py` asserts this.

## "What would you change for production?"

1. Real-time streaming ingestion (Kafka/Kinesis) instead of batch CSV
2. Real carrier data from EDI/API feeds
3. ML-based root cause attribution (not just reason hints)
4. Slack/PagerDuty alerting integration for anomaly flags
5. Model retraining cadence (monthly for SARIMAX, quarterly for anomaly thresholds)

## "Tell me about a hard bug."

The cost identity check (`linehaul + fuel + accessorial = total`) failed by tiny amounts -- $487.43 vs $487.42. Root cause: Python float arithmetic accumulating rounding error. Fixed by switching to `decimal.Decimal` with 2-place quantization and computing total as the exact sum. The test now asserts equality with zero tolerance across 1M+ rows. Lesson: never use floats for money.

## Likely SQL whiteboard question

"Find carriers whose OTP has declined in the last 4 weeks vs the prior 4 weeks by more than 5 percentage points."

Template: `sql/queries/q28_carriers_with_otp_decline_30d.sql`. Practice writing from scratch: CTE with conditional aggregation by date range, then filter on the delta.

## Likely Excel question

"How would you build a pivot table to show cost-per-shipment by shipper tier and service type?"

Walk through `reports/pivot_pack.xlsx` sheet 4 (Shipper Cost-to-Serve): rows = shipper, columns = service type, values = average cost per shipment. Frozen panes, autofilter, Calibri 11pt.
