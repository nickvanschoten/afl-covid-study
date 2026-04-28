# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

**Date**: 04/28/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper presents an interesting natural experiment evaluating the effect of crowd absence on umpire bias during the 2020 AFL season. While the construction of the Expected Partisanship Index and the decomposition of game dynamics are strong, several methodological choices weaken the primary causal claims. Specifically, the paper struggles with a known pre-trend violation, inconsistent inference standards, and the interpretation of null results without a power analysis.

This paper uses a compelling natural experiment to isolate the effects of crowd absence on umpire bias, building on a highly detailed dataset. The authors introduce a clever continuous treatment metric to resolve measurement error in attendance data and provide an insightful structural decomposition of game dynamics. However, the reliance on an undetrended baseline model in the face of a pre-trend violation and the lack of a statistical power analysis limit the strength of the null findings.

**Unresolved Pre-Trend Violation Requires Bounding**

Section 4.2 reveals a statistically significant pre-treatment deviation in 2018 (+0.365, p=0.033), violating the fundamental parallel trends assumption of the Difference-in-Differences design. Section 4.2.1 notes that unit-specific linear detrending is degenerate. The authors proceed with the baseline model while merely acknowledging the anomaly. Changing the reference year to 2016 and conducting a placebo test fails to rescue the identification strategy from this established violation. Standard DiD estimates are biased when parallel trends fail. This casts doubt on the validity of the central null finding. Apply modern partial identification methods, such as Rambachan and Roth (2023) bounds, to demonstrate whether the null result holds under the magnitude of trend violations implied by the 2018 deviation.

**Inconsistent Standard Error Clustering Across Models**

Section 4.4 describes Model 1 as using HC1-robust OLS, which produces a borderline significant treatment effect (p=0.059). Models 2-5 employ two-way cluster-robust standard errors. Dismissing the Model 1 result as an artifact of a 'relaxed inference standard' is unconvincing when the authors deliberately chose to apply different clustering strategies across the specifications. A credible empirical strategy demands applying a uniform, theoretically motivated clustering approach to all models. Managing statistical significance through ad hoc specification choices limits confidence in the stability of the findings. Re-estimate Model 1 using the exact same two-way cluster-robust standard errors applied to Models 2-5, and report whether the coefficient remains significant.

**Look-Ahead Bias in the Club Prestige Index Construction**

Section 3.3 defines the Club Prestige Index (CPI) using a 'Membership Anchor' computed as a static average from the 2015-2019 window. Applying a static 2015-2019 average to observations from 2012-2014 introduces look-ahead bias. The prestige measure for those early matches incorporates future information. This construction directly contradicts the claim that the CPI prevents data leakage and is strictly pre-determined. The null finding regarding institutional brand bias in Section 5.2 may simply be an artifact of this misspecification muting dynamic variation in club stature over time. Reconstruct the CPI using a rolling, strictly lagged membership average (e.g., a 3-year trailing window) for all components to ensure the index reflects contemporaneous prestige.

**Absence of Statistical Power Analysis for the Null Finding**

The central claim in Section 5.1 rests on interpreting statistically insignificant coefficients as definitive evidence that partisan crowds do not cause umpire bias. Failing to reject the null hypothesis is not equivalent to proving a zero effect. This is particularly true given the massive structural noise introduced by the 2020 'Tactical Compression' discussed in Section 6. Readers cannot determine whether the null result reflects a true absence of bias or merely a lack of statistical power to detect it amidst the pandemic-induced variance. This omission leaves the strong behavioral claims in the conclusion lacking empirical support. Include a formal minimum detectable effect (MDE) calculation to demonstrate that the primary specification possessed sufficient power to detect a historically plausible crowd-effect size.

**SUTVA Violations and Inseparable Concurrent Treatments**

Section 6.1 contends that the continuous EPI treatment successfully separates crowd absence from the democratized fatigue of the hub season. This logic assumes the hub shock only linearly shifted the outcome via the observed proxies for rest and travel. The entire league experienced a simultaneous, unprecedented structural transformation that altered fundamental gameplay dynamics (Section 6.3). Consequently, the Stable Unit Treatment Value Assumption (SUTVA) is highly suspect. The baseline potential outcomes are likely undefined for the 2020 season, making the isolation of the psychological umpire mechanism from the physiological player mechanism incomplete. Add a simulation or bounding exercise allowing for unobserved, non-linear interactions between the hub shock and the EPI to verify whether the crowd effect can genuinely be isolated.

**Unverified fatigue mechanism for tactical compression**

The paper attributes the structural collapse in dynamic gameplay to democratised fatigue from short rest cycles. It establishes that the 2020 season featured many short-rest games and distinct tactical shifts. It never formally links the two. This is a major omission because the entire alternative explanation for the null result rests on fatigue driving the gameplay changes. Claiming causality requires demonstrating that short rest actually degrades these specific metrics in the data. Regress Forward Efficiency and Tackle Rate on the short-rest indicator using the pooled dataset to verify that fatigue actively suppresses dynamic gameplay.

**Missing aggregation of diffuse tactical shifts**

The authors argue that tactical compression eliminates the home free-kick advantage through a diffuse decay in physical dominance. They show that contested possession, clearance, and tackle metrics all narrowed toward zero in 2020, though none significantly. This leaves a central claim unsubstantiated. A collection of non-significant shifts does not automatically sum to the significant 1.29-foul drop in the primary outcome. The paper must show these tactical changes are quantitatively sufficient to explain the convergence. Train a baseline regression predicting home free-kick differential from the three tactical differentials. Then feed this model the 2020 tactical averages and verify that the predicted drop matches the observed convergence.

**Worked example of the Away Fan Fallacy**

The Expected Partisanship Index resolves the measurement error that plagues raw attendance figures. The text claims large Victorian derbies act as neutral venues, inflating crowd pressure scores and driving the naive model's spurious significance. Readers are given the final regression output but no intuition for how the data actually moves. This makes it hard to evaluate the paper's primary methodological contribution. Provide a concrete comparison of two representative matches. Compute raw attendance and EPI for a high-attendance neutral derby like Collingwood versus Carlton alongside a smaller partisan match like Geelong versus Fremantle. Show exactly how the index reweights these observations to alter the estimator's leverage.

**Recommendation**: major revision

**Key revision targets**:

1. Apply partial identification methods (e.g., Rambachan and Roth bounds) to address the 2018 pre-trend violation in the primary DiD specification.
2. Unify the standard error clustering strategy across all models, specifically re-estimating Model 1 with two-way cluster-robust standard errors.
3. Provide a Minimum Detectable Effect (MDE) calculation to confirm the study had adequate power to detect a meaningful treatment effect.
4. Reconstruct the Club Prestige Index using strictly trailing windows to eliminate look-ahead bias in the 2012-2014 sample.

**Status**: [Pending]

---

## Detailed Comments (22)

### 1. Inconsistent free-kick normalisation

**Status**: [Pending]

**Quote**:
> | Metric | Baseline | 2020 | Change | p-value |
> |---|---|---|---|---|
> | **FK/60 min (nominal)** | 23.44 | 23.91 | +2.0% | **0.319 (ns)** |
> | FK/60 min (actual, previous spec) | 18.36 | 19.03 | +3.6% | 0.036* |
> | **TK/60 min (nominal)** | 98.14 | 94.60 | −3.6% | **0.020*** |
> | TK/60 min (actual, previous spec) | 64.62 | 59.52 | −7.9% | < 0.001*** |
> | **CP/60 min (nominal) [corrected]** | 211.74 | 221.01 | +4.4% | **< 0.001*** |

**Feedback**:
The reported conversion from actual to nominal free-kick rates contains an algebraic error. A proper normalization must preserve the underlying event count. Applying the actual baseline rate of 18.36 across 121.5 minutes yields 37.18 total free kicks per game. Converting this total to an 80-minute nominal game yields a rate of 27.88. The table instead reports 23.44. Similarly, the 2020 nominal rate should be 30.26, not 23.91. If the underlying data is correct, the nominal rate increased by 8.5%, not 2.0%. This directly contradicts the core claim that free-kick density remained stable. Recalculate these figures.

---

### 2. Unreproducible mechanical duration effect

**Status**: [Pending]

**Quote**:
> Mechanical duration effects account for only −0.434 of the observed **1.130** differential drop (baseline +1.51 minus 2020 mean +0.38) even under a conservative non-linear fatigue assumption (k=2, double density in removed minutes).

**Feedback**:
The figure of -0.434 does not follow from the stated assumption. We drop 16 minutes from an 80-minute game. If the density of the removed 16 minutes is exactly twice the density of the retained 64 minutes, solving 64x + 16(2x) = 1.51 yields a base density of x = 1.51 / 96. The expected drop from the 16 minutes is therefore 32x, which equals 0.503. The published calculation understates the mechanical effect. Correct the duration effect bounds using the exact algebraic derivation.

---

### 3. Invalid inference from placebo test on anomalous year

**Status**: [Pending]

**Quote**:
> The placebo is solidly null. This falsification check demonstrates that the design does not automatically generate significance, even in the year with the acknowledged pre-trend anomaly.

**Feedback**:
A placebo test run on a year with a known anomaly is uninformative when it returns a null result. Section 4.2.1 already establishes that 2018 contains a statistically significant pre-trend deviation. A well-powered placebo check should flag this deviation. A null result here simply means the pooled specification dilutes the 2018 anomaly—likely by averaging it against the low 2019 trough. This demonstrates poor specification sensitivity rather than a valid design. Run the placebo test on a stable year, such as 2017, to prove the estimator does not generate spurious significance.

---

### 4. Common Support Metric Contradicts Fatigue Mechanism

**Status**: [Pending]

**Quote**:
> A formal overlap diagnostic confirms only 11.1% of 2020 observations fall outside the [5th, 95th] percentile range of the baseline rest-day differential distribution, and a two-sample KS test fails to reject identical distributions (D = 0.108, p = 0.071).

**Feedback**:
Checking overlap on the rest-day differential misses the physiological mechanism. The paper argues that an extreme, absolute lack of rest democratized fatigue. A match where both teams rest for 4 days yields a differential of 0. This is exactly like a baseline match where both rest for 7 days. The differential distributions can overlap perfectly even if the absolute rest distributions are entirely disjoint. You must evaluate the common support using the marginal distributions of absolute rest days for both teams to show whether the 2020 effect is identified within baseline fatigue ranges.

---

### 5. Mathematically impossible collinearity claim

**Status**: [Pending]

**Quote**:
> To assess whether the 2018 coefficient threatens identification, we attempted to augment the primary specification with unit-specific linear time trends via a within-entity centred season index (`season_within`). Diagnostic testing confirmed that in this balanced panel structure—where each matchup entity appears exactly once per season—`season_within` is perfectly collinear with the entity fixed effects and is absorbed by `drop_absorbed=True`. This is a structural property of the balanced panel, not a software artefact: the entity-mean projection spans the within-trend exactly when entity coverage is uniform across time.

**Feedback**:
This mathematical justification for why the detrending failed is wrong. A globally centered time index takes the same sequence of values for every entity. Its dot product with any entity indicator is zero, making it strictly orthogonal to entity fixed effects. Software drops this variable because a uniform time trend is perfectly collinear with the year fixed effects already in the model. Estimating true unit-specific linear trends requires interacting the continuous time index with the entity indicators. Revise the text to correctly state what collinearized, and interact the time index with entity IDs if unit-specific detrending is intended.

---

### 6. Absolute Indicator Fails to Capture Asymmetry

**Status**: [Pending]

**Quote**:
> To robustly isolate the crowd effect from the logistics of the 2020 hub season, we engineer two hub controls: `days_rest_diff`, a continuous measure of home rest days minus away rest days, and `home_interstate_2020`, a binary indicator for designated 'home' teams playing outside their home state. These directly address severe logistical asymmetries without requiring a full geospatial distance matrix.

**Feedback**:
Constructing `home_interstate_2020` as an absolute indicator fails to capture the relative logistical burden. In a hub environment, both teams are often relocated to the same state. The home team playing interstate is no relative disadvantage if the away team is also interstate. This breaks the intended parallel with the `days_rest_diff` variable, which correctly measures the net difference. Replace the absolute indicator with a relative measure of interstate travel burden.

---

### 7. Misaligned Identification Mechanisms

**Status**: [Pending]

**Quote**:
> Our identification strategy isolates pathway (1) from pathways (2) and (3) through three mechanisms. First, we adopt a directed team-pair fixed-effect structure as our primary specification to cleanly isolate strict home-ground advantage. Second, we integrate direct controls for hub logistical asymmetries. Third, we standardise all rate metrics to per-60-minutes using an exogenous duration denominator—discussed in Section 6.2.

**Feedback**:
Directed team-pair fixed effects cannot separate concurrent time-varying shocks. They only absorb time-invariant baseline differences between teams. Democratized fatigue and reduced quarter lengths occurred exactly at the same time as the crowd lockouts. The fixed effects are blind to this temporal overlap. You isolate the crowd effect by exploiting the continuous variance of the EPI against the uniform hub shocks, not through fixed effects. Correct the text to properly assign the identification properties to the correct mechanisms.

---

### 8. False Dichotomy in Evaluating 2018 Deviation

**Status**: [Pending]

**Quote**:
> All pre-treatment coefficients save one are statistically indistinguishable from zero under two-way clustering. The 2018 deviation (p = 0.033) persists regardless of reference year choice, confirming it reflects a genuine structural event—most plausibly the AFL's 2018 mid-season rule changes—rather than an artefact of the omitted year.

**Feedback**:
The persistence of the 2018 coefficient across reference years does not prove a structural event occurred. Shifting the reference year merely applies a uniform linear shift to all coefficients. A Type I statistical noise spike will persist identically under this transformation. Asserting this persistence confirms a genuine structural event presents a false dichotomy. Soften the claim to note that the deviation persists, but acknowledge it could reflect either an unobserved structural break or standard sampling variance.

---

### 9. Contradictory Claim on Uniform Fatigue

**Status**: [Pending]

**Quote**:
> Both groups decline in 2020, but the Bottom 25% (Least Hostile) collapses by −1.638 residual free kicks against only −0.154 for the Top 25% (Most Hostile)—a 1.48-foul gap that directly contradicts the crowd-pressure prediction. If crowd removal drove the convergence, the most hostile matchups should have collapsed the most; instead they were the most stable. This is consistent with a global fatigue mechanism operating uniformly across matchup types.

**Feedback**:
A 1.48-foul gap between quartiles demonstrates a highly heterogeneous effect. A uniform mechanism would cause both groups to experience similar declines. While the direction of the gap contradicts the crowd-pressure hypothesis, calling the resulting collapse uniform defies the numbers presented in the same paragraph. Revise the conclusion to explicitly address why the least hostile environments experienced a collapse ten times larger than the most hostile environments.

---

### 10. Mischaracterization of Point Estimate

**Status**: [Pending]

**Quote**:
> We emphasise that a null result—a coefficient near zero with a confidence interval that includes zero—provides no empirical basis for inferring any directional behavioural tendency. Any point estimate is consistent with sampling noise. The officials are not being swayed by the cheer squad in the data we can observe.

**Feedback**:
Describing the `deficit_x_epi` coefficient as near zero misrepresents the actual estimate of +0.745 reported just prior. An effect size of nearly three-quarters of a free kick is substantively large in this context. A wide confidence interval prevents rejecting the null, but conflating this lack of precision with a measured true zero masks the model's uncertainty. Change 'a coefficient near zero' to 'a statistically insignificant result' to accurately describe the regression output.

---

### 11. Contradiction regarding magnitude of null point estimates

**Status**: [Pending]

**Quote**:
> First, constructing a credible treatment variable in crowd-presence studies requires decomposing raw attendance into its constituent hostility signals. The Expected Partisanship Index resolves the measurement error that causes naive attendance models to recover spurious significance. A coding error identified during review—wherein the sensitivity pipeline silently overwrote fan-split overrides before computing EPI—has been corrected; the null result is now demonstrably robust to genuine parameter variation across all 12 grid configurations (coef range +0.717 to +0.749, all null).

**Feedback**:
Asserting the result is demonstrably robust contradicts the large magnitude of the point estimates. Ranging from +0.717 to +0.749, these coefficients suggest a substantial but imprecisely estimated positive effect. Characterizing this as a robust null misleads readers about the difference between a tightly bound zero and a noisy positive reading. Rewrite this sentence to state the estimates remain statistically insignificant, but acknowledge the large point estimates indicate the effect is imprecise.

---

### 12. Conflating Non-Significance with Zero Effect

**Status**: [Pending]

**Quote**:
> The `CPI_diff` coefficient across Models 4 and 5 is non-significant at any conventional level. A club possessing greater measured prestige—evidenced by larger rolling previous-season average home attendance, stronger recent form, and higher primetime allocation—confers no systematic free-kick advantage. The badge on the jumper provides no statistical armour in front of the officials.

**Feedback**:
Failing to reject the null hypothesis does not prove the effect is exactly zero. Asserting that club prestige confers no systematic free-kick advantage overstates what standard hypothesis testing allows, especially without reporting equivalence bounds. The models merely fail to detect an advantage. Adjust the phrasing to 'confers no statistically detectable free-kick advantage in these models' to respect the limits of statistical inference.

---

### 13. Manski Bounds Yield Estimates, Not P-Values

**Status**: [Pending]

**Quote**:
> Manski-style conservative bounds return p = 0.464 and p = 0.188.

**Feedback**:
Manski bounds calculate an identified set for a parameter—producing an upper and lower bound on the treatment effect. They do not return p-values. You can calculate Imbens-Manski confidence sets or conduct hypothesis tests against these bounds, but stating the bounds themselves return p-values is a fundamental category error. Report the actual identified set of coefficients, and separately clarify what specific null hypotheses the p-values refer to.

---

### 14. Contradictory claim of pre-trend validation

**Status**: [Pending]

**Quote**:
> We validate this null result through four formal identification checks: a naive attendance benchmark, a placebo test, an event-study parallel trends validation, and direct heterogeneous-confound tests interacting fatigue proxies with EPI.

**Feedback**:
Claiming the parallel trends assumption is validated directly contradicts Section 4.2.1, which labels the 2018 deviation an unresolved pre-trend anomaly. Calling the assumption validated in the introduction mischaracterizes the mixed diagnostic results presented later in the text. Change 'an event-study parallel trends validation' to 'an event-study parallel trends diagnostic' so the opening summary aligns with the paper's actual empirical findings.

---

### 15. Inconsistent Tactical Control Variable

**Status**: [Pending]

**Quote**:
> Separately, three game-state controls represent the physical state of play: `cp_diff` (home minus away contested possessions), `kicks_diff` (kicks), and `clearance_diff` (clearances). These are explicitly excluded from our primary causal identification models to prevent post-treatment bias and deployed only in a dedicated mediation specification.

**Feedback**:
The inclusion of `kicks_diff` contradicts the metrics used in Section 6.4, where the paper specifically analyzes tackles to test the physical dominance hypothesis. Kicks measure general ball movement, whereas tackles measure the physical contest intensity required for the fatigue-driven collapse mechanism. Replace `kicks_diff` with `tackles_diff` here to ensure internal consistency and align the control variables with the structural thesis.

---

### 16. Invalid Aggregation of Event-Study Dummies

**Status**: [Pending]

**Quote**:
> | Year | Coefficient | 95% CI | p-value |
> |---|---|---|---|
> | 2012–2017 | Mainly null | — | > 0.10 |

**Feedback**:
Aggregating five distinct years into a single row obscures the individual variance required to evaluate parallel trends. An event-study specification produces independent coefficients and standard errors for each interaction term. Assigning a single generic p-value to the entire block prevents the reader from verifying whether any specific pre-treatment year deviated from zero. Expand this row to list the exact coefficients and p-values for every year from 2012 to 2017.

---

### 17. Missing synthesis of Disposal Differential

**Status**: [Pending]

**Quote**:
> The CP, clearance, and tackle differentials all narrow toward zero in 2020, consistent with democratised fatigue eroding the home team's structural physical advantage. None reach conventional significance individually—the signal is diffuse across multiple contest channels, precisely what a full-match structural compression mechanism would produce, as opposed to a single discrete tactical failure.

**Feedback**:
The text synthesizes CP, clearance, and tackle differentials but omits the Disposal Differential. The table immediately above shows Disposal Differential experienced the largest absolute change (-7.95) and has a near-significant p-value of 0.051. Ignoring this metric in the summary text reads like selective reporting. Readers will wonder why the strongest signal is excluded from the narrative. Add 'disposal differential' to the list of narrowing metrics in the text.

---

### 18. Contradictory free-kick differentials in Appendix table

**Status**: [Pending]

**Quote**:
> | **Differential Drop** | Baseline +1.51 − 2020 +0.38 = **1.130**; mechanical bound (k=2) = −0.434; residual = 0.696 |
> | **Tactical Differentials** | CP diff +3.42→+1.34 (ns); CL diff +0.67→+0.33 (ns); FK diff +1.59→+0.30 (p=0.009) |

**Feedback**:
The table reports contradictory values for the same metric on adjacent lines. The 'Differential Drop' row states the free-kick baseline was +1.51 and 2020 was +0.38. The 'Tactical Differentials' row immediately below states the FK diff dropped from +1.59 to +0.30. These cannot both be correct. Unify the numbers, or explicitly label the distinction if one is an adjusted rate and the other is a raw count.

---

### 19. Unquantified bounds on duration confound

**Status**: [Pending]

**Quote**:
> First, the AFL shortened quarters from 20 to 16 minutes, mechanically reducing all counting statistics including total free kicks and their differential, regardless of any change in umpire behaviour.

**Feedback**:
Introducing the duration confound without immediately quantifying it allows the reader to assume shortened games explain the entire convergence. Section 6.2 calculates this mechanical effect explains less than 40% of the drop. Adding a forward reference right here sets expectations accurately. Consider appending '(though Section 6.2 shows this explains only a fraction of the observed drop)' so the reader knows tactical mechanisms are still necessary.

---

### 20. Misleading description of positive point estimate

**Status**: [Pending]

**Quote**:
> The ball became trapped in congested midfield scrums. Critically, **Free Kicks per 60 minutes did not decline significantly**. The entire 13.2% raw-count decline is a volume effect of the game-duration reduction—not a change in adjudication standards.

**Feedback**:
Characterizing the shift as 'did not decline significantly' strongly implies a negative point estimate that failed to reach significance. The table clearly shows the nominal rate increased by 2.0%. Describing an absolute increase as a non-significant decline obscures the direction of the data. Change the phrasing to '**Free Kicks per 60 minutes slightly increased**' to faithfully report the positive point estimate.

---

### 21. Ambiguous presentation of rate changes in table

**Status**: [Pending]

**Quote**:
> | **Forward Efficiency** (Marks Inside 50 / Inside 50s, i.e. MI50 / I50) | 22.6% | 20.5% | **−9.2%** | < 0.0001 |

**Feedback**:
Reporting a relative percentage change for a variable that is inherently a percentage creates ambiguity. Readers tend to calculate the absolute difference and might misinterpret -9.2% as a massive 9.2 percentage point drop. Standard practice for rate variables requires reporting changes in percentage points. Update the table to report this as '-2.1 pp' to prevent confusion regarding the magnitude of the shift.

---

### 22. Inaccurate classification of Forward Efficiency

**Status**: [Pending]

**Quote**:
> Converting all metrics to their nominal-time-normalised rates reveals the structural shift:
> 
> | Metric | Baseline (2012–2019) | 2020 | Change | p-value |
> |---|---|---|---|---|
> | **Forward Efficiency** (Marks Inside 50 / Inside 50s, i.e. MI50 / I50) | 22.6% | 20.5% | **−9.2%** | < 0.0001 |

**Feedback**:
The introductory text categorizes all metrics in the table as nominal-time-normalised rates. Forward Efficiency is a dimensionless probability ratio of two events. Time-normalizing both the numerator and denominator mathematically cancels the time scalar. The metric is fundamentally independent of time. Adjust the introductory sentence to note that the table includes both time-normalised rates and dimensionless event efficiencies.

---
