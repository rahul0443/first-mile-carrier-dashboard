# Methodology

## Why Synthetic Data

Real freight data is proprietary. No public dataset exists at the granularity needed for this project (shipment-level, with carrier identity, cost breakdowns, and defect flags). Synthetic generation allows:

1. Full control over data characteristics (volume, distribution shape, anomaly injection)
2. Reproducibility via fixed random seed
3. Free distribution without NDA concerns
4. Demonstration of the same analytical skills applied to real data

## Calibration Sources

Every distribution parameter in `src/config.py` cites a public benchmark:

| Parameter | Value | Source |
|---|---|---|
| OTP baseline | 87% | FreightWaves SONAR OTPI, 2024 |
| Dwell time median | 45 min | Trucker Tools 2024 Detention Study |
| Dwell time P90 | 120 min | Trucker Tools 2024 Detention Study |
| Trailer utilization (FTL) | 78% | ATRI 2024 Operational Costs Report |
| Trailer utilization (LTL) | 64% | ATRI 2024 Operational Costs Report |
| Linehaul CPM | $2.43/mi | Cass Information Systems Freight Index, 2024 |
| Modal split (FTL/LTL/IM) | 62/28/10 | ATA/BTS 2024 |
| Defect rate | 2.3% | DAT Solutions 2024 Freight Quality Benchmark |
| Q4 cost lift | +12% | Cass Freight Index seasonal pattern, 2024 |
| Shipper concentration | Top-20 = 55% | FreightWaves SONAR, 2024 |

## Realism Features

- **Missing data:** ~0.4% NULL pickup timestamps (EDI/API tracking failures)
- **Negative dwell:** ~0.1% records where driver arrived before appointment
- **Trailing-month degradation:** Last 30 days show ~5pp lower OTP
- **Injected anomaly:** 14-day window in month 8 with known OTP collapse
- **Shipper churn:** 5 top-20 shippers with >30% volume decline in last 90 days
- **Cost identity:** `linehaul + fuel + accessorial = total` exact across all rows (Decimal arithmetic)

## Limitations

1. Lane distances are randomized within realistic ranges, not computed from geographic coordinates
2. No real carrier reputations or historical performance data
3. No actual regulatory complexity (HOS, ELD, insurance)
4. No real shipper relationships or contract terms
5. Seasonality is simplified to Q4 peak; real freight has more complex patterns
6. No weather, traffic, or incident disruption modeling
