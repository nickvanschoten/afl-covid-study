# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

## 1. Introduction

Why do home teams consistently receive favourable penalty differentials in professional sports? In sports science, this phenomenon is frequently attributed to the "Noise of Affirmation"—the hypothesis that partisan crowds subconsciously nudge adjudicators into favouring the home side. Historically, Australian Football League (AFL) home teams have enjoyed a persistent free-kick advantage, with the distribution of home free-kick differentials peaking meaningfully to the right of zero across the 2012–2019 baseline. However, researchers estimating these effects routinely confront a fundamental identification challenge: disentangling crowd-induced bias from genuine home-ground performance quality and from the structural noise intrinsic to complex contest sports.

The 2020 AFL season provides a rare natural experiment to isolate this mechanism. COVID-19 lockdowns forced the league into geographically isolated hubs, rendering stadiums entirely empty for the season's duration. If partisan crowds cause umpire bias, removing them should flatten the free-kick differential. At first glance, the 2020 data appears to confirm this. The home free-kick advantage collapsed.

This paper argues that this conclusion is premature and econometrically unsound. Our contribution is threefold. First, we develop a novel continuous treatment metric—the **Expected Partisanship Index (EPI)**—to resolve the severe measurement error present in raw attendance figures. Second, we deploy a **Continuous Treatment Difference-in-Differences (DiD)** framework and demonstrate, across five Panel OLS specifications with entity and time fixed effects, that the EPI crowd-pressure coefficient is statistically indistinguishable from zero. We further validate this null result through three formal identification checks: a naive attendance benchmark demonstrating the endogeneity of raw figures, a placebo test assigning a fake treatment year, and an event-study plot confirming the parallel trends assumption holds across all seven pre-treatment seasons. Third, we demonstrate that the observed convergence in 2020 free-kick differentials was driven not by referee psychology, but by a structural collapse in dynamic gameplay—what we term "Tactical Compression"—caused by the democratised fatigue of an unprecedented hub season played on shortened quarters and four-day breaks.

We structure the paper as follows. Section 2 presents the motivating distributional evidence. Section 3 details the data and formal construction of our treatment and control indices. Section 4 outlines the identification strategy, including causal structure, key assumptions, and their empirical defences. Section 5 presents the main umpire-bias results. Section 6 investigates the physiological and tactical mechanisms. Section 7 concludes with appropriate scope limitations.

> **[Figure 1 Descriptor: A density plot titled "2012-2019 Baseline: Home Free Kick Differential Distribution". The distribution forms a right-skewed bell curve centred near +1.51, indicating a persistent historical free-kick advantage for the home team.]**

> **[Figure 2 Descriptor: A density plot titled "The Convergence: Baseline vs. 2020 Free Kick Differential Distributions". Two overlapping distributions are shown: the blue 2012–2019 baseline (mean = +1.51) and the pink 2020 hub season (mean = +0.38). The 2020 distribution has shifted materially leftward, consistent with a convergence toward zero differential.]**

---

## 2. Motivating Example

Consider a naive pre/post comparison of free-kick differentials. In the 2012–2019 baseline, home teams won the free-kick count at a mean rate of +1.51 free kicks per game. In the 2020 hub season, this differential collapsed to +0.38. At first glance, this convergence appears to confirm the crowd-pressure hypothesis: remove the fans, remove the bias.

However, accepting this conclusion requires ignoring two compounding confounds unique to the 2020 season. First, the AFL shortened quarters from 20 to 16 minutes, mechanically reducing all counting statistics including total free kicks, regardless of any change in umpire behaviour. Second, the hub environment imposed democratised fatigue—both home and away teams experienced identical travel burdens, accommodation disruption, and four-day rest cycles—restructuring the physical dynamics of contests irrespective of crowd presence.

This paper's central identification challenge is to isolate the crowd channel from these concurrent structural shocks.

Compounding the measurement problem, raw attendance figures are a deeply flawed proxy for crowd partisanship. A crowd of 35,000 at Melbourne's MCG for a cross-city derby is approximately evenly split; a crowd of 35,000 at Geelong's sold-out GMHBA Stadium is composed predominantly of partisan home support. Treating attendance as homogeneous produces the "Away Fan Fallacy": large Victorian derbies register artificially inflated "crowd pressure" scores despite functioning as neutral venues.

---

## 3. Study Data and Measurement

### 3.1 Dataset

Match-level statistics for all 1,736 AFL regular-season contest from 2012 to 2020 (153 clubs × matchup × season observations) were scraped from AFL Tables (afltables.com). Variables include scored free kicks for and against each team, contested possessions, disposals, tackles, marks, marks inside 50, and clearances. Actual elapsed match time (`game_time_mins`) was parsed directly from the AFL Tables match records for every game in the dataset.

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

where `hist_att` is the historical baseline attendance and `venue_capacity` is the venue's published maximum capacity (capped at 1.0). The density term `hist_att / venue_capacity` differentiates between a sparse crowd in a large stadium and a compressed crowd in a small fortress venue. The index is then standardised to a z-score using the mean and standard deviation of the pre-2020 distribution, ensuring the 2020 observations are comparable on the same scale without contaminating the scaling parameters.

**Endogeneity Resolution.** Club membership data, which anchors the fan-split calculation, is drawn from a fixed 2015–2019 average rather than a rolling figure that could include concurrent pandemic-year values. This ensures the EPI is strictly pre-determined and exogenous to the 2020 shock.

The continuous DiD treatment parameter, `deficit_x_epi`, is computed as:

```
deficit_ratio = (expected_attendance - actual_attendance) / expected_attendance
deficit_x_epi = deficit_ratio × epi_z
```

For 2020 matches, `deficit_ratio` ≈ 1.0 (complete crowd removal). For pre-2020 matches, `deficit_ratio` ≈ 0. This creates a continuous interaction that yields cross-sectional variation within the 2020 treatment year itself: matchups with historically high EPI have a larger `deficit_x_epi` than historically neutral ones.

**Empirical Justification.** To demonstrate that the EPI is necessary—not merely cosmetically preferable—we estimate a benchmark model replacing `deficit_x_epi` with `deficit × raw_attendance_z`. This naive specification recovers a borderline-significant crowd coefficient (`deficit × raw_attendance = +2.00`, p = 0.050). Our EPI-based Model 3 yields a statistically indistinguishable-from-zero coefficient. The naive model's spurious significance is the "Away Fan Fallacy" in action: large stadium crowds are not uniformly partisan, and controlling for this measurement error eliminates the false signal.

### 3.3 The Club Prestige Index (CPI)

To test for institutional brand bias, we construct a **Club Prestige Index (CPI)** measuring whether umpires subconsciously favour historically prominent clubs. The CPI is computed annually for each club using three components:

1. **Membership Anchor** (*mem_z*): The club's static average membership (2015–2019 window), z-scored within each season
2. **Halo Effect** (*win_z*): The club's win percentage in season *t-1* (a single one-period lag), z-scored within each season
3. **Primetime Allocation** (*prime_z*): The proportion of the club's games in season *t-1* scheduled on Thursday or Friday nights—the AFL's designated marquee broadcast slots—z-scored within each season

The composite CPI score is defined as:

```
CPI_raw = (mem_z + win_z + prime_z) / 3
CPI_score = z-score of CPI_raw, computed within each season
```

The use of lagged values for win percentage and primetime allocation prevents data leakage: the CPI for season *t* is computed exclusively from information available before season *t* commences. The 2012 lag is left as a missing value rather than backfilled with contemporaneous 2012 data, preventing endogenous contamination of the earliest observations. The matchup-level treatment variable is then `CPI_diff = home_CPI - away_CPI`.

### 3.4 Game-State Controls

Following the panel construction, we include three time-varying match-level controls to absorb the physical state of play: `cp_diff` (home minus away contested possessions), `kicks_diff` (home minus away kicks), and `clearance_diff` (home minus away clearances). These controls capture the territory and ball-control asymmetry that genuinely determines free-kick receipt, preventing the crowd coefficient from absorbing variation driven by physical dominance.

---

## 4. Identification Strategy

### 4.1 Causal Structure

The empirical design rests on the following causal structure. Let *Y* denote the home free-kick differential. The causal diagram contains three distinct 2020-specific pathways:

1. **Crowd removal pathway**: Empty stadiums → reduced partisan noise → (hypothesised) umpire behaviour shift → *Y*
2. **Fatigue pathway**: Hub conditions + 4-day breaks → democratised fatigue → tactical compression (less dynamic play) → *Y*
3. **Quarter length pathway**: 16-minute quarters → reduced total game duration → lower counting statistics → mechanically lower total free kicks (but not necessarily differential)

Our identification strategy isolates pathway (1) from pathways (2) and (3) through two mechanisms. First, game-state controls (CP differential, clearances, kicks) directly absorb the tactical signature of pathway (2). Second, the continuous EPI interaction exploits *within-2020* cross-sectional heterogeneity: if crowds drive the differential, the games that historically produced the most partisan atmospheres should show the largest EPI-weighted drop. Finding instead that both high-EPI and low-EPI matchups converge indistinguishably is evidence against pathway (1). Third, for pathway (3), we standardise all rate metrics to per-60-minutes using actual elapsed game time—an exogenous, rule-set denominator—rather than per-disposal rates, which are endogenous to the very game-style shifts we are measuring.

### 4.2 Formal Parallel Trends Assumption

**Assumption 1** (Parallel Trends, Continuous Treatment). *In the absence of the 2020 stadium lockouts, the expected change in home free-kick differentials is mean-independent of the continuous EPI treatment intensity across its full support. That is, E[Y(0)_t − Y(0)_{t-1} | EPI = e] is constant in e for all e in the support of EPI, where Y(0) denotes the potential outcome under no crowd removal.*

This formulation is appropriate for a continuous treatment design. It requires that, absent the lockout, the conditional trend in free-kick differentials would have been identical for high-EPI matchups and low-EPI matchups—not merely that a binary "treated group" and "control group" follow parallel trends.

**Empirical Defence.** We validate this assumption through a dynamic event-study specification. We interact the EPI variable with individual year dummies for every season from 2012 to 2020, omitting 2019 as the reference year. The resulting EPI × Year coefficients for the seven pre-treatment seasons are:

| Year | Coefficient | 95% CI | p-value |
|---|---|---|---|
| 2012 | −0.282 | [−1.961, +1.398] | 0.742 |
| 2013 | −0.384 | [−1.980, +1.212] | 0.637 |
| 2014 | −0.204 | [−1.535, +1.127] | 0.763 |
| 2015 | −0.155 | [−1.452, +1.141] | 0.814 |
| 2016 | −0.376 | [−1.639, +0.887] | 0.559 |
| 2017 | −0.380 | [−1.807, +1.048] | 0.602 |
| 2018 | +0.181 | [−1.179, +1.540] | 0.794 |
| **2019** | **0.000** | **[reference]** | **—** |
| 2020 | +0.542 | [−0.807, +1.890] | 0.431 |

Every pre-treatment coefficient is statistically indistinguishable from zero at any conventional significance level. The confidence intervals uniformly straddle zero with no systematic drift. This provides strong empirical support for Assumption 1: the EPI does not differentially co-move with the free-kick differential in the years prior to the lockout shock.

> **[Figure 3 Descriptor: An event-study plot titled "Parallel Trends Validation: EPI × Season Interactions (reference year: 2019)." Blue circles represent pre-treatment seasons 2012–2018, a grey square marks the 2019 reference at zero, and a red diamond marks the 2020 treatment year. All pre-treatment points cluster tightly around zero with overlapping 95% cluster-robust confidence intervals. A dashed horizontal zero line and vertical boundary markers at ±0.5 seasons around 2019 demarcate the pre- and post-treatment periods.]**

### 4.3 Placebo Test

To confirm that the fixed-effect structure is not mechanically absorbing random variance and manufacturing artificial results, we conduct a placebo test. We exclude 2020 from the sample and assign a fake treatment year by setting `deficit_ratio = 1.0` for all 2018 matches. Re-estimating the primary continuous DiD on this altered panel yields:

```
deficit_x_epi (PLACEBO 2018): coefficient = +0.344, p = 0.526
```

The placebo coefficient is statistically indistinguishable from zero. The entity and time fixed effects do not manufacture significance in the absence of a genuine treatment. This rules out the possibility that our empirical design is prone to false positives.

### 4.4 Model Specifications

We estimate five Panel OLS specifications via `linearmodels.PanelOLS` with entity (matchup) and time (season) fixed effects, using standard errors clustered at the matchup level throughout.

- **Model 1**: Base binary DiD (covid_season indicator only)
- **Model 2**: Continuous EPI DiD (deficit_ratio + epi_z + deficit_x_epi)
- **Model 3**: Continuous EPI DiD + game-state controls (cp_diff, kicks_diff, clearance_diff)
- **Model 4**: Brand Bias baseline (CPI_diff as primary regressor)
- **Model 5**: Full specification (EPI continuous DiD + CPI_diff + game-state controls)

> **[Figure 4 Descriptor: A coefficient forest plot charting the key causal parameter estimates with cluster-robust 95% confidence intervals across all five Panel OLS model specifications. The "deficit_x_epi" coefficient for Models 2, 3, and 5 and the "CPI_diff" coefficient for Models 4 and 5 each sit at or extremely close to the zero line, with confidence intervals clearly overlapping zero in every specification.]**

---

## 5. Main Results: Umpire Bias

### 5.1 The Noise of Affirmation: A Null Result

The core identification logic is as follows: if partisan crowds cause umpire bias, the matchups that historically generated the most hostile atmospheres—quantified by a high EPI—should exhibit the largest shift in free-kick differentials when those crowds were removed in 2020. They did not.

Across all five Panel OLS specifications, the `deficit_x_epi` coefficient is statistically indistinguishable from zero. The crowd-pressure coefficient does not attain significance at the 10% level in any specification, including Model 3 with full game-state controls. Cluster-robust 95% confidence intervals confirm that partisanship, as measured by the EPI, exerts no detectable causal influence on the home free-kick differential.

We emphasise that a null result—a coefficient near zero with a confidence interval that includes zero—provides no empirical basis for inferring any directional behavioural tendency. Any point estimate observed is consistent with sampling noise. We make no claims about umpire psychology beyond the finding that our data cannot detect a statistically significant crowd effect.

**EPI Stratification Evidence.** As a non-parametric complement to the regression results, we split all matchups into quartiles by their historical EPI and compare the mean home free-kick differential over time for the top 25% (most hostile) and bottom 25% (least hostile) groups:

| Group | 2019 Mean FK Diff | 2020 Mean FK Diff | Delta |
|---|---|---|---|
| Top 25% Most Hostile | +1.417 | +2.966 | **+1.549** |
| Bottom 25% Least Hostile | +0.440 | −0.710 | **−1.150** |

If crowd noise drove umpire bias, the high-EPI group should have exhibited the sharpest collapse in 2020 when their historically hostile crowds were removed. Instead, the low-EPI neutral matchups showed the steeper convergence toward zero differential, while the high-EPI matchups actually increased their FK differential. This stratification provides a transparent, non-model-dependent replication of the regression null result.

> **[Figure 5 Descriptor: A line chart titled "EPI Stratification: Mean Home FK Differential by Crowd Hostility Quartile." Two series are shown from 2012 to 2020: the Top 25% Most Hostile matchups (plotted in red/pink) and the Bottom 25% Least Hostile matchups (plotted in blue). Both series track positive FK differentials through the baseline period, with the high-EPI group consistently higher. In 2020, the low-EPI series falls below zero while the high-EPI series remains elevated, contradicting the crowd-pressure prediction. A shaded yellow band demarcates the 2020 season.]**

### 5.2 Institutional Brand Bias: Also Null

The CPI results are equally conclusive. The `CPI_diff` coefficient across Models 4 and 5 is approximately +0.166 (p ≈ 0.28), non-significant at any conventional level. A club possessing greater measured prestige—larger memberships, stronger recent form, higher primetime allocation—confers no systematic free-kick advantage. The badge on the jumper provides no statistical armour in front of the officials.

---

## 6. Mechanisms: Tactical Compression

### 6.1 The Exclusion Restriction: Separating Crowds from Fatigue

Section 5 establishes a null effect of crowd removal on the free-kick *differential*. Yet total free kicks per match declined by 13.2% in raw terms. This apparent paradox requires explanation. We argue the decline in total penalties is attributable not to umpire psychology but to a structural collapse in the *type* of play that generates free kicks—with the critical mechanism being the democratisation of fatigue under hub conditions.

The exclusion restriction requires that our treatment variable (crowd removal, operationalised through the EPI deficit interaction) affects the outcome only through the crowd-noise channel, not through concurrent structural changes. We address this in two ways. First, our game-state controls (contested possessions, clearances, kicks) are time-varying covariates that directly capture the tactical signature of the fatigue channel; controlling for them absorbs the mechanical correlation between schedule compression and the free-kick differential. Second, we note that the fatigue channel predicts a symmetric reduction in *both* home and away free kicks, which would lower the total count without mechanically altering the differential. The observed convergence in the *differential* toward zero therefore requires an additional explanation beyond simple volume compression—and our results show the crowd channel is not that explanation.

The remaining explanation for differential convergence is physiological symmetry: hub conditions equalised the fatigue burden between home and away sides, eroding the home team's traditional fourth-quarter energy advantage that historically allowed them to break contests into space and generate contact-driven free kicks through superior athleticism in the final term.

### 6.2 Denominator Integrity: Per-60-Minute Normalisation

The 2020 AFL season operated under 16-minute quarters rather than the standard 20 minutes. This reduces the nominal playing time from 80 to 64 minutes—a theoretical ratio of 0.800. However, actual elapsed match time, parsed directly from the AFL Tables match records for all 1,736 games in our dataset, reveals a more precise empirical ratio. The average actual match duration was 101.5 minutes in 2020 versus 122.0 minutes in the 2012–2019 baseline, yielding an empirical ratio of **0.8374**. This 3.7-percentage-point deviation from the nominal constant reflects real behavioural differences under hub conditions (faster play-on, reduced interchange rotation delays, fewer injury stoppages), and using it rather than a nominal constant is strictly more defensible.

We therefore normalise all counting metrics to **per-60-minutes** rates using actual `game_time_mins` as the denominator—an exogenous variable set by AFL rules, not by team tactics. This eliminates the endogeneity present in per-disposal rates, where the denominator itself is a product of the game-style shifts we are measuring.

### 6.3 Quantitative Decomposition of Gameplay

Converting all metrics to their temporally-normalised rates reveals the true structural shift:

| Metric | Baseline (2012–2019) | 2020 | Change | p-value |
|---|---|---|---|---|
| **Forward Efficiency** (MI50 / Total I50) | 22.6% | 20.5% | **−9.2%** | < 0.0001 |
| **Contested Possession Rate** (CP / DI) | 38.4% | 39.9% | **+3.8%** | < 0.0001 |
| **Tackles per 60 min** | 64.6 | 59.5 | **−7.9%** | < 0.0001 |
| **Free Kicks per 60 min (Dynamic proxy)** | 18.95 | 19.32 | +1.9% | 0.319 (ns) |
| **Free Kicks per 60 min (Static proxy)** | 17.78 | 18.45 | +3.8% | 0.260 (ns) |

Two findings from this table are of particular importance. First, the collapse in **Forward Efficiency** (−9.2%) is a structural breakdown: midfielders lacked the anaerobic capacity to break from contested zones, and forwards could not generate clean leads. The ball became trapped in congested midfield scrums—"Trench Warfare." Second, and critically, **Free Kicks per 60 minutes did not decline significantly** in either the dynamic or static proxy category. When normalised to actual game time, the free-kick rate was stable. The entire 13.2% raw-count decline is a volume effect attributable to the 20-minute reduction in match duration—not to a change in how umpires applied their adjudication standards.

**A Note on Tackle Rate Reconciliation.** An earlier draft described the Tackle Rate as "dropping 4.1%" while a figure note described it as "ticking up slightly in 2020." This discrepancy arose from using a disposal-based denominator (TK/DI), which is endogenous to the same style shifts being measured. Using the exogenous per-60-minutes denominator, tackles per 60 minutes declined by **7.9% (p < 0.0001)** from a mean of 64.6 to 59.5. The apparent "tick up" in an earlier figure reflects only the 2019-to-2020 single-year increment: 2019 was the all-time sample low for tackling intensity (61.2 TK/60min), and 2020 (59.5 TK/60min) sits approximately 5 tackles per 60 minutes below the full baseline mean. There is no contradiction: the year-over-year trend from 2019 to 2020 is marginally positive, but 2020 remains the second-lowest tackling season in the sample and well below the baseline mean on the appropriate exogenous metric.

### 6.4 Linking Structural Collapse to the Free-Kick Differential

It is important to distinguish between the decline in *total* free kicks and the convergence of the *home-away differential*. A global reduction in free-kick volume does not mechanically eliminate home-team bias; umpires could still award a disproportionate share of the remaining free kicks to the home side.

The mechanism linking Tactical Compression to differential convergence operates through the spatial and energy economics of open play. Under normal conditions, home teams accumulate a free-kick advantage primarily through a fourth-quarter energy premium: fresher legs allow them to break contests into space, force more forward-50 contests, and generate the forward-moving collision physics (Holding the Man, Push in the Back, Holding the Ball) that constitute the preponderance of contact-driven free kicks. Hub conditions democratised fatigue: both sides were equally travel-burdened, sleep-disrupted, and four-day-rested. Without an energy asymmetry, the home team could not sustain the fourth-quarter territorial dominance that structurally generates FK differentials. The convergence is therefore explained by the erosion of the *energy source* of the advantage, not by any change in umpire adjudication.

> **[Figure 6 Descriptor: A two-panel time-series chart from 2012 to 2020. The upper panel shows Tackles per 60 min, peaking in 2016 at 69.1 before declining to 59.5 in 2020. The lower panel shows Free Kicks per 60 min, which remains broadly stable across the entire 2012–2020 period, demonstrating that the raw free-kick count decline was a volume effect of shorter game time, not a change in adjudication density.]**

> **[Figure 7 Descriptor: A grid of four box plots comparing the 2012-2019 baseline to the 2020 season. The panels display: (1) Forward Efficiency (MI50 / I50), showing a significant downward shift in its median in 2020; (2) Contested Possession Rate, showing a material upward shift in 2020; (3) Tackles per 60 min, showing a material downward shift; and (4) Free Kicks per 60 min, showing no systematic change in its median between the two periods.]**

---

## 7. Conclusion

What began as an investigation into referee psychology resolved into a precise mapping of tactical and physiological dynamics in Australian Rules Football. Our findings carry three implications for sports analytics and the broader literature on officiating bias.

First, constructing a credible treatment variable in crowd-presence studies requires decomposing raw attendance into its constituent hostility signals. The raw attendance figure conflates stadium capacity, fan allegiance proportions, and historical draw patterns. The Expected Partisanship Index, by incorporating venue density and membership-weighted fan splits using a strictly pre-treatment calibration window, eliminates the measurement error that causes naive attendance models to recover spurious significance.

Second, the parallel trends assumption in continuous treatment DiD designs must be stated in its appropriate form: the expected change in untreated potential outcomes must be mean-independent of the full continuous treatment dosage, not merely constant across a binary group split. Our event-study validation confirms this continuous-form assumption holds across all seven pre-treatment seasons, with no detectable pre-trend drift in the EPI–free-kick differential relationship.

Third, and most broadly, the Tactical Compression findings illustrate how an extreme structural shock can dominate and statistically mask environmental pressure channels that may well operate under normal conditions. Our results establish that, in the specific and extraordinary context of the 2020 AFL hub season, behavioural shifts in game style were of sufficient magnitude to render any crowd-based umpire bias statistically undetectable. We caution against extending this finding to a categorical claim about the absence of crowd effects under normal operating conditions; the appropriate conclusion is that tactical compression, in this instance, was the dominant explanatory force.

The officials are not being swayed by the cheer squad in the data we can observe. Whether that represents a structural truth about officiating psychology—or whether it reflects the fact that the 2020 season was simply too structurally abnormal to permit the usual crowd-pressure mechanisms to operate—is a question that future research, ideally exploiting partial-crowd variation in other sporting contexts, should address.

---

## Appendix A: Methodological Summary

| Component | Implementation |
|---|---|
| **Causal Framework** | Continuous Treatment Difference-in-Differences |
| **Treatment Variable** | Expected Partisanship Index (EPI): `EPI_raw = hist_att × density × fan_split`, standardised pre-2020 |
| **Deficit Interaction** | `deficit_x_epi = deficit_ratio × epi_z` |
| **Panel Estimator** | `linearmodels.PanelOLS` with entity (matchup) and time (season) fixed effects |
| **Standard Errors** | Clustered at the matchup level |
| **Parallel Trends Validation** | Event-study: EPI × Year dummies, 2019 reference, all pre-treatment p > 0.55 |
| **Placebo Test** | Fake treatment 2018: `deficit_x_epi_placebo` coef = +0.344, p = 0.526 |
| **Naive Benchmark** | Raw attendance model: `deficit × att_z` coef = +2.00, p = 0.050 |
| **Rate Denominator** | Actual elapsed game time (`game_time_mins`), per-60-minutes normalisation |
| **Game Time** | 2012–2019 mean = 122.0 min; 2020 mean = 101.5 min; empirical ratio = 0.8374 |
| **CPI** | `(mem_z + lag_win_pct_z + lag_primetime_z) / 3`, within-season standardised, single t-1 lag |
| **Models estimated** | 5 Panel OLS specifications (M1–M5), all reported |