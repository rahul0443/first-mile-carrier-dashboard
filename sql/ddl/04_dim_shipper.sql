-- DDL: dim_shipper
-- Shipper dimension representing vendors and sellers using the inbound program.

CREATE TABLE IF NOT EXISTS dim_shipper (
    shipper_id          INTEGER PRIMARY KEY,
    shipper_name        VARCHAR NOT NULL,
    vendor_type         VARCHAR NOT NULL,    -- Brand / Wholesaler / 3PL
    ship_volume_tier    VARCHAR NOT NULL,    -- Top20 / Mid / LongTail
    onboarding_date     DATE NOT NULL,
    account_manager     VARCHAR NOT NULL,
    industry_segment    VARCHAR NOT NULL
);
