# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

**Date**: 04/26/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper provides an empirical analysis of umpire bias using the 2020 AFL season's COVID-19 lockout as a natural experiment. It introduces the Expected Partisanship Index to isolate crowd pressure from tactical changes.

The paper presents a clever natural experiment to isolate crowd pressure from umpire bias. The construction of the Expected Partisanship Index is a useful methodological contribution for sports econometrics. However, the causal identification fails due to an unresolved structural pre-trend violation and severe confounding between the continuous treatment metric and the concurrent fatigue shock.

**Linear detrending fails to resolve the 2018 pre-trend violation**

Section 4.2.1 attempts to fix a significant 2018 pre-trend deviation (p=0.026) by adding unit-specific linear time trends. The deviation persists. The authors wave this away as a one-off structural event like a rule change. This reasoning is flawed. Linear detrending only fixes continuous drift. It does nothing to resolve a discrete asymmetric shock. If a 2018 rule change affected high-EPI and low-EPI matchups differently, the parallel trends assumption fails. The baseline counterfactual is compromised. You must show this shock does not carry forward into 2020. Drop 2018 from the panel to see if the pre-trends hold, or explicitly model the 2018 rule changes to prove they are orthogonal to the EPI treatment.

**Confounding between the fatigue shock and the continuous EPI treatment**

The paper tries to isolate the crowd lockout from the democratised fatigue of the hub season. Yet Section 5.1 shows a massive divergence. The lowest-EPI quartile dropped by -1.638 in 2020, while the highest-EPI quartile only fell by -0.154. You correctly note this contradicts the crowd hypothesis. But it also creates a fatal identification problem. This divergence means the hub fatigue shock hit low-EPI and high-EPI matchups differently. If the secondary shock has heterogeneous effects across the treatment distribution, the continuous DiD estimate is confounded. The EPI variable is absorbing the asymmetric impact of the hub logistics. You need to interact your hub proxies (`days_rest_diff`, `home_interstate_2020`) directly with baseline EPI to strip this out, or restrict the estimation to a subsample where the fatigue shock was empirically symmetric.

**Endogenous time normalization biases the game-play rates**

Section 6.2 normalizes free kicks to a per-60-minute rate using actual elapsed match time. This choice introduces clear endogeneity. The clock in the AFL stops for whistles and major stoppages. The elapsed time is mechanically determined by the number of free kicks awarded. Dividing the free kick count by a duration that shrinks or grows based on that exact count introduces simultaneity bias. You acknowledge that this metric absorbs game-style variation, but you use it anyway to argue that free kick rates remained stable in Section 6.3. Swap this out for the strictly exogenous nominal playing time ratio (80 minutes vs 64 minutes). Rerun the rate calculations to confirm whether the finding of stable penalty density survives an exogenous denominator.

**Omitted home-away differentials for tactical game-state metrics**

The paper claims the convergence in the free-kick differential stems from a collapse in the home team's physical dominance due to democratized fatigue. While Section 6.3 documents league-wide shifts in gameplay like reduced forward efficiency and lower tackle rates, it never reports whether the home-away differential in these metrics actually vanished. A global reduction in tackles does not automatically mean the home team lost its relative physical advantage. This omission leaves the tactical compression argument incomplete. To prove that fatigue erased the home side's territorial dominance, the manuscript must show the physical advantage disappearing. Compute the pre-2020 to 2020 shift in the mean home-away differential for contested possessions and clearances. Verify that the baseline physical asymmetry collapsed in tandem with the penalty advantage.

**Missing concrete calculations for novel partisanship indices**

The manuscript introduces the Expected Partisanship Index (EPI) and Club Prestige Index (CPI) to resolve measurement errors, but it never computes these metrics for identifiable real-world cases. The text contrasts a large Melbourne derby with a Geelong home game to illustrate the 'Away Fan Fallacy'. Yet it fails to supply the actual EPI values for these specific matchups. Readers will wonder if the proposed formulas produce empirically sensible rankings. A novel theoretical index needs a concrete demonstration to prove the formula achieves the desired re-weighting. Calculate and display the EPI for a few standard matchup types, such as a prominent Victorian derby and an interstate fortress game. Present the top and bottom clubs on the CPI to help readers calibrate their intuitions about the prestige metric.

**Missing 2020 data in quarter-level scoring analysis**

Section 6.4 uses quarter-level scoring margins to argue that the home team enjoyed a persistent structural dominance throughout the match during the baseline era. The authors supply the mean per-quarter margins for 2012-2019 to disprove the idea of a late-game energy surge. Oddly, the text never reports the corresponding quarter-level margins for the 2020 hub season. A natural question is whether this structural dominance actually disappeared during the treatment year, as the fatigue mechanism implies. Presenting the baseline data without the treatment data makes the empirical test half-finished. Compute and report the mean per-quarter home scoring margins for 2020 alongside the baseline figures. Confirm that these within-quarter advantages flattened toward zero to validate the proposed energy erosion mechanism.

**Recommendation**: major revision

**Key revision targets**:

1. Demonstrate that the 2018 structural shock does not compromise the 2020 counterfactual by dropping 2018 from the sample and re-estimating the event study.
2. Control for the heterogeneous impact of hub fatigue across the EPI distribution by interacting the hub logistical proxies with the baseline EPI.
3. Replace the endogenous elapsed-time denominator with the exogenous nominal time ratio for all rate normalizations in Section 6.

**Status**: [Pending]

---

## Detailed Comments (21)

### 1. Collinearity invalidates the linear detrending check

**Status**: [Pending]

**Quote**:
> We construct a within-entity centred season index (`season_within`) for each matchup-directed pair and include it alongside standard entity and time fixed effects.
> 
> The detrended Model 2 yields `deficit_x_epi` = +0.745, p = 0.211—numerically identical to the undetrended estimate—on 1,736 observations.

**Feedback**:
The identical parameter estimates flag a technical implementation error. Adding a single unit-centred season index to a model that already specifies exhaustive entity and time fixed effects causes perfect multicollinearity. The fixed effects absorb both the unit means and the aggregate linear trend. The estimation software therefore drops the collinear vector without warning, returning the original unmodified model. A valid robustness check requires interacting the season index with the individual entity dummy variables to estimate separate slopes.

---

### 2. Inconsistent denominator for rates

**Status**: [Pending]

**Quote**:
> This discrepancy arose from using a disposal-based denominator (TK/DI), which is endogenous to the same style shifts being measured. Using the exogenous per-60-minutes denominator, tackles per 60 minutes declined by **7.9% (p < 0.0001)** from a mean of 64.6 to 59.5.

**Feedback**:
The manuscript correctly identifies that disposal-based denominators are endogenous to tactical shifts. However, the preceding table evaluates the Contested Possession Rate using this exact ratio (CP / DI). This internal contradiction compromises the empirical findings. If total disposals shifted during the hub season, the disposal-scaled metric suffers from the exact bias you identify for tackle rates. The 3.8% increase in contested possessions per disposal may merely reflect a drop in uncontested disposals rather than a structural increase in contested play. Calculate and present an exogenous, per-60-minutes rate for Contested Possessions.

---

### 3. Incorrect mechanism for duration ratio

**Status**: [Pending]

**Quote**:
> This 3.2-percentage-point deviation from the nominal constant reflects real behavioural differences under hub conditions (faster play-on, reduced interchange rotation delays, fewer injury stoppages).

**Feedback**:
The listed behavioural mechanisms conflict with the observed direction of the game time ratio. The empirical ratio (0.8320) exceeds the nominal ratio (0.800), meaning the 2020 matches shrank less than expected. This indicates that games contained a proportionally higher share of stoppage time relative to live play. The mechanisms you list—faster play and fewer delays—would reduce stoppage time and drive the empirical ratio below 0.800. Readers will notice this arithmetic contradiction. Reevaluate the tactical mechanisms driving the extended relative durations, such as fatigue-induced delays or prolonged ball-ups.

---

### 4. Improbable invariant p-value in grid search

**Status**: [Pending]

**Quote**:
> | **EPI Sensitivity** | 12-point fan-split grid (non-VIC 0.65–0.95 × VIC-derby 0.35–0.65): null result invariant (p = 0.211 throughout) |

**Feedback**:
Reporting a p-value of exactly 0.211 across all 12 points of the sensitivity grid strongly points to a coding error. Because the fan split acts as a multiplicative weight in the EPI formula, altering it changes the variance of the treatment variable. This change in variance propagates through the standardizations and interaction terms, altering the standard errors of the regression estimator. Finding mathematically identical p-values across a sensitivity grid suggests the estimation loop failed to update the underlying parameter. Verify the simulation code and report the actual range of test statistics.

---

### 5. Data leakage in Membership Anchor

**Status**: [Pending]

**Quote**:
> The use of lagged values for win percentage and primetime allocation prevents data leakage: the CPI for season *t* is computed exclusively from information available before season *t* commences. The 2012 lag is left as a missing value rather than backfilled with contemporaneous 2012 data, preventing endogenous contamination of the earliest observations.

**Feedback**:
The text asserts that the CPI relies exclusively on strictly prior data. This conflicts with the definition of the membership anchor component. By deriving the membership metric from a static 2015–2019 window, the index for baseline years like 2012 incorporates future information. This introduces the precise forward-looking data leakage the design claims to avoid. Clarify that while the form and scheduling parameters are properly lagged, the membership anchor relies on subsequent data for the earliest seasons in the panel.

---

### 6. Mischaracterization of kicks as physical state

**Status**: [Pending]

**Quote**:
> Separately, we construct three game-state controls to represent the physical state of play: `cp_diff` (home minus away contested possessions), `kicks_diff` (kicks), and `clearance_diff` (clearances).

**Feedback**:
Kicks represent a fundamental method of ball distribution rather than a measure of physical collision or contest density. Using a kick differential to capture physical play conflicts with the paper's central argument regarding tactical compression. Section 6.3 relies heavily on reduced tackle rates to demonstrate physical collapse. Swap the kick differential for a tackle differential to ensure your covariates align with the stated physiological mechanisms.

---

### 7. Time-invariant FEs cannot isolate concurrent pathways

**Status**: [Pending]

**Quote**:
> Our identification strategy isolates pathway (1) from pathways (2) and (3) through three mechanisms. First, we adopt a directed team-pair fixed-effect structure as our primary specification (e.g., Collingwood hosting West Coast is a separate entity from West Coast hosting Collingwood) to cleanly isolate strict home-ground advantage.

**Feedback**:
The econometric justification overstates the capability of fixed effects. Because crowd lockouts, hub fatigue, and shortened quarters all occur simultaneously during the 2020 season, time-invariant pair fixed effects cannot separate them. The directed fixed effects isolate the aggregate 2020 treatment from baseline pair heterogeneity, but they do not disentangle the distinct mechanisms operating within the treatment year. Clarify that the direct hub controls and metric standardization handle the isolation of the concurrent pathways.

---

### 8. Anomalous reference year falsifies parallel trends assumption

**Status**: [Pending]

**Quote**:
> All seven pre-treatment point estimates are positive relative to the 2019 reference year, consistent with 2019 being an anomalously low period relative to the prior seven seasons. All pre-treatment coefficients save one are statistically indistinguishable from zero at conventional significance levels under two-way clustering.

**Feedback**:
Identifying 2019 as an anomalously low period invalidates it as a solitary reference year for the event study. The parallel trends assumption requires a stable trajectory between the pre-treatment and treatment periods. If 2019 reflects a severe negative deviation, the subsequent rise in 2020 confounds any treatment effect with natural mean reversion toward the 2012–2018 baseline. A single outlier year compromises the counterfactual. You should pool 2012–2018 as the stable reference baseline or explicitly address the threat of mean reversion from the 2019 trough.

---

### 9. Fallacy of equating individual non-significance with zero pre-trend

**Status**: [Pending]

**Quote**:
> All pre-treatment coefficients save one are statistically indistinguishable from zero at conventional significance levels under two-way clustering.

**Feedback**:
The text relies on the lack of individual statistical significance to assert the absence of pre-trends. This reasoning ignores the directional uniformity of the estimates. All seven pre-treatment coefficients are positive, ranging from +0.169 to +0.817. This systematic bias indicates a joint deviation from the 2019 reference year, while the large standard errors generated by two-way clustering obscure the individual significance tests. Acknowledge this uniform directional bias rather than relying on underpowered marginal tests to defend the parallel trends assumption.

---

### 10. Contradictory clustering justification

**Status**: [Pending]

**Quote**:
> All models employ Time (season) fixed effects, and robust two-way cluster-robust standard errors (clustered by entity and time index) are used to prevent understating uncertainty given that unobserved team-level shocks correlate across matchups. We note that in a dyadic panel, a shock to one team propagates across all of that team's matchups; a matchup-level cluster is a pragmatic approximation that does not fully absorb node-level shocks.

**Feedback**:
The mathematical justification for the standard error clustering contains a contradiction. Matchup-level clustering groups repeated observations of a specific pair over time. It assumes independence across different opponents, meaning it explicitly fails to address team-level shocks that propagate across the schedule. While the text eventually admits this limitation, the opening premise wrongly states the clustering is used to handle cross-matchup correlations. Revise the initial sentence to clarify that matchup-level clustering accounts for autocorrelation within the same team pairing, rather than broad node-level shocks.

---

### 11. Degenerate undirected fixed effects

**Status**: [Pending]

**Quote**:
> - **Model 1**: Baseline Specification (Undirected Matchup FEs, no controls)
> - **Model 2**: Primary Causal Identification (Directed Team-Pair FEs, no controls)
> - **Model 3**: Hub Travel Robustness (Directed Team-Pair FEs + resting days differential + interstate override dummy)

**Feedback**:
Specifying undirected pair fixed effects against an antisymmetric differential outcome renders the estimator degenerate. A free-kick differential flips its sign depending on which team hosts the match. An undirected parameter averages the positive and negative iterations of the pair, causing the expected intercept to cancel out to zero. The fixed effect therefore fails to absorb the latent team-quality differences. You should replace Model 1 with an additive structure specifying separate home and away team fixed effects.

---

### 12. Contradictory Mechanism for Baseline Advantage

**Status**: [Pending]

**Quote**:
> The mechanism linking Tactical Compression to differential convergence operates through the spatial and energy economics of open play. Under normal conditions, home teams accumulate a free-kick advantage primarily through a late-game energy premium: fresher legs allow them to break contests into space, force more forward-50 contests, and generate the forward-moving collision physics (Holding the Man, Push in the Back, Holding the Ball) that constitute the preponderance of contact-driven free kicks. Hub conditions imposed comparable travel burdens and condensed fixture schedules on both sides: teams faced shortened preparation windows, shared accommodation environments, and regular four-day turnarounds. Without a reliable energy asymmetry, the home team could not sustain the late-game territorial dominance that structurally generates FK differentials.

**Feedback**:
The theoretical argument depends on a late-game energy premium to explain the historical home advantage. This contradicts the empirical results presented in Section 6.4. The data demonstrates that baseline scoring margins are uniform across all quarters, and the text specifically rejects the late-game surge hypothesis in favor of a persistent structural dominance. Establishing a mechanism only to falsify it directly with quarter-level data confuses the narrative. Align this paragraph with the empirical findings by replacing the late-game claims with the persistent, match-long structural dominance mechanism.

---

### 13. Conflation of absolute fatigue and relative rest

**Status**: [Pending]

**Quote**:
> Short turnarounds, defined as breaks of 5 days or fewer, were a structural hallmark of the 2020 hub season, imposing an overwhelming physical burden on athletes. To validate whether this fatigue channel is structurally operative across eras, we queried the historical pre-2020 dataset for all matches played on short rest. In the entire 2012–2019 baseline (N=1,583 matches), there were *exactly five* short-rest games. The physical shock of the 2020 regular season (N=31 short rest games) was an unprecedented historical discontinuity. Hub conditions democratised an extreme, novel form of fatigue between home and away sides, effectively eroding the home team's traditional energy premium in the contest's closing stages.

**Feedback**:
The passage conflates absolute systemic fatigue with relative rest differentials. The historical discontinuity relies on absolute rest metrics, identifying 31 games with breaks of five days or fewer. Yet the common support robustness check depends entirely on the relative rest-day differential between opponents. If both teams experience a short turnaround, absolute fatigue is extreme but their rest differential is zero. Validating the model support on the differential metric fails to address the absolute physical shock driving the tactical collapse. Distinguish between these two concepts and clarify whether the hub mechanism requires asymmetric rest or merely symmetric absolute fatigue.

---

### 14. Leftover author note in text

**Status**: [Pending]

**Quote**:
> **A Note on Tackle Rate Reconciliation.** An earlier draft described the Tackle Rate as "dropping 4.1%" while a figure note described it as "ticking up slightly in 2020." This discrepancy arose from using a disposal-based denominator (TK/DI), which is endogenous to the same style shifts being measured. Using the exogenous per-60-minutes denominator, tackles per 60 minutes declined by **7.9% (p < 0.0001)** from a mean of 64.6 to 59.5. At 59.5 TK/60min, 2020 represents a strict decline of 1.7 TK/60min from the previous low of 61.2 recorded in 2019—making 2020 the lowest tackling season in the entire sample. Any suggestion of a marginal uptick reflects a figure that used a disposal-based denominator and should be disregarded.

**Feedback**:
This paragraph reads as internal correspondence or a response to reviewers rather than formal manuscript text. Instructing the reader to disregard a figure implies the document contains uncorrected legacy content. Published research should correct inconsistent tables and figures rather than publishing meta-commentary warning readers to ignore them. Remove this transitional note and ensure all charts reflect the exogenous per-60-minutes denominator.

---

### 15. Conflating pre-trends with shock

**Status**: [Pending]

**Quote**:
> Using the exogenous per-60-minutes denominator, tackles per 60 minutes declined by **7.9% (p < 0.0001)** from a mean of 64.6 to 59.5. At 59.5 TK/60min, 2020 represents a strict decline of 1.7 TK/60min from the previous low of 61.2 recorded in 2019—making 2020 the lowest tackling season in the entire sample.

**Feedback**:
Comparing the 2020 treatment year against an eight-year pooled baseline overstates the magnitude of the discrete shock. The data shows a pre-existing downward drift in tackling, reaching 61.2 by 2019. The 7.9% structural decline absorbs years of this baseline trend. The actual drop from the immediate pre-treatment year is significantly smaller. Present the explicit 2019 values in the table alongside the baseline mean to distinguish the discrete 2020 tactical compression shock from the long-term trend.

---

### 16. Contradiction in causal interpretation

**Status**: [Pending]

**Quote**:
> Third, and most broadly, the Tactical Compression findings illustrate how an extreme structural shock can dominate and statistically mask environmental pressure channels that may well operate under normal conditions. Our results establish that, in the specific and extraordinary context of the 2020 AFL hub season, behavioural shifts in game style were of sufficient magnitude to render any crowd-based umpire bias statistically undetectable.

**Feedback**:
The conclusion misunderstands the mechanics of multivariate regression. The empirical models isolate the independent effect of crowd removal by explicitly controlling for hub logistics and standardizing for game duration. If a multiple regression returns a null coefficient for the treatment, it indicates the variable has no independent effect. It does not suggest the effect was statistically masked by the control parameters. If the impact were genuinely masked, it would imply the separation strategy failed. State clearly that the isolated effect of crowd absence is indistinguishable from zero once tactical shifts are accommodated.

---

### 17. Imprecise use of measurement error

**Status**: [Pending]

**Quote**:
> First, we develop a novel continuous treatment metric—the **Expected Partisanship Index (EPI)**—to resolve the severe measurement error present in raw attendance figures.

**Feedback**:
The term measurement error technically applies to miscounted raw data. The core argument addresses construct validity. Total attendance fails to distinguish between neutral crowds and hostile partisan environments, making it a flawed proxy for crowd pressure. While measurement error can describe proxy deviations in strict econometric parlance, readers might assume you are questioning the accuracy of the gate counts. Adjust the phrasing to indicate that you are resolving a proxy failure rather than correcting corrupted venue data.

---

### 18. Non-standard terminology for awarded free kicks

**Status**: [Pending]

**Quote**:
> Variables include scored free kicks for and against each team, contested possessions, disposals, tackles, marks, marks inside 50, and clearances.

**Feedback**:
The phrase scored free kicks misaligns with standard Australian Rules Football terminology. Umpires award free kicks. Players do not score them. Readers unfamiliar with the sport might infer you are only counting penalty events that directly lead to points. Change the wording to specify awarded free kicks to ensure the methodology unambiguously covers all penalty events.

---

### 19. Discrete nature of rest days variable

**Status**: [Pending]

**Quote**:
> we engineer two new hub controls: `days_rest_diff`, a continuous measure of home rest days minus away rest days

**Feedback**:
The differential between opponent rest days derives from integer values. This makes it a discrete measure. Describing an integer-valued gap as continuous mischaracterizes the parameter. Update the text to identify the variable as discrete.

---

### 20. Conflation of post-treatment bias and collider bias

**Status**: [Pending]

**Quote**:
> While we explicitly note that conditioning on post-treatment variables invites collider bias—preventing us from claiming strict identification of total causal mediation—the extreme associative density of these covariates strongly reinforces our underlying thesis: physical gameplay dynamics are structurally correlated with the variance observed.

**Feedback**:
Conditioning on a post-treatment mediator introduces over-control bias by blocking the causal pathway. This is distinct from collider bias, which requires the mediator to act as a common effect of the treatment and an unobserved confounder. The terminology obscures the exact mechanism disrupting the mediation design. Replace the reference to collider bias with a note on post-treatment bias.

---

### 21. Causal leap from mechanical bounds

**Status**: [Pending]

**Quote**:
> Over 0.696 of that collapse remains entirely unexplained by simple mechanical duration limits, proving that tactical compression depressed play organically throughout the entire contest.

**Feedback**:
The mechanical bound calculation effectively dismisses the shorter game clock as the sole driver. It does not prove that tactical compression caused the remainder of the drop. The unexplained variance could arise from other concurrent shocks. The mathematical bound rejects one hypothesis but cannot confirm another. Soften the phrasing to state that the residual gap requires an organic behavioural explanation without prematurely declaring the tactical mechanism proven by this specific calculation.

---
