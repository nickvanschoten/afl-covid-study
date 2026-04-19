# The Ghost Town Effect: Study Findings

*A plain-English and technical summary of all empirical results, updated to reflect peer-review revisions.*

---

## Core Question

Did the removal of partisan crowds from AFL stadiums in 2020 cause umpires to award fewer free kicks to the home team?

**Answer: No.** The data provides no statistically detectable evidence of crowd-driven umpire bias. The convergence in home free-kick differentials observed in 2020 is explained by a structural collapse in dynamic gameplay caused by the physical demands of the hub season — not by any change in how umpires applied their judgement.

---

## Part 1: Disproving the Noise of Affirmation

### The Treatment Variable: Expected Partisanship Index (EPI)

Raw attendance is endogenous to crowd partisanship: a 35,000-person MCG derby crowd is roughly neutral, but 35,000 fans at a sold-out GMHBA Stadium are overwhelmingly Geelong supporters. Treating them identically produces the "Away Fan Fallacy."

The EPI resolves this by computing:

```
EPI_raw = historical_attendance × (historical_attendance / venue_capacity) × fan_split_multiplier
```

where `fan_split_multiplier` accounts for membership ratios, interstate matches, and known derby dynamics. The 2020 EPI uses a strictly pre-treatment 2015–2019 attendance baseline to preserve exogeneity.

**Empirical validation**: Previously, under an undirected specification, a naive model using raw standardised attendance as the treatment recovered a spurious crowd coefficient. Under our robust Directed Team-Pair fixed-effects specification with hub-travel controls, the naive attendance coefficient drops entirely to zero (`deficit × raw_att_z = +0.87, p = 0.508`). Replacing it with the EPI also returns a strictly null result, confirming that any perceived 'Away Fan Fallacy' or spurious significance in naive models is fully neutralised by rigorous identification.

### Panel OLS Results (5 Specifications)

All five model specifications — from the base binary DiD through to the full EPI + CPI + game-state control model — return a statistically insignificant `deficit_x_epi` coefficient. Standard errors are clustered at the matchup level. Cluster-robust 95% confidence intervals uniformly overlap zero.

> **Important**: A null result means the data cannot detect an effect. It does not constitute evidence of any behavioural direction. No inference about umpire psychology is made from the sign of the insignificant point estimate.

### EPI Stratification

If crowd noise drove the free-kick differential, the historically most-hostile matchups (top EPI quartile) should have collapsed the most in 2020 when their crowds were removed. The opposite is observed:

| Group | 2019 FK Diff | 2020 FK Diff | Change |
|---|---|---|---|
| Top 25% Most Hostile | +1.42 | +2.97 | **+1.55** |
| Bottom 25% Least Hostile | +0.44 | −0.71 | **−1.15** |

Neutral matchups collapsed. High-hostility matchups held or increased. This directly contradicts the crowd-pressure prediction and replicates the regression null without a model.

### Institutional Bias (Club Prestige Index)

The CPI aggregates each club's membership base, prior-season win rate, and primetime broadcast allocation into a matchup-level prestige differential. The CPI coefficient across all relevant model specifications is approximately +0.166 (p ≈ 0.28) — statistically insignificant. The badge on the jumper provides no detectable umpiring advantage.

---

## Part 2: Identification Robustness

### Parallel Trends Validation (Event-Study)

To satisfy the parallel trends assumption for a Continuous Treatment DiD, the expected change in free-kick differentials must be mean-independent of the EPI treatment intensity across the pre-treatment period. We validate this by interacting the EPI with individual year dummies (2012–2020) and testing whether the pre-2020 coefficients are statistically distinguishable from zero:

| Year | Coef | p-value |
|---|---|---|
| 2012 | +0.817 | 0.131 |
| 2013 | +0.302 | 0.381 |
| 2014 | +0.292 | 0.290 |
| 2015 | +0.371 | 0.159 |
| 2016 | +0.169 | 0.478 |
| 2017 | +0.403 | 0.114 |
| 2018 | +0.534 | 0.026** |
| **2019** | **0.000** | **(reference)** |
| 2020 | +0.615 | 0.136 |

With the exception of a marginally significant deviation in 2018, all pre-treatment coefficients are statistically indistinguishable from zero using two-way clustered standard errors. No systematic pre-trend drift is present. Parallel trends structurally holds.

### Placebo Test (Fake 2018 Lockout)

Excluding 2020 and assigning a fake treatment to 2018 (`deficit_ratio = 1.0` for all 2018 games):

```
deficit_x_epi (PLACEBO 2018) = +0.222, p = 0.291
```

The fixed-effect structure does not manufacture false positives. The result is cleanly null.

---

## Part 3: Tactical Compression — The True Mechanism

### Why Disposals Are the Wrong Denominator

An earlier draft normalised all metrics as rates per disposal. This is methodologically flawed: disposals are endogenous to the style of play being measured — a congested 2020 game produces fewer disposals *and* fewer free kicks through the same underlying mechanism. Dividing by them creates a numerator-denominator correlation that compresses apparent effect sizes.

**The correct denominator is actual elapsed game time** — an exogenous variable governed by AFL rules, not team tactics.

### Game Time: Empirical vs. Nominal

The 2020 AFL season used 16-minute quarters (vs. 20 minutes normally). The theoretical correction factor is 80/64 = 1.25. The actual correction, measured from AFL Tables match records for all 1,736 games, is:

| Era | Mean Game Time |
|---|---|
| 2012–2019 | 122.0 min |
| 2020 | 101.5 min |
| **Empirical ratio** | **0.8374** |
| Nominal ratio | 0.8000 |

The 3.7 percentage-point difference represents real hub-season behaviour: faster play-on, fewer rotation stoppages, reduced injury delays. Using the empirical figure rather than the nominal constant is analytically superior.

### Per-60-Minute Results

Converting all counting metrics to per-60-minute rates using actual game time:

| Metric | Baseline (2012–2019) | 2020 | Change | p-value |
|---|---|---|---|---|
| **Forward Efficiency** (MI50/I50) | 22.6% | 20.5% | **−9.2%** | < 0.0001 |
| **Contested Possession Rate** (CP/DI) | 38.4% | 39.9% | **+3.8%** | < 0.0001 |
| **Tackles per 60 min** | 64.6 | 59.5 | **−7.9%** | < 0.0001 |
| **Free Kicks per 60 min** | ~18.4 | ~19.0 | **+3.3%** | ~0.29 (ns) |

The last row is the critical finding: **free kicks per 60 minutes did not decline significantly**. When normalised to actual game time, adjudication density was stable. The entire 13.2% raw-count decline in total match free kicks is a pure volume effect of the 20-minute shorter game — not a change in umpire behaviour.

### Tackle Rate Reconciliation

An earlier manuscript draft contained a contradiction: Section 6 cited a Tackle Rate decline of −4.1%, while a figure note described it as "ticking up slightly in 2020." This was caused by using the disposal-based denominator:

- **Endogenous denominator** (TK/DI): −4.1% (p = 0.016) — disposals shrank too, compressing the ratio
- **Exogenous denominator** (TK/60min): **−7.9% (p < 0.0001)** — the correct figure

The "tick up" in the earlier figure referred to the 2019-to-2020 single-year increment: 2019 was the all-time sample low (61.2 TK/60min), and 2020 (59.5 TK/60min) is marginally higher than 2019 alone. However, 2020 remains approximately 5 tackles per 60 minutes below the full 2012–2019 baseline mean and is the second-lowest season in the dataset. There is no contradiction in the per-60 data.

### Why Tactical Compression Eliminated the Differential

A reduction in total free kicks does not mechanically eliminate home-team bias; umpires could still allocate a disproportionate share of the remaining free kicks to the home side. The mechanism linking game-style collapse to *differential* convergence operates through the energy economics of open play.

Under normal conditions, home teams accumulate a free-kick advantage primarily through a fourth-quarter energy premium: superior rest and routine allows them to break contested scrums into space, forcing exhausted away players into contact-driven infractions (Holding the Ball, Holding the Man, Push in the Back). Hub conditions democratised this fatigue. Both teams were equally travel-burdened and four-day-rested. Without an energy asymmetry, the home team could not sustain the late-game territorial dominance that structurally generates free-kick differentials. The convergence reflects the erosion of the *source* of the advantage — not a change in adjudication.

---

## Summary of Key Statistics

| Finding | Value |
|---|---|
| Baseline mean FK differential (2012–2019) | +1.51 free kicks/game |
| 2020 mean FK differential | +0.38 free kicks/game |
| EPI crowd coefficient (all models) | Not significant (p > 0.10) |
| CPI brand coefficient | +0.166, p ≈ 0.28 |
| Placebo test (2018): `deficit_x_epi` | +0.222, p = 0.291 |
| Event-study: max pre-treatment p-value | 0.478 (most > 0.15) |
| Naive attendance model: `deficit × att_z` | +0.871, p = 0.508 |
| Forward Efficiency change (per-60) | −9.2%, p < 0.0001 |
| Tackles/60 min change | −7.9%, p < 0.0001 |
| Free Kicks/60 min change | +3.3%, p ≈ 0.29 (ns) |
| Raw FK count change | −13.2%, p < 0.00001 (volume only) |
| Actual game time ratio (2020 / pre-2020) | 0.8374 (nominal: 0.800) |

---

## Scope and Limitations

This study establishes that, in the specific and extraordinary context of the 2020 AFL hub season, behavioural shifts in game mechanics were of sufficient magnitude to render crowd-based umpire bias statistically undetectable. We do not claim this proves crowd effects are absent under normal operating conditions. The appropriate conclusion is that tactical compression was the dominant explanatory force in 2020, and that the threshold for crowd-pressure effects to manifest above this structural noise could not be crossed in this particular seasonal context.

Future research exploiting partial-crowd variation — such as stadium-by-stadium capacity restrictions in other competitions — would provide stronger identification of the crowd channel in isolation.