-- DDL: dim_carrier
-- Carrier dimension with tiered segmentation.

CREATE TABLE IF NOT EXISTS dim_carrier (
    carrier_id              INTEGER PRIMARY KEY,
    carrier_name            VARCHAR NOT NULL,
    carrier_tier            VARCHAR NOT NULL,    -- Strategic / Core / Tactical / Spot
    equipment_type          VARCHAR NOT NULL,
    region_primary          VARCHAR NOT NULL,
    partnership_start_date  DATE NOT NULL,
    target_otp_pct          DOUBLE NOT NULL,
    contract_type           VARCHAR NOT NULL      -- Dedicated / Contract / Spot
);
