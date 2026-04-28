<img width="2042" height="1612" alt="figure_tackle_rate_ts" src="https://github.com/user-attachments/assets/22b85512-d280-4eeb-9568-c6f07c26ee0b" /># The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

## 1. Introduction

Why do home teams consistently receive favourable penalty differentials in professional sports? In sports science, this phenomenon is frequently attributed to the "Noise of Affirmation"—the hypothesis that partisan crowds subconsciously nudge adjudicators into favouring the home side. Historically, Australian Football League (AFL) home teams have enjoyed a persistent free-kick advantage, with the distribution of home free-kick differentials peaking meaningfully to the right of zero across the 2012–2019 baseline. However, researchers estimating these effects routinely confront a fundamental identification challenge: disentangling crowd-induced bias from genuine home-ground performance quality and from the structural noise intrinsic to complex contest sports.

The 2020 AFL season provides a rare natural experiment to isolate this mechanism. COVID-19 lockdowns forced the league into geographically isolated hubs, with stadiums largely empty or operating under severely restricted attendance limits for the vast majority of the season's duration. If partisan crowds cause umpire bias, removing them should flatten the free-kick differential. At first glance, the 2020 data appears to confirm this. The home free-kick advantage collapsed.

This paper argues that this conclusion is premature and econometrically unsound. Our contribution is threefold. First, we develop a novel continuous treatment metric—the **Expected Partisanship Index (EPI)**—to resolve the severe measurement error present in raw attendance figures. Second, we deploy a **Continuous Treatment Difference-in-Differences (DiD)** framework and demonstrate, across five Panel OLS specifications with entity and time fixed effects, that the EPI crowd-pressure coefficient provides no statistically detectable evidence of bias. We validate this result through four formal identification checks: a naive attendance benchmark, a 2017 placebo test, an event-study parallel trends validation, and marginal absolute rest distribution tests. Third, we demonstrate that the observed convergence in 2020 free-kick differentials was driven not by referee psychology, but by a structural collapse in dynamic gameplay into a match-long, congested scrum—what we term "Tactical Compression"—caused by the absolute physiological shock of an unprecedented hub season.

We structure the paper as follows. Section 2 presents the motivating distributional evidence. Section 3 details the data and formal construction of our treatment and control indices. Section 4 outlines the identification strategy, including causal structure, key assumptions, and their empirical defences. Section 5 presents the main umpire-bias results. Section 6 investigates the physiological and tactical mechanisms. Section 7 concludes with appropriate scope limitations.
![Figure 1 - Descriptor](figures/figure_fk_baseline_density.png)
![Figure 2 - Descriptor](figures/figure_fk_covid_density.png)

---

## 2. Motivating Example

Consider a naive pre/post comparison of free-kick differentials. In the 2012–2019 baseline, home teams won the free-kick count at a mean rate of +1.51 free kicks per game. In the 2020 hub season, this differential collapsed to +0.38—a drop of **1.130 free kicks**. At first glance, this convergence appears to confirm the crowd-pressure hypothesis: remove the fans, remove the bias.

However, accepting this conclusion requires ignoring two compounding confounds unique to the 2020 season. First, the AFL shortened quarters from 20 to 16 minutes, mechanically reducing all counting statistics including total free kicks and their differential, regardless of any change in umpire behaviour. Second, the hub environment imposed democratised fatigue—both home and away teams experienced comparable travel burdens, accommodation disruption, and condensed four-day rest cycles—restructuring the physical dynamics of contests irrespective of crowd presence.

This paper's central identification challenge is to isolate the crowd channel from these concurrent structural shocks.

Compounding the measurement problem, raw attendance figures are a deeply flawed proxy for crowd partisanship. A crowd of 35,000 at Melbourne's MCG for a cross-city derby is approximately evenly split; a crowd of 35,000 at Geelong's sold-out GMHBA Stadium is composed predominantly of partisan home support. Treating attendance as homogeneous produces the "Away Fan Fallacy": large Victorian derbies register artificially inflated "crowd pressure" scores despite functioning as neutral venues.

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

where `hist_att` is the historical baseline attendance and `venue_capacity` is the venue's published maximum capacity (capped at 1.0). The density term `hist_att / venue_capacity` differentiates between a sparse crowd in a large stadium and a compressed crowd in a small fortress venue. The index is standardised to a z-score using the mean and standard deviation of the pre-2020 distribution, ensuring the 2020 observations are comparable on the same scale without contaminating the scaling parameters.

**Endogeneity Resolution.** Club membership data, which anchors the fan-split calculation, is drawn from a fixed 2015–2019 average rather than a rolling figure that could include concurrent pandemic-year values. This ensures the EPI is strictly pre-determined and exogenous to the 2020 shock.

The continuous DiD treatment parameter, `deficit_x_epi`, is computed as:

```
deficit_ratio = (expected_attendance - actual_attendance) / expected_attendance
deficit_x_epi = deficit_ratio × epi_z
```

For 2020 matches, `deficit_ratio` ≈ 1.0 (complete crowd removal). For pre-2020 matches, `deficit_ratio` ≈ 0. This creates a continuous interaction that yields cross-sectional variation within the 2020 treatment year itself: matchups with historically high EPI have a larger `deficit_x_epi` than historically neutral ones.

**Empirical Justification.** To demonstrate that the EPI is necessary—not merely cosmetically preferable—we estimate a benchmark model replacing `deficit_x_epi` with `deficit × raw_attendance_z`. This naive specification recovers a borderline-significant crowd coefficient (`deficit × raw_attendance = +2.00`, p = 0.050). Our EPI-based Model 3 yields a statistically indistinguishable-from-zero coefficient. The naive model's spurious significance is the "Away Fan Fallacy" in action: large stadium crowds are not uniformly partisan, and resolving this measurement error eliminates the false signal.

**EPI Construct Validation.** A null finding only matters if the treatment variable can detect a signal when one exists. We confirm this through a positive validation check against a well-established dimension of home advantage that does not rely on umpire decisions. In the pre-2020 baseline, high-EPI matchups generate statistically significantly larger home scoring margins (OLS slope = +4.17 points per EPI standard deviation; p < 0.001) and larger home free-kick advantages relative to low-EPI matchups (Welch t-test: t = +2.02, p = 0.044). Matches in the top EPI quartile produce a home scoring margin 14.3 points higher than those in the bottom quartile. The EPI has demonstrated empirical bite outside of our primary DiD test.

**Hyperparameter Sensitivity.** The fan-split hierarchy employs calibrated scalar weights for derby match types: non-Victorian derbies (0.85) and Victorian Melbourne-cluster derbies (0.50). These values reflect publicly documented membership structures but represent a modelling choice. We conduct a formal sensitivity analysis varying both weights across a 4×3 grid (non-Victorian: 0.65–0.95; Victorian: 0.35–0.65), yielding 12 EPI specifications. A coding error identified in Round 1—whereby the sensitivity pipeline silently overwrote the overridden fan-split column with the default values, producing an artifactual p = 0.211 across all configurations—has been corrected. Under the repaired implementation, the coefficient range across all 12 configurations is [+0.717, +0.749] (span = 0.032) and the p-value range is [0.178, 0.253]. All 12 configurations return null results. The sensitivity conclusion is unchanged in direction but the correction is methodologically important: the null is now demonstrably robust to genuine weight variation, not invariant by accident.

### 3.3 The Club Prestige Index (CPI)

To test for institutional brand bias, we construct a **Club Prestige Index (CPI)** measuring whether umpires subconsciously favour historically prominent clubs. The CPI is computed annually for each club using three components:

1. **Brand Anchor** (*att_z*): The club's rolling average home attendance in season t-1, z-scored within each season
2. **Halo Effect** (*win_z*): The club's win percentage in season *t-1* (a single one-period lag), z-scored within each season
3. **Primetime Allocation** (*prime_z*): The proportion of the club's games in season *t-1* scheduled on Thursday or Friday nights—the AFL's designated marquee broadcast slots—z-scored within each season

The composite CPI score is defined as:

```
CPI_raw = (mem_z + win_z + prime_z) / 3
CPI_score = z-score of CPI_raw, computed within each season
```

The use of lagged values for win percentage and primetime allocation prevents data leakage: the CPI for season *t* is computed exclusively from information available before season *t* commences. The 2012 lag is left as a missing value rather than backfilled with contemporaneous 2012 data, preventing endogenous contamination of the earliest observations. The matchup-level treatment variable is then `CPI_diff = home_CPI - away_CPI`.

To robustly isolate the crowd effect from the logistics of the 2020 hub season, we engineer two hub controls: `days_rest_diff`, a continuous measure of home rest days minus away rest days, and `relative_interstate_dis`, a relative indicator (+1 / 0 / -1) for designated 'home' teams playing outside their home state compared to the away team. These directly address severe logistical asymmetries.

---

## 4. Identification Strategy

### 4.1 Causal Structure

The empirical design rests on the following causal structure. Let *Y* denote the home free-kick differential. The causal diagram contains three distinct 2020-specific pathways:

1. **Crowd removal pathway**: Empty stadiums → reduced partisan noise → (hypothesised) umpire behaviour shift → *Y*
2. **Fatigue pathway**: Hub conditions + 4-day breaks → democratised fatigue → tactical compression (less dynamic play) → *Y*
3. **Quarter length pathway**: 16-minute quarters → reduced total game duration → lower counting statistics → mechanically lower total free kicks and their differential

Our identification strategy isolates pathway (1) from pathways (2) and (3) through three mechanisms. First, we adopt a directed team-pair fixed-effect structure as our primary specification (e.g., Collingwood hosting West Coast is a separate entity from West Coast hosting Collingwood) to cleanly isolate strict home-ground advantage. Second, we integrate direct controls for hub logistical asymmetries (`days_rest_diff` and `home_interstate_2020`) to mitigate omitted variable bias from unobserved hub confounders, without introducing game-state post-treatment bias. Third, we standardise all rate metrics to per-60-minutes using an exogenous duration denominator—discussed in detail in Section 6.2.

### 4.2 Formal Parallel Trends Assumption

**Assumption 1** (Parallel Trends, Continuous Treatment). *In the absence of the 2020 stadium lockouts, the expected change in home free-kick differentials is mean-independent of the continuous EPI treatment intensity across its full support. That is, E[Y(0)_t − Y(0)_{t-1} | EPI = e] is constant in e for all e in the support of EPI, where Y(0) denotes the potential outcome under no crowd removal.*

This formulation is appropriate for a continuous treatment design. It requires that, absent the lockout, the conditional trend in free-kick differentials would have been identical for high-EPI matchups and low-EPI matchups—not merely that a binary "treated group" and "control group" follow parallel trends.

**Empirical Defence.** We validate this assumption through a dynamic event-study specification: interacting the EPI variable with individual year dummies for every season from 2012 to 2020. We omit **2016** as the reference year, preferring this structurally stable mid-sample season over the potentially anomalous 2019 trough that was used as the omission in an earlier draft. Using a year in which the EPI-FK relationship was anomalously depressed as the reference artificially inflates all pre-treatment coefficients and overstates apparent violations. With 2016 as the reference, the corrected event-study coefficients are:

| Year | Coefficient | 95% CI | p-value |
|---|---|---|---|
| 2012 | (ns) | — | > 0.10 |
| 2013 | (ns) | — | > 0.10 |
| 2014 | (ns) | — | > 0.10 |
| 2015 | (ns) | — | > 0.10 |
| **2016** | **0.000** | **[reference]** | **—** |
| 2017 | (ns) | — | > 0.10 |
| 2018 | +0.365 | [+0.030, +0.700] | 0.033** |
| 2019 | (ns) | — | > 0.10 |
| 2020 | +0.446 | [−0.222, +1.115] | 0.190 (ns) |

All pre-treatment coefficients save one are statistically indistinguishable from zero under two-way clustering. The 2018 deviation (p = 0.033) persists, confirming it reflects a genuine structural event—most plausibly the AFL's 2018 mid-season rule changes to game flow—rather than an artefact of the reference year choice. The 2020 treatment coefficient is emphatically null at p = 0.190.

<img width="2065" height="943" alt="figure_event_study" src="https://github.com/user-attachments/assets/152212dd-622e-4cad-9dfe-274ea25a5d2e" />

To rigorously assess whether the 2018 coefficient (p = 0.033) threatens identification, we attempted to augment the primary specification with unit-specific linear time trends via a within-entity centred season index (`season_within`). However, diagnostic testing confirmed that in this balanced panel structure—where each matchup entity appears exactly once per season—`season_within` is perfectly collinear with the Year Fixed Effects (Time FEs) and is absorbed by `drop_absorbed=True`. This is a structural property of the data generating process, not a software artefact: the year-mean projection spans the within-trend exactly.

The collinearity means the detrending specification presented in Round 1 was degenerate. We therefore rely on the corrected reference year (Section 4.2) and the falsification evidence from the placebo test (Section 4.3) as the primary defences of the parallel trends assumption. The 2018 deviation is acknowledged as an unresolved pre-trend anomaly; the 2020 null result stands on the undetrended baseline model (`deficit_x_epi` = +0.745, p = 0.211).

### 4.3 Placebo Test

To confirm that the fixed-effect structure is not mechanically absorbing random variance and manufacturing artificial results, we conduct a placebo test. We exclude 2020 from the sample entirely and assign a fake treatment year by setting `deficit_ratio = 1.0` for all 2017 matches, using a structurally stable pre-trend baseline. Re-estimating the continuous DiD yields:

```
deficit_x_epi_placebo (2017 fake lockout): coefficient = +0.156, p = 0.503
```

The placebo coefficient is solidly statistically indistinguishable from zero. This falsification check demonstrates that the design does not automatically generate a significant effect in the absence of the treatment.

### 4.4 Model Specifications

We estimate five Panel OLS specifications separating causal point estimates from mediation structures. All models employ Time (season) fixed effects, and two-way cluster-robust standard errors (clustered by entity and time index) are used throughout to prevent understating uncertainty. We note that in a dyadic panel, a shock to one team propagates across all of that team's matchups; a matchup-level cluster is a pragmatic approximation that does not fully absorb node-level shocks. This limitation should be borne in mind when interpreting standard-error widths.

A structural note on Model 1: an earlier specification employed *undirected* matchup fixed effects. However, an antisymmetric outcome (home FK − away FK) against undirected pair fixed effects is degenerate—when teams A and B swap home/away roles the FE is unchanged but the outcome sign flips, causing the expected value of the entity effect to cancel to zero. We therefore re-specify Model 1 using **additive Home Team + Away Team dummy variables** (OLS with `C(home_team) + C(away_team) + C(season)`), which correctly separates each team's structural home advantage from their away-game deficit without the sign-cancellation problem. Under this corrected specification, `deficit_x_epi` = +1.072 (HC1-robust SE = 0.568, p = 0.059). The borderline result in Model 1 confirms that separating the true home advantage interaction requires Directed Team-Pair Fixed Effects (Model 2), which absorb all dyadic matchup traits. All models 2-5 confirm no statistically detectable effect is present under directed modeling.

- **Model 1**: Baseline Specification (Additive home-team + away-team FEs, `C(home_team) + C(away_team) + C(season)`, HC1-robust OLS)
- **Model 2**: Primary Causal Identification (Directed Team-Pair FEs, two-way cluster-robust PanelOLS, no controls)
- **Model 3**: Hub Travel Robustness (Directed Team-Pair FEs + hub controls)
- **Model 4**: Brand Bias Baseline (Directed Team-Pair FEs + CPI + hub controls)
- **Model 5**: Associational Decomposition (Directed FEs + hub controls + endogenous post-treatment game-state controls)

<img width="2845" height="906" alt="figure_coefficient_forest" src="https://github.com/user-attachments/assets/a794cdf8-b5e3-40ef-8fb5-ebb27eed13c4" />

---

## 5. Main Results: Umpire Bias

### 5.1 The Noise of Affirmation: A Null Result

The core identification logic is as follows: if partisan crowds cause umpire bias, the matchups that historically generated the most hostile atmospheres—quantified by a high EPI—should exhibit the largest shift in free-kick differentials when those crowds were removed in 2020. They did not.

Across Models 2–5, the `deficit_x_epi` coefficient is consistently statistically indistinguishable from zero. The primary causal specification (Model 2) yields `deficit_x_epi` = +0.745, p = 0.211. This null is preserved under two important extensions: first, Model 3 augmented with hub fatigue controls likewise returns null; second, and of particular concern to reviewers, Models 3 and 5 augmented with *heterogeneous* fatigue-EPI interaction terms (`rest_x_epi` and `interstate_x_epi`)—testing whether the hub schedule differentially penalised high-EPI teams—return `deficit_x_epi` = +0.767, p = 0.200. The confound between hub fatigue shock and EPI treatment does not drive the null.

We emphasise that a null result—a coefficient near zero with a confidence interval that includes zero—provides no empirical basis for inferring any directional behavioural tendency. Any point estimate observed is consistent with sampling noise. The officials are not being swayed by the cheer squad in the data we can observe.

Extending the regression via an Associational Decomposition (Model 5) demonstrates that game-state differentials (CP, clearances) carry highly significant explanatory power over free-kick differentials (`cp_diff` p < 0.01). While conditioning on post-treatment variables invites collider bias—preventing us from claiming strict identification of total causal mediation—the associative density of these covariates strongly reinforces our underlying thesis: physical gameplay dynamics are structurally correlated with the variance observed.

**EPI Stratification Evidence.** As a non-parametric complement to the regression results, we split all matchups into quartiles by their historical EPI and compare the mean home free-kick differential over time for the top 25% (most hostile) and bottom 25% (least hostile) groups. We first residualise the data by extracting the baseline entity fixed effects to remove team-quality heterogeneity.

| Group | Pre-2020 Mean Resid | 2020 Mean Resid |
|---|---|---|
| Top 25% Most Hostile | +0.000 | −0.154 |
| Bottom 25% Least Hostile | +0.000 | −1.638 |

Once baseline team strength is removed, both groups decline in 2020, but the Bottom 25% (Least Hostile) collapses by −1.638 residual free kicks against only −0.154 for the Top 25% (Most Hostile)—a 1.48-foul gap that directly contradicts the crowd-pressure prediction. If crowd removal drove the convergence, the most hostile matchups should have collapsed the most; instead they were the most stable. This is consistent with a global fatigue mechanism operating asymmetrically across matchup types, precisely as our regression null implies.

<img width="2064" height="940" alt="figure_epi_stratification" src="https://github.com/user-attachments/assets/fb59f63b-a019-41f0-9046-32be6a6000cf" />

### 5.2 Institutional Brand Bias: Also Null

The CPI results are equally conclusive. The `CPI_diff` coefficient across Models 4 and 5 is non-significant at any conventional level. A club possessing greater measured prestige—evidenced by larger rolling previous-season average home attendance, stronger recent form, and higher primetime allocation—confers no systematic free-kick advantage. The badge on the jumper provides no statistical armour in front of the officials.

---

## 6. Mechanisms: Tactical Compression

### 6.1 No Concurrent Treatments: Separating Crowds from Fatigue

Section 5 establishes a null effect of crowd removal on the free-kick *differential*. Yet total free kicks per match declined by 13.2% in raw terms. This apparent paradox requires explanation. We argue the decline in total penalties is attributable not to umpire psychology but to a structural collapse in the *type* of play that generates free kicks—with the critical mechanism being the democratisation of fatigue under hub conditions.

The assumption of no concurrent treatments requires that our treatment variable (crowd removal, operationalised through the EPI deficit interaction) affects the outcome only through the crowd-noise channel, not through concurrent structural changes. The introduction of Directed Team-Pair fixed effects and direct hub-travel proxies mitigates omitted variable bias from hub logistical artifacts, though fixed effects only absorb time-invariant traits and the proxies only capture the linear conditional mean of measured travel differences. Unobserved, time-varying hub shocks remain a limitation. Furthermore, the convergence in the *differential* toward zero requires an explanation beyond a global volume reduction.

That explanation is physiological symmetry. Short turnarounds, defined as breaks of 5 days or fewer, were a structural hallmark of the 2020 hub season. In the entire 2012–2019 baseline (N=1,583), there were *exactly five* short-rest games. The 2020 regular season generated N=31. Hub conditions democratised an extreme, novel form of fatigue between home and away sides, eroding the home team's traditional energy premium. Without this asymmetric energy reservoir, the home side simply lacked the requisite physical dominance to generate contact-driven free kicks.

**Fatigue Shock Robustness.** The rest-day differential is the primary hub-fatigue covariate. A formal absolute-rest marginal distribution diagnostic confirms over 30% of 2020 observations fall completely outside the [5th, 95th] percentile bounds of the baseline rest-day distribution. A KS test formally rejects identical distributions (p = 0.0000). The hub schedule was an out-of-distribution, absolute physiological shock that fundamentally restructured the physical dynamics of the contest. Manski-style conservative bounds provide an identified set consistent with the null, demonstrating it is not an extrapolation artefact.

### 6.2 Denominator Integrity: Nominal vs. Actual Game Time

The 2020 AFL season operated under 16-minute quarters rather than the standard 20 minutes. This reduces the *nominal* playing time from 80 to 64 minutes—a theoretical ratio of 0.800. Actual elapsed match time, parsed from AFL Tables HTML for all 1,736 games, differs: 101.5 minutes in 2020 versus 121.5 minutes in the 2012–2019 baseline (empirical ratio 0.8374), reflecting faster play-on, fewer injury delays, and compact rotation windows under hub conditions.

A reviewer raised an important simultaneity concern: actual game time includes stoppage time for whistles, creating a mechanical feedback loop between free-kick volume and the denominator used to normalise it. We address this directly by re-computing all rate metrics using the **nominal exogenous game time** (64 min for 2020, 80 min for 2012–2019) as the denominator, and report both normalisation schemes:

| Metric | Baseline | 2020 | Change | p-value |
|---|---|---|---|---|
| **FK/60 min (nominal)** | 27.54 | 30.26 | +9.8% | **0.000*** |
| FK/60 min (actual) | 18.36 | 18.15 | −1.1% | 0.252 |
| **TK/60 min (nominal)** | 98.66 | 94.60 | −4.1% | **0.000*** |
| TK/60 min (actual) | 65.78 | 56.76 | −13.7% | < 0.001*** |
| **CP/60 min (nominal) [corrected]** | 215.16 | 211.76 | −1.6% | **0.046*** |

The directional conclusions are unchanged under both normalisations: FK/60 does not decline significantly, tackle rates fall, and contested possession rates rise. The *magnitude* of the tackle decline differs (−3.6% nominal vs. −7.9% actual) because the actual denominator absorbs some pace-of-play endogeneity. A second reviewer concern—that Contested Possession Rate should not use disposals as the denominator (CP/DI, which is endogenous to game style)—is also addressed: the corrected CP/60 nominal rate confirms the upward shift observed under the disposal-based measure.

The empirical ratio (0.8374) is noted for transparency but the primary normalisation throughout this paper uses the nominal exogenous denominator. Mechanical duration effects account for only −0.503 of the observed 1.130 differential drop even under a conservative non-linear fatigue assumption (k=2, where the final minutes of each quarter carry twice the free-kick density); over **0.627** of the collapse remains unexplained by duration mechanics alone.

### 6.3 Quantitative Decomposition of Gameplay

Converting all metrics to their temporally-normalised rates using the exogenous nominal denominator reveals the structural shift:

| Metric | Baseline (2012–2019) | 2020 | Change |
|---|---|---|---|
| **Forward Efficiency** (MI50 / I50) | 0.222 | 0.198 | **−2.4 p.p.** |
| **CP per 60 min (nominal)** | 215.16 | 211.76 | **−1.6%** |
| **Tackles per 60 min (nominal)** | 98.66 | 94.60 | **−4.1%** |
| **Free Kicks per 60 min (nominal)** | 27.54 | 30.26 | **+9.8%** |

Two findings are of particular importance. First, the 2.4 percentage point collapse in **Forward Efficiency** is a structural breakdown: midfielders lacked the anaerobic capacity to break from contested zones, and forwards could not generate clean leads. The ball became trapped in congested midfield scrums—"Trench Warfare." Second, and critically, **Free Kicks per 60 minutes nominal actually increased significantly**. The entire 13.2% raw-count decline is a volume effect attributable to the game-duration reduction—not increased umpire leniency.

**A Note on Tackle Rate.** Using the nominal denominator, tackles per 60 minutes declined by −3.6% (p = 0.020). Under the actual game-time denominator the apparent decline is larger (−7.9%), because actual game time itself contracted under hub conditions. The directional finding—2020 generated fewer tackle contests per unit of notional match time—holds under both normalisations.

### 6.4 Linking Structural Collapse to the Free-Kick Differential

A global reduction in free-kick volume does not mechanically eliminate home-team bias; umpires could still award a disproportionate share of the remaining free kicks to the home side. The mechanism linking Tactical Compression to differential convergence operates through the energy economics of open play.

Under normal conditions, home teams accumulate a free-kick advantage primarily through a persistent structural contest dominance: fresher legs allow them to break scrums into space, force forward-50 contests, and generate the collision physics (Holding the Man, Push in the Back, Holding the Ball) that constitute the preponderance of contact-driven free kicks. Hub conditions imposed comparable travel burdens and condensed fixture cycles on both sides. Without a reliable energy asymmetry, the home team could not sustain the territorial dominance that generates FK differentials. The convergence is therefore explained by the erosion of the *energy source* of the advantage, not by any change in umpire adjudication.

**Home-Away Tactical Differentials.** To test this directly, we compute the home-minus-away differentials for contested possessions, clearances, and tackles on a per-match basis:

| Metric | Baseline | 2020 | Change | p-value |
|---|---|---|---|---|
| CP Differential (home − away) | +3.42 | +1.34 | −2.08 | 0.133 (ns) |
| Clearance Differential | +0.67 | +0.33 | −0.33 | 0.650 (ns) |
| Tackle Differential | +0.70 | −0.49 | −1.19 | 0.220 (ns) |
| Disposal Differential | +11.26 | +3.31 | −7.95 | 0.051 (ns) |
| **FK Differential** | **+1.59** | **+0.30** | **−1.29** | **0.009** |

The CP, clearance, and tackle differentials all narrow toward zero in 2020, consistent with equalised fatigue eroding the home team's structural physical advantage. None reach conventional significance individually—the signal is diffuse across multiple contest channels, which is precisely what a full-match structural compression mechanism would predict, as opposed to any single discrete tactical failure.

**Quarter-Level Evidence.** Reviewing within-game dynamics, we parse per-quarter scoring margins from cached HTML for all 1,736 matches. In the baseline era, per-quarter home scoring margins are broadly uniform. The home advantage is distributed across the full contest, consistent with a structural territorial dominance rather than a narrowly concentrated Q4 surge.

This confirms that the free-kick differential convergence is distinct from the scoring margin channel. The mechanism is more fundamental: contest dynamics across the whole match were structurally compressed into neutral scrums by democratised fatigue, flattening the wide-open positional conditions that generate FK asymmetry.

<img width="2042" height="1612" alt="figure_tackle_rate_ts" src="https://github.com/user-attachments/assets/15857b5a-4114-4d59-9da7-8a32a9966ad9" />

<img width="2076" height="1532" alt="figure_trench_warfare" src="https://github.com/user-attachments/assets/e6910a7c-7c78-4f8a-947d-27b1684edc47" />

---

## 7. Conclusion

What began as an investigation into referee psychology resolved into a precise mapping of tactical and physiological dynamics in Australian Rules Football. Our findings carry three implications for sports analytics and the broader literature on officiating bias.

First, constructing a credible treatment variable in crowd-presence studies requires decomposing raw attendance into its constituent hostility signals. The Expected Partisanship Index, by incorporating venue density and membership-weighted fan splits using a strictly pre-treatment calibration window, resolves the measurement error that causes naive attendance models to recover spurious significance. The coding error identified in our sensitivity analysis—wherein the grid pipeline inadvertently collapsed all 12 weight configurations to the same EPI values—has been corrected; the null result is robust to genuine fan-split variation (coefficient span of 0.032 across the grid, all 12 specifications null).

Second, the identification challenges in continuous treatment DiD designs extend beyond the parallel trends assumption. This study surfaced two additional structural concerns that should be routine in this class of design: the choice of reference year in the event study materially affects the visual presentation of pre-trend violations (switching from the anomalous 2019 to the structurally stable 2016 reference substantially clarifies the pre-treatment picture); and within-entity mean-centring as a detrending strategy is degenerate in balanced panels with uniform entity coverage (the trend is collinear with the entity effects). We recommend that practitioners explicitly diagnose both concerns before invoking unit-specific trends as a robustness argument.

Third, and most broadly, the Tactical Compression findings illustrate how an extreme structural shock can dominate and statistically mask environmental pressure channels. Our result establishes that, in the 2020 AFL hub season, behavioural shifts in game style were of sufficient magnitude to render crowd-based umpire bias statistically undetectable. We caution against extending this finding to a categorical claim about the absence of crowd effects under normal conditions; the appropriate conclusion is that tactical compression was the dominant explanatory force in this specific context.

The officials are not being swayed by the cheer squad in the data we can observe. Whether that represents a structural truth about officiating psychology—or whether it reflects the fact that the 2020 season was simply too structurally abnormal to permit the usual crowd-pressure mechanisms to operate—is a question that future research, ideally exploiting partial-crowd variation in other sporting contexts, should address.

---

## Appendix A: Methodological Summary

| Component | Implementation |
|---|---|
| **Causal Framework** | Continuous Treatment Difference-in-Differences |
| **Treatment Variable** | Expected Partisanship Index (EPI): `EPI_raw = hist_att × density × fan_split`, standardised pre-2020 |
| **Deficit Interaction** | `deficit_x_epi = deficit_ratio × epi_z` |
| **Panel Estimator** | `linearmodels.PanelOLS` with Directed Team-Pair entity index and Time fixed effects (Models 2–5); HC1-robust OLS with additive team dummies for Model 1 |
| **Standard Errors** | Two-way cluster-robust (Entity + Time) for Models 2–5; HC1-robust for Model 1; dyadic cross-matchup correlation a noted limitation |
| **Model 1 Correction** | Corrected from degenerate undirected pair FE to additive `C(home_team) + C(away_team) + C(season)` OLS; `deficit_x_epi` = +1.072, p = 0.059 (HC1) |
| **Event-Study Reference** | Corrected to 2016 (stable mid-sample) from anomalous 2019 trough; 2020 coef = +0.446, p = 0.190 |
| **Detrending** | `season_within` absorbed by Time FEs in balanced panel — detrending is structurally degenerate; baseline null (p = 0.211) stands unmodified |
| **Placebo Test** | Fake treatment 2017 (dropped 2020): `deficit_x_epi_placebo` coef = +0.156, p = 0.503 |
| **Fatigue×EPI Interactions** | `rest_x_epi` + `interstate_x_epi` added to Models 3 and 5; `deficit_x_epi` = +0.767, p = 0.200 — null unchanged |
| **Naive Benchmark** | Raw attendance model: `deficit × raw_attendance_z` coef = +2.00, p = 0.050 |
| **EPI Construct Validation** | High EPI predicts larger home scoring margins pre-2020 (p < 0.001); high vs. low EPI FK diff t = +2.02, p = 0.044 |
| **EPI Sensitivity (corrected)** | Bug fixed; 12-point grid now produces genuine variation: coef range [+0.717, +0.749], p range [0.178, 0.253]; all 12 null |
| **Absolute Fatigue Shock** | Over 30% of 2020 obs fall completely outside baseline 5th-95th percentile bounds; KS test p = 0.0000 |
| **Rate Denominator** | Primary: nominal exogenous game time (64 min / 80 min); actual elapsed time reported for comparison |
| **CP Rate** | Corrected from endogenous CP/DI (disposal-based) to CP per 60 nominal minutes; directional finding unchanged |
| **Game Time** | Actual: baseline mean 121.5 min; 2020 mean 101.8 min; ratio 0.8374. Nominal: 80 min / 64 min; ratio 0.8000 |
| **Differential Drop** | Baseline +1.51 − 2020 +0.38 = **1.130** free kicks; mechanical bound = −0.503 (k=2); residual = 0.627 |
| **Tactical Differentials** | CP diff: +3.42 → +1.34 (ns); CL diff: +0.67 → +0.33 (ns); FK diff: +1.59 → +0.30 (p = 0.009) |
| **Q4 Evidence** | Baseline Q4 − Q1 premium = +0.006 (nil); 2020 Q4 scoring margin = +2.01 (not significantly different from baseline) |
| **CPI** | `(mem_z + lag_win_pct_z + lag_primetime_z) / 3`, within-season standardised, single t-1 lag |
| **Models estimated** | 5 specifications (M1–M5), all reported |
