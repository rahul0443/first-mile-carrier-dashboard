-- DDL: fact_shipment
-- The central fact table recording individual shipment events.
-- Grain: one row per shipment.

CREATE TABLE IF NOT EXISTS fact_shipment (
    shipment_id         VARCHAR PRIMARY KEY,
    shipment_date_key   INTEGER NOT NULL,
    carrier_id          INTEGER NOT NULL,
    lane_id             INTEGER NOT NULL,
    shipper_id          INTEGER NOT NULL,
    service_type_id     INTEGER NOT NULL,
    pickup_appt_ts      TIMESTAMP NOT NULL,
    pickup_actual_ts    TIMESTAMP,           -- nullable: ~0.4% missing (tracking gap)
    delivery_appt_ts    TIMESTAMP NOT NULL,
    delivery_actual_ts  TIMESTAMP,
    on_time_pickup      BOOLEAN NOT NULL,
    on_time_delivery    BOOLEAN NOT NULL,
    dwell_minutes       DOUBLE NOT NULL,     -- can be negative (early arrival)
    defect_flag         BOOLEAN NOT NULL,
    defect_reason       VARCHAR,             -- nullable when defect_flag = FALSE
    trailer_utilization_pct DOUBLE NOT NULL,  -- 0.0 to 1.0
    distance_miles      DOUBLE NOT NULL,
    weight_lbs          DOUBLE NOT NULL,
    pallet_count        INTEGER NOT NULL,
    linehaul_cost_usd   DECIMAL(10,2) NOT NULL,
    fuel_surcharge_usd  DECIMAL(10,2) NOT NULL,
    accessorial_cost_usd DECIMAL(10,2) NOT NULL,
    total_cost_usd      DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (shipment_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (carrier_id)        REFERENCES dim_carrier(carrier_id),
    FOREIGN KEY (lane_id)           REFERENCES dim_lane(lane_id),
    FOREIGN KEY (shipper_id)        REFERENCES dim_shipper(shipper_id),
    FOREIGN KEY (service_type_id)   REFERENCES dim_service_type(service_type_id)
);
