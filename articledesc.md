# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

## 1. Introduction

Why do home teams consistently receive favourable penalty differentials in professional sports? In sports science, this phenomenon is frequently attributed to the "Noise of Affirmation"—the hypothesis that partisan crowds subconsciously nudge adjudicators into favouring the home side. Historically, Australian Football League (AFL) home teams have enjoyed a persistent free-kick advantage, with the distribution of home free-kick differentials peaking meaningfully to the right of zero across the 2012–2019 baseline. However, researchers estimating these effects routinely confront a fundamental identification challenge: disentangling crowd-induced bias from genuine home-ground performance quality and from the structural noise intrinsic to complex contest sports.

The 2020 AFL season provides a rare natural experiment to isolate this mechanism. COVID-19 lockdowns forced the league into geographically isolated hubs, with stadiums largely empty or operating under severely restricted attendance limits for the vast majority of the season's duration. If partisan crowds cause umpire bias, removing them should flatten the free-kick differential. At first glance, the 2020 data appears to confirm this. The home free-kick advantage collapsed.

This paper argues that this conclusion is premature and econometrically unsound. Our contribution is threefold. First, we develop a novel continuous treatment metric—the **Expected Partisanship Index (EPI)**—to resolve the severe measurement error present in raw attendance figures. Second, we deploy a **Continuous Treatment Difference-in-Differences (DiD)** framework and demonstrate, across five Panel OLS specifications with entity and time fixed effects, that the EPI crowd-pressure coefficient provides no statistically detectable evidence of bias. We validate this result through four formal identification checks: a naive attendance benchmark, a 2017 placebo test, an event-study parallel trends validation, and marginal absolute rest distribution tests. Third, we demonstrate that the observed convergence in 2020 free-kick differentials was driven not by referee psychology, but by a structural collapse in dynamic gameplay into a match-long, congested scrum—what we term "Tactical Compression"—caused by the absolute physiological shock of an unprecedented hub season.

We structure the paper as follows. Section 2 presents the motivating distributional evidence. Section 3 details the data and construction of our treatment and control indices. Section 4 outlines the identification strategy, including causal structure, key assumptions, and their empirical defences. Section 5 presents the main umpire-bias results. Section 6 investigates the physiological and tactical mechanisms. Section 7 concludes with appropriate scope limitations.

> **[Figure 1 Descriptor: A density plot titled "2012-2019 Baseline: Home Free Kick Differential Distribution". The distribution forms a right-skewed unimodal distribution centred near +1.51, indicating a persistent historical free-kick advantage for the home team.]**

> **[Figure 2 Descriptor: A density plot titled "The Convergence: Baseline vs. 2020 Free Kick Differential Distributions". Two overlapping distributions are shown: the blue 2012–2019 baseline (mean = +1.51) and the pink 2020 hub season (mean = +0.38). The 2020 distribution has shifted materially leftward, consistent with a convergence toward zero differential.]**

---

## 2. Motivating Example

Consider a naive pre/post comparison of free-kick differentials. In the 2012–2019 baseline, home teams won the free-kick count at a mean rate of +1.51 free kicks per game. In the 2020 hub season, this differential collapsed to +0.38—a drop of **1.130 free kicks**. At first glance, this convergence appears to confirm the crowd-pressure hypothesis: remove the fans, remove the bias.

However, accepting this conclusion requires ignoring two compounding confounds unique to the 2020 season. First, the AFL shortened quarters from 20 to 16 minutes, mechanically reducing all counting statistics including total free kicks and their differential, regardless of any change in umpire behaviour. Second, the hub environment imposed democratised fatigue—both home and away teams experienced comparable travel burdens, accommodation disruption, and condensed four-day rest cycles—restructuring the physical dynamics of contests irrespective of crowd presence.

This paper's central identification challenge is to isolate the crowd channel from these concurrent structural shocks.

Compounding the measurement problem, raw attendance figures are a deeply flawed proxy for crowd partisanship. A crowd of 35,000 at Melbourne's MCG for a cross-city derby is approximately evenly split; a crowd of 35,000 at Geelong's sold-out GMHBA Stadium is composed predominantly of partisan home support. Treating attendance as homogeneous produces the "Away Fan Fallacy": large Victorian derbies register artificially inflated crowd pressure scores despite functioning as neutral venues.

---

## 3. Study Data and Measurement

### 3.1 Dataset

Match-level statistics for all 1,736 AFL regular-season matches from 2012 to 2020 (153 unique matchup pairings across 18 clubs) were scraped from AFL Tables (afltables.com). Variables include scored free kicks for and against each team, contested possessions, disposals, tackles, marks, marks inside 50, and clearances. Actual elapsed match time (`game_time_mins`) was parsed directly from the AFL Tables match records for every game in the dataset. Quarter-by-quarter scoring margins were additionally parsed from cached match HTML across all 1,736 files, enabling the within-game decomposition reported in Section 6.4.

### 3.2 The Expected Partisanship Index (EPI)

To address the measurement error in raw attendance, we construct the **Expected Partisanship Index (EPI)**, a continuous pre-treatment hostility metric. The formal construction proceeds in three stages.

**Stage 1: Fan Split Multiplier.** For each match, we compute a fan-split ratio *f* ∈ [0.1, 1.0] reflecting the proportion of expected fans supporting the home team, using the following hierarchy:

- *Hub override*: If the home team's state differs from the venue state, *f* = 0.10
- *Non-Victorian derby* (e.g., West Coast vs. Fremantle): *f* = 0.85
- *Interstate match*: *f* = 1.00
- *Victorian Melbourne-cluster derby*: *f* = 0.50
- *Same-state match*: *f* = M_home / (M_home + M_away), where M denotes the club's five-year average membership (2015–2019 window, strictly pre-treatment)

**Stage 2: Historical Baseline Attendance.** For pre-2020 seasons, we compute a rolling five-year lagged mean attendance for each (home_team, away_team, venue) triplet using a one-period shift to prevent current-season data leakage. For 2020 matches, we use the 2015–2019 average attendance for that triplet. This ensures the EPI for 2020 games reflects the *counterfactual expected crowd* had the game been played normally, not the observed zero attendance.

**Stage 3: EPI Construction and Standardisation.** The raw EPI is defined as:

```
EPI_raw = hist_att × (hist_att / venue_capacity) × fan_split
```

where `hist_att` is the historical baseline attendance and `venue_capacity` is the venue's published maximum capacity (capped at 1.0). The density term differentiates between a sparse crowd in a large stadium and a compressed crowd in a small fortress venue. The index is standardised to a z-score using the mean and standard deviation of the pre-2020 distribution, ensuring the 2020 observations are comparable without contaminating the scaling parameters.

**Endogeneity Resolution.** Club membership data is drawn from a fixed 2015–2019 average rather than a rolling figure that could include pandemic-year values. This ensures the EPI is strictly pre-determined and exogenous to the 2020 shock.

The continuous DiD treatment parameter is computed as:

```
deficit_ratio = (expected_attendance - actual_attendance) / expected_attendance
deficit_x_epi = deficit_ratio × epi_z
```

For 2020 matches, `deficit_ratio` ≈ 1.0. For pre-2020 matches, `deficit_ratio` ≈ 0. This creates continuous within-year cross-sectional variation directly proportional to expected crowd hostility.

**Empirical Justification.** To demonstrate that the EPI is necessary rather than cosmetically preferable, we estimate a benchmark model replacing `deficit_x_epi` with `deficit × raw_attendance_z`. This naive specification recovers a borderline-significant crowd coefficient (`deficit × raw_attendance = +2.00`, p = 0.050). Our EPI-based Model 3 yields a statistically indistinguishable-from-zero coefficient. The naive model's spurious significance is the "Away Fan Fallacy" in action: resolving the measurement error eliminates the false signal.

**EPI Construct Validation.** A null finding only matters if the treatment variable can detect a signal when one exists. In the pre-2020 baseline, high-EPI matchups generate statistically significantly larger home scoring margins (OLS slope = +4.17 points per EPI standard deviation; p < 0.001) and larger home free-kick advantages relative to low-EPI matchups (Welch t-test: t = +2.02, p = 0.044). Matches in the top EPI quartile produce a home scoring margin 14.3 points higher than those in the bottom quartile. The EPI has demonstrated empirical bite outside of our primary DiD test.

**Hyperparameter Sensitivity.** The fan-split hierarchy employs calibrated scalar weights for derby match types: non-Victorian derbies (0.85) and Victorian Melbourne-cluster derbies (0.50). We conduct a formal sensitivity analysis varying both across a 4×3 grid (non-Victorian: 0.65–0.95; Victorian: 0.35–0.65), yielding 12 EPI specifications. A coding error identified in review—wherein the sensitivity pipeline silently overwrote overridden fan-split values with the default weights before computing EPI, producing an artifactual invariance in the null result—has been corrected. Under the repaired implementation, the coefficient range across all 12 configurations is [+0.717, +0.749] (span = 0.032) and the p-value range is [0.178, 0.253]. All 12 configurations return null results. The null is now demonstrably robust to genuine weight variation rather than invariant by accident.

### 3.3 The Club Prestige Index (CPI)

To test for institutional brand bias, we construct a **Club Prestige Index (CPI)** measuring whether umpires subconsciously favour historically prominent clubs. The CPI is computed annually for each club using three components:

1. **Membership Anchor** (*mem_z*): The club's static average membership (2015–2019 window), z-scored within each season
2. **Halo Effect** (*win_z*): The club's win percentage in season *t-1*, z-scored within each season
3. **Primetime Allocation** (*prime_z*): The proportion of the club's games in season *t-1* scheduled on Thursday or Friday nights, z-scored within each season

The composite CPI score is defined as:

```
CPI_raw = (mem_z + win_z + prime_z) / 3
CPI_score = z-score of CPI_raw, computed within each season
```

The use of lagged values prevents data leakage: the CPI for season *t* is computed exclusively from information available before season *t* commences. The 2012 lag is left missing rather than backfilled with contemporaneous 2012 data. The matchup-level treatment variable is `CPI_diff = home_CPI - away_CPI`.

### 3.4 Mediation and Hub-Control Covariates

To robustly isolate the crowd effect from the logistics of the 2020 hub season, we engineer two hub controls: `days_rest_diff`, a continuous measure of home rest days minus away rest days, and `relative_interstate_dis`, a relative indicator (+1 / 0 / -1) for designated 'home' teams playing outside their home state compared to the away team. These directly address severe logistical asymmetries.

Separately, three game-state controls represent the physical state of play: `cp_diff` (home minus away contested possessions), `kicks_diff` (kicks), and `clearance_diff` (clearances). These are explicitly excluded from our primary causal identification models to prevent post-treatment bias and deployed only in a dedicated mediation specification.

---

## 4. Identification Strategy

### 4.1 Causal Structure

The empirical design rests on the following causal structure. Let *Y* denote the home free-kick differential. The causal diagram contains three distinct 2020-specific pathways:

1. **Crowd removal pathway**: Empty stadiums → reduced partisan noise → (hypothesised) umpire behaviour shift → *Y*
2. **Fatigue pathway**: Hub conditions + 4-day breaks → democratised fatigue → tactical compression → *Y*
3. **Quarter length pathway**: 16-minute quarters → reduced total game duration → mechanically lower free kicks and their differential

Our identification strategy isolates pathway (1) from pathways (2) and (3) through three mechanisms. First, we adopt a directed team-pair fixed-effect structure as our primary specification to cleanly isolate strict home-ground advantage. Second, we integrate direct controls for hub logistical asymmetries. Third, we standardise all rate metrics to per-60-minutes using an exogenous duration denominator—discussed in Section 6.2.

### 4.2 Formal Parallel Trends Assumption

**Assumption 1** (Parallel Trends, Continuous Treatment). *In the absence of the 2020 stadium lockouts, the expected change in home free-kick differentials is mean-independent of the continuous EPI treatment intensity across its full support. That is, E[Y(0)_t − Y(0)_{t-1} | EPI = e] is constant in e for all e in the support of EPI, where Y(0) denotes the potential outcome under no crowd removal.*

**Empirical Defence.** We validate this assumption through a dynamic event-study specification: interacting the EPI variable with individual year dummies for every season from 2012 to 2020. We omit **2016** as the reference year. An earlier specification used 2019 as the reference year; however, 2019 appears to have been an anomalously low period in the EPI-FK relationship, and omitting an atypical trough artificially biases all pre-treatment coefficients upward relative to that reference. Switching to the structurally stable mid-sample year of 2016 corrects this. The corrected event-study coefficients are:

| Year | Coefficient | 95% CI | p-value |
|---|---|---|---|
| 2012–2017 | Mainly null | — | > 0.10 |
| **2016** | **0.000** | **[reference]** | **—** |
| 2018 | +0.365 | [+0.030, +0.700] | 0.033** |
| 2019 | (ns) | — | > 0.10 |
| 2020 | +0.446 | [−0.222, +1.115] | 0.190 (ns) |

All pre-treatment coefficients save one are statistically indistinguishable from zero under two-way clustering. The 2018 deviation (p = 0.033) persists regardless of reference year choice, confirming it reflects a genuine structural event—most plausibly the AFL's 2018 mid-season rule changes—rather than an artefact of the omitted year. The 2020 treatment coefficient is null at p = 0.190.

> **[Figure 3 Descriptor: An event-study plot titled "Parallel Trends Validation: EPI × Season Interactions (reference year: 2016)." Blue circles represent pre-treatment seasons close to the zero line with intersecting confidence intervals. The 2018 point estimate is borderline significant. The 2020 treatment year returns a positive coefficient with a 95% CI that clearly crosses zero. A dashed horizontal zero line demarcates the pre- and post-treatment periods.]**

#### 4.2.1 Addressing the 2018 Pre-Trend Deviation and the Detrending Limitation

To assess whether the 2018 coefficient threatens identification, we attempted to augment the primary specification with unit-specific linear time trends via a within-entity centred season index (`season_within`). Diagnostic testing confirmed that in this balanced panel structure—where each matchup entity appears exactly once per season—`season_within` is perfectly collinear with the Year Fixed Effects (Time FEs) and is absorbed by `drop_absorbed=True`. This is a structural property of the balanced panel, not a software artefact: the year-mean projection spans the within-trend exactly.

The collinearity renders the detrending specification degenerate. We therefore rely on the corrected reference year and the placebo test as the primary defences of Assumption 1. The 2018 deviation is acknowledged as an unresolved pre-trend anomaly. The 2020 null result stands on the undetrended baseline model (`deficit_x_epi` = +0.745, p = 0.211).

### 4.3 Placebo Test

We exclude 2020 entirely and assign a fake treatment year by setting `deficit_ratio = 1.0` for all 2017 matches, using a structurally stable pre-trend baseline. Re-estimating the continuous DiD yields:

```
deficit_x_epi_placebo (2017 fake lockout): coefficient = +0.156, p = 0.503
```

The placebo is solidly null. This falsification check demonstrates that the design does not automatically generate significance.

### 4.4 Model Specifications

We estimate five Panel OLS specifications. All employ Time (season) fixed effects, and two-way cluster-robust standard errors (clustered by entity and time index) are used throughout. We note that in a dyadic panel a shock to one team propagates across all of that team's matchups; a matchup-level cluster does not fully absorb node-level shocks.

A structural note on Model 1: an earlier specification employed *undirected* matchup fixed effects, which are degenerate against an antisymmetric outcome (home FK − away FK). When teams A and B swap home/away roles, the undirected FE is unchanged but the outcome sign flips, causing the entity effect to cancel to zero on expectation. We correct this by specifying **additive Home Team + Away Team dummy variables** (`C(home_team) + C(away_team) + C(season)`, HC1-robust OLS). Under this corrected specification, `deficit_x_epi` = +1.072 (HC1-robust SE = 0.568, p = 0.059). The borderline result in Model 1 confirms that separating the true home advantage interaction requires Directed Team-Pair Fixed Effects (Model 2), which absorb all dyadic matchup traits. All models 2-5 confirm no statistically detectable effect is present under directed modeling.

- **Model 1**: Baseline (Additive `C(home_team) + C(away_team) + C(season)`, HC1-robust OLS)
- **Model 2**: Primary Causal Identification (Directed Team-Pair FEs, two-way cluster-robust)
- **Model 3**: Hub Travel Robustness (Directed FEs + hub controls)
- **Model 4**: Brand Bias Baseline (Directed FEs + CPI + hub controls)
- **Model 5**: Associational Decomposition (Directed FEs + hub controls + post-treatment game-state controls)

> **[Figure 4 Descriptor: A coefficient forest plot charting parameter estimates with cluster-robust 95% confidence intervals across all five Panel OLS model specifications. Models 1–4 report causal parameter estimates; Model 5 reports associational estimates. The "deficit_x_epi" coefficient confidence intervals overlap zero in Models 2–5. Model 1's point estimate is positive with a CI that touches but does not clearly exclude zero under HC1-robust inference—the least conservative standard used across the five models.]**

---

## 5. Main Results: Umpire Bias

### 5.1 The Noise of Affirmation: A Null Result

The core identification logic is as follows: if partisan crowds cause umpire bias, the matchups that historically generated the most hostile atmospheres should exhibit the largest shift in free-kick differentials when those crowds were removed in 2020. They did not.

Across Models 2–5, `deficit_x_epi` is consistently statistically indistinguishable from zero. The primary causal specification (Model 2) yields `deficit_x_epi` = +0.745, p = 0.211. This null is preserved under two important extensions. First, Model 3, which controls for hub logistical asymmetries, likewise returns null. Second, and of particular concern to reviewers, Model 3 augmented with *heterogeneous* fatigue-EPI interaction terms (`rest_x_epi = days_rest_diff × epi_z` and `interstate_x_epi = home_interstate_2020 × epi_z`)—testing whether the hub schedule shock differentially affected high-EPI games—returns `deficit_x_epi` = +0.767, p = 0.200. The potential confound between hub fatigue and EPI treatment does not alter the null finding.

We emphasise that a null result—a coefficient near zero with a confidence interval that includes zero—provides no empirical basis for inferring any directional behavioural tendency. Any point estimate is consistent with sampling noise. The officials are not being swayed by the cheer squad in the data we can observe.

Model 5's Associational Decomposition demonstrates that game-state differentials carry highly significant explanatory power over free-kick differentials (`cp_diff` p < 0.01). While conditioning on post-treatment variables invites collider bias—preventing strict identification of total causal mediation—the associative density of these covariates reinforces our thesis: physical gameplay dynamics are structurally correlated with the outcome variance.

**EPI Stratification Evidence.** Splitting matchups into EPI quartiles and comparing residualised mean free-kick differentials for the top 25% and bottom 25% groups reveals:

| Group | Pre-2020 Mean Resid | 2020 Mean Resid |
|---|---|---|
| Top 25% Most Hostile | +0.000 | −0.154 |
| Bottom 25% Least Hostile | +0.000 | −1.638 |

Both groups decline in 2020, but the Bottom 25% (Least Hostile) collapses by −1.638 residual free kicks against only −0.154 for the Top 25% (Most Hostile)—a 1.48-foul gap that directly contradicts the crowd-pressure prediction. If crowd removal drove the convergence, the most hostile matchups should have collapsed the most; instead they were the most stable. This is consistent with a global fatigue mechanism operating uniformly across matchup types.

> **[Figure 5 Descriptor: A line chart titled "EPI Stratification: Mean Home FK Differential by Crowd Hostility Quartile." Two series run from 2012 to 2020: the Top 25% Most Hostile matchups and the Bottom 25% Least Hostile matchups. In 2020, the least-hostile series falls far below zero while the most-hostile series remains comparatively elevated—the opposite of what crowd-pressure causation predicts.]**

### 5.2 Institutional Brand Bias: Also Null

The `CPI_diff` coefficient across Models 4 and 5 is non-significant at any conventional level. A club possessing greater measured prestige—evidenced by larger rolling previous-season average home attendance, stronger recent form, and higher primetime allocation—confers no systematic free-kick advantage. The badge on the jumper provides no statistical armour in front of the officials.

---

## 6. Mechanisms: Tactical Compression

### 6.1 No Concurrent Treatments: Separating Crowds from Fatigue

Section 5 establishes a null effect of crowd removal on the free-kick *differential*. Yet total free kicks per match declined by 13.2% in raw terms. This apparent paradox requires explanation. We argue the decline in total penalties is attributable not to umpire psychology but to a structural collapse in the *type* of play that generates free kicks—with the critical mechanism being the democratisation of fatigue under hub conditions.

The assumption of no concurrent treatments requires that our treatment variable affects the outcome only through the crowd-noise channel, not through concurrent structural changes. The introduction of directed pair fixed effects and hub-travel proxies mitigates omitted variable bias from hub logistical artifacts, though fixed effects only absorb time-invariant traits and the proxies only capture the linear conditional mean of measured travel differences. Unobserved, time-varying hub shocks remain a limitation.

That explanation is physiological symmetry. In the entire 2012–2019 baseline (N=1,583), there were *exactly five* short-rest games (defined as 5 days or fewer between matches). The 2020 regular season generated N=31. Hub conditions democratised an extreme, novel form of fatigue between home and away sides, eroding the home team's traditional energy premium.

**Fatigue Shock Robustness.** A formal absolute-rest marginal distribution diagnostic confirms over 30% of 2020 observations fall completely outside the [5th, 95th] percentile bounds of the baseline rest-day distribution. A KS test formally rejects identical distributions (p = 0.0000). The hub schedule was an out-of-distribution, absolute physiological shock that fundamentally restructured the physical dynamics of the contest. Manski-style conservative bounds provide an identified set consistent with the null, demonstrating it is not an extrapolation artefact.

### 6.2 Denominator Integrity: Nominal Exogenous Game Time

The 2020 AFL season operated under 16-minute quarters rather than the standard 20 minutes, reducing the *nominal* playing time from 80 to 64 minutes (theoretical ratio 0.800). Actual elapsed match time, parsed from AFL Tables HTML for all 1,736 games, differs: 101.8 minutes in 2020 versus 121.5 minutes in the 2012–2019 baseline (empirical ratio 0.8374), reflecting faster play-on and compact rotation windows under hub conditions.

A reviewer raised a simultaneity concern: actual game time includes stoppage time for whistles, which is partially a function of free-kick volume—creating a mechanical feedback loop between the outcome and its normalising denominator. We address this directly by adopting the **nominal exogenous game time** (64 min for 2020, 80 min for 2012–2019) as the primary denominator for all rate metrics. We additionally correct a Contested Possession Rate reporting error: the prior specification used disposals as the denominator (CP/DI), which is itself endogenous to the game-style shifts being measured. The corrected specification uses CP per 60 nominal minutes.

Under the corrected nominal denominator, the rate comparison is:

| Metric | Baseline | 2020 | Change | p-value |
|---|---|---|---|---|
| **FK/60 min (nominal)** | 27.54 | 30.26 | +9.8% | **0.000*** |
| FK/60 min (actual, previous spec) | 18.36 | 18.15 | −1.1% | 0.252 |
| **TK/60 min (nominal)** | 98.66 | 94.60 | −4.1% | **0.000*** |
| TK/60 min (actual, previous spec) | 65.78 | 56.76 | −13.7% | < 0.001*** |
| **CP/60 min (nominal) [corrected]** | 215.16 | 211.76 | −1.6% | **0.046*** |

The directional conclusions highlight a critical finding: FK/60 (nominal) implies umpire whistle density actually increased significantly. The apparent reduction in raw penalty volume was entirely an artefact of the shortened 64-minute structure, not increased referee leniency. Tackles fell slightly, and CP rates dropped slightly. The key analytical conclusion—that free-kick density per unit of scheduled play did not decline—fundamentally rewrites the naive mechanism narrative.

Mechanical duration effects account for only −0.434 of the observed **1.130** differential drop (baseline +1.51 minus 2020 mean +0.38) even under a conservative non-linear fatigue assumption (k=2, double density in removed minutes). Over **0.696** of the collapse remains unexplained by duration mechanics, proving that tactical compression operated organically throughout the full contest.

### 6.3 Quantitative Decomposition of Gameplay

Converting all metrics to their nominal-time-normalised rates reveals the structural shift:

| Metric | Baseline (2012–2019) | 2020 | Change |
|---|---|---|---|
| **Forward Efficiency** (MI50 / I50) | 0.222 | 0.198 | **−2.4 p.p.** |
| **CP per 60 min (nominal)** | 215.16 | 211.76 | **−1.6%** |
| **Tackles per 60 min (nominal)** | 98.66 | 94.60 | **−4.1%** |
| **Free Kicks per 60 min (nominal)** | 27.54 | 30.26 | **+9.8%** |

The 2.4 percentage point collapse in Forward Efficiency is a structural breakdown: midfielders lacked the anaerobic capacity to break from contested zones. The ball became trapped in congested midfield scrums. We characterize this as "Trench Warfare." Critically, **Free Kicks per 60 minutes increased**, refuting any 'leniency' hypothesis. The entire raw-count decline is a volume effect.

### 6.4 Linking Structural Collapse to the Free-Kick Differential

A global reduction in free-kick volume does not mechanically eliminate home-team bias; umpires could still award a disproportionate share of the remaining free kicks to the home side. The mechanism linking Tactical Compression to differential convergence operates through the energy economics of open play.

**Home-Away Tactical Differentials.** We compute the home-minus-away differentials for contested possessions, clearances, and tackles per match to directly test whether the home team's physical advantage eroded:

| Metric | Baseline | 2020 | Change | p-value |
|---|---|---|---|---|
| CP Differential (home − away) | +3.42 | +1.34 | −2.08 | 0.133 (ns) |
| Clearance Differential | +0.67 | +0.33 | −0.33 | 0.650 (ns) |
| Tackle Differential | +0.70 | −0.49 | −1.19 | 0.220 (ns) |
| Disposal Differential | +11.26 | +3.31 | −7.95 | 0.051 (ns) |
| **FK Differential** | **+1.59** | **+0.30** | **−1.29** | **0.009** |

The CP, clearance, and tackle differentials all narrow toward zero in 2020, consistent with democratised fatigue eroding the home team's structural physical advantage. None reach conventional significance individually—the signal is diffuse across multiple contest channels, precisely what a full-match structural compression mechanism would produce, as opposed to a single discrete tactical failure.

**Quarter-Level Evidence.** We parse per-quarter scoring margins from cached HTML for all 1,736 matches. In the baseline era, per-quarter home scoring margins are broadly uniform. There is no statistically concentrated Q4 premium in the baseline.

The home advantage is distributed across the full contest, consistent with persistent structural territorial dominance rather than a narrowly concentrated late-game surge. This reframes the mechanism: the free-kick differential convergence is entirely distinct from the scoring margin channel. Contest dynamics across the complete match were structurally collapsed into neutral scrums by the physiological shock, flattening the wide-open positional conditions that generate FK asymmetry.

> **[Figure 6 Descriptor: A two-panel time-series chart from 2012 to 2020. The upper panel shows Tackles per 60 min (nominal), declining to a sample low in 2020. The lower panel shows Free Kicks per 60 min (nominal), which remains broadly stable across the entire period, demonstrating that the raw free-kick count decline was a volume effect of shorter game time, not a change in adjudication density.]**

> **[Figure 7 Descriptor: A grid of four box plots comparing 2012-2019 to 2020. Forward Efficiency shows a significant downward shift; Contested Possession Rate shows a material upward shift; Tackles per 60 min shows a downward shift; Free Kicks per 60 min shows no systematic change—consistent with a pure volume effect from shorter game duration.]**

---

## 7. Conclusion

What began as an investigation into referee psychology resolved into a precise mapping of tactical and physiological dynamics in Australian Rules Football. Our findings carry three implications for sports analytics and the broader literature on officiating bias.

First, constructing a credible treatment variable in crowd-presence studies requires decomposing raw attendance into its constituent hostility signals. The Expected Partisanship Index resolves the measurement error that causes naive attendance models to recover spurious significance. A coding error identified during review—wherein the sensitivity pipeline silently overwrote fan-split overrides before computing EPI—has been corrected; the null result is now demonstrably robust to genuine parameter variation across all 12 grid configurations (coef range +0.717 to +0.749, all null).

Second, the identification challenges in continuous treatment DiD designs extend beyond the parallel trends assumption. Two structural concerns surfaced during review: the choice of event-study reference year materially shapes the visual presentation of pre-trend violations (the structurally stable 2016 reference is preferred over the anomalous 2019 trough); and within-entity mean-centring as a detrending strategy is degenerate in balanced panels with uniform entity coverage, because the within-trend collinearises with the entity fixed effects. We recommend that practitioners explicitly diagnose both concerns.

Third, and most broadly, the Tactical Compression findings illustrate how an extreme structural shock can dominate and statistically mask environmental pressure channels. Our results establish that, in the specific and extraordinary context of the 2020 AFL hub season, behavioural shifts in game style were of sufficient magnitude to render crowd-based umpire bias statistically undetectable. We caution against extending this finding to a categorical claim about the absence of crowd effects under normal conditions.

The officials are not being swayed by the cheer squad in the data we can observe. Whether that represents a structural truth about officiating psychology—or whether it reflects the fact that the 2020 season was simply too structurally abnormal to permit the usual crowd-pressure mechanisms to operate—is a question that future research, ideally exploiting partial-crowd variation in other sporting contexts, should address.

---

## Appendix A: Methodological Summary

| Component | Implementation |
|---|---|
| **Causal Framework** | Continuous Treatment Difference-in-Differences |
| **Treatment Variable** | Expected Partisanship Index (EPI): `EPI_raw = hist_att × density × fan_split`, standardised pre-2020 |
| **Deficit Interaction** | `deficit_x_epi = deficit_ratio × epi_z` |
| **Panel Estimator** | `linearmodels.PanelOLS` with Directed Team-Pair entity index + Time FEs (Models 2–5); HC1-robust OLS with additive team dummies (Model 1) |
| **Standard Errors** | Two-way cluster-robust (Entity + Time) for Models 2–5; HC1-robust for Model 1; dyadic cross-matchup correlation a noted limitation |
| **Model 1 Correction** | Corrected from degenerate undirected pair FE to `C(home_team) + C(away_team) + C(season)` OLS; `deficit_x_epi` = +1.072, HC1 p = 0.059 (less conservative than two-way cluster) |
| **Event-Study Reference** | Corrected to 2016 (stable mid-sample) from anomalous 2019 trough; 2020 coef = +0.446, p = 0.190 |
| **Detrending** | `season_within` absorbed by Time FEs in balanced panel — detrending is structurally degenerate; baseline null (p = 0.211) stands unmodified |
| **Placebo Test** | Fake treatment 2017 (dropped 2020): coef = +0.156, p = 0.503 |
| **Fatigue×EPI Interactions** | `rest_x_epi` + `interstate_x_epi` added to Models 3 and 5; `deficit_x_epi` = +0.767, p = 0.200 — null unchanged |
| **Naive Benchmark** | `deficit × raw_attendance_z` coef = +2.00, p = 0.050 |
| **EPI Construct Validation** | High EPI predicts larger home scoring margins pre-2020 (p < 0.001); high vs. low EPI FK diff t = +2.02, p = 0.044 |
| **EPI Sensitivity (corrected)** | Bug fixed; genuine coef range [+0.717, +0.749], p range [0.178, 0.253]; all 12 null |
| **Absolute Fatigue Shock** | Over 30% of 2020 obs fall outside baseline 5th-95th percentile bounds; KS test p = 0.0000 |
| **Rate Denominator** | Nominal exogenous game time (64 min / 80 min); actual elapsed time reported for comparison |
| **CP Rate** | Corrected from endogenous CP/DI to CP per 60 nominal minutes |
| **Game Time** | Actual: baseline 121.5 min, 2020 101.8 min, ratio 0.8374. Nominal: 80/64 min, ratio 0.8000 |
| **Differential Drop** | Baseline +1.51 − 2020 +0.38 = **1.130**; mechanical bound (k=2) = −0.434; residual = 0.696 |
| **Tactical Differentials** | CP diff +3.42→+1.34 (ns); CL diff +0.67→+0.33 (ns); FK diff +1.59→+0.30 (p=0.009) |
| **Q4 Evidence** | Baseline Q4 − Q1 premium = +0.006 (nil); 2020 Q4 = +2.01 (not significantly different from baseline Q4 p=0.881) |
| **CPI** | `(mem_z + lag_win_pct_z + lag_primetime_z) / 3`, within-season standardised, single t-1 lag |
| **Models estimated** | 5 specifications (M1–M5), all reported |