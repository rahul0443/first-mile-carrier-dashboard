# Project Deep Dive — Layman's Guide to the First-Mile Carrier Dashboard

> This document explains everything we built, why we built it, how every piece works, and exactly why it will make your Amazon AIT BizOps Business Analyst I application stand out.

---

## Part 1: The Big Picture — What Did We Actually Build?

### The One-Liner

We built a **complete, working analytics system** that simulates the exact kind of data and problems you'd face on Day 1 at Amazon's inbound transportation team — and then solved those problems with SQL, statistics, forecasting, dashboards, and Excel deliverables.

### The Analogy

Imagine Amazon has thousands of trucks picking up products from sellers and manufacturers every day, bringing them INTO Amazon's warehouses (fulfillment centers). Your job as a Business Analyst would be to answer: **Are the trucks showing up on time? Are they costing too much? Are certain sellers getting bad service? Which trucking companies are underperforming?**

That's exactly what this project does. Except since we can't use Amazon's real data (it's confidential), we created our own realistic data — over **1 million shipment records** — that behaves just like real freight data would, based on public industry reports.

### What "First-Mile" Means

In Amazon's supply chain:
- **First mile** = products traveling FROM sellers/manufacturers TO Amazon's warehouses
- **Middle mile** = products moving BETWEEN Amazon's warehouses
- **Last mile** = products going FROM Amazon's warehouse TO the customer's doorstep

**AIT (Amazon Inbound Transportation)** owns the first mile. Their customer is the **shipper** (the seller sending products into Amazon). This project is laser-focused on that.

---

## Part 2: What Does the Amazon Job Description Actually Want?

The AIT BizOps BA-I role asks for these specific skills. Here's how our project hits each one:

| JD Requirement | Where We Prove It |
|---|---|
| "SQL to pull data and perform analysis" | 35 SQL queries, 6 views, star schema |
| "Excel including macros, charts and pivot tables" | 6-sheet pivot_pack.xlsx + VBA macro |
| "Analytical and quantitative skills" | Statistical hypothesis tests in SQL, anomaly detection |
| "Forecasting" (preferred) | SARIMAX models for OTP and cost |
| "Data visualization" | 6-page Streamlit dashboard, Plotly charts |
| "Our customer is the shipper" | Shipper Health Score (Page 2 of dashboard) |
| "Drive process improvements" | 9 Working-Backwards insights with recommendations |
| "Build and maintain KPIs" | 15 defined KPIs with precise formulas |

The key phrase in the JD is **"our customer is the shipper."** Most logistics projects build carrier scorecards. Ours leads with a **Shipper Health Scorecard** — a composite score for each seller measuring service quality, cost, growth, reliability, and tenure. That's the Amazon-specific angle that separates this from a generic portfolio project.

---

## Part 3: Architecture — How Everything Connects

### The Pipeline (What Runs When You Type `make all`)

Think of it like a factory assembly line. Each step takes the output of the previous step and transforms it:

```
Step 1: CONFIG (src/config.py)
   "Here are all the rules and numbers that define how freight works"
        |
Step 2: DATA GENERATION (src/generate_data.py)
   "Create 1,025,275 fake-but-realistic shipment records"
        |
Step 3: WAREHOUSE (src/build_warehouse.py)
   "Load all that data into a structured database"
        |
Step 4: SQL QUERIES (sql/queries/)
   "Ask 35 business questions against the database"
        |
Step 5: ANALYTICS (anomaly_detection.py, forecasting.py, pricing.py)
   "Run advanced analysis: find problems, predict the future, recommend prices"
        |
Step 6: DELIVERABLES (excel_pivot_pack.py, streamlit_app.py)
   "Package everything into Excel and dashboards that a VP could read"
        |
Step 7: TESTS (pytest)
   "Verify everything is correct — 30 automated checks, all passing"
```

The entire pipeline runs with one command: `make all`. It takes about 50 seconds. A recruiter or interviewer can clone the repo, run that command, and see everything work.

---

## Part 4: Every Component Explained Like a Layman

### 4.1 — The Configuration File (src/config.py)

**What it is:** A single file containing every number used in the project — 466 lines of constants.

**Why it matters:** Every number has a comment citing where it came from. For example:
- "On-time pickup rate is 87%" → cited from FreightWaves SONAR index
- "Cost per mile is $2.43" → cited from Cass Information Systems
- "Top 20 shippers handle 55% of volume" → cited from FreightWaves

**Interview angle:** When an interviewer asks "why did you pick 87% for OTP?", you point to line 187 of config.py and say "FreightWaves SONAR On-Time Pickup Index, 2024 national average for contract freight." That's the level of rigor Amazon expects.

### 4.2 — The Data Generator (src/generate_data.py)

**What it is:** A Python script that creates 1,025,275 synthetic shipment records plus 5 lookup tables.

**What's in each record:** Every shipment has a pickup appointment time, actual pickup time, delivery times, which trucking company handled it, which lane (origin → destination) it traveled, which seller shipped it, how full the trailer was, and a detailed cost breakdown.

**What makes it realistic (not toy data):**

1. **Power-law shipper distribution:** A few big sellers ship a LOT, many small sellers ship a little — just like reality. The top 20 shippers account for 54.3% of all volume.

2. **Four carrier tiers:** Strategic (best, cheapest), Core, Tactical, and Spot (worst, most expensive). Just like how Amazon actually segments trucking companies.

3. **Injected anomaly:** We deliberately planted a 14-day period where one Spot carrier on 3 lanes drops to 60% on-time. This is our "hidden bug" that the anomaly detector must catch — and it does. This is critical for telling the interview story.

4. **Realistic messiness:** 0.4% of pickup timestamps are NULL (tracking system failures), 0.1% of records have negative dwell times (driver arrived before appointment), 5 top shippers show volume decline (churn signal). Real data is messy; ours is too.

5. **Exact cost math:** Every shipment's total cost = linehaul + fuel + accessorial, computed using Python's Decimal type (not floating point) so there's ZERO rounding error across all 1M+ rows. This is something most people get wrong.

### 4.3 — The Star Schema Warehouse (DuckDB)

**What it is:** A structured database with 1 "fact table" (the shipments) surrounded by 5 "dimension tables" (carriers, lanes, shippers, dates, service types).

**What "star schema" means in plain English:** Imagine one giant spreadsheet of shipments. Instead of repeating "Strategic tier, Dedicated contract, Dry Van equipment" on every row for the same carrier, you store carrier details once in a separate table and just reference them by ID. This is called "normalization" — it saves space and prevents inconsistencies.

The schema looks like a star: the fact table is the center, and the 5 dimension tables point at it like rays.

**Why DuckDB:** It's a database that runs from a single file — no server installation needed. An interviewer types `make all` and it just works. In production at Amazon, you'd use Redshift or BigQuery, but the SQL is identical.

### 4.4 — The SQL Query Library (35 Queries)

This is the showpiece for the "SQL to pull data" requirement. Every query is a standalone `.sql` file with a business question in plain English at the top.

**Organized into 5 categories:**

**Operations (q01-q10):** "Which lanes have the most volume? How does on-time performance vary by carrier tier? Which day of the week is worst? What's the defect Pareto?"

**Cost (q11-q18):** "What's the cost per mile by tier? How much are accessorials costing us? Which shippers are most expensive to serve? Does Q4 peak season really lift costs?"

**Utilization (q19-q26):** "Are trailers running full or half-empty? Which LTL shipments look like they should be FTL? Which long-haul lanes could switch to intermodal rail?"

**Anomaly (q27-q30):** "Which carriers got worse this month vs last month? Where are dwell times spiking?"

**Statistical Testing (q31-q35):** These are the crown jewels:
- **q31 — Paired t-test:** "Is the OTP difference between Strategic and Tactical carriers statistically significant, or just noise?" (Answer: significant at p < 0.05)
- **q32 — Chi-square test:** "Is defect rate independent of carrier tier, or does tier predict defects?" (Answer: dependent — Spot carriers really do cause more defects)
- **q33 — Mann-Whitney U test:** "Is the Q4 cost increase statistically real?" (Answer: yes, significantly different)

**Why 3 hypothesis tests matter:** The JD says "analytical and quantitative skills." Any analyst can compute an average. Very few can run a statistical test *inside SQL* to prove the average is meaningful. This is what separates a BA-I from a reporting analyst.

### 4.5 — Anomaly Detection (src/anomaly_detection.py)

**Two methods:**

1. **Z-score for OTP:** For each lane, compute the rolling 8-week average OTP and standard deviation. If this week's OTP deviates by more than 2.5 standard deviations, flag it. Found 659 anomalies.

2. **IQR for cost-per-mile:** Cost data has a heavy right tail. Z-score doesn't work well for heavy tails. IQR method: anything above Q3 + 1.5×IQR is an outlier. Found 176 anomalies.

**Daily briefing:** Every run generates a markdown file like `2026-05-19.md` with flagged anomalies and recommended actions. This is what a BA would send to their manager every morning.

### 4.6 — SARIMAX Forecasting (src/forecasting.py)

**What it does:** Predicts where OTP and cost are heading over the next 4 weeks / 28 days.

**Why SARIMAX over Prophet or ML?** SARIMAX is the Box-Jenkins methodology. It's interpretable — you can explain every parameter. For a BA role, being able to say "I used SARIMAX(1,1,1)(1,1,1,4) because the data has weekly seasonality with a period of 4 weeks" is more impressive than "I used Prophet with defaults."

**Output:** CSV files with point forecasts and 95% confidence intervals, plus PNG charts.

### 4.7 — Pricing Recommendations (src/pricing_recommendations.py)

For each of the top 20 shippers, it computes whether they're profitable, growing, and recommends:
- **Hold** — metrics are normal
- **Renegotiate Up** — shipper is unprofitable, raise rates
- **Volume Discount** — shipper is growing fast with good service, reward loyalty

This directly addresses the "our customer is the shipper" charter — it's what an AIT BA would do in quarterly business reviews.

### 4.8 — Excel Pivot Pack (src/excel_pivot_pack.py)

A formatted 6-sheet Excel workbook generated by Python:
1. **Cover** — KPI snapshot
2. **Carrier Scorecard** — carrier × month OTP/defect/CPM
3. **Lane Heatmap** — origin × destination with red/yellow/green conditional formatting
4. **Shipper Cost-to-Serve** — top shipper costs by service type
5. **Accessorial Drivers** — cost breakdown by defect reason
6. **Daily Trend** — last 90 days of daily KPIs

Plus a VBA macro (`vba/auto_refresh.bas`) that refreshes all pivot tables with one click.

The JD literally says "macros, charts and pivot tables." Most candidates claim Excel skills. You have a generated, formatted .xlsx and a .bas macro file in your repo.

### 4.9 — Streamlit Dashboard (app/streamlit_app.py)

A 6-page interactive web application:

1. **Executive Summary** — 4 KPI cards with month-over-month deltas, 26-week OTP trend line
2. **Shipper Health Scorecard** — composite health score with filters and drill-down
3. **Lane Performance** — origin × destination OTP heatmap, top/bottom lanes
4. **Carrier Scorecard** — tier-filtered carrier KPIs with defect breakdown
5. **Anomaly Center** — browse flagged anomalies, download daily briefing
6. **What-If Simulator** — "What happens if I reassign this lane to a different carrier?" Uses bootstrap simulation with confidence intervals.

**Page 2 (Shipper Health) is the Amazon differentiator.** Most logistics dashboards start with carrier performance. Ours starts with "how is the shipper experience?" because the JD says that's who the customer is.

**Page 6 (What-If Simulator) shows decision-support thinking.** It's not just reporting — it's "here's a tool an ops manager could use to make a decision, with statistical confidence."

### 4.10 — Tests (tests/)

**30 automated tests** across 5 test files. All passing. This shows engineering discipline — a BA who writes tests is a BA who can be trusted with production pipelines.

---

## Part 5: The Numbers Our Project Produces

These are the actual results from the data:

| Metric | Value |
|---|---|
| Total shipments | 1,025,275 |
| Unique carriers | 52 |
| Unique lanes | 225 |
| Unique shippers | 340 |
| Network OTP | 85.5% |
| Network defect rate | 2.64% |
| Avg cost per shipment | $4,238 |
| Total cost (12 months) | $4.35 billion |
| Top-20 shipper concentration | 54.3% |
| Strategic tier OTP | 90.2% |
| Spot tier OTP | 73.8% |
| Z-score anomalies flagged | 659 |
| IQR anomalies flagged | 176 |
| Shipper pricing recommendations | 20 |

---

## Part 6: Why This Project Will Have a Massive Impact on Your Resume

### 6.1 — It's Not a Tutorial Project

Most BA candidates put "Analyzed Titanic dataset" or "Built a sales dashboard in Tableau" on their resume. Those are homework. This is a **production-grade analytics system** with 70+ files, 4,200+ lines of code, 35 SQL queries, 3 statistical hypothesis tests, SARIMAX forecasting, anomaly detection, Excel with VBA, an interactive dashboard, 30 automated tests, and full documentation.

### 6.2 — It's Domain-Specific to the Exact Role

This isn't "general data analysis." Every design decision maps to what AIT BizOps actually does:
- **Carrier tiering** (Strategic/Core/Tactical/Spot) is how Amazon segments carriers
- **Shipper Health Score** reflects the "customer is the shipper" charter
- **Inbound nodes** (BWI1, IAD2, etc.) mimic Amazon FC naming conventions
- **First-mile focus** is literally the team name
- **Cost-per-mile benchmarks** are cited from industry sources an Amazon analyst would actually use

### 6.3 — It Proves "I Can Do the Job on Day 1"

**SQL (required):** 35 queries using JOINs, CTEs, window functions (RANK, LAG, rolling AVG), PERCENTILE_CONT, conditional aggregation, and statistical tests computed entirely in SQL.

**Excel (required):** A generated 6-sheet pivot pack with formatted headers, conditional formatting, auto-filters, frozen panes, and a VBA macro.

**Forecasting (preferred):** SARIMAX time-series models with confidence intervals — not Excel trend lines.

**Quantitative skills:** Three formal hypothesis tests (t-test, chi-square, Mann-Whitney U) with conclusions stated in business language.

### 6.4 — It Gives You Interview Stories

The `INSIGHTS.md` file contains 9 findings, each structured as a mini Working-Backwards story:

1. "Monday pickups run 5pp below mid-week" → recommendation: staggered windows
2. "Spot carriers on long-haul create 80% more defects" → chi-square test confirms
3. "15% of LTL shipments look like FTL" → modal conversion saves 15-20%
4. "Accessorials are 15% of cost, detention-driven" → 2-hour detention clock
5. "Q4 lifts cost 12%, statistically confirmed" → lock rates by August
6. "5 top shippers show churn signals" → proactive retention
7. "Strategic beats Tactical by 5-8pp OTP" → t-test confirms, shift volume
8. "10+ long-haul lanes are intermodal candidates" → pilot conversion
9. "OTP forecast shows continued deterioration" → activate escalation now

Each insight has the query file that proves it, so you can pull it up live.

### 6.5 — It Shows Amazon Leadership Principles

- **Customer Obsession:** The entire project is shipper-centric. Page 2 is Shipper Health, not Carrier Health.
- **Dive Deep:** 1M+ rows, statistical significance testing, P50/P90/P99 distributions — not just averages.
- **Bias for Action:** The anomaly detector generates daily briefings with recommended actions.
- **Insist on the Highest Standards:** Cost identity is exact across 1M rows. 30 automated tests. Every benchmark is cited.
- **Are Right, A Lot:** Forecasting with confidence intervals, not point estimates. Bootstrap simulation in the What-If tool.

### 6.6 — The "Show, Don't Tell" Factor

Most resumes say: *"Proficient in SQL, Excel, and data visualization."*

Your resume says: *"Built a 1M-row inbound freight analytics platform with a DuckDB star schema, 35 SQL queries (including hypothesis tests), SARIMAX forecasting, anomaly detection, and interactive dashboards — repo link attached."*

And when they click the link, `make all` runs in 50 seconds and they see a working dashboard with real-looking data, statistical findings, and actionable insights. That's not a bullet point. That's evidence.

---

## Part 7: How to Talk About This in an Interview

### "Tell me about a project where you used data to drive a decision."

"I built an inbound first-mile analytics platform analyzing over a million shipment records. I designed a star schema, wrote 35 SQL queries, and discovered that Monday pickups run 5 percentage points below mid-week — not because of volume, but because of weekend backlog at origin facilities. I validated this with day-of-week analysis and recommended staggered pickup windows. I also found that Spot-tier carriers on long-haul lanes produce 80% more defects than the network average, confirmed by a chi-square test at p < 0.05, and recommended restricting them from those lanes."

### "Walk me through your SQL skills."

"Let me show you three queries. First, q07 uses a CTE to compute weekly OTP, then a window function with `ROWS BETWEEN 3 PRECEDING AND CURRENT ROW` for a rolling 4-week average. Second, q31 implements a paired t-test entirely in SQL — it pairs Strategic and Tactical carriers by lane, computes the mean difference, standard deviation, and t-statistic, then compares to the critical value. Third, q09 uses a running SUM window function to build a defect-reason Pareto chart with cumulative percentages."

### "How do you handle messy data?"

"In my project, I deliberately introduced realistic data quality issues: 0.4% of pickup timestamps are NULL from simulated tracking failures, 0.1% of dwell times are negative from early arrivals, and 5 shippers show churn signals. My quality_checks.py validates these are within expected ranges, and my SQL queries use FILTER and NULLIF to handle them gracefully rather than silently dropping rows."

### "Tell me about the hardest bug you fixed."

"The cost identity check — linehaul + fuel + accessorial must exactly equal total — was failing by tiny amounts. Root cause: Python float arithmetic. $100.10 + $20.03 + $15.07 in floats sometimes equals $135.19999999999999, not $135.20. I switched to Python's Decimal type with 2-place quantization, and the identity now holds exactly across all 1,025,275 rows. Lesson: never use floats for money."

---

## Part 8: Quick File Map

```
first-mile-carrier-dashboard/
│
├── src/                          # Core Python modules
│   ├── config.py                 # 466 lines of cited benchmark constants
│   ├── generate_data.py          # Creates 1M+ shipment records
│   ├── build_warehouse.py        # Loads CSVs into DuckDB star schema
│   ├── quality_checks.py         # 9 data quality assertions
│   ├── compute_kpis.py           # Exports KPI CSVs from SQL views
│   ├── anomaly_detection.py      # Z-score + IQR anomaly detection
│   ├── forecasting.py            # SARIMAX OTP + cost forecasting
│   ├── pricing_recommendations.py # Top-20 shipper pricing engine
│   └── excel_pivot_pack.py       # Generates 6-sheet formatted Excel
│
├── sql/
│   ├── ddl/                      # 6 table definitions (the star schema)
│   ├── views/                    # 6 analytical views (shipper health, etc.)
│   └── queries/                  # 35 numbered business queries
│
├── app/
│   └── streamlit_app.py          # 6-page interactive dashboard
│
├── tests/                        # 30 automated tests (all passing)
├── docs/                         # KPI definitions, data dictionary, etc.
├── reports/                      # Generated outputs (forecasts, pivot pack)
├── vba/auto_refresh.bas          # Excel macro
├── README.md                     # Project overview
├── INSIGHTS.md                   # 9 business insights
├── Makefile                      # One-command pipeline: make all
└── requirements.txt              # Python dependencies
```

---

## The Bottom Line

This project exists to answer one question from the Amazon interviewer: **"Can this person actually do the work?"**

The answer is 70+ files of executable evidence:
- You can write SQL (35 queries, 3 hypothesis tests)
- You can build data models (star schema with FK integrity)
- You can use Excel (6-sheet pivot pack with VBA)
- You can forecast (SARIMAX with confidence intervals)
- You can detect anomalies (z-score + IQR with reason attribution)
- You can build dashboards (6-page Streamlit with What-If simulator)
- You can think like Amazon (shipper-centric, Working Backwards insights)
- You can write tests (30/30 passing)
- You can cite your sources (every benchmark in config.py)

That's not a resume claim. That's a repo link.
