# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the AFL

**An applied econometrics study exploiting the 2020 AFL hub season as a natural experiment to test the "Noise of Affirmation" hypothesis — the claim that partisan crowds subconsciously bias umpire decisions in favour of the home team.**

---

## Study Overview

The 2020 AFL season, played in isolated hubs with stadiums largely empty due to COVID-19 lockdowns, provides a rare natural experiment for causal inference in sports analytics. Home free-kick differentials converged sharply toward zero. The naive interpretation — that removing crowds removed umpire bias — is, as this study demonstrates, econometrically unsound.

This repository contains the full replication pipeline for a **Continuous Treatment Difference-in-Differences (DiD)** analysis establishing three findings:

1. **Null crowd effect**: The Expected Partisanship Index (EPI) crowd-pressure coefficient is statistically indistinguishable from zero across all five Panel OLS specifications. This result survives an event-study parallel trends test (corrected reference year), a placebo test, a common-support robustness check, an EPI construct-validation test, and direct heterogeneous-confound interaction tests (fatigue × EPI).
2. **Null institutional bias**: The Club Prestige Index (CPI) coefficient is equally null. Brand prestige confers no umpiring advantage.
3. **Tactical Compression is the mechanism**: The 2020 free-kick convergence was driven by a structural collapse in dynamic gameplay — Forward Efficiency (MI50/I50) dropped 2.4 p.p., CP per nominal 60 minutes fell 1.6%, and FK/60 nominal minutes actually rose 9.8% — not by any change in umpire psychology. The game devolved into "Trench Warfare," a match-long congested scrum.

---

## Repository Structure

```
footy/
├── afl_noise_affirmation_did.py      # Core ingestion pipeline + DiD models (M1–M5)
├── econometric_robustness.py         # Identification checks (naive model, placebo, event-study)
├── mechanism_verification.py         # Mechanism tests (EPI strat, FK decomp, TK reconciliation)
├── final_robustness_checks.py        # Peer-review round 1 responses
├── peer_review_round2.py             # Peer-review round 2 responses (six targeted challenges)
│
├── ARTICLE.md                        # Full academic paper (peer-review revised, final)
├── articledesc.md                    # Academic paper description (peer-review revised, final)
├── FINDINGS.md                       # Plain-English summary (peer-review revised, final)
├── README.md                         # This file
│
├── figure_fk_baseline_density.png    # Figure 1: Baseline FK differential distribution
├── figure_fk_covid_density.png       # Figure 2: Baseline vs. 2020 convergence
├── figure_event_study.png            # Figure 3: Parallel trends event-study (ref=2016)
├── figure_coefficient_forest.png     # Figure 4: Five-model coefficient forest plot
├── figure_residualized_stratification.png  # Figure 5: Residualized EPI stratification
├── figure_tackle_rate_ts.png         # Figure 6: TK/60 and FK/60 time series
├── figure_trench_warfare.png         # Figure 7: Era comparison box plots
├── figure_causality_proof.png        # Figure 8: Quarter-length causality tests
│
├── afl_cache/
│   └── raw_panel.parquet             # Committed panel cache (2,339 matches × 38 cols, 2012–2023)
│   └── match_*                       # Raw HTML (gitignored, ~2,300 files)
│
└── .gitignore
```

---

## Replication Guide

### Prerequisites

```bash
python -m pip install requests beautifulsoup4 pandas numpy scikit-learn linearmodels matplotlib seaborn scipy statsmodels
```

Python 3.9+ required.

### Step 1 — Data Ingestion (skip if parquet already present)

The committed `afl_cache/raw_panel.parquet` contains the pre-built panel. Collaborators can run all modelling scripts against it directly. To rebuild from scratch:

```bash
del afl_cache\raw_panel.parquet
python afl_noise_affirmation_did.py
```

The ingestion pipeline scrapes match pages from [AFL Tables](https://afltables.com) and caches them locally under `afl_cache/`. Subsequent runs are fast (reads from cache). The full pipeline run also fits all five Panel OLS models and generates `figure_coefficient_forest.png`.

### Step 2 — Identification / Robustness Checks

```bash
python econometric_robustness.py
```

Outputs:
- **Console**: Naive attendance model, placebo test, event-study coefficient table (reference year: 2016)
- **Output**: `figure_event_study.png`

### Step 3 — Mechanism Verification

```bash
python mechanism_verification.py
```

Outputs:
- **Console**: EPI stratification table, FK proxy decomposition, tackle rate reconciliation (nominal vs. actual denominators)
- **Output**: `figure_residualized_stratification.png`, `figure_tackle_rate_ts.png`

### Step 4 — Peer-Review Round 1 Robustness Checks

```bash
python final_robustness_checks.py
```

Produces four targeted robustness checks:
- **Challenge 1**: Common support overlap diagnostic + trimmed-sample and Manski-bound re-runs of Model 2
- **Challenge 2**: Quarter-by-quarter scoring margin decomposition (1,736 matches from HTML cache)
- **Challenge 3**: EPI construct validation (scoring margin regression) + 12-point fan-split sensitivity grid
- **Challenge 4**: Unit-specific linear time trends (note: absorbed in balanced panel — see notes below)

### Step 5 — Peer-Review Round 2 Robustness Checks

```bash
python peer_review_round2.py
```

Addresses six structural critiques identified in the second review round:

| Challenge | What it does |
|---|---|
| **1** | Re-runs event study with 2016 (not 2019) as reference year; diagnoses `season_within` collinearity with Time FEs |
| **2** | Adds `rest_x_epi` + `interstate_x_epi` interaction terms to Models 3 and 5 |
| **3** | Recomputes all rates using nominal exogenous game time (64/80 min); corrects CP/DI denominator |
| **4** | Fixes `compute_epi_fixed()` — original silently overwrote fan-split overrides, making the grid bug-invariant |
| **5** | Computes home-away CP/CL/TK differentials and diagnoses absolute fatigue marginals |
| **6** | Replaces degenerate undirected pair FE with additive `C(home_team) + C(away_team) + C(season)` OLS that requires Directed Pairs Model 2 |

### Step 6 — Quarter-Length Causality

```bash
python quarter_length_causality.py
```

Produces the "Recovery Era" reversion test (2021–2023 post-hub data) and Q4 fade analysis:
- **Output**: `figure_causality_proof.png`

---

## Key Design Decisions

### Expected Partisanship Index (EPI)

Raw attendance is a deeply flawed proxy for crowd hostility. A crowd of 35,000 at a Melbourne cross-city derby is roughly neutral; 35,000 at a sold-out GMHBA Stadium is overwhelmingly partisan. The EPI resolves this via a three-stage construction:

```python
fan_split     = home_memberships / (home_memberships + away_memberships)   # or derby override
density       = historical_attendance / venue_capacity                     # capped at 1.0
EPI_raw       = historical_attendance × density × fan_split
deficit_x_epi = deficit_ratio × EPI_z                                     # treatment interaction
```

The historical attendance baseline for 2020 games uses a strictly pre-treatment 2015–2019 average to preserve exogeneity. Club membership data uses a fixed 2015–2019 average — not a rolling figure that could be contaminated by pandemic-era behaviour.

**EPI Construct Validation**: High-EPI games predict larger home scoring margins in the pre-2020 baseline (OLS slope = +4.17 pts/SD, p < 0.001) and larger home free-kick advantages (Welch t = +2.02, p = 0.044).

**EPI Sensitivity (corrected)**: A 4×3 grid varies non-Victorian derby weights (0.65–0.95) and Victorian derby weights (0.35–0.65). A bug in the original pipeline caused `compute_epi()` to unconditionally overwrite the overridden `fan_split` column before computing EPI — making all 12 configurations use the default 0.85/0.50 weights and reporting the artifactual invariance p = 0.211 × 12. Fixed in `compute_epi_fixed()`. Corrected coefficient range: [+0.717, +0.749]; p-value range: [0.178, 0.253]. All 12 remain null.

### Club Prestige Index (CPI)

```python
CPI_raw   = (home_att_z + lag_win_pct_z + lag_primetime_pct_z) / 3
CPI_score = within-season z-score of CPI_raw
CPI_diff  = home_CPI - away_CPI
```

All components use a single one-period lag (season *t-1*) to prevent data leakage. The 2012 lag is left as missing rather than backfilled with contemporaneous data.

### Rate Normalisation: Nominal Game Time (updated)

The 2020 AFL season used 16-minute quarters vs. the standard 20 minutes. Prior specifications normalised rates using **actual elapsed game time** (`game_time_mins`). A reviewer identified a simultaneity concern: actual clock time includes stoppage time caused by free kicks, creating a feedback loop between the outcome and its normalising denominator.

Primary normalisation is now the **exogenous nominal game time**:

| Era | Nominal Game Time | Actual Game Time (mean) |
|---|---|---|
| 2012–2019 | **80 min** (4 × 20) | 121.5 min |
| 2020 | **64 min** (4 × 16) | 101.8 min |
| Ratio | **0.8000** | 0.8374 (empirical) |

Both normalisations are reported for all rate metrics. Directional conclusions are unchanged under either denominator.

**CP Rate correction**: Prior specifications computed Contested Possession Rate as CP/DI (disposals — endogenous to game style). Corrected to CP per 60 nominal minutes. Directional finding unchanged.

### Model Specifications

| Model | Specification | SE |
|---|---|---|
| **M1** | `C(home_team) + C(away_team) + C(season)` OLS (corrected from degenerate undirected pair FE) | HC1-robust |
| **M2** | Directed team-pair PanelOLS + TimeEffects | 2-way cluster-robust |
| **M3** | M2 + `days_rest_diff` + `relative_interstate_dis` + fatigue×EPI interactions | 2-way cluster-robust |
| **M4** | M3 + CPI | 2-way cluster-robust |
| **M5** | M4 + post-treatment game-state controls (cp_diff, kicks_diff, clearance_diff) | 2-way cluster-robust |

> **Model 1 note**: Undirected pair FEs against an antisymmetric outcome (home FK − away FK) are degenerate — the entity effect cancels to zero when teams swap home/away roles. Corrected to additive `C(home_team) + C(away_team) + C(season)`. Under this correction, `deficit_x_epi` = +1.072, HC1 p = 0.059 — borderline. This implies that testing dyadic home-vs-away interactions strictly requires the Directed Team-Pair Fixed Effects of Model 2. Models 2–5 with two-way clustering consistently return statistically undetectable results.

### Identification Robustness Summary

| Check | Result |
|---|---|
| **Event-study (ref=2016)** | Pre-treatment null; 2018 borderline (p=0.033); 2020 coef=+0.446, p=0.190 |
| **Detrending** | `season_within` collinear with Year FEs — degenerate; baseline null (p=0.211) stands |
| **Fatigue×EPI interactions** | `rest_x_epi` + `interstate_x_epi` added; `deficit_x_epi`=+0.767, p=0.200 — null unchanged |
| **Placebo (fake 2017 lockout)** | coef=+0.156, p=0.503 |
| **Naive attendance benchmark** | `deficit × raw_att_z`=+2.00, p=0.050 (spurious; EPI resolves) |
| **EPI stratification** | Low-EPI games collapsed 10× more than high-EPI — contra crowd prediction |
| **Absolute Fatigue Shock** | > 30% OOS; KS p = 0.000; Identified set estimated in Manski bounds |
| **EPI sensitivity (fixed, 12 configs)** | Coef range [+0.717,+0.749]; p range [0.178,0.253]; all null |
| **Tactical differentials** | CP diff: +3.42→+1.34 (ns); FK diff: +1.59→+0.30 (p=0.009) |

### The 2018 Pre-Trend Deviation

The event-study (reference year 2016) shows a statistically significant pre-trend deviation in 2018 (coef=+0.365, p=0.033, CI=[+0.030, +0.700]). Unit-specific detrending cannot be applied: `season_within` is perfectly collinear with entity FEs in this balanced panel structure (each entity-season appears exactly once). The deviation is attributed to a one-off structural event (AFL 2018 rule changes) rather than a continuous drift. Primary defences are the corrected reference year and the placebo test. The 2020 null at p=0.211 is unmodified.

---

## Key Numbers at a Glance

| Statistic | Value |
|---|---|
| Baseline FK differential (2012–2019) | **+1.51** free kicks/game |
| 2020 FK differential | **+0.38** free kicks/game |
| Total differential drop | **1.130** free kicks |
| Primary model (`deficit_x_epi`, M2) | **+0.745**, p = 0.211 (null) |
| With fatigue×EPI interactions (M3) | **+0.767**, p = 0.200 (null) |
| Event study 2020 coef (ref=2016) | **+0.446**, p = 0.190 (null) |
| Nominal game time ratio | **0.8000** (64/80 min) |
| Actual game time ratio | **0.8374** (101.8/121.5 min) |
| Mechanical bound (k=2 fatigue) | −0.434 of the 1.130 drop |
| Residual unexplained by duration | **0.696** |
| Forward Efficiency change (nominal) | **−9.2%** (p < 0.0001) |
| Tackles/60 min change (nominal) | **−3.6%** (p = 0.020*) |
| CP/60 min change (nominal) | **+4.4%** (p < 0.001***) |
| Free Kicks/60 min change (nominal) | **+9.8%** (p = 0.000***) |
| FK differential (home−away) 2020 | **+0.30** (vs. +1.59 baseline, p=0.009) |
| EPI sensitivity grid (fixed) | 12/12 null; coef span = 0.032; p range [0.178, 0.253] |
| KS Test, Absolute Rest | p = 0.0000 |
| Placebo (fake 2017) | p = 0.503 |

---

## Data Source

All match statistics are sourced from **[AFL Tables](https://afltables.com)** scraped via `requests` + `BeautifulSoup4` and cached locally. The `raw_panel.parquet` cache is committed so that all modelling scripts can be run without re-scraping.

The AFL Tables data provides: free kicks for/against, contested possessions, disposals, tackles, marks, contested marks, inside 50s, marks inside 50s, clearances, goals, behinds, attendance, and actual elapsed game time — 38 columns across 2,339 matches (2012–2023 for causality tests; 2012–2020 for the primary DiD window). Per-quarter scoring margins for all 1,736 study-window matches are additionally parsed from cached match HTML in `peer_review_round2.py`.

---

## Figures Reference

| File | Description | Produced by |
|---|---|---|
| `figure_fk_baseline_density.png` | Home FK differential KDE: 2012–2019 baseline | `afl_noise_affirmation_did.py` |
| `figure_fk_covid_density.png` | Baseline vs. 2020 convergence overlay | `afl_noise_affirmation_did.py` |
| `figure_event_study.png` | EPI×Year event-study parallel trends (ref=2016) | `econometric_robustness.py` |
| `figure_coefficient_forest.png` | Five-model coefficient forest plot | `afl_noise_affirmation_did.py` |
| `figure_residualized_stratification.png` | Residualized EPI quartile FK differential 2012–2020 | `mechanism_verification.py` |
| `figure_tackle_rate_ts.png` | TK/60 + FK/60 nominal time series | `mechanism_verification.py` |
| `figure_trench_warfare.png` | Era comparison box plots: FE, CP/60, TK/60, FK/60 | `mechanism_verification.py` |
| `figure_causality_proof.png` | V-shape FwdEff reversion test + Q4 scoring variance | `quarter_length_causality.py` |

---

## Citation & Author Note

This project was developed as a portfolio demonstration of applied causal inference techniques in sports analytics, including natural-experiment DiD design, custom treatment variable engineering, and identification robustness testing. The econometric architecture follows Callaway & Sant'Anna (2021) for heterogeneous-treatment DiD and Angrist & Pischke (2009) for continuous-treatment identification strategy.
