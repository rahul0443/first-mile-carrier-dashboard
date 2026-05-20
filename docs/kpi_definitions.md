# KPI Definitions

Precise computation formulas for each KPI used in the dashboard and SQL queries.

## Operational KPIs

### 1. OTP-P (On-Time Pickup %)
`% of shipments where pickup_actual_ts <= pickup_appt_ts + 15 minutes`

Excludes shipments with NULL pickup_actual_ts (tracking gaps). The 15-minute tolerance is industry standard for contract freight.

### 2. OTD (On-Time Delivery %)
`% of shipments where delivery_actual_ts <= delivery_appt_ts + 15 minutes`

### 3. Average Dwell (minutes)
`MEAN(dwell_minutes) WHERE dwell_minutes > 0`

Excludes negative dwell (early arrivals). Reported as mean; P50/P90/P99 used for distribution analysis.

### 4. Defect Rate %
`% of shipments WHERE defect_flag = TRUE`

### 5. Trailer Utilization %
`Volume-weighted MEAN(trailer_utilization_pct)`

Values 0.0-1.0. Reported as percentage. Truncated normal distribution by service type.

### 6. Volume
`COUNT(shipment_id)` by entity (carrier, lane, shipper, network).

## Cost KPIs

### 7. Cost per Shipment
`MEAN(total_cost_usd)`

### 8. Cost per Mile (CPM)
`MEAN(total_cost_usd / distance_miles)`

Excludes zero-distance records.

### 9. Cost per Pallet
`MEAN(total_cost_usd / pallet_count)`

### 10. Accessorial Share
`MEAN(accessorial_cost_usd / total_cost_usd)`

### 11. Cost-to-Serve (per shipper)
`SUM(total_cost_usd) / COUNT(shipment_id)` grouped by shipper.

### 12. Lane Profitability Index
`(benchmark_cpm - observed_cpm) / benchmark_cpm`

Positive = below benchmark (profitable). Benchmark CPM = $2.43/mile (Cass 2024).

## Shipper Composite KPI

### 13. Shipper Health Score (SHS)
Weighted composite, 0-100:
- **30% Service:** `(OTD_rate * 0.6 + defect_free_rate * 0.4) * 100`
- **25% Cost:** `(1 - (shipper_CPS - tier_avg_CPS) / tier_avg_CPS) * 100`, clamped [0,100]
- **20% Growth:** `50 + (vol_90d - vol_prior_90d) / vol_prior_90d * 100`, clamped [0,100]
- **15% Reliability:** `(1 - OTP_stddev * 2) * 100`, clamped [0,100]
- **10% Tenure:** `MIN(months_on_platform / 24, 1) * 100`

## Anomaly KPIs

### 14. Anomaly Count
Count of flagged (lane, week) or (carrier, day) pairs in the last 14 days.

### 15. Trend Velocity
- WoW OTP change: `current_week_OTP - prior_week_OTP` (percentage points)
- MoM cost change: `(current_month_cost - prior_month_cost) / prior_month_cost * 100`
