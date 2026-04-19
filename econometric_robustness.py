"""
econometric_robustness.py
=========================
Three identification robustness checks for the AFL "Noise of Affirmation" study.

  Task 1 - Naive Attendance Model   : Raw pre-treatment attendance as treatment.
                                       Expected to find spurious significance due
                                       to the "Away Fan Fallacy" (endogeneity).
                                       Justifies the EPI instrument.

  Task 2 - Placebo Test             : Fake treatment year (2018 as lockout year,
                                       2020 excluded). Must return a null result.

  Task 3 - Event-Study / Parallel   : Year-by-year EPIxYear_Dummy interactions
             Trends Plot              with 2019 as the omitted reference year.
                                       2012-2018 coefficients must hover at zero
                                       to satisfy the parallel trends assumption.

Depends on the shared pipeline in afl_noise_affirmation_did.py and the
pre-built afl_cache/raw_panel.parquet.
"""

import warnings
import logging

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from linearmodels.panel import PanelOLS

# Pull the shared pipeline helpers
from afl_noise_affirmation_did import (
    clean_data,
    compute_epi,
    calculate_cpi_metrics,
    build_panel,
    _setup_style,
    ACCENT_NORMAL,
    ACCENT_COVID,
    ACCENT_EFFECT,
    SEASONS,
)

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SEP = "=" * 78

# ---------------------------------------------------------------------------
# Shared data loading helper
# ---------------------------------------------------------------------------

def load_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load raw parquet, run the full feature-engineering pipeline, and return
    both the match-level DataFrame and the aggregated panel MultiIndex df.
    """
    log.info("Loading raw panel from cache ...")
    raw = pd.read_parquet("afl_cache/raw_panel.parquet")

    cleaned  = clean_data(raw)
    featured = compute_epi(cleaned)
    featured = calculate_cpi_metrics(featured)
    panel    = build_panel(featured)

    log.info("Panel loaded: %d obs, %d matchups",
             len(panel), panel.index.get_level_values("matchup_id").nunique())
    return featured, panel


# ---------------------------------------------------------------------------
# Task 1 - Naive Attendance Model (endogeneity comparison)
# ---------------------------------------------------------------------------

def task1_naive_attendance(panel: pd.DataFrame) -> None:
    """
    Replace EPI with raw historical attendance as the continuous treatment.

    The 'Away Fan Fallacy' predicts that this naive model will falsely recover
    a significant crowd coefficient, because big crowd != partisan crowd.
    Contrasting this result with our EPI model empirically justifies the
    instrument construction.
    """
    print(f"\n{SEP}")
    print("  TASK 1 - Naive Attendance Model (endogeneity benchmark)")
    print(f"{SEP}")
    print(
        "  Theory: Raw attendance conflates stadium size with crowd allegiance.\n"
        "  A big MCG derby crowd is 50/50, a small GMHBA crowd is 95% Geelong.\n"
        "  We expect this model to find a spurious significant coefficient,\n"
        "  empirically motivating the EPI instrument.\n"
    )

    p = panel.copy().reset_index()

    # Standardise raw historical attendance using pre-2020 fit
    pre_mask = p["season"] < 2020
    att_mean = p.loc[pre_mask, "attendance"].mean()
    att_std  = p.loc[pre_mask, "attendance"].std()
    p["attendance_z"] = (p["attendance"] - att_mean) / att_std

    # Naive interaction: deficit_ratio x raw attendance_z
    p["deficit_x_att"] = p["deficit_ratio"] * p["attendance_z"]

    p = p.set_index(["matchup_id", "season"])
    required = ["home_fk_diff", "deficit_ratio", "attendance_z",
                "deficit_x_att", "cp_diff", "kicks_diff", "clearance_diff"]
    p_clean = p.dropna(subset=required)

    log.info("Task 1: fitting naive attendance model on %d obs ...", len(p_clean))
    m_naive = PanelOLS.from_formula(
        "home_fk_diff ~ deficit_ratio + attendance_z + deficit_x_att "
        "+ cp_diff + kicks_diff + clearance_diff "
        "+ EntityEffects + TimeEffects",
        data=p_clean,
        drop_absorbed=True,
    )
    res_naive = m_naive.fit(cov_type="clustered", cluster_entity=True)

    print(res_naive.summary.tables[1])

    # Highlight the key coefficient
    coef = res_naive.params["deficit_x_att"]
    pval = res_naive.pvalues["deficit_x_att"]
    sig  = "*** p<0.01" if pval < 0.01 else ("** p<0.05" if pval < 0.05
           else ("* p<0.10" if pval < 0.10 else "not significant"))
    print(f"\n  >>  deficit x raw_attendance  coef = {coef:+.4f}  ({sig})")
    print(
        "  Compare this to Model 3 (EPI): deficit_x_epi was NOT significant.\n"
        "  If naive attendance IS significant, it proves EPI removes endogeneity.\n"
    )


# ---------------------------------------------------------------------------
# Task 2 - Placebo Test (fake treatment year = 2018)
# ---------------------------------------------------------------------------

def task2_placebo(featured: pd.DataFrame) -> None:
    """
    Drop 2020. Pretend 2018 is the lockout year (deficit_ratio = 1.0 for all
    2018 games). Re-run the continuous DiD. Must return a null result on
    deficit_x_epi to rule out spurious fixed-effect absorption.
    """
    print(f"\n{SEP}")
    print("  TASK 2 - Placebo Test (fake lockout: 2018, drop 2020)")
    print(f"{SEP}")
    print(
        "  Null hypothesis: if the 2020 result is real and not an artefact\n"
        "  of our fixed-effect specification, a fake treatment year (2018)\n"
        "  must produce a statistically insignificant coefficient.\n"
    )

    # Work from match-level data and rebuild panel with placebo assignment
    df = featured.copy()

    # Drop 2020 entirely
    df = df[df["season"] != 2020].copy()

    # Assign placebo: 2018 treated as a full lockout (deficit_ratio = 1.0)
    df["deficit_ratio_placebo"] = np.where(df["season"] == 2018,
                                            1.0,
                                            df["deficit_ratio"])
    df["deficit_x_epi_placebo"] = df["deficit_ratio_placebo"] * df["epi_z"]

    # Build a fresh panel with the placebo columns
    from afl_noise_affirmation_did import build_panel as _bp
    p_placebo = _bp(df)

    # Swap in the placebo columns (re-aggregate already happened above via build_panel)
    # We need the placebo columns to survive the aggregation - recalculate post-agg
    p = p_placebo.copy().reset_index()
    pre_mask = p["season"] != 2018
    p["deficit_ratio_placebo"] = np.where(p["season"] == 2018, 1.0, 0.0)
    p["deficit_x_epi_placebo"] = p["deficit_ratio_placebo"] * p["epi_z"]
    p = p.set_index(["matchup_id", "season"])

    required = ["home_fk_diff", "deficit_ratio_placebo",
                "epi_z", "deficit_x_epi_placebo",
                "cp_diff", "kicks_diff", "clearance_diff"]
    p_clean = p.dropna(subset=required)

    log.info("Task 2: placebo panel has %d obs (2012-2019, excl. 2020) ...",
             len(p_clean))
    m_placebo = PanelOLS.from_formula(
        "home_fk_diff ~ deficit_ratio_placebo + epi_z + deficit_x_epi_placebo "
        "+ cp_diff + kicks_diff + clearance_diff "
        "+ EntityEffects + TimeEffects",
        data=p_clean,
        drop_absorbed=True,
    )
    res_placebo = m_placebo.fit(cov_type="clustered", cluster_entity=True)

    print(res_placebo.summary.tables[1])

    coef = res_placebo.params["deficit_x_epi_placebo"]
    pval = res_placebo.pvalues["deficit_x_epi_placebo"]
    sig  = "*** p<0.01" if pval < 0.01 else ("** p<0.05" if pval < 0.05
           else ("* p<0.10" if pval < 0.10 else "PASS NOT SIGNIFICANT - placebo passes"))
    print(f"\n  >>  deficit_x_epi (PLACEBO 2018)  coef = {coef:+.4f}  ({sig})\n")


# ---------------------------------------------------------------------------
# Task 3 - Event-Study / Parallel Trends Plot
# ---------------------------------------------------------------------------

def task3_event_study(panel: pd.DataFrame,
                      out_path: str = "figure_event_study.png") -> None:
    """
    Dynamic event-study specification.

    Interact EPI with individual year dummies (2012-2020), omitting 2019
    as the reference year. Plot coefficients + 95% CI.

    Pre-treatment coefficients (2012-2018) should hover around zero,
    validating parallel trends. The 2020 coefficient should deviate
    if the crowd shock has a real effect.
    """
    print(f"\n{SEP}")
    print("  TASK 3 - Event-Study: Parallel Trends Test")
    print(f"{SEP}")
    print(
        "  Reference year: 2019 (omitted dummy).\n"
        "  Pre-treatment years 2012-2018 must show zero coefficients.\n"
        "  The 2020 shock is the only year allowed to deviate.\n"
    )

    p = panel.copy().reset_index()

    # Create year dummies, dropping 2019 (reference)
    years = sorted(p["season"].unique())
    ref_year = 2019
    non_ref_years = [y for y in years if y != ref_year]

    for yr in non_ref_years:
        p[f"yr_{yr}"] = (p["season"] == yr).astype(float)
        p[f"epi_x_{yr}"] = p["epi_z"] * p[f"yr_{yr}"]

    p = p.set_index(["matchup_id", "season"])

    # Build formula: epi_z (reference-year level) + interactions for each year
    interaction_terms = " + ".join(f"epi_x_{yr}" for yr in non_ref_years)
    formula = (
        f"home_fk_diff ~ epi_z + {interaction_terms} "
        f"+ cp_diff + kicks_diff + clearance_diff "
        f"+ EntityEffects + TimeEffects"
    )

    required_base = ["home_fk_diff", "epi_z", "cp_diff", "kicks_diff", "clearance_diff"]
    required_int  = [f"epi_x_{yr}" for yr in non_ref_years]
    p_clean = p.dropna(subset=required_base)

    log.info("Task 3: fitting event-study model on %d obs ...", len(p_clean))
    m_es = PanelOLS.from_formula(formula, data=p_clean, drop_absorbed=True)
    res_es = m_es.fit(cov_type="clustered", cluster_entity=True)

    # Extract coefficients for the EPIxYear interaction terms
    coefs, lows, highs, yr_labels = [], [], [], []
    ci = res_es.conf_int()

    for yr in non_ref_years:
        term = f"epi_x_{yr}"
        if term in res_es.params.index:
            coefs.append(res_es.params[term])
            lows.append(ci.loc[term, "lower"])
            highs.append(ci.loc[term, "upper"])
            yr_labels.append(yr)

    # Insert the reference year (2019) with coefficient = 0 and CI = 0
    insert_pos = yr_labels.index(2020) if 2020 in yr_labels else len(yr_labels)
    yr_labels.insert(insert_pos, ref_year)
    coefs.insert(insert_pos, 0.0)
    lows.insert(insert_pos, 0.0)
    highs.insert(insert_pos, 0.0)

    print("\n  Year-by-year EPI interaction coefficients (ref = 2019):")
    print(f"  {'Year':>6}  {'Coef':>8}  {'95% CI':>20}  {'p-value':>8}")
    print("  " + "-" * 50)
    for i, yr in enumerate(yr_labels):
        if yr == ref_year:
            print(f"  {yr:>6}  {'0.000':>8}  {'[reference]':>20}  {'-':>8}")
            continue
        term = f"epi_x_{yr}"
        pval = res_es.pvalues.get(term, np.nan)
        stars = "***" if pval < 0.01 else ("**" if pval < 0.05
                else ("*" if pval < 0.10 else ""))
        ci_str = f"[{lows[i]:+.3f}, {highs[i]:+.3f}]"
        print(f"  {yr:>6}  {coefs[i]:>+8.3f}  {ci_str:>20}  {pval:>7.4f}{stars}")

    # -----------------------------------------------------------------------
    # Plot
    # -----------------------------------------------------------------------
    _setup_style()
    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")

    xs = list(range(len(yr_labels)))
    x_to_yr = dict(zip(xs, yr_labels))

    # Error bars
    errs_lo = [c - l for c, l in zip(coefs, lows)]
    errs_hi = [h - c for c, h in zip(coefs, highs)]

    pre_mask  = [y < 2020 for y in yr_labels]
    post_mask = [y == 2020 for y in yr_labels]
    ref_mask  = [y == ref_year for y in yr_labels]

    def _plot_group(mask, color, label, marker="o", zorder=5):
        xs_g  = [x for x, m in zip(xs, mask) if m]
        c_g   = [c for c, m in zip(coefs, mask) if m]
        el_g  = [e for e, m in zip(errs_lo, mask) if m]
        eh_g  = [e for e, m in zip(errs_hi, mask) if m]
        ax.errorbar(xs_g, c_g, yerr=[el_g, eh_g],
                    fmt=marker, color=color, ms=9, lw=2,
                    elinewidth=1.8, capsize=5, capthick=1.8,
                    label=label, zorder=zorder)

    _plot_group(pre_mask,  ACCENT_NORMAL, "Pre-treatment (2012-2018)")
    _plot_group(post_mask, ACCENT_COVID,  "Treatment year (2020)", marker="D")
    _plot_group(ref_mask,  "#6b7280",      "Reference year (2019, omitted)", marker="s")

    # Connect dots with a thin line
    ax.plot(xs, coefs, color="#374151", lw=1.2, zorder=1, ls="--", alpha=0.6)

    # Reference lines
    ax.axhline(0, color="#6b7280", lw=1.4, ls="--", alpha=0.7, label="Zero line")
    ax.axvline(xs[yr_labels.index(ref_year)] - 0.5,
               color="#fbbf24", lw=1.2, ls=":", alpha=0.6)
    ax.axvline(xs[yr_labels.index(ref_year)] + 0.5,
               color="#fbbf24", lw=1.2, ls=":", alpha=0.6, label="Treatment boundary")

    ax.set_xticks(xs)
    ax.set_xticklabels(yr_labels, fontsize=11, color="#d1d5db")
    ax.set_xlabel("Season", fontsize=12, color="#9ca3af")
    ax.set_ylabel("EPI x Year Coefficient\n(vs. 2019 reference)", fontsize=11, color="#9ca3af")
    ax.set_title(
        "Event-Study: Parallel Trends Validation\n"
        "EPI x Season Interactions - Cluster-Robust 95% CI  (reference: 2019)",
        fontsize=13, color="#f3f4f6", pad=12,
    )
    ax.tick_params(colors="#9ca3af")
    ax.grid(True, axis="y", alpha=0.3, color="#374151")
    ax.spines["bottom"].set_color("#374151")
    ax.spines["left"].set_color("#374151")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend = ax.legend(
        fontsize=10, framealpha=0.25,
        facecolor="#1f2937", edgecolor="#374151", labelcolor="#e5e7eb",
    )

    plt.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="#0f1117")
    log.info("Event-study plot saved -> %s", out_path)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{SEP}")
    print("  AFL 'Noise of Affirmation' - Econometric Robustness Checks")
    print(f"{SEP}\n")

    featured, panel = load_panel()

    # Task 1: naive attendance benchmark
    task1_naive_attendance(panel)

    # Task 2: placebo (fake 2018 lockout)
    task2_placebo(featured)

    # Task 3: event-study parallel trends
    task3_event_study(panel, out_path="figure_event_study.png")

    print(f"\n{SEP}")
    print("  Robustness checks complete.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
