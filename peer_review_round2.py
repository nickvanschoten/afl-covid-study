"""
peer_review_round2.py
=====================
Six targeted responses to the second round of peer-review critiques.

  Challenge 1 - Event-Study Reference Year & Detrending Collinearity
  Challenge 2 - Heterogeneous Fatigue x EPI Confound (interaction terms)
  Challenge 3 - Exogenous Nominal Game Time for Rate Normalisation
  Challenge 4 - Grid-Search Bug Fix (fan-split override pre-empted by compute_epi)
  Challenge 5 - Tactical Differentials (CP, CL) + 2020 Q4 Scoring Margins
  Challenge 6 - Model 1 Degeneracy (replace undirected pair FE with additive team FEs)

Requires: afl_cache/raw_panel.parquet, afl_cache/match_*.html (for Q4 parsing).
Depends on: afl_noise_affirmation_did (pipeline helpers).
"""

import re
import warnings
import logging
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from bs4 import BeautifulSoup
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

from afl_noise_affirmation_did import (
    clean_data,
    build_panel,
    calculate_cpi_metrics,
    fan_split_multiplier,
    TEAM_STATE,
    VENUE_STATE,
    NON_VIC_DERBIES,
    CITY_GROUPS,
    CLUB_MEMBERSHIPS,
    VENUE_CAPACITY,
)

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SEP  = "=" * 78
SEP2 = "-" * 78
CACHE_FILE = Path("afl_cache/raw_panel.parquet")
CACHE_DIR  = Path("afl_cache")
STUDY_SEASONS = list(range(2012, 2021))


# ---------------------------------------------------------------------------
# Fixed compute_epi that respects a pre-supplied fan_split column
# ---------------------------------------------------------------------------

def compute_epi_fixed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Equivalent to afl_noise_affirmation_did.compute_epi, but DOES NOT
    overwrite df['fan_split'] when that column already exists.
    This is the fix for Challenge 4: the original function unconditionally
    re-computes fan_split, defeating any override set before the call.
    """
    df = df.copy()

    # --- Step 1: Fan Split multiplier — only if not already supplied -------
    if "fan_split" not in df.columns:
        df["fan_split"] = df.apply(
            lambda r: fan_split_multiplier(r["home_team"], r["away_team"], r["venue"]),
            axis=1,
        )

    # --- Step 2: Historical average attendance ---
    df = df.sort_values(["home_team", "away_team", "venue", "season"])
    pre2020 = df[df["season"] < 2020].copy()

    def _rolling_hist_att(group):
        return group.shift(1).rolling(window=5, min_periods=1).mean()

    pre2020["hist_att"] = (
        pre2020.groupby(["home_team", "away_team", "venue"])["attendance"]
        .transform(_rolling_hist_att)
    )
    venue_avg = pre2020.groupby("venue")["attendance"].mean()
    global_avg = pre2020["attendance"].mean()
    pre2020["hist_att"] = pre2020["hist_att"].fillna(
        pre2020["venue"].map(venue_avg)
    ).fillna(global_avg)

    # --- Step 3: 2020 rows — use 2015-2019 average ---
    last5_avg = (
        df[df["season"].between(2015, 2019)]
        .groupby(["home_team", "away_team", "venue"])["attendance"]
        .mean()
        .rename("hist_att")
        .reset_index()
    )
    covid_rows = df[df["season"] == 2020].copy()
    covid_rows = covid_rows.merge(last5_avg, on=["home_team", "away_team", "venue"], how="left")
    venue_avg_covid = df[df["season"].between(2015, 2019)].groupby("venue")["attendance"].mean()
    global_avg_covid = df[df["season"].between(2015, 2019)]["attendance"].mean()
    covid_rows["hist_att"] = (
        covid_rows["hist_att"]
        .fillna(covid_rows["venue"].map(venue_avg_covid))
        .fillna(global_avg_covid)
    )

    # --- Step 4: Combine ---
    combined = pd.concat([pre2020, covid_rows], ignore_index=True)
    combined = combined.sort_values(["season", "home_team", "away_team"])

    # --- Step 5: EPI ---
    venue_caps = combined["venue"].map(VENUE_CAPACITY)
    default_cap = pd.Series(VENUE_CAPACITY).mean()
    combined["density"] = (combined["hist_att"] / venue_caps.fillna(default_cap)).clip(0.0, 1.0)
    combined["epi_raw"] = combined["hist_att"] * combined["density"] * combined["fan_split"]

    # --- Step 6: Standardise using pre-2020 fit ---
    scaler = StandardScaler()
    pre2020_epi = combined[combined["season"] < 2020]["epi_raw"].values.reshape(-1, 1)
    scaler.fit(pre2020_epi)
    combined["epi_z"] = scaler.transform(
        combined["epi_raw"].values.reshape(-1, 1)
    ).ravel()

    # --- Step 7: Deficit ratio + interaction ---
    combined["expected_attendance"] = combined["hist_att"]
    actual_att = np.where(
        combined["season"] == 2020,
        combined["attendance"].fillna(0.0),
        combined["attendance"].fillna(combined["expected_attendance"]),
    )
    combined["deficit_ratio"] = (combined["expected_attendance"] - actual_att) / combined["expected_attendance"]
    combined["deficit_ratio"] = combined["deficit_ratio"].replace([np.inf, -np.inf], 0.0)
    combined["deficit_ratio"] = combined["deficit_ratio"].clip(0.0, 1.0).fillna(0.0)
    combined["deficit_x_epi"] = combined["deficit_ratio"] * combined["epi_z"]

    return combined


# ---------------------------------------------------------------------------
# Shared loader
# ---------------------------------------------------------------------------

def load_pipeline(fan_split_overrides: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load raw parquet -> clean -> (optional fan-split override) -> EPI -> CPI -> panel.
    fan_split_overrides: {'non_vic': float, 'vic_derby': float}
    """
    raw = pd.read_parquet(CACHE_FILE)
    raw = raw[raw["season"].isin(STUDY_SEASONS)].copy()
    df = clean_data(raw)

    if fan_split_overrides:
        nv_w  = fan_split_overrides.get("non_vic",   0.85)
        vic_w = fan_split_overrides.get("vic_derby", 0.50)

        def _override(home_team, away_team, venue):
            home_state  = TEAM_STATE.get(home_team)
            away_state  = TEAM_STATE.get(away_team)
            venue_state = VENUE_STATE.get(venue)
            if home_state and venue_state and home_state != venue_state:
                return 0.1
            if (home_team, away_team) in NON_VIC_DERBIES:
                return nv_w
            if home_state and away_state and home_state != away_state:
                return 1.0
            home_city = CITY_GROUPS.get(home_team)
            away_city = CITY_GROUPS.get(away_team)
            if home_city == "Melbourne" and away_city == "Melbourne":
                return vic_w
            home_mems = CLUB_MEMBERSHIPS.get(home_team, 40000)
            away_mems = CLUB_MEMBERSHIPS.get(away_team, 40000)
            return home_mems / (home_mems + away_mems)

        # Pre-compute override BEFORE calling compute_epi so it is respected
        df["fan_split"] = df.apply(
            lambda r: _override(r["home_team"], r["away_team"], r["venue"]), axis=1
        )

    # Use the fixed version that does not overwrite fan_split
    df = compute_epi_fixed(df)
    df = calculate_cpi_metrics(df)
    panel = build_panel(df, entity_col="matchup_directed_id")
    return df, panel


def _run_model2(panel: pd.DataFrame, label: str = "Model 2") -> dict:
    """Primary causal specification (Model 2) on a panel slice."""
    p = panel.copy()
    required = ["home_fk_diff", "deficit_ratio", "epi_z",
                "deficit_x_epi", "days_rest_diff", "relative_interstate_dis"]
    p = p.dropna(subset=required)
    try:
        m = PanelOLS.from_formula(
            "home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi "
            "+ days_rest_diff + relative_interstate_dis "
            "+ EntityEffects + TimeEffects",
            data=p, drop_absorbed=True,
        )
        res = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        return {
            "label": label,
            "coef": res.params.get("deficit_x_epi", np.nan),
            "se":   res.std_errors.get("deficit_x_epi", np.nan),
            "pval": res.pvalues.get("deficit_x_epi", np.nan),
            "n":    int(res.nobs),
        }
    except Exception as e:
        log.warning("Model 2 failed for %s: %s", label, e)
        return {"label": label, "coef": np.nan, "se": np.nan, "pval": np.nan, "n": 0}


# ===========================================================================
# Challenge 1 – Event-Study Reference Year Fix & Detrending Collinearity
# ===========================================================================

def challenge1_event_study_fix(df: pd.DataFrame, panel: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 1: Event-Study Reference Year Fix & Detrending Collinearity")
    print(SEP)
    print(
        "  Reviewer critiques:\n"
        "  (a) 2019 is an anomalous trough; using it as the omitted year biases\n"
        "      all pre-treatment coefficients upward.\n"
        "  (b) unit-specific linear trends via season_within collinearize with FEs.\n"
        "\n"
        "  Fix A: Re-run event study with 2016 as the reference year (mid-sample stable).\n"
        "  Fix B: Clarify the detrending: season_within = season - entity_mean(season)\n"
        "         is NOT collinear with entity FEs (it has zero entity mean by construction\n"
        "         but varies within entity). The actual collinearity risk arises if\n"
        "         season_c is ALSO included. We confirm this by running the detrended\n"
        "         spec and checking whether season_within survives drop_absorbed.\n"
    )

    p = panel.copy().reset_index()

    # ---- Part A: Re-run event study using 2016 as reference year ----------
    ref_year = 2016
    years = sorted(p["season"].unique())
    non_ref_years = [y for y in years if y != ref_year]

    for yr in non_ref_years:
        p[f"yr_{yr}"] = (p["season"] == yr).astype(float)
        p[f"epi_x_{yr}"] = p["epi_z"] * p[f"yr_{yr}"]

    p_es = p.set_index(["matchup_directed_id", "season"])
    interaction_terms = " + ".join(f"epi_x_{yr}" for yr in non_ref_years)
    formula_es = (
        f"home_fk_diff ~ epi_z + {interaction_terms} "
        f"+ days_rest_diff + relative_interstate_dis "
        f"+ EntityEffects + TimeEffects"
    )
    p_es_clean = p_es.dropna(subset=["home_fk_diff", "epi_z", "days_rest_diff"])

    log.info("Challenge 1A: event study (ref=2016) on %d obs ...", len(p_es_clean))
    m_es = PanelOLS.from_formula(formula_es, data=p_es_clean, drop_absorbed=True)
    res_es = m_es.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    ci = res_es.conf_int()

    print(f"\n  --- 1A: Event Study Re-Run (Reference Year = 2016) ---")
    print(f"  {'Year':<6}  {'Coef':>8}  {'95% CI':>22}  {'P-val':>9}  Sig")
    print(f"  {'-'*54}")
    for yr in years:
        if yr == ref_year:
            print(f"  {yr:<6}  {'0.000':>8}  {'[reference]':>22}  {'-':>9}")
            continue
        term = f"epi_x_{yr}"
        if term not in res_es.params.index:
            print(f"  {yr:<6}  {'absorbed':>8}")
            continue
        c  = res_es.params[term]
        lo = ci.loc[term, "lower"]
        hi = ci.loc[term, "upper"]
        pv = res_es.pvalues[term]
        sig = "***" if pv < 0.01 else ("**" if pv < 0.05 else ("*" if pv < 0.10 else "ns"))
        note = " <-- 2020 (TREATMENT)" if yr == 2020 else (" <-- 2018 pre-trend?" if yr == 2018 else "")
        print(f"  {yr:<6}  {c:>+8.3f}  [{lo:>+8.3f}, {hi:>+7.3f}]  {pv:>9.4f}  {sig}{note}")

    p2020_new = res_es.pvalues.get("epi_x_2020", np.nan)
    p2018_new = res_es.pvalues.get("epi_x_2018", np.nan)
    print(f"\n  KEY: 2020 coefficient: {res_es.params.get('epi_x_2020', np.nan):+.3f}  p={p2020_new:.4f}")
    print(f"  KEY: 2018 coefficient: {res_es.params.get('epi_x_2018', np.nan):+.3f}  p={p2018_new:.4f}")
    print(f"  With 2016 as reference, all pre-treatment coefficients are now measured")
    print(f"  relative to a structurally stable mid-sample year, not the 2019 trough.")

    # ---- Part B: Confirm detrended model collinearity status ---------------
    print(f"\n  --- 1B: Detrending Collinearity Verification ---")
    p2 = panel.copy().reset_index()
    p2["season_c"] = p2["season"] - 2012
    # Within-entity mean-centred season trend (zero mean per entity)
    p2["season_within"] = p2.groupby("matchup_directed_id")["season_c"].transform(
        lambda x: x - x.mean()
    )
    p2 = p2.set_index(["matchup_directed_id", "season"])
    required_dt = ["home_fk_diff", "deficit_ratio", "epi_z", "deficit_x_epi",
                   "days_rest_diff", "relative_interstate_dis", "season_within"]
    p2_clean = p2.dropna(subset=required_dt)

    try:
        m_dt = PanelOLS.from_formula(
            "home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi "
            "+ days_rest_diff + relative_interstate_dis "
            "+ season_within "
            "+ EntityEffects + TimeEffects",
            data=p2_clean, drop_absorbed=True,
        )
        res_dt = m_dt.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        survived = "season_within" in res_dt.params.index
        c_dx  = res_dt.params.get("deficit_x_epi", np.nan)
        p_dx  = res_dt.pvalues.get("deficit_x_epi", np.nan)
        c_sw  = res_dt.params.get("season_within", np.nan)
        p_sw  = res_dt.pvalues.get("season_within", np.nan)
        print(f"  season_within survived drop_absorbed: {survived}")
        print(f"  deficit_x_epi (detrended): coef={c_dx:+.4f}  p={p_dx:.4f}")
        print(f"  season_within:             coef={c_sw:+.4f}  p={p_sw:.4f}")
        if survived:
            print(f"\n  CONFIRMED: season_within is NOT collinear with entity FEs.")
            print(f"  The within-entity demeaning correctly produces a valid trend absorber.")
        else:
            print(f"\n  WARNING: season_within was absorbed — collinearity confirmed.")
            print(f"  This means entity FEs fully span the within-trend, so the detrended")
            print(f"  spec degenerates. The 2020 null result still stands on the baseline model.")
    except Exception as e:
        log.error("Detrended model failed: %s", e)


# ===========================================================================
# Challenge 2 – Heterogeneous Fatigue x EPI Confound
# ===========================================================================

def challenge2_fatigue_epi_interactions(panel: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 2: Heterogeneous Fatigue × EPI Confound")
    print(SEP)
    print(
        "  Reviewer critique: the 2020 hub fatigue shock (days_rest_diff) affected\n"
        "  high-EPI games differently — e.g. teams playing 'at home' in hubs may have\n"
        "  faced different schedule intensities at their most hostile historical venues.\n"
        "  If fatigue × EPI is correlated with deficit × EPI, the continuous DiD is\n"
        "  confounded. Fix: add fatigue × EPI interaction terms to Model 3 and Model 5.\n"
    )

    p = panel.copy()
    required = ["home_fk_diff", "deficit_ratio", "epi_z", "deficit_x_epi",
                "days_rest_diff", "relative_interstate_dis",
                "cp_diff", "kicks_diff", "clearance_diff"]
    p = p.dropna(subset=required)

    # Pre-compute interaction terms (not in panel by default)
    p2 = p.copy().reset_index()
    p2["rest_x_epi"]       = p2["days_rest_diff"]     * p2["epi_z"]
    p2["interstate_x_epi"] = p2["relative_interstate_dis"] * p2["epi_z"]
    p2 = p2.set_index(["matchup_directed_id", "season"])

    # --- Model 3 extended: Hub Robustness + Fatigue×EPI interactions ---
    print(f"\n  --- Model 3 Extended (Hub Robustness + Fatigue×EPI Interactions) ---")
    log.info("Fitting Model 3 Extended ...")
    try:
        m3e = PanelOLS.from_formula(
            "home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi "
            "+ days_rest_diff + relative_interstate_dis "
            "+ rest_x_epi + interstate_x_epi "
            "+ EntityEffects + TimeEffects",
            data=p2, drop_absorbed=True,
        )
        res3e = m3e.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        key_params = ["deficit_x_epi", "days_rest_diff", "relative_interstate_dis",
                      "rest_x_epi", "interstate_x_epi"]
        print(f"  {'Parameter':<25}  {'Coef':>8}  {'SE':>7}  {'P-val':>9}  Sig")
        print(f"  {'-'*55}")
        for p_name in key_params:
            if p_name not in res3e.params.index:
                print(f"  {p_name:<25}  [absorbed/dropped]")
                continue
            c  = res3e.params[p_name]
            s  = res3e.std_errors[p_name]
            pv = res3e.pvalues[p_name]
            sig = "***" if pv < 0.01 else ("**" if pv < 0.05 else ("*" if pv < 0.10 else "ns"))
            print(f"  {p_name:<25}  {c:>+8.4f}  {s:>7.4f}  {pv:>9.4f}  {sig}")
        c_dx = res3e.params.get("deficit_x_epi", np.nan)
        p_dx = res3e.pvalues.get("deficit_x_epi", np.nan)
        print(f"\n  KEY: deficit_x_epi coef={c_dx:+.4f}  p={p_dx:.4f}")
        if p_dx >= 0.10:
            print(f"  RESULT: deficit_x_epi remains null after fatigue×EPI interactions.")
            print(f"  The confound does not explain the null result.")
        else:
            print(f"  RESULT: Significance changes with interactions — confound threat is real.")
    except Exception as e:
        log.error("Model 3 Extended failed: %s", e)

    # --- Model 5 extended: Mediation + Fatigue×EPI interactions ---
    print(f"\n  --- Model 5 Extended (Mediation + Fatigue×EPI Interactions) ---")
    log.info("Fitting Model 5 Extended ...")
    try:
        m5e = PanelOLS.from_formula(
            "home_fk_diff ~ deficit_x_epi "
            "+ days_rest_diff + relative_interstate_dis "
            "+ rest_x_epi + interstate_x_epi "
            "+ cp_diff + kicks_diff + clearance_diff "
            "+ EntityEffects + TimeEffects",
            data=p2, drop_absorbed=True,
        )
        res5e = m5e.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        key5 = ["deficit_x_epi", "rest_x_epi", "interstate_x_epi", "cp_diff"]
        print(f"  {'Parameter':<25}  {'Coef':>8}  {'SE':>7}  {'P-val':>9}  Sig")
        print(f"  {'-'*55}")
        for p_name in key5:
            if p_name not in res5e.params.index:
                continue
            c  = res5e.params[p_name]
            s  = res5e.std_errors[p_name]
            pv = res5e.pvalues[p_name]
            sig = "***" if pv < 0.01 else ("**" if pv < 0.05 else ("*" if pv < 0.10 else "ns"))
            print(f"  {p_name:<25}  {c:>+8.4f}  {s:>7.4f}  {pv:>9.4f}  {sig}")
    except Exception as e:
        log.error("Model 5 Extended failed: %s", e)


# ===========================================================================
# Challenge 3 – Exogenous Nominal Game Time for Rate Normalisation
# ===========================================================================

def challenge3_nominal_game_time(df: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 3: Exogenous Nominal Game Time for Rate Normalisation")
    print(SEP)
    print(
        "  Reviewer critique 1: game_time_mins is partially endogenous — actual clock\n"
        "  time includes stoppage time for whistles, creating simultaneity with FK volume.\n"
        "  Reviewer critique 2: we warned against per-disposal CP denominators but then\n"
        "  reported CPR = total_cp / total_di in some tables.\n"
        "\n"
        "  Fix: define nominal game time from AFL rules:\n"
        "    2020 -> 4 x 16 = 64 nominal minutes\n"
        "    2012-2019 -> 4 x 20 = 80 nominal minutes\n"
        "  Recalculate ALL rate metrics (FK/60, TK/60, CP/60) using this exogenous\n"
        "  denominator. Print the updated comparison table.\n"
    )

    df2 = df.copy()

    # --- Nominal quarter lengths ---
    df2["quarter_mins"] = np.where(df2["season"] == 2020, 16.0, 20.0)
    df2["nominal_game_time"] = df2["quarter_mins"] * 4.0  # 64 or 80 min

    # Total counts
    df2["total_fk"]  = df2["home_fk_for"] + df2["away_fk_for"]
    df2["total_tk"]  = df2["home_tk"]      + df2["away_tk"]
    df2["total_cp"]  = df2["home_cp"]      + df2["away_cp"]
    df2["total_di"]  = df2["home_di"]      + df2["away_di"]
    df2["total_i50"] = df2["home_i50"]     + df2["away_i50"]
    df2["total_mi50"]= df2["home_mi50"]    + df2["away_mi50"]
    df2["total_cl"]  = df2["home_cl"]      + df2["away_cl"]

    t_nom = df2["nominal_game_time"].clip(lower=20)  # guard

    # Nominal per-60-min rates (challenger)
    df2["fk_p60_nom"]  = df2["total_fk"]  / t_nom * 60
    df2["tk_p60_nom"]  = df2["total_tk"]  / t_nom * 60
    df2["cp_p60_nom"]  = df2["total_cp"]  / t_nom * 60

    # Retain actual-time rates for comparison
    t_act = df2["game_time_mins"].clip(lower=20)
    df2["fk_p60_act"]  = df2["total_fk"]  / t_act * 60
    df2["tk_p60_act"]  = df2["total_tk"]  / t_act * 60
    df2["cp_p60_act"]  = df2["total_cp"]  / t_act * 60

    # Endogenous disposal-denominated CPR for contrast
    di_safe = df2["total_di"].clip(lower=1)
    i50_safe = df2["total_i50"].clip(lower=1)
    df2["cpr_disposal"]  = df2["total_cp"]  / di_safe        # endogenous
    df2["fwd_eff"]       = df2["total_mi50"] / i50_safe      # ratio — unaffected by time

    baseline = df2[df2["season"] < 2020].copy()
    covid    = df2[df2["season"] == 2020].copy()

    def _compare(metric_label, b_col, c_col, format_pct=True):
        b = baseline[b_col].dropna()
        c = covid[c_col].dropna()
        t, p = stats.ttest_ind(b, c, equal_var=False)
        chg = 100 * (c.mean() - b.mean()) / b.mean() if format_pct else (c.mean() - b.mean())
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        chg_str = f"{chg:>+8.1f}%" if format_pct else f"{chg:>+8.3f}"
        return b.mean(), c.mean(), chg_str, p, sig

    print(f"\n  {'Metric':<38}  {'Baseline':>10}  {'2020':>9}  {'Change':>8}  {'P-val':>9}  Sig")
    print(f"  {'-'*82}")

    rows = [
        ("FK/60 min (NOMINAL denom)",           "fk_p60_nom",   "fk_p60_nom", True),
        ("FK/60 min (ACTUAL denom, prev spec)",  "fk_p60_act",   "fk_p60_act", True),
        ("TK/60 min (NOMINAL denom)",           "tk_p60_nom",   "tk_p60_nom", True),
        ("TK/60 min (ACTUAL denom, prev spec)",  "tk_p60_act",   "tk_p60_act", True),
        ("CP/60 min (NOMINAL denom) [FIX]",     "cp_p60_nom",   "cp_p60_nom", True),
        ("CPR disposal-based [ENDOGENOUS]",      "cpr_disposal", "cpr_disposal", True),
        ("Forward Efficiency (MI50/I50) [ratio]","fwd_eff",      "fwd_eff",    True),
    ]

    for label, b_col, c_col, pct in rows:
        b_m, c_m, chg_s, p_val, sig = _compare(label, b_col, c_col, format_pct=pct)
        print(f"  {label:<38}  {b_m:>10.3f}  {c_m:>9.3f}  {chg_s:>8}  {p_val:>9.4f}  {sig}")

    print(f"\n  INTERPRETATION:")
    print(f"  Nominal denominators eliminate the stoppage-time endogeneity critique.")
    print(f"  CPR computed per nominal minute (not per disposal) removes the endogenous")
    print(f"  denominator concern raised for Contested Possessions rates.")
    print(f"  Comparison with actual-time denominators shows the direction and magnitude")
    print(f"  of any bias introduced by using actual vs. nominal game time.")

    # Report raw game times for reference
    print(f"\n  Game Time Reference:")
    print(f"    Baseline mean actual game time:  {baseline['game_time_mins'].mean():.1f} min")
    print(f"    2020 mean actual game time:       {covid['game_time_mins'].mean():.1f} min")
    print(f"    Empirical ratio (2020/baseline):  {covid['game_time_mins'].mean() / baseline['game_time_mins'].mean():.4f}")
    print(f"    Nominal baseline game time:       80 min   (4x20)")
    print(f"    Nominal 2020 game time:           64 min   (4x16)")
    print(f"    Nominal ratio:                    {64/80:.4f}")


# ===========================================================================
# Challenge 4 – Grid-Search Bug Fix
# ===========================================================================

def challenge4_grid_bug_fix() -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 4: Grid-Search Bug Fix (Fan-Split Override)")
    print(SEP)
    print(
        "  Reviewer critique: exactly p=0.211 across all 12 grid points indicates\n"
        "  a bug where the loop did not actually update the underlying EPI parameter.\n"
        "\n"
        "  Root cause (confirmed by code inspection):\n"
        "  load_pipeline() set df['fan_split'] via the override, then called\n"
        "  compute_epi(df). However, compute_epi() (line 633-635 in original)\n"
        "  unconditionally overwrites df['fan_split'] by calling fan_split_multiplier\n"
        "  for every row — defeating the pre-computed override. Result: every grid\n"
        "  point uses the default 0.85/0.50 weights, producing identical EPI columns\n"
        "  and therefore identical p-values.\n"
        "\n"
        "  Fix: compute_epi_fixed() (defined in this script) skips the fan_split\n"
        "  recomputation step when the column already exists in df.\n"
    )

    # Demonstrate the bug is fixed: run 2 points and confirm coefficients differ
    non_vic_grid  = [0.65, 0.75, 0.85, 0.95]
    vic_derby_grid = [0.35, 0.50, 0.65]

    sens_results = []
    n_grid = len(non_vic_grid) * len(vic_derby_grid)
    log.info("Running FIXED sensitivity grid (%d configurations) ...", n_grid)

    for nv_w, vd_w in product(non_vic_grid, vic_derby_grid):
        _, p_sens = load_pipeline(fan_split_overrides={"non_vic": nv_w, "vic_derby": vd_w})
        res = _run_model2(p_sens, f"nv={nv_w:.2f} vd={vd_w:.2f}")
        res["non_vic"]   = nv_w
        res["vic_derby"] = vd_w
        sens_results.append(res)
        log.info("  nv=%.2f  vd=%.2f  ->  coef=%+.4f  p=%.4f",
                 nv_w, vd_w, res["coef"], res["pval"])

    sens_df = pd.DataFrame(sens_results)

    print(f"\n  FIXED Sensitivity Grid — deficit_x_epi (Model 2)")
    print(f"  {'Non-VIC w':>9}  {'VIC Derby w':>11}  {'Coef':>8}  {'SE':>7}  {'P-val':>9}  Sig")
    print(f"  {'-'*56}")
    for _, row in sens_df.iterrows():
        sig = "***" if row["pval"] < 0.01 else ("**" if row["pval"] < 0.05
              else ("*" if row["pval"] < 0.10 else "ns"))
        mark = " <-- BASELINE" if (abs(row["non_vic"] - 0.85) < 0.01
                                    and abs(row["vic_derby"] - 0.50) < 0.01) else ""
        print(f"  {row['non_vic']:>9.2f}  {row['vic_derby']:>11.2f}  "
              f"{row['coef']:>+8.4f}  {row['se']:>7.4f}  {row['pval']:>9.4f}  {sig}{mark}")

    n_sig  = (sens_df["pval"] < 0.05).sum()
    n_null = (sens_df["pval"] >= 0.05).sum()
    coef_range = sens_df["coef"].max() - sens_df["coef"].min()
    p_range    = sens_df["pval"].max() - sens_df["pval"].min()

    print(f"\n  Coefficient range: [{sens_df['coef'].min():+.4f}, {sens_df['coef'].max():+.4f}]"
          f"  (span = {coef_range:.4f})")
    print(f"  P-value range:     [{sens_df['pval'].min():.4f}, {sens_df['pval'].max():.4f}]"
          f"  (span = {p_range:.4f})")
    print(f"  Null (p>=0.05): {n_null}/{n_grid}  |  Significant: {n_sig}/{n_grid}")

    if coef_range < 0.0001:
        print(f"\n  BUG NOT FIXED: coefficients still identical. Inspect compute_epi_fixed().")
    else:
        print(f"\n  BUG CONFIRMED FIXED: coefficients now vary across grid points.")
        if n_null == n_grid:
            print(f"  NULL RESULT IS ROBUST: survives all {n_grid} fan-split weight configurations.")
        elif n_null >= int(0.8 * n_grid):
            print(f"  LARGELY ROBUST: null in {n_null}/{n_grid} specs.")
        else:
            print(f"  NOTE: null fails in {n_sig}/{n_grid} configurations — requires attention.")


# ===========================================================================
# Challenge 5 – Tactical Differentials & 2020 Q4 Scoring Margins
# ===========================================================================

def _parse_qtr_scores(html: str) -> dict | None:
    """Parse cumulative quarter scores from AFL Tables HTML."""
    soup = BeautifulSoup(html, "html.parser")
    tbls = soup.find_all("table")
    if not tbls:
        return None
    rows = tbls[0].find_all("tr")
    if len(rows) < 3:
        return None

    def _bolds(row):
        return [
            int(b.get_text(strip=True).replace(",", ""))
            for b in row.find_all("b")
            if b.get_text(strip=True).lstrip("-").isdigit()
        ][:4]

    home_cum = _bolds(rows[1])
    away_cum = _bolds(rows[2])
    if len(home_cum) < 4 or len(away_cum) < 4:
        return None

    def _incr(c):
        return [c[0]] + [c[i] - c[i-1] for i in range(1, 4)]

    hq = _incr(home_cum)
    aq = _incr(away_cum)
    return {f"home_q{i+1}": hq[i] for i in range(4)} | {f"away_q{i+1}": aq[i] for i in range(4)}


def challenge5_tactical_differentials_and_q4(df: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 5: Tactical Differentials & 2020 Quarter-by-Quarter Margins")
    print(SEP)
    print(
        "  Reviewer critiques:\n"
        "  (a) A global reduction in tackles/FK does not prove the HOME TEAM lost\n"
        "      its physical advantage. Report the home-away DIFFERENTIAL for\n"
        "      Contested Possessions and Clearances.\n"
        "  (b) Quarter-level 2020 scoring margins were not provided. Report them.\n"
    )

    # ---- Part A: Tactical differentials (home - away) ----------------------
    print(f"\n  --- 5A: Home-Away Tactical Differentials ---")

    df2 = df.copy()
    df2["cp_diff"]        = df2["home_cp"]    - df2["away_cp"]
    df2["clearance_diff"] = df2["home_cl"]    - df2["away_cl"]
    df2["tk_diff"]        = df2["home_tk"]    - df2["away_tk"]
    df2["di_diff"]        = df2["home_di"]    - df2["away_di"]

    baseline = df2[df2["season"] < 2020].copy()
    covid    = df2[df2["season"] == 2020].copy()

    tac_metrics = [
        ("CP Differential (home_cp - away_cp)",   "cp_diff"),
        ("Clearance Diff (home_cl - away_cl)",     "clearance_diff"),
        ("Tackle Diff (home_tk - away_tk)",        "tk_diff"),
        ("Disposal Diff (home_di - away_di)",      "di_diff"),
        ("FK Differential (home_fk - away_fk)",   "home_fk_diff"),
    ]

    print(f"\n  {'Metric':<40}  {'Baseline':>10}  {'2020':>9}  {'Change':>8}  {'P-val':>9}  Sig")
    print(f"  {'-'*82}")
    for label, col in tac_metrics:
        b = baseline[col].dropna()
        c = covid[col].dropna()
        if len(b) == 0 or len(c) == 0:
            continue
        t, p = stats.ttest_ind(b, c, equal_var=False)
        chg  = c.mean() - b.mean()
        sig  = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        print(f"  {label:<40}  {b.mean():>+10.3f}  {c.mean():>+9.3f}  {chg:>+8.3f}  {p:>9.4f}  {sig}")

    print(f"\n  INTERPRETATION:")
    print(f"  A value near zero indicates the home team lost its differential advantage")
    print(f"  in that dimension in 2020. A significantly reduced CP or Clearance")
    print(f"  differential supports the democratised-fatigue mechanism.")

    # ---- Part B: Parse Q-by-Q scoring margins from HTML -------------------
    print(f"\n  --- 5B: Per-Quarter Home Scoring Margins (Baseline & 2020) ---")

    records = []
    match_info = df[["season", "match_url"]].copy()

    for _, row in match_info.iterrows():
        season = int(row["season"])
        url    = row["match_url"]
        game_part = url.split("stats/games/")[-1]
        fname = re.sub(r"[^a-z0-9]", "_", game_part.lower()).strip("_")
        cache_f = CACHE_DIR / f"match_{fname}"
        if not cache_f.exists():
            continue
        html = cache_f.read_text(encoding="utf-8", errors="replace")
        parsed = _parse_qtr_scores(html)
        if parsed is None:
            continue
        rec = {"season": season}
        for q in [1, 2, 3, 4]:
            rec[f"margin_q{q}"] = parsed[f"home_q{q}"] - parsed[f"away_q{q}"]
        records.append(rec)

    if not records:
        print(f"  No cached HTML found in {CACHE_DIR}. Skipping Q4 parsing.")
        return

    qdf = pd.DataFrame(records)
    base_q = qdf[qdf["season"] < 2020].copy()
    cov_q  = qdf[qdf["season"] == 2020].copy()
    log.info("Q4 dataset: %d baseline + %d 2020 matches parsed", len(base_q), len(cov_q))

    print(f"\n  Per-Quarter Home Scoring Margin — Baseline 2012–2019 vs 2020:")
    print(f"  {'Quarter':<10}  {'Baseline Mean':>14}  {'2020 Mean':>12}  "
          f"{'Change':>8}  {'t-stat':>7}  {'P-val':>9}  Sig")
    print(f"  {'-'*78}")
    for q in [1, 2, 3, 4]:
        b = base_q[f"margin_q{q}"].dropna()
        c = cov_q[f"margin_q{q}"].dropna()
        t, p = stats.ttest_ind(b, c, equal_var=False)
        chg = c.mean() - b.mean()
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        print(f"  {'Q'+str(q):<10}  {b.mean():>+14.3f}  {c.mean():>+12.3f}  "
              f"{chg:>+8.3f}  {t:>+7.3f}  {p:>9.4f}  {sig}")

    # Year-by-year Q4 for context
    print(f"\n  Year-by-Year Q4 Home Scoring Margin:")
    print(f"  {'Season':<8}  {'Q1':>7}  {'Q2':>7}  {'Q3':>7}  {'Q4':>7}  {'Q4-Q1':>9}")
    print(f"  {'-'*52}")
    for yr in sorted(qdf["season"].unique()):
        sub = qdf[qdf["season"] == yr]
        ms = [sub[f"margin_q{q}"].mean() for q in [1,2,3,4]]
        mark = " <-- 2020" if yr == 2020 else ""
        print(f"  {yr:<8}  {ms[0]:>+7.2f}  {ms[1]:>+7.2f}  {ms[2]:>+7.2f}  {ms[3]:>+7.2f}"
              f"  {ms[3]-ms[0]:>+9.2f}{mark}")

    # Q4 vs Q1 premium test
    b_q1 = base_q["margin_q1"].mean()
    b_q4 = base_q["margin_q4"].mean()
    c_q1 = cov_q["margin_q1"].mean()
    c_q4 = cov_q["margin_q4"].mean()
    print(f"\n  Q4 Premium (Q4 margin minus Q1 margin):")
    print(f"    Baseline: Q1={b_q1:+.3f}  Q4={b_q4:+.3f}  Premium={b_q4-b_q1:+.3f}")
    print(f"    2020:     Q1={c_q1:+.3f}  Q4={c_q4:+.3f}  Premium={c_q4-c_q1:+.3f}")
    t_q4, p_q4 = stats.ttest_ind(base_q["margin_q4"], cov_q["margin_q4"], equal_var=False)
    t_q1, p_q1 = stats.ttest_ind(base_q["margin_q1"], cov_q["margin_q1"], equal_var=False)
    print(f"    Q4 t-test (baseline vs 2020): t={t_q4:+.3f}  p={p_q4:.4f}")
    print(f"    Q1 t-test (baseline vs 2020): t={t_q1:+.3f}  p={p_q1:.4f}")


# ===========================================================================
# Challenge 6 – Model 1 Degeneracy: Additive Home + Away Team FEs
# ===========================================================================

def challenge6_model1_additive_fes(df: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  CHALLENGE 6: Model 1 Degeneracy — Additive Home + Away Team Fixed Effects")
    print(SEP)
    print(
        "  Reviewer critique: undirected pair FEs against an antisymmetric outcome\n"
        "  (home FK - away FK) are degenerate. When teams A and B swap home/away,\n"
        "  the undirected FE is the same entity but the outcome flips sign, so\n"
        "  the FE cancels to zero on expectation — the estimator is ill-specified.\n"
        "\n"
        "  Fix: replace undirected pair FE with ADDITIVE HOME_TEAM + AWAY_TEAM\n"
        "  dummy variables. This allows each team's typical home-advantage and\n"
        "  away-deficit to enter separately, without the antisymmetry problem.\n"
        "  Implementation: OLS with C(home_team) + C(away_team) + C(season).\n"
    )

    # Filter to 2012-2020 study window, require key columns
    d = df.copy()
    required = ["home_fk_diff", "deficit_ratio", "epi_z", "deficit_x_epi",
                "home_team", "away_team", "season"]
    d = d.dropna(subset=required)

    # Additive team + season dummies via OLS
    log.info("Fitting Model 1 ADDITIVE (OLS + home_team + away_team + season dummies) ...")
    try:
        formula_add = (
            "home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi "
            "+ C(home_team) + C(away_team) + C(season)"
        )
        res_add = smf.ols(formula_add, data=d).fit(
            cov_type="HC1"   # heteroskedasticity-robust; cluster not easily available in smf OLS
        )

        coef_dx = res_add.params.get("deficit_x_epi", np.nan)
        se_dx   = res_add.bse.get("deficit_x_epi", np.nan)
        pval_dx = res_add.pvalues.get("deficit_x_epi", np.nan)
        ci_dx   = res_add.conf_int().loc["deficit_x_epi"]
        coef_dr = res_add.params.get("deficit_ratio", np.nan)
        pval_dr = res_add.pvalues.get("deficit_ratio", np.nan)
        coef_ez = res_add.params.get("epi_z", np.nan)
        pval_ez = res_add.pvalues.get("epi_z", np.nan)

        sig = "***" if pval_dx < 0.01 else ("**" if pval_dx < 0.05
              else ("*" if pval_dx < 0.10 else "not significant"))

        print(f"\n  Model 1 (ADDITIVE FEs): OLS with home_team + away_team + season dummies")
        print(f"  N obs:        {int(res_add.nobs)}")
        print(f"  R-squared:    {res_add.rsquared:.4f}")
        print(f"  Key parameters:")
        print(f"  {'Parameter':<22}  {'Coef':>8}  {'SE':>7}  {'P-val':>9}  Sig")
        print(f"  {'-'*52}")
        for name, c, p in [
            ("deficit_x_epi", coef_dx, pval_dx),
            ("deficit_ratio",  coef_dr, pval_dr),
            ("epi_z",          coef_ez, pval_ez),
        ]:
            s = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else "ns"))
            print(f"  {name:<22}  {c:>+8.4f}  {res_add.bse.get(name, np.nan):>7.4f}"
                  f"  {p:>9.4f}  {s}")

        print(f"\n  deficit_x_epi 95% CI: [{ci_dx.iloc[0]:+.4f}, {ci_dx.iloc[1]:+.4f}]")
        print(f"  Result: {sig}")

        if pval_dx >= 0.10:
            print(f"\n  CONCLUSION: Additive-FE Model 1 confirms the null result.")
            print(f"  The undirected-pair FE degeneracy does not drive our finding.")
        else:
            print(f"\n  NOTE: Significance shifts under additive FEs. Review the structure.")

        # Compare: run PanelOLS with directed FEs for direct comparison
        print(f"\n  --- Comparison: Directed FE Model 2 (for reference) ---")
        panel_d = build_panel(d, entity_col="matchup_directed_id")
        res_m2 = _run_model2(panel_d, "Model 2 (Directed FEs)")
        print(f"  deficit_x_epi  coef={res_m2['coef']:+.4f}  se={res_m2['se']:.4f}"
              f"  p={res_m2['pval']:.4f}  n={res_m2['n']}")

    except Exception as e:
        log.error("Model 1 additive FEs failed: %s", e)


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print(f"\n{SEP}")
    print("  AFL 'Noise of Affirmation' — Peer Review Round 2 Robustness Checks")
    print(f"{SEP}\n")
    print(
        "  Responding to six reviewer challenges:\n"
        "    1. Event-study reference year (2019 trough) + detrending collinearity\n"
        "    2. Heterogeneous fatigue×EPI confound in Models 3 and 5\n"
        "    3. Nominal game time denominator (eliminate stoppage-time endogeneity)\n"
        "    4. Grid-search bug fix (fan-split override silently defeated)\n"
        "    5. Tactical differentials (CP, CL) + 2020 per-quarter scoring margins\n"
        "    6. Model 1 degeneracy (additive home+away team FEs)\n"
    )

    log.info("Loading pipeline (2012-2020 study window) ...")
    df, panel = load_pipeline()
    log.info("Pipeline ready: %d match-level rows", len(df))

    challenge1_event_study_fix(df, panel)
    challenge2_fatigue_epi_interactions(panel)
    challenge3_nominal_game_time(df)
    challenge4_grid_bug_fix()
    challenge5_tactical_differentials_and_q4(df)
    challenge6_model1_additive_fes(df)

    print(f"\n{SEP}")
    print("  All six challenges addressed. Review printed outputs above.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
