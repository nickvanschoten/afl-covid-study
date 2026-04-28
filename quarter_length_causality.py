"""
quarter_length_causality.py
============================
Definitive causal tests linking AFL 2020's 16-minute quarters to the
"Trench Warfare" game style observed in that season.

Two independent tests:

  Phase 1 – Reversion Test
      Compare CPR and Forward Efficiency across three eras:
        Baseline    (2012-2019): standard 20-min quarters
        COVID Hub   (2020):      16-min quarters
        Recovery    (2021-2023): return to 20-min quarters
      Hypothesis: if 16-min rule caused congestion, 2021-2023 must snap back
      to mirror the baseline, isolating 2020 as the sole structural anomaly.

  Phase 2 – Visualisation (figure_causality_proof.png)
      Bar chart of Forward Efficiency across three eras ("V-shape").

Dependencies: pandas, numpy, scipy, matplotlib, seaborn
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

CACHE_FILE = Path("afl_cache/raw_panel.parquet")
CACHE_DIR  = Path("afl_cache")
SEP = "=" * 72

# ---------------------------------------------------------------------------
# Era labels
# ---------------------------------------------------------------------------
ERAS = {
    "Baseline\n(2012-2019)": lambda s: s < 2020,
    "COVID Hub\n(2020)":     lambda s: s == 2020,
    "Recovery\n(2021-2023)": lambda s: s > 2020,
}
ERA_ORDER = list(ERAS.keys())
ERA_PALETTE = {
    "Baseline\n(2012-2019)": "#4ade80",   # green
    "COVID Hub\n(2020)":     "#f87171",   # red
    "Recovery\n(2021-2023)": "#60a5fa",   # blue
}


# ---------------------------------------------------------------------------
# Phase 1 – Reversion Test
# ---------------------------------------------------------------------------

def load_and_compute_metrics() -> pd.DataFrame:
    """Load raw parquet and compute CPR and Forward Efficiency."""
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"{CACHE_FILE} missing. Run extraction first.")

    df = pd.read_parquet(CACHE_FILE)
    log.info("Loaded %d rows covering seasons %s–%s",
             len(df), df["season"].min(), df["season"].max())

    required = ["home_cp", "away_cp", "home_di", "away_di",
                "home_i50", "away_i50", "home_mi50", "away_mi50", "season"]
    df = df.dropna(subset=[c for c in required if c in df.columns]).copy()

    df["total_di"]   = df["home_di"]   + df["away_di"]
    df["total_cp"]   = df["home_cp"]   + df["away_cp"]
    df["total_i50"]  = df["home_i50"]  + df["away_i50"]
    df["total_mi50"] = df["home_mi50"] + df["away_mi50"]

    df["CPR"]              = df["total_cp"]   / df["total_di"].clip(lower=1)
    df["Forward_Efficiency"] = df["total_mi50"] / df["total_i50"].clip(lower=1)

    # Assign era label
    def _era(season):
        if season < 2020:
            return "Baseline\n(2012-2019)"
        elif season == 2020:
            return "COVID Hub\n(2020)"
        else:
            return "Recovery\n(2021-2023)"

    df["era"] = df["season"].apply(_era)
    return df


def run_reversion_test(df: pd.DataFrame) -> None:
    """Print three-era summary table for CPR and Forward Efficiency."""
    print(f"\n{SEP}")
    print("  PHASE 1 – REVERSION TEST: Three-Era Comparison")
    print(SEP)
    print(
        "  Hypothesis: If 16-min quarters caused congestion, 2021-2023 stats\n"
        "  must revert to mirror the 2012-2019 baseline, isolating 2020 as\n"
        "  the sole structural anomaly.\n"
    )

    metrics = {
        "Contested Possession Rate (CPR)": "CPR",
        "Forward Efficiency (MI50 / I50)": "Forward_Efficiency",
    }

    for metric_name, col in metrics.items():
        print(f"\n  --- {metric_name} ---")
        print(f"  {'Era':<25}  {'N':>5}  {'Mean':>8}  {'Std':>8}")
        print("  " + "-" * 52)
        era_data = {}
        for era_label in ERA_ORDER:
            subset = df[df["era"] == era_label][col].dropna()
            era_data[era_label] = subset
            print(f"  {era_label.replace(chr(10), ' '):<25}  "
                  f"{len(subset):>5}  {subset.mean():>8.4f}  {subset.std():>8.4f}")

        # Pairwise t-tests: Baseline vs COVID, COVID vs Recovery, Baseline vs Recovery
        pairs = [
            ("Baseline\n(2012-2019)", "COVID Hub\n(2020)", "Baseline vs COVID"),
            ("COVID Hub\n(2020)",     "Recovery\n(2021-2023)", "COVID vs Recovery"),
            ("Baseline\n(2012-2019)", "Recovery\n(2021-2023)", "Baseline vs Recovery"),
        ]
        print(f"\n  {'Comparison':<30}  {'t-stat':>8}  {'p-value':>10}  {'Verdict':>6}")
        print("  " + "-" * 62)
        for a, b, label in pairs:
            t, p = stats.ttest_ind(era_data[a], era_data[b], equal_var=False)
            sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
            print(f"  {label:<30}  {t:>+8.3f}  {p:>10.4e}  {sig:>6}")

    # Snap-back verdict
    b_cpr  = df[df["era"] == "Baseline\n(2012-2019)"]["CPR"].mean()
    c_cpr  = df[df["era"] == "COVID Hub\n(2020)"]["CPR"].mean()
    r_cpr  = df[df["era"] == "Recovery\n(2021-2023)"]["CPR"].mean()
    b_fe   = df[df["era"] == "Baseline\n(2012-2019)"]["Forward_Efficiency"].mean()
    c_fe   = df[df["era"] == "COVID Hub\n(2020)"]["Forward_Efficiency"].mean()
    r_fe   = df[df["era"] == "Recovery\n(2021-2023)"]["Forward_Efficiency"].mean()

    cpr_revert  = abs(r_cpr - b_cpr) < abs(c_cpr - b_cpr)
    fe_revert   = abs(r_fe  - b_fe)  < abs(c_fe  - b_fe)

    print(f"\n  SNAP-BACK VERDICT:")
    print(f"    CPR  : Baseline={b_cpr:.4f}  2020={c_cpr:.4f}  Recovery={r_cpr:.4f}  "
          f"->  {'REVERSION CONFIRMED [OK]' if cpr_revert else 'No clear reversion'}")
    print(f"    FwdEff: Baseline={b_fe:.4f}  2020={c_fe:.4f}  Recovery={r_fe:.4f}   "
          f"->  {'REVERSION CONFIRMED [OK]' if fe_revert else 'No clear reversion'}")


# ---------------------------------------------------------------------------
# Phase 2 – Visualisation
# ---------------------------------------------------------------------------

def generate_causality_figure(df: pd.DataFrame, out_path: str = "figure_causality_proof.png") -> None:
    """
    Bar chart – Forward Efficiency across three eras (V-shape)
    """
    sns.set_theme(style="whitegrid")
    fig, ax0 = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#0f1117")

    # --- Bar chart of Forward Efficiency by Era ---
    era_means = (
        df.groupby("era")["Forward_Efficiency"]
        .agg(mean="mean", sem="sem")
        .reindex(ERA_ORDER)
        .reset_index()
    )
    era_labels_clean = [e.replace("\n", " ") for e in ERA_ORDER]
    colors = [ERA_PALETTE[e] for e in ERA_ORDER]

    ax0.set_facecolor("#0f1117")
    bars = ax0.bar(era_labels_clean, era_means["mean"].values, color=colors,
                   width=0.5, zorder=3, alpha=0.9, edgecolor="#1f2937", linewidth=1.2)
    ax0.errorbar(era_labels_clean, era_means["mean"].values,
                 yerr=1.96 * era_means["sem"].values,
                 fmt="none", color="#f9fafb", capsize=5, lw=2, zorder=4)

    # Annotate each bar with its mean value
    for bar, val in zip(bars, era_means["mean"].values):
        ax0.text(bar.get_x() + bar.get_width() / 2, val + 0.001,
                 f"{val:.4f}", ha="center", va="bottom",
                 fontsize=10, color="#f9fafb", fontweight="bold")

    ax0.set_title("Forward Efficiency by Era\n(Marks Inside 50 / Inside 50s)",
                  fontsize=12, color="#f3f4f6", pad=10)
    ax0.set_ylabel("Forward Efficiency", fontsize=11, color="#9ca3af")
    ax0.set_xlabel("")
    ax0.tick_params(colors="#9ca3af", labelsize=10)
    ax0.grid(True, axis="y", alpha=0.25, color="#374151")
    ax0.spines["bottom"].set_color("#374151")
    ax0.spines["left"].set_color("#374151")
    ax0.spines["top"].set_visible(False)
    ax0.spines["right"].set_visible(False)

    # Annotate the V-shape narrative
    ax0.annotate("-> 16-min\nquarters", xy=(1, era_means["mean"].iloc[1]),
                 xytext=(1.3, era_means["mean"].iloc[1] - 0.003),
                 fontsize=8.5, color="#f87171",
                 arrowprops=dict(arrowstyle="->", color="#f87171", lw=1.2))


    fig.suptitle(
        "Quarter Length Causality Proof: V-Shape Reversion",
        fontsize=14, color="#f9fafb", y=1.02,
    )
    plt.tight_layout(pad=1.5)
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="#0f1117")
    log.info("Causality proof figure saved -> %s", out_path)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{SEP}")
    print("  QUARTER LENGTH CAUSALITY ANALYSIS")
    print(f"{SEP}\n")

    # Phase 1
    df = load_and_compute_metrics()
    run_reversion_test(df)

    # Phase 2
    log.info("Generating figure_causality_proof.png ...")
    generate_causality_figure(df, out_path="figure_causality_proof.png")

    print(f"\n{SEP}")
    print("  Analysis complete.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
