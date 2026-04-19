# The Ghost Town Effect: Causal Inference, Umpire Bias, and Tactical Compression in the Australian Football League

**Date**: 04/17/2026
**Domain**: statistics/causal_inference
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper leverages the 2020 AFL season to test whether home-field umpire bias is driven by crowd noise or structural factors. It introduces the Net Partisan Hostility Index (EPI) and uses a Fuzzy Difference-in-Differences design to conclude that umpire bias is a myth, attributing the drop in free-kick differentials to fatigue-induced tactical changes.

The paper cleverly exploits a natural experiment to test the long-standing "Noise of Affirmation" hypothesis against a physiological explanation. The construction of the Net Partisan Hostility Index correctly identifies the flaw in using raw attendance figures. The empirical execution fails, however, to resolve the severe confounding between empty stadiums and concurrent pandemic rule changes.

**Exclusion Restriction Violation and Confounded Treatment**

The identification strategy treats the 2020 season as an exogenous shock that removed crowd noise. Section 6 explicitly details that the 2020 season also introduced 16-minute quarters and four-day breaks. This violates the exclusion restriction. The intervention affects the outcome via extreme fatigue and structural game changes, not just the absence of crowds. If the 2020 indicator captures both empty stadiums and "democratised fatigue," the DiD framework cannot cleanly isolate umpire bias. The authors must explain how the model mathematically separates the EPI parameter from the concurrent physiological shock. The revision should exploit within-2020 variation if some games had partial crowds or different rest advantages.

**Pre-Treatment Trends Invalidate Assumption 1**

Assumption 1 requires parallel trends before the 2020 intervention. The paper claims that physiological "Trench Warfare" mechanics drive the free-kick differential. Figure 5 demonstrates that these exact mechanics began drifting heavily in 2017. The Contested Possession Rate and Uncontested Mark Ratio broke trend years before the pandemic. If the underlying cause of the free-kick collapse was already shifting for three years, the parallel trends assumption for the free-kick differential is highly suspect. Provide an event-study plot showing the pre-2020 coefficient path for the free-kick differential to prove it was stable before the lockdown.

**Direct Contradiction on Tackle Rate Outcomes**

The text in Section 6 asserts that the Tackle Rate dropped by 4.1% in 2020. It uses this statistic to support the "Trench Warfare" mechanism. The description for Figure 5 notes that the Tackle Rate "ticks up slightly in the final 2020 season." The paper cannot claim a statistically significant drop while graphing an increase. Rectify this discrepancy. If the tackle rate actually increased, the authors must revise the interpretation of how fatigue altered the free-kick variance.

**Absence of Formal Identification Framework and Placebo Tests**

The paper makes aggressive claims about causal identification but omits standard verification tools for observational panels. There is no Directed Acyclic Graph (DAG) demonstrating how the model controls for the simultaneous shocks of shortened games and empty stadiums. The analysis lacks placebo tests. Estimating the models with fake intervention years is expected practice to ensure the fixed effects are not simply absorbing random variance. Add a formal causal diagram. Report placebo test results using 2018 or 2019 as fake treatments in an appendix.

**Missing stratification of the EPI treatment**

The paper relies on the Net Partisan Hostility Index (EPI) to supply continuous treatment variation. The core logic dictates that matchups with historically high EPI should experience a much sharper drop in home advantage in 2020 than low-EPI matchups. We never actually see this empirically demonstrated outside the regression table. Readers need a visual or tabular split showing the free-kick differential trajectory for the top quartile of historical EPI versus the bottom quartile. Plot the raw means of these two groups from 2012 through 2020 to verify that the high-hostility games collapsed exactly as the theory predicts, rather than just pointing to a zero coefficient in the Panel OLS.

**Omitted comparison to raw attendance models**

A major stated contribution is that the EPI corrects the severe endogeneity of raw attendance figures, which the authors dismiss as a statistical trap. Yet the paper never estimates a model using these raw attendance figures to prove they actually generate different results. Claiming a novel metric fixes a bias requires showing the bias in action. Estimate the standard DiD using raw pre-treatment attendance instead of the EPI. Report whether this naive specification falsely finds a significant crowd effect or if it yields the same null result. This baseline comparison is required to justify the complex construction of the new index.

**Unverified decomposition of free-kick categories**

The 'Trench Warfare' mechanism makes a specific prediction about which types of penalties should disappear. The text argues that open-play infractions like 'holding the man' and 'push in the back' vanished because exhausted players stopped running. This is a directly testable implication. The paper leaves it completely untouched, relying instead on a blunt 13.2% drop in total match free kicks. Decompose the penalty data into dynamic-play free kicks versus static or technical infringements. Compute the 2019-to-2020 shift for these specific sub-categories. This will empirically confirm whether the structural collapse selectively depressed run-and-gun penalties as the authors claim.

**Recommendation**: major revision

**Key revision targets**:

1. Address the exclusion restriction violation by proving the model separates the crowd absence from the schedule compression/shortened quarters.
2. Add an event-study plot demonstrating the free-kick differential coefficients in the years leading up to 2020 to defend the parallel trends assumption.
3. Correct the contradiction between the Section 6 text and Figure 5 regarding the Tackle Rate.
4. Provide a formal DAG and run placebo tests using fake intervention years to validate the empirical design.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Conflating a statistical null with a behavioral tendency

**Status**: [Pending]

**Quote**:
> Across five separate Panel OLS model specifications, adjusting for physical game states such as contested possessions and territory control, the crowd pressure coefficient is statistically dead. Furthermore, our data reveals a marginal tendency for umpires to overcompensate in empty stadiums, subtly protecting the home team when the eerie silence set in. Cluster-robust 95% confidence intervals confirm that crowd partisanship fails to reach statistical significance.

**Feedback**:
The text asserts a "marginal tendency for umpires to overcompensate" while simultaneously acknowledging the coefficient is "statistically dead" and "fails to reach statistical significance." A statistically insignificant point estimate provides no evidence of a behavioral tendency. A null result simply means the data cannot detect an effect. Asserting a subtle behavioral shift based on a parameter sitting near the zero line is a fundamental statistical error. Remove the claim regarding the umpires' tendency to overcompensate.

---

### 2. Conflation of total free kick volume with home differential

**Status**: [Pending]

**Quote**:
> This completely solves the free-kick paradox. High-variance free kick counts—such as holding the man, push in the back, and holding the ball—are generated by open, dynamic football where exhausted players are forced into desperate, lunging tackles. When that dynamic play is replaced with a grinding, 36-man scrum where the whistle constantly blows for a neutral ball-up, free kick variance naturally disappears. The free kicks didn't dry up because the fans were gone; they dried up because the run-and-gun mechanics of the sport ground to a halt.

**Feedback**:
The tactical breakdown explains the drop in overall penalty volume, but it does not "completely solve the free-kick paradox." The Introduction defines this paradox specifically as home teams receiving a favourable penalty differential. The argument conflates a reduction in total free kicks with the elimination of the home-team bias. A drop in total volume does not mechanically erase umpire favoritism. An official could still disproportionately award the remaining free kicks to the home team. The mechanism requires further evidence linking the structural collapse directly to the elimination of the differential.

---

### 3. Mischaracterization of the DiD framework

**Status**: [Pending]

**Quote**:
> Second, utilizing a Fuzzy Difference-in-Differences (DiD) framework, we demonstrate that umpires are remarkably resilient to crowd pressure; the crowd pressure coefficient is statistically dead across all model specifications.

**Feedback**:
The term "Fuzzy Difference-in-Differences" mischaracterizes the empirical strategy. Fuzzy DiD designs apply when treatment assignment involves non-compliance, using a group-by-time assignment as an instrument. The text explicitly notes that stadiums went "completely quiet," indicating a perfectly enforced lockdown. Variation in treatment intensity stems from interacting this sharp time shock with a continuous baseline measure. This constitutes a Continuous Treatment DiD, not a Fuzzy DiD. Update the methodology description to reflect a continuous assignment.

---

### 4. Inconsistent parallel trends assumption

**Status**: [Pending]

**Quote**:
> **Assumption 1** (Parallel Trends and Exogeneity). *In the absence of the 2020 stadium lock-outs, the free-kick differential trajectory between high-EPI and low-EPI matchups would have remained parallel.*

**Feedback**:
The parallel trends condition dichotomizes the sample into "high-EPI" and "low-EPI" groups. This categorical formulation contradicts the framework's reliance on continuous variation in treatment intensity. For a continuous treatment design to hold, the expected change in untreated potential outcomes must be independent of the continuous treatment dosage across its entire support. Revise the assumption to explicitly state that the expected change in free-kick differentials is independent of the continuous EPI treatment intensity.

---

### 5. Missing mathematical formula for EPI

**Status**: [Pending]

**Quote**:
> **Net Partisan Hostility Index (EPI)**
> To address the measurement error in raw attendance, we engineer a continuous variable capturing genuine environmental hostility. The EPI recalculates historical pressure by factoring in two components:
> * *Stadium Density:* We scale expected crowds against venue capacity to differentiate between an echo chamber (35,000 at the MCG) and a fortress (35,000 at GMHBA Stadium).
> * *Proportional Fan Splits:* We adjust for same-state match-ups using 5-year average club membership data to accurately map true crowd allegiance.

**Feedback**:
The text introduces the EPI as a continuous variable constructed from two sub-components but omits the formal mathematical equation defining their aggregation. Stating that the index factors in stadium density and fan splits leaves the exact mechanics ambiguous. The components could be added, multiplied, or logarithmically scaled. Without an explicit algebraic construction, readers cannot replicate the treatment variable. Provide the formal equation defining the index.

---

### 6. Potential endogeneity in 5-year average

**Status**: [Pending]

**Quote**:
> **Net Partisan Hostility Index (EPI)**
> To address the measurement error in raw attendance, we engineer a continuous variable capturing genuine environmental hostility. The EPI recalculates historical pressure by factoring in two components:
> * *Stadium Density:* We scale expected crowds against venue capacity to differentiate between an echo chamber (35,000 at the MCG) and a fortress (35,000 at GMHBA Stadium).
> * *Proportional Fan Splits:* We adjust for same-state match-ups using 5-year average club membership data to accurately map true crowd allegiance.

**Feedback**:
The construction of the EPI relies on a "5-year average" of club membership data. A rolling average that includes the treatment year introduces endogeneity. Club memberships likely react to the same exogenous pandemic shocks analyzed in the study. Using endogenous, concurrent data to compute a baseline hostility index violates the exogeneity required of a treatment variable. Specify whether this metric uses a strictly pre-treatment, fixed window (e.g., 2015-2019) to ensure the index remains uncontaminated.

---

### 7. Missing mathematical formulation for CPI

**Status**: [Pending]

**Quote**:
> **Club Prestige Index (CPI)**
> To test for institutional bias, we construct a Club Prestige Index. This index tracks club memberships, recent premiership success, and Friday night primetime allocations to measure whether umpires subconsciously favour large brands.

**Feedback**:
The Club Prestige Index is conceptually introduced but lacks a formal mathematical definition. Tracking disparate components like memberships, historical success, and broadcast allocations requires a specific aggregation method. The paper does not specify if it uses standardization, principal component analysis, or an explicit weighting scheme. Without the exact formula showing how inputs are scaled and combined, the index cannot be evaluated for robustness. Add the mathematical equation defining the CPI.

---

### 8. Contradiction between standardization methodology and reported metrics

**Status**: [Pending]

**Quote**:
> To address this, we strictly convert all counting metrics to per-disposal standardized rates. 
> 
> **Quantitative Decompositions of Gameplay**
> Once the math is normalised, the true driver of the statistical anomaly appears. We observe a catastrophic structural collapse in game mechanics in 2020 compared to the 2012-2019 baseline:
> * Forward Efficiency (Marks Inside 50 / Total I50) dropped by 9.2% (p < 0.0001).
> * Contested Possession Rate increased by 3.8% (p < 0.0001).
> * Total Match Free Kicks decreased by 13.2% (p < 0.00001).

**Feedback**:
The text claims all counting metrics undergo strict conversion to "per-disposal standardized rates," but the subsequent list contradicts this rule. "Forward Efficiency" is an event ratio, not a per-disposal rate. More problematically, "Total Match Free Kicks" is a raw per-game count. This represents the exact type of unstandardized metric the preceding paragraph warns against using due to shortened 2020 game lengths. Convert "Total Match Free Kicks" to a per-disposal rate, and clarify that the standardization approach includes event ratios.

---

### 9. Mismatch between in-text metrics and Figure 4 panels

**Status**: [Pending]

**Quote**:
> * Forward Efficiency (Marks Inside 50 / Total I50) dropped by 9.2% (p < 0.0001).
> * Contested Possession Rate increased by 3.8% (p < 0.0001).
> * Total Match Free Kicks decreased by 13.2% (p < 0.00001).
> * Tackle Rate dropped by 4.1% (p = 0.016).
> 
> > **[Figure 4 Descriptor: A grid of four box plots comparing the 2012-2019 Baseline to the 2020 COVID season. "Forward Efficiency (MI50 Ratio)" exhibits a significant downward shift in its median and quartile ranges in 2020. "Stoppage Density (Clearance Rate)", "Standardized Margin", and "Goal Accuracy" show similar median values between the two periods.]**

**Feedback**:
The metrics highlighted in the main text do not align with those presented in Figure 4. The prose emphasizes changes in the Contested Possession Rate, Total Match Free Kicks, and Tackle Rate to establish the structural collapse in game mechanics. Figure 4 instead displays box plots for Stoppage Density, Standardized Margin, and Goal Accuracy, none of which receive textual analysis. Visualizations must directly support the surrounding arguments. Replace the irrelevant panels in Figure 4 with the metrics actively discussed in the text.

---

### 10. Overstated physiological mapping claims

**Status**: [Pending]

**Quote**:
> What started as an investigation into referee psychology turned into a definitive mapping of athlete physiology. Our findings highlight a core lesson in data science and applied econometrics: just because two variables move at the same time—such as empty stadiums and falling free-kick differentials—does not mean they are having a conversation.

**Feedback**:
Declaring the study a "definitive mapping of athlete physiology" severely overstates the empirical evidence. The methodology relies entirely on econometric modeling of match-level aggregates like tackle rates and total free-kick counts. These variables establish behavioral proxies for fatigue and tactical shifts. They do not constitute actual physiological data. Revise the conclusion to accurately reflect that the study maps tactical compression and macro-level player behavior rather than definitive physiological mechanics.

---

### 11. Unjustified historical generalization

**Status**: [Pending]

**Quote**:
> Our findings highlight a core lesson in data science and applied econometrics: just because two variables move at the same time—such as empty stadiums and falling free-kick differentials—does not mean they are having a conversation. The officials are not being swayed by the cheer squad; they are simply adjudicating the game in front of them.

**Feedback**:
The categorical assertion that officials are not swayed by the cheer squad extends too far beyond the paper's scope. The analysis shows that a severe structural shift in the game dictates penalty rates during the abnormal 2020 season. This tactical collapse does not definitively prove that historical home-ground penalty advantages were entirely free of crowd-induced bias. An alternative interpretation is that extreme tactical compression simply overrides standard crowd effects. Limit the claim to note that behavioral shifts in game style can dominate or obscure environmental pressures, rather than concluding crowd bias never existed.

---

### 12. Contradictory crowd environment description

**Status**: [Pending]

**Quote**:
> Conversely, a 50/50 split at the MCG presents a completely different psychological environment compared to a locked-out, hostile Friday night Showdown at Adelaide Oval. Treating attendance as a single, uniform metric produces garbage-in, garbage-out models.

**Feedback**:
The phrase "locked-out, hostile" contains a logical contradiction. A locked-out game implies an empty stadium, which cannot produce the hostile partisan pressure the sentence aims to illustrate. The intended contrast is clearly between a neutral, evenly split crowd at the MCG and an intensely partisan home crowd in Adelaide. Replace "locked-out" with "sold-out" or "packed" to accurately describe the high-hostility environment.

---

### 13. Ambiguous timeframe for recent success

**Status**: [Pending]

**Quote**:
> **Club Prestige Index (CPI)**
> To test for institutional bias, we construct a Club Prestige Index. This index tracks club memberships, recent premiership success, and Friday night primetime allocations to measure whether umpires subconsciously favour large brands.

**Feedback**:
The temporal scope of "recent premiership success" is undefined. A premiership won one year ago carries different prestige weight than one won ten years ago. Without a specified lookback window or decay function, the index's construction is ambiguous and impossible to replicate. Specify the exact time window or decay function used to score historical success.

---

### 14. Contradiction in model count between text and figure

**Status**: [Pending]

**Quote**:
> iggest shift when crowds disappeared. They didn't. 
> 
> Across five separate Panel OLS model specifications, adjusting for physical game states such as contested possessions and territory control, the crowd pressure coefficient is statistically dead. Furthermore, our data reveals a marginal tendency for umpires to overcompensate in empty stadiums, subtly protecting the home team when the eerie silence set in. Cluster-robust 95% confidence intervals confirm that crowd partisanship fails to reach statistical significance. 
> 
> > **[Figure 3 Descriptor: A coefficient forest plot charting the "AFL Noise of Affirmation" with cluster-robust 95% confidence intervals across three models (Base Fuzzy DiD, Continuous DiD, and Continuous DiD + Controls). The crucial causal p

**Feedback**:
The text asserts that the crowd pressure coefficient is evaluated across five separate Panel OLS model specifications. However, the descriptor for Figure 3 indicates the plot only charts confidence intervals across three models. This numerical discrepancy creates confusion regarding the actual empirical support for the null finding. If five models were estimated, document all five in the text or an appendix. Ensure the prose aligns with the presented figures.

---

### 15. Acronym mismatch for treatment metric

**Status**: [Pending]

**Quote**:
> First, we develop a novel continuous treatment metric—the Net Partisan Hostility Index (EPI)—to resolve the severe endogeneity present in raw attendance figures.

**Feedback**:
The acronym "EPI" does not match the phrase "Net Partisan Hostility Index". This inconsistency creates ambiguity about whether EPI is a leftover from an earlier draft or refers to a different metric entirely. Because this metric anchors the identification strategy, its naming must be internally consistent throughout the manuscript. Either change the acronym to NPHI or rename the metric to align with EPI.

---
