# Insights -- Inbound First-Mile Carrier Performance

Each insight follows the Working Backwards format: start with the shipper or
operator pain point, present the finding, cite the supporting evidence, and
recommend action.

---

### Insight #1: Monday pickup reliability is costing shippers 3-5pp in OTP

**Shipper or operator pain.** Shippers scheduling Monday pickups experience
systematically lower on-time performance, creating cascading delivery delays
that erode shipper trust in the network.

**Finding.** Monday OTP averages 82-83%, compared to mid-week (Tue-Thu) at
88-89%. This 5-6pp gap is consistent across all carrier tiers and is not
explained by volume spikes -- Monday volume is only 2% above average. The
root cause is weekend backlog at origin facilities creating morning congestion.

**Supporting evidence.** `sql/queries/q06_otp_by_dayofweek.sql`

**Recommendation.** Implement staggered Monday pickup windows: shift 30% of
Monday appointments to 0600-0800 (pre-congestion) or to Tuesday. Expected
improvement: 2-3pp on Monday OTP. Test on top-10 volume lanes first.

**Caveats.** Shipper facility operating hours may constrain early-morning
pickups. Validate with facility managers before rolling out.

**Mapped to.** Pickup gaps

---

### Insight #2: Spot carriers on long-haul lanes drive 80% more defects

**Shipper or operator pain.** Shippers on lanes served by Spot carriers
experience defect rates nearly double the network average, leading to refused
shipments, inventory gaps, and reprocessing costs.

**Finding.** Spot-tier carriers show a defect rate ~1.8x the baseline (4.1%
vs 2.3% network average). On long-haul lanes (>1500 miles), the compounding
effect of tier and distance pushes defect rates above 5%. The chi-square test
(q32) confirms defect rate dependence on carrier tier is statistically
significant (p < 0.05).

**Supporting evidence.** `sql/queries/q32_chi_square_defect_independence.sql`,
`sql/queries/q04_defect_rate_trend_monthly.sql`

**Recommendation.** Restrict Spot carriers from long-haul lanes where defect
rates exceed 4%. Reallocate to Strategic/Core carriers with contractual
defect-rate SLAs. Estimated defect reduction: 1.5pp on affected lanes.

**Caveats.** Capacity constraints may force Spot usage during peak. Implement
as a soft restriction with exception approval workflow.

**Mapped to.** Pickup gaps, Accessorials (defect-driven reprocessing)

---

### Insight #3: 15% of LTL shipments show FTL-like utilization -- modal mismatch

**Shipper or operator pain.** Shippers paying LTL rates for shipments that
fill 70%+ of a trailer are overpaying for consolidation services they don't
need, eroding their cost-to-serve ratio.

**Finding.** Query q21 identifies LTL lanes where average trailer utilization
exceeds 70% and average weight exceeds 30,000 lbs. These shipments are
effectively FTL loads paying LTL premiums. Converting them would reduce
cost-per-pallet by an estimated 15-20%.

**Supporting evidence.** `sql/queries/q21_modal_mismatch_candidates.sql`,
`sql/queries/q19_trailer_utilization_by_service_type.sql`

**Recommendation.** Flag the top 15 modal mismatch lanes for FTL conversion
review. Work with shippers to consolidate orders into full truckloads where
weekly volume supports it.

**Caveats.** Some shippers may have operational constraints (e.g., receiving
dock hours) that favor LTL delivery windows.

**Mapped to.** Trailer utilization

---

### Insight #4: Accessorials account for 15% of total cost -- detention is the driver

**Shipper or operator pain.** Accessorial charges are opaque to shippers and
create unpredictable cost overruns that undermine budgeting and trust.

**Finding.** Accessorial costs average 15% of total shipment cost, with a
heavy right tail -- some shipments see accessorials exceeding 40% of linehaul.
The dominant driver is detention at destination facilities. Carriers with
dwell P90 > 120 minutes charge 25-30% more in accessorials.

**Supporting evidence.** `sql/queries/q12_accessorial_as_pct_of_total.sql`,
`sql/queries/q16_accessorial_pareto_by_reason.sql`

**Recommendation.** Implement a 2-hour detention clock with automated
escalation at 90 minutes. Target the 10 facilities with highest dwell P90
for dock scheduling optimization. Expected reduction: 3-5pp in accessorial
share.

**Caveats.** Facility-side changes require cross-functional coordination.
Start with owned/operated facilities before third-party.

**Mapped to.** Accessorials

---

### Insight #5: Q4 peak season lifts cost-per-mile by ~12% -- statistically confirmed

**Shipper or operator pain.** Shippers face unpredictable cost increases
during peak season, making Q4 budget forecasts unreliable.

**Finding.** The Mann-Whitney test (q33) confirms Q4 cost-per-mile is
significantly higher than non-Q4 (p < 0.05). The lift is approximately 12%,
driven by both linehaul rate increases and elevated spot carrier usage. The
SARIMAX cost forecast captures this seasonal pattern.

**Supporting evidence.** `sql/queries/q33_q4_cost_lift_significance.sql`,
`sql/queries/q15_seasonal_cost_lift_q4.sql`, `src/forecasting.py`

**Recommendation.** Lock in Q4 contract rates by August. Use the SARIMAX
28-day cost forecast to alert procurement when actual costs exceed the
upper prediction interval, triggering early carrier negotiations.

**Caveats.** Macro factors (diesel prices, regulatory changes) can
amplify or dampen the seasonal pattern.

**Mapped to.** Accessorials (peak surcharges), Pickup gaps (capacity squeeze)

---

### Insight #6: 5 top-20 shippers show >30% volume decline -- churn risk

**Shipper or operator pain.** Losing a top-20 shipper creates a revenue hole
that takes 3-6 months to backfill. Early detection is critical.

**Finding.** The Shipper Health Score surface identifies 5 top-20 shippers
with 90-day volume declines exceeding 30% compared to the prior 90 days.
Cross-referencing with service metrics, 3 of these shippers also received
below-network-average OTD, suggesting service quality may be a contributing
factor.

**Supporting evidence.** `sql/views/v_shipper_health.sql`,
`sql/queries/q24_shipper_volume_pareto.sql`,
`src/pricing_recommendations.py`

**Recommendation.** Trigger account review for all shippers with SHS below 50
AND negative growth. The pricing recommendation module suggests tier changes
for each. Prioritize retention outreach for shippers where service gaps are
fixable.

**Caveats.** Volume declines may reflect shipper-side business changes (e.g.,
seasonal product cycles) rather than dissatisfaction.

**Mapped to.** Trailer utilization (revenue per lane), Pickup gaps (shipper experience)

---

### Insight #7: Strategic carriers outperform Tactical by 5-8pp OTP -- validated statistically

**Shipper or operator pain.** Operators need confidence that carrier tiering
decisions are backed by data, not just intuition.

**Finding.** The paired t-test (q31) confirms the OTP difference between
Strategic and Tactical tiers is statistically significant at alpha=0.05.
Strategic carriers average 92-93% OTP vs Tactical at 84-86%. The difference
holds lane-by-lane, controlling for route difficulty.

**Supporting evidence.** `sql/queries/q31_hypothesis_strategic_vs_tactical_otp.sql`,
`sql/queries/q02_otp_by_carrier_tier.sql`

**Recommendation.** Shift 10% of Tactical-tier volume on underperforming
lanes to Strategic carriers. Use the What-If Simulator (Streamlit Page 6)
to model the projected OTP and cost impact before executing.

**Caveats.** Strategic carriers may not have capacity for additional volume.
Validate with carrier account managers before commitment.

**Mapped to.** Pickup gaps (carrier reliability)

---

### Insight #8: Intermodal conversion on 10+ long-haul lanes could save 15-20% per mile

**Shipper or operator pain.** Shippers on long-haul FTL lanes are paying
premium truckload rates when intermodal could deliver comparable service
at lower cost.

**Finding.** Query q22 identifies 10+ FTL lanes over 1,500 miles with
sufficient weekly volume to support intermodal containers. Current CPM on
these lanes averages $3.20+; intermodal benchmark suggests ~$2.50-2.70.

**Supporting evidence.** `sql/queries/q22_intermodal_conversion_candidates.sql`,
`sql/queries/q18_long_haul_vs_short_haul_economics.sql`

**Recommendation.** Pilot intermodal conversion on the top 5 candidate
lanes. Accept the transit time SLA increase (48h -> 120h) in exchange for
15-20% CPM reduction. Monitor defect rates during pilot.

**Caveats.** Intermodal requires rail-compatible origin/destination. Not
all lanes have rail access. Transit time extension may not be acceptable
for time-sensitive shippers.

**Mapped to.** Trailer utilization

---

### Insight #9: Network OTP forecast shows continued deterioration over 4 weeks

**Shipper or operator pain.** Without forward-looking indicators, operators
react to problems after shippers have already felt the impact.

**Finding.** The SARIMAX 4-week OTP forecast projects continued decline from
the current trailing-month level. The 95% prediction interval does not
include the 90% target for any of the 4 forecast weeks, suggesting the
deterioration is structural rather than noise.

**Supporting evidence.** `src/forecasting.py`, `reports/forecast_otp.csv`,
`reports/forecast_otp.png`

**Recommendation.** Activate the carrier performance escalation protocol
now, not after the forecast materializes. Focus on the trailing-month
degradation pattern identified in the data: if it's driven by specific
carriers or lanes, target interventions there.

**Caveats.** SARIMAX assumes stationarity after differencing. A structural
break (e.g., new carrier onboarding, network redesign) would invalidate
the forecast. Retrain monthly.

**Mapped to.** Pickup gaps (proactive intervention)
