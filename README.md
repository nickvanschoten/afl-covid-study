# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the AFL

**An applied econometrics study exploiting the 2020 AFL hub season as a natural experiment to test the "Noise of Affirmation" hypothesis — the claim that partisan crowds subconsciously bias umpire decisions in favour of the home team.**

---

## Study Overview

The 2020 AFL season, played entirely in isolated hubs with empty stadiums due to COVID-19 lockdowns, provides a rare natural experiment for causal inference in sports analytics. Home free-kick differentials converged sharply toward zero. The naive interpretation — that removing crowds removed umpire bias — is, as this study demonstrates, econometrically unsound.

This repository contains the full replication pipeline for a **Continuous Treatment Difference-in-Differences (DiD)** analysis establishing three findings:

1. **Null crowd effect**: The Expected Partisanship Index (EPI) crowd-pressure coefficient is statistically indistinguishable from zero across all five Panel OLS specifications, validated by an event-study parallel trends test, a placebo test, and an EPI stratification analysis.
2. **Null institutional bias**: The Club Prestige Index (CPI) coefficient is equally null. Brand prestige confers no umpiring advantage.
3. **Tactical Compression is the mechanism**: The 2020 free-kick convergence was driven by a structural collapse in dynamic gameplay — Forward Efficiency (MI50 rate) dropped 9.2%, tackles per 60 minutes dropped 7.9% — not by any change in umpire psychology.

---

## Repository Structure

```
footy/
├── afl_noise_affirmation_did.py     # Core ingestion pipeline + DiD econometric models
├── econometric_robustness.py        # Identification checks (naive model, placebo, event-study)
├── mechanism_verification.py        # Mechanism tests (EPI strat, FK decomp, TK reconciliation)
├── tactical_compression_eda.py      # Game-style EDA (CPR, TR, UMR year-over-year)
├── fatigue_vs_intensity_eda.py      # Within-2020 rest-day micro-climate analysis
│
├── articledesc.md                   # Full academic paper description (peer-review revised)
├── FINDINGS.md                      # Plain-English summary of results
├── README.md                        # This file
│
├── figure_fk_baseline_density.png   # Figure 1: Baseline FK differential distribution
├── figure_fk_covid_density.png      # Figure 2: Baseline vs 2020 convergence
├── figure_event_study.png           # Figure 3: Parallel trends event-study plot
├── figure_coefficient_forest.png    # Figure 4: Five-model coefficient forest plot
├── figure_epi_stratification.png    # Figure 5: High-EPI vs Low-EPI group trajectories
├── figure_tackle_rate_ts.png        # Figure 6: TK/60min and FK/60min time series
├── figure_trench_warfare.png        # Figure 7: Era comparison box plots
├── figure_game_style_evolution.png  # Supplementary: CPR, TR, UMR year-over-year
├── figure_rest_impact.png           # Supplementary: rest-day fatigue micro-climate
│
├── afl_cache/
│   └── raw_panel.parquet            # Committed panel cache (1,736 matches × 38 cols)
│   └── match_*                      # Raw HTML (gitignored, ~1,800 files)
│
└── .gitignore
```

---

## Replication Guide

### Prerequisites

```bash
python -m pip install requests beautifulsoup4 pandas numpy scikit-learn linearmodels matplotlib seaborn scipy
```

Python 3.9+ required.

### Step 1 — Data Ingestion (optional if parquet already present)

The committed `afl_cache/raw_panel.parquet` contains the pre-built panel; collaborators can skip ingestion and run EDA/modelling scripts directly. If you need to rebuild from scratch (e.g., after adding new stat columns):

```bash
# Remove cached panel, then run the main pipeline
del afl_cache\raw_panel.parquet
python afl_noise_affirmation_did.py
```

The ingestion pipeline scrapes ~1,800 match pages from [AFL Tables](https://afltables.com) and caches them locally under `afl_cache/`. Subsequent runs are fast (reads from cache). The full pipeline run also fits all five Panel OLS models and generates `figure_coefficient_forest.png` and `figure_marginal_effect.png`.

### Step 2 — Identification / Robustness Checks

```bash
python econometric_robustness.py
```

Produces:
- **Console**: Naive attendance model table, placebo test table, event-study coefficient table
- **Output**: `figure_event_study.png`

### Step 3 — Mechanism Verification

```bash
python mechanism_verification.py
```

Produces:
- **Console**: EPI stratification table, FK proxy decomposition table, tackle rate reconciliation
- **Output**: `figure_epi_stratification.png`, `figure_tackle_rate_ts.png`

### Step 4 — Game-Style EDA

```bash
python tactical_compression_eda.py
```

Produces:
- **Console**: T-test results for CPR, TR, UMR
- **Output**: `figure_baseline_density.png` (TR KDE), `figure_covid_density.png` (UMR KDE), `figure_game_style_evolution.png`

### Step 5 — Rest-Day Micro-Climate (Supplementary)

```bash
python fatigue_vs_intensity_eda.py
```

Produces:
- **Console**: Short-rest vs normal-rest comparison within 2020
- **Output**: `figure_rest_impact.png`

---

## Key Design Decisions

### Expected Partisanship Index (EPI)

Raw attendance is a deeply flawed proxy for crowd hostility. A crowd of 35,000 at a Melbourne cross-city derby is roughly neutral; 35,000 at a sold-out GMHBA Stadium is overwhelmingly partisan. The EPI resolves this via a three-stage construction:

```
fan_split     = home_memberships / (home_memberships + away_memberships)   # or derby override
density       = historical_attendance / venue_capacity                     # capped at 1.0
EPI_raw       = historical_attendance × density × fan_split
deficit_x_epi = deficit_ratio × EPI_z                                     # treatment interaction
```

The historical attendance baseline for 2020 games uses a strictly pre-treatment 2015–2019 average window to preserve exogeneity. Club membership data uses a fixed 2015–2019 average — not a rolling figure that could be contaminated by pandemic-era behaviour.

**Justification**: A naive model using `deficit × raw_attendance_z` recovers a spurious borderline-significant coefficient (+2.00, p = 0.050). Replacing it with the EPI eliminates the false signal, empirically validating the instrument.

### Club Prestige Index (CPI)

```
CPI_raw   = (mem_z + lag_win_pct_z + lag_primetime_pct_z) / 3
CPI_score = within-season z-score of CPI_raw
CPI_diff  = home_CPI - away_CPI
```

All components use a single one-period lag (season *t-1*) to prevent data leakage. The 2012 lag is left as a missing value rather than backfilled with contemporaneous data.

### Per-60-Minute Normalisation

The 2020 AFL season used 16-minute quarters vs. the standard 20 minutes. Rather than applying a nominal correction factor of 80/64 = 1.25, we parse actual **elapsed game time** from AFL Tables HTML for every match:

- 2012–2019 mean game time: **122.0 minutes**
- 2020 mean game time: **101.5 minutes**
- Empirical ratio: **0.8374** (vs nominal 0.800)

All counting metrics are expressed as **per 60 minutes** using this exogenous denominator, eliminating the endogeneity present in per-disposal rates (where disposals themselves are a product of the game-style shifts being measured).

### Identification Robustness

| Check | Result |
|---|---|
| **Parallel trends (event-study)** | All 7 pre-treatment EPI×Year coefficients: p = 0.56–0.81, CI spans zero |
| **Placebo test (fake 2018 lockout)** | `deficit_x_epi_placebo` = +0.344, p = 0.526 — null |
| **Naive attendance benchmark** | `deficit × raw_att_z` = +2.00, p = 0.050 — spurious |
| **EPI stratification** | Low-EPI games collapsed more than high-EPI — contra crowd prediction |

---

## Data Source

All match statistics are sourced from **[AFL Tables](https://afltables.com)** scraped via `requests` + `BeautifulSoup4` and cached locally. The `raw_panel.parquet` cache is committed to the repository so that EDA and modelling scripts can be run without re-scraping.

The AFL Tables data provides: free kicks for/against, contested possessions, disposals, tackles, marks, contested marks, inside 50s, marks inside 50s, clearances, goals, behinds, attendance, and actual elapsed game time — 38 columns across 1,736 matches (2012–2020).

---

## Figures Reference

| File | Description | Produced by |
|---|---|---|
| `figure_fk_baseline_density.png` | Home FK differential KDE: 2012–2019 baseline | `afl_noise_affirmation_did.py` |
| `figure_fk_covid_density.png` | Baseline vs. 2020 convergence overlay | `afl_noise_affirmation_did.py` |
| `figure_event_study.png` | EPI×Year event-study parallel trends plot | `econometric_robustness.py` |
| `figure_coefficient_forest.png` | Five-model coefficient forest plot | `afl_noise_affirmation_did.py` |
| `figure_epi_stratification.png` | High vs. Low EPI quartile FK differential 2012–2020 | `mechanism_verification.py` |
| `figure_tackle_rate_ts.png` | TK/60min + FK/60min year-over-year time series | `mechanism_verification.py` |
| `figure_trench_warfare.png` | Era comparison box plots: FE, CPR, TK/60, FK/60 | `tactical_compression_eda.py` |
| `figure_game_style_evolution.png` | CPR, TR, UMR year-over-year evolution | `tactical_compression_eda.py` |
| `figure_rest_impact.png` | Short vs. normal rest within 2020 | `fatigue_vs_intensity_eda.py` |

---

## Citation & Author Note

This project was developed as a portfolio demonstration of applied causal inference techniques in sports analytics, including natural-experiment DiD design, custom treatment variable engineering, and identification robustness testing. The econometric architecture follows Callaway & Sant'Anna (2021) for heterogeneous-treatment DiD and Angrist & Pischke (2009) for continuous-treatment identification strategy.
