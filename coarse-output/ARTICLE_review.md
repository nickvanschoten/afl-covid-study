# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

**Date**: 04/19/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper investigates the impact of crowd absence on umpire bias and game dynamics during the 2020 AFL hub season. It introduces a Net Partisan Hostility Index to measure crowd pressure and concludes that the observed drop in free-kick differentials was driven by extreme fatigue rather than changes in referee psychology.

The manuscript identifies a fascinating natural experiment and smartly pivots from a pure umpiring analysis to examining structural gameplay changes. The documentation of the 'Trench Warfare' mechanism is convincing. The econometric execution suffers from severe confounding between the crowd lockout and the physical realities of the relocation hubs.

**Uncontrolled Confounding from Hub Relocation**

The empirical strategy in Section 4 treats the 2020 season as an experiment isolating the absence of crowds. The text explicitly acknowledges in Section 6 that 2020 was a hub season with teams facing severe schedule compression. Relocating teams to centralized hubs fundamentally altered travel burdens, meaning the designated home team often had a massive logistical advantage entirely separate from crowd noise. This violates Assumption 1 because the treatment indicator captures both zero attendance and extreme travel asymmetry. Re-specify the model to include controls for travel distance and hub residency duration for both competing teams.

**Endogenous Control Variables in the Main Specification**

The main regression models in Section 5 adjust for physical game states like contested possessions and territory control. Section 6 simultaneously argues that the 2020 season structurally altered these exact variables due to the fatigue effect. Including variables altered by the treatment as controls in the main regression introduces severe post-treatment bias. Conditioning on gameplay mechanics blocks the causal path, guaranteeing the crowd pressure coefficient is biased toward zero. Remove all post-treatment match statistics from the primary specification, reserving them strictly for secondary mediation analyses.

**Misspecified Fixed Effects in the DiD Framework**

The panel data specification in Section 4 lists Entity (Matchup) and Time (Season) fixed effects. Including a Season fixed effect in a model where the treatment occurs uniformly in a single season perfectly collinearizes with the post-treatment indicator. A generic Matchup fixed effect also fails to specify the direction of the fixture, meaning a game where Team A hosts Team B is treated identically to Team B hosting Team A. This construction prevents the model from isolating true home advantage. Replace the matchup fixed effect with directed team-pair fixed effects and ensure the treatment interaction term is properly identified against the season fixed effects.

**Absence of Parallel Trends Verification**

The authors state Assumption 1 requires parallel trends, yet Section 5 provides no empirical validation for this claim. A valid continuous DiD design relies on proving that high-EPI and low-EPI fixtures followed similar free-kick trajectories before the 2020 disruption. The current manuscript jumps directly from the model definition to a coefficient forest plot of the main effects. Readers cannot verify whether the observed convergence was an existing pre-trend rather than a sharp break in 2020. Add an event-study regression that interacts the Net Partisan Hostility Index with individual year dummies from 2012 to 2019, plotting the coefficients to demonstrate flat pre-treatment trends.

**Inadequate Standard Error Clustering**

The empirical strategy clusters standard errors at the matchup level. Unobserved shocks in sports data are heavily correlated within teams across a season due to coaching strategies and roster compositions. Assuming that a team's disciplinary record in one matchup is independent of their record against a different opponent systematically underestimates the standard errors. This choice artificially inflates the precision of the estimates presented in Section 5. Re-estimate all models with two-way clustered standard errors at the home team and away team levels, or at the team-season level.

**Missing formulation and worked examples of the EPI**

The paper stakes its primary methodological contribution on the Net Partisan Hostility Index (EPI). Section 3 provides only a qualitative outline of stadium density and fan splits. The actual mathematical formula is entirely absent. Without explicit equations, the metric is impossible to replicate or interrogate. Readers also lack intuition for how the raw inputs map to the final continuous scale. Provide the formal equation for the EPI. Then, compute the index for at least two concrete historical matchups—such as a Collingwood versus Essendon MCG clash against a West Coast versus Fremantle Derby—to demonstrate exactly how the scaling and membership adjustments operate in practice.

**Unverified fatigue mechanism outside the treatment year**

The authors assert that athlete physiology, rather than empty stadiums, caused the free-kick convergence. They base this entirely on aggregate differences between the 2012-2019 baseline and the unique 2020 hub season. This implies a testable restriction: high fatigue should consistently reduce free-kick variance, regardless of the year. The current draft merely correlates two simultaneous anomalies in 2020 without showing the mechanism operates independently of the pandemic context. Exploit the pre-2020 baseline data to test this. Identify matches where teams played off short turnarounds, and compute whether these structurally fatigued, normal-crowd fixtures exhibit the same drop in forward efficiency and free-kick variance seen in 2020.

**Missing comparison against naive attendance models**

The introduction claims the continuous EPI metric resolves severe endogeneity that plagues raw attendance figures. The manuscript never actually compares the Fuzzy DiD results against a standard binary design. If a naive model comparing simply "crowds" to "no crowds" yields the exact same null coefficient for umpire bias, the methodological value of the EPI is questionable. The paper needs to prove its new index does empirical work. Estimate a baseline DiD model using a simple binary lock-out indicator and present it alongside the main Fuzzy DiD results in Section 5. Verify whether the continuous treatment specification fundamentally alters the point estimates or standard errors compared to the naive approach.

**Recommendation**: major revision

**Key revision targets**:

1. Remove post-treatment game state variables from the main DiD specification to eliminate post-treatment bias.
2. Re-specify the fixed effects to use directed team-pairs and resolve the exact collinearity with the season fixed effect.
3. Add controls for travel distance and schedule breaks to isolate the crowd absence from the hub logistical asymmetries.
4. Include an event-study plot demonstrating parallel pre-trends for the EPI metric across the 2012-2019 baseline.
5. Update standard errors to cluster at the team or team-season level.

**Status**: [Pending]

---

## Detailed Comments (8)

### 1. Unstandardized Counting Statistic

**Status**: [Pending]

**Quote**:
> Once the math is normalised, the true driver of the statistical anomaly appears. We observe a catastrophic structural collapse in game mechanics in 2020 compared to the 2012-2019 baseline:
> * Forward Efficiency (Marks Inside 50 / Total I50) dropped by 9.2% (p < 0.0001).
> * Contested Possession Rate increased by 3.8% (p < 0.0001).
> * Total Match Free Kicks decreased by 13.2% (p < 0.00001).

**Feedback**:
The mechanisms section claims all counting metrics are converted to per-disposal rates to adjust for 16-minute quarters. Yet, the bulleted list reports a 13.2% decrease in 'Total Match Free Kicks'—a raw counting statistic. Because total regulation game time dropped by 20% in the hub season (from 80 to 64 minutes), a 13.2% drop in total free kicks mechanically implies that the frequency of free kicks relative to game length actually increased. This arithmetic contradiction breaks the core conclusion that free kicks 'dried up.' Replace the raw count with the corresponding standardized rate, such as free kicks per 100 minutes or per disposal, and re-evaluate whether the tactical compression narrative holds.

---

### 2. Misnomer of continuous DiD as Fuzzy DiD

**Status**: [Pending]

**Quote**:
> First, we develop a novel continuous treatment metric—the Net Partisan Hostility Index (EPI)—to resolve the severe endogeneity present in raw attendance figures. Second, utilizing a Fuzzy Difference-in-Differences (DiD) framework, we demonstrate that umpires are remarkably resilient to crowd pressure; the crowd pressure coefficient is statistically dead across all model specifications.

**Feedback**:
The manuscript describes its empirical strategy as a 'Fuzzy Difference-in-Differences (DiD) framework' immediately after defining a continuous treatment metric. This terminology is confusing. In applied econometrics, Fuzzy DiD designates an instrumental variable approach designed to address imperfect compliance. The empirical strategy described here models continuous treatment intensity. Conflating these frameworks obscures the identification strategy. Furthermore, characterizing a coefficient as 'statistically dead' is informal. Revise the text to specify a continuous DiD design and state that the crowd pressure coefficient is 'statistically indistinguishable from zero'.

---

### 3. Contradictory significance interpretation

**Status**: [Pending]

**Quote**:
> Furthermore, our data reveals a marginal tendency for umpires to overcompensate in empty stadiums, subtly protecting the home team when the eerie silence set in. Cluster-robust 95% confidence intervals confirm that crowd partisanship fails to reach statistical significance.

**Feedback**:
The manuscript asserts a 'marginal tendency for umpires to overcompensate' while explicitly noting the effect fails to reach statistical significance. This interprets statistical noise as a substantive behavioral trend. A non-significant point estimate means the observed difference cannot be reliably distinguished from zero. Readers will be misled if the text assigns physical or psychological meaning to the sign of an insignificant coefficient. State directly that the point estimate is positive but provides no statistical evidence of overcompensation. Remove the speculative behavioral narrative.

---

### 4. Equating absence of evidence with evidence of absence

**Status**: [Pending]

**Quote**:
> We estimate another near-zero, non-significant coefficient. The badge on the jumper gives a team no statistical armour; the myth of the umpiring ride is dead, and officials are remarkably resilient.

**Feedback**:
The conclusion treats a non-significant coefficient as definitive proof that institutional bias is exactly zero. A failure to reject the null hypothesis merely demonstrates a lack of evidence, not evidence of absence. The true effect could remain undetected due to measurement error or insufficient statistical power. Avoid asserting that 'the myth of the umpiring ride is dead.' Soften the claim to state that the data provides no statistical evidence that club prestige influences umpiring decisions.

---

### 5. Overstated physiological scope

**Status**: [Pending]

**Quote**:
> What started as an investigation into referee psychology turned into a definitive mapping of athlete physiology.

**Feedback**:
Characterizing the study as a 'definitive mapping of athlete physiology' vastly overstates the empirical evidence provided. The analysis relies exclusively on match-level statistical aggregates to infer tactical compression. The researchers did not collect or analyze any direct biomechanical or physiological tracking data. Revise the claim to state the study reveals significant structural shifts in match dynamics and tactical behavior rather than mapping physiology.

---

### 6. Inconsistent metrics for free-kick distributions

**Status**: [Pending]

**Quote**:
> Consider a naive pre/post comparison of free-kick differentials. In the 2012-2019 baseline, home teams enjoyed a distinct free-kick advantage, with the distribution peaking meaningfully to the right of zero. In the 2020 hub season, the home and away distributions converge.

**Feedback**:
The text switches terminology between match differentials and raw team counts. A free-kick differential is a single match-level value. It produces one distribution that historically peaks to the right of zero. Stating that 'home and away distributions converge' describes two separate distributions of raw counts, not a differential. If the accompanying figure plots differentials, the phrasing should reflect a single distribution centering around zero.

---

### 7. Contradictory description of hostile crowds

**Status**: [Pending]

**Quote**:
> If the Western Bulldogs host Collingwood at Marvel Stadium, raw attendance numbers simulate a massive home-ground advantage, despite Collingwood fans likely taking over the building. Conversely, a 50/50 split at the MCG presents a completely different psychological environment compared to a locked-out, hostile Friday night Showdown at Adelaide Oval.

**Feedback**:
Describing a match as both 'locked-out' and 'hostile' creates a paradox. A locked-out stadium has zero attendance. It cannot generate the partisan pressure the passage intends to illustrate. The intended contrast appears to be between a large neutral crowd and a similarly large but intensely partisan one. Change 'locked-out' to 'sold-out' to maintain the logical contrast.

---

### 8. Conflating Frequency with Variance

**Status**: [Pending]

**Quote**:
> High-variance free kick counts—such as holding the man, push in the back, and holding the ball—are generated by open, dynamic football where exhausted players are forced into desperate, lunging tackles. When that dynamic play is replaced with a grinding, 36-man scrum where the whistle constantly blows for a neutral ball-up, free kick variance naturally disappears.

**Feedback**:
The passage conflates a reduction in the mean frequency of fouls with a disappearance of statistical variance. Transitioning to a congested game style lowers the total count of holding-the-ball tackles. A decrease in the mean does not automatically eliminate variance across matches. Furthermore, explaining the convergence in home-away differentials requires analyzing the relative differences between teams, not just absolute totals. Adjust the terminology to describe a drop in the total frequency of discretionary free kicks rather than a loss of variance.

---
