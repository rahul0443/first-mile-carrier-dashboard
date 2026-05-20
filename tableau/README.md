# Tableau Public Mirror

The Tableau visualization provides the leadership view of the same data
powering the Streamlit dashboard.

## Published URL

[Paste your Tableau Public URL here after publishing]

## How to Rebuild

1. Run `make all` to regenerate all data
2. The extract CSV is generated at `tableau/tableau_extract.csv`
3. Open Tableau Public Desktop, connect to the CSV
4. Build the four views:
   - KPI strip (OTP, Dwell, Defect, Cost/Shipment)
   - Lane heatmap (origin x destination, colored by OTP)
   - Carrier scorecard with sparklines
   - Monthly trend ribbon
5. Publish to Tableau Public
6. Paste the URL above

## Extract Schema

The extract contains a 60-day window of joined fact + dimension data:
- shipment_id, date, carrier_name, carrier_tier
- origin_city, origin_state, dest_fc_id, lane_type
- shipper_name, vendor_type, service_name
- on_time_pickup, on_time_delivery, dwell_minutes
- defect_flag, defect_reason, trailer_utilization_pct
- distance_miles, total_cost_usd, cost_per_mile
