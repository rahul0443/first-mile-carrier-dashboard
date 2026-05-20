# Data Dictionary

## Fact Table

### fact_shipment
| Column | Type | Description |
|---|---|---|
| shipment_id | VARCHAR | Primary key. Format: SHP-YYYYMMDD-NNNNNNN |
| shipment_date_key | INTEGER | FK to dim_date (YYYYMMDD format) |
| carrier_id | INTEGER | FK to dim_carrier |
| lane_id | INTEGER | FK to dim_lane |
| shipper_id | INTEGER | FK to dim_shipper |
| service_type_id | INTEGER | FK to dim_service_type |
| pickup_appt_ts | TIMESTAMP | Scheduled pickup appointment |
| pickup_actual_ts | TIMESTAMP | Actual pickup time. NULL ~0.4% (tracking gap) |
| delivery_appt_ts | TIMESTAMP | Scheduled delivery appointment |
| delivery_actual_ts | TIMESTAMP | Actual delivery time |
| on_time_pickup | BOOLEAN | TRUE if actual <= appt + 15min tolerance |
| on_time_delivery | BOOLEAN | TRUE if actual <= appt + 15min tolerance |
| dwell_minutes | DOUBLE | Time at facility. Can be negative (early arrival ~0.1%) |
| defect_flag | BOOLEAN | TRUE if shipment had a quality issue |
| defect_reason | VARCHAR | Category of defect. NULL when defect_flag = FALSE |
| trailer_utilization_pct | DOUBLE | 0.0-1.0. Fraction of trailer capacity used |
| distance_miles | DOUBLE | Lane distance (denormalized from dim_lane) |
| weight_lbs | DOUBLE | Shipment weight |
| pallet_count | INTEGER | Number of pallets |
| linehaul_cost_usd | DECIMAL(10,2) | Base transportation cost |
| fuel_surcharge_usd | DECIMAL(10,2) | Fuel surcharge (~20% of linehaul) |
| accessorial_cost_usd | DECIMAL(10,2) | Accessorial charges |
| total_cost_usd | DECIMAL(10,2) | Exact: linehaul + fuel + accessorial |

## Dimension Tables

### dim_carrier
| Column | Type | Description |
|---|---|---|
| carrier_id | INTEGER | Primary key |
| carrier_name | VARCHAR | e.g., STR-01, COR-05, TAC-12, SPO-03 |
| carrier_tier | VARCHAR | Strategic / Core / Tactical / Spot |
| equipment_type | VARCHAR | Dry Van / Reefer / Flatbed / Intermodal Container |
| region_primary | VARCHAR | Northeast / Southeast / Midwest / Southwest / West |
| partnership_start_date | DATE | When carrier was onboarded |
| target_otp_pct | DOUBLE | Tier-specific OTP target |
| contract_type | VARCHAR | Dedicated / Contract / Spot |

### dim_lane
| Column | Type | Description |
|---|---|---|
| lane_id | INTEGER | Primary key |
| origin_city | VARCHAR | Origin metro |
| origin_state | VARCHAR | Two-letter state code |
| origin_zip3 | VARCHAR | 3-digit ZIP prefix |
| dest_city | VARCHAR | Destination city |
| dest_state | VARCHAR | Two-letter state code |
| dest_zip3 | VARCHAR | 3-digit ZIP prefix |
| dest_fc_id | VARCHAR | Inbound node ID (e.g., BWI1, IAD2) |
| distance_miles | DOUBLE | Lane distance (80-2400 miles) |
| lane_type | VARCHAR | Short (<500mi) / Mid (500-1500mi) / Long (>1500mi) |

### dim_shipper
| Column | Type | Description |
|---|---|---|
| shipper_id | INTEGER | Primary key |
| shipper_name | VARCHAR | e.g., Shipper-001 |
| vendor_type | VARCHAR | Brand / Wholesaler / 3PL |
| ship_volume_tier | VARCHAR | Top20 / Mid / LongTail |
| onboarding_date | DATE | When shipper joined the platform |
| account_manager | VARCHAR | Assigned account manager |
| industry_segment | VARCHAR | Industry classification |

### dim_date
| Column | Type | Description |
|---|---|---|
| date_key | INTEGER | Primary key (YYYYMMDD) |
| date | DATE | Calendar date |
| year | INTEGER | Calendar year |
| quarter | INTEGER | 1-4 |
| month | INTEGER | 1-12 |
| week_of_year | INTEGER | ISO week number |
| day_of_week | INTEGER | 0=Monday, 6=Sunday |
| is_weekend | BOOLEAN | Saturday or Sunday |
| is_holiday | BOOLEAN | US federal holiday |
| is_peak_season | BOOLEAN | October-December |

### dim_service_type
| Column | Type | Description |
|---|---|---|
| service_type_id | INTEGER | Primary key |
| service_name | VARCHAR | FTL / LTL / Intermodal |
| transit_time_sla_hours | INTEGER | Service-level transit window |
| target_otp_pct | DOUBLE | Mode-specific OTP target |
| target_defect_rate_pct | DOUBLE | Mode-specific defect target |
