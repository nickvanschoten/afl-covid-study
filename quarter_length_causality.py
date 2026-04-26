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

  Phase 2 – Q4 Fade Test (within-game intensity)
      For every cached match HTML, parse the cumulative quarter scores and
      derive Q1 and Q4 *within-quarter* scoring outputs.
      Q4_Variance = Q4_Output - Q1_Output
      Hypothesis: In 20-min eras defences tire → Q4 scoring >> Q1.
      In the 16-min 2020 era, if intensity is maintained across the match,
      this variance compresses to near-zero.

  Phase 3 – Visualisation (figure_causality_proof.png)
      Left:  Bar chart of Forward Efficiency across three eras ("V-shape").
      Right: Boxplot of Q4 Output Variance: Baseline vs 2020.

Dependencies: pandas, numpy, scipy, matplotlib, seaborn, beautifulsoup4
"""

import re
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
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
# Phase 2 – Q4 Fade Test
# ---------------------------------------------------------------------------

def _parse_quarter_scores_from_html(html: str) -> dict:
    """
    Parse cumulative quarter scores from an AFL Tables match HTML page.

    The header table rows look like:
      <td>TeamName</td>
      <td align=center>G.B.<b>CumScore_Q1</b></td>
      <td align=center>G.B.<b>CumScore_Q2</b></td>
      <td align=center>G.B.<b>CumScore_Q3</b></td>
      <td align=center>G.B.<b>CumScore_Q4</b></td>

    Returns dict with home_q1, home_q4, away_q1, away_q4 as floats,
    or empty dict if parsing fails.
    """
    soup = BeautifulSoup(html, "html.parser")

    # The first table on the page is the scoreline header table.
    # It has 6 rows: header, home scores, away scores, margin, qrt scores, umpires.
    tables = soup.find_all("table")
    if not tables:
        return {}

    header_table = tables[0]
    rows = header_table.find_all("tr")

    # We expect at least 3 rows (row 0 = info, row 1 = home, row 2 = away)
    if len(rows) < 3:
        return {}

    def _extract_quarter_scores(row) -> list[int]:
        """Extract the 4 bold cumulative totals from the score row."""
        scores = []
        for b_tag in row.find_all("b"):
            try:
                scores.append(int(b_tag.get_text(strip=True).replace(",", "")))
            except ValueError:
                pass
        return scores[:4]  # Q1, Q2, Q3, Q4 cumulative

    home_cumulative = _extract_quarter_scores(rows[1])
    away_cumulative = _extract_quarter_scores(rows[2])

    if len(home_cumulative) < 4 or len(away_cumulative) < 4:
        return {}

    # Within-quarter scores (incremental, not cumulative)
    def _incremental(cumulative: list[int]) -> list[int]:
        return [cumulative[0]] + [cumulative[i] - cumulative[i - 1]
                                  for i in range(1, 4)]

    home_qtr = _incremental(home_cumulative)
    away_qtr = _incremental(away_cumulative)

    return {
        "home_q1": home_qtr[0],
        "home_q4": home_qtr[3],
        "away_q1": away_qtr[0],
        "away_q4": away_qtr[3],
    }


def build_quarter_dataset() -> pd.DataFrame:
    """
    Walk every cached match HTML file (2012–2020 only for the baseline/2020 test)
    and extract Q1 + Q4 within-quarter scoring.
    Returns a DataFrame with columns: season, match_url, q1_total, q4_total, q4_variance.
    """
    parquet = pd.read_parquet(CACHE_FILE)[["season", "match_url"]]
    # Filter: 2012–2020 is all we need for the Baseline vs 2020 fade test
    parquet = parquet[parquet["season"] <= 2020].copy()

    records = []
    skipped = 0

    for _, row in parquet.iterrows():
        season    = int(row["season"])
        match_url = row["match_url"]

        # Re-derive cache filename the same way the parser does
        game_part = match_url.split("stats/games/")[-1]
        fname = re.sub(r"[^a-z0-9]", "_", game_part.lower()).strip("_")
        cache_f = CACHE_DIR / f"match_{fname}"

        if not cache_f.exists():
            skipped += 1
            continue

        html = cache_f.read_text(encoding="utf-8", errors="replace")
        scores = _parse_quarter_scores_from_html(html)
        if not scores:
            skipped += 1
            continue

        q1_total = scores["home_q1"] + scores["away_q1"]
        q4_total = scores["home_q4"] + scores["away_q4"]

        records.append({
            "season":      season,
            "match_url":   match_url,
            "q1_total":    q1_total,
            "q4_total":    q4_total,
            "q4_variance": q4_total - q1_total,   # positive = Q4 > Q1
        })

    log.info("Q4 Fade dataset: %d rows parsed, %d skipped", len(records), skipped)
    df = pd.DataFrame(records)
    df["era"] = df["season"].apply(
        lambda s: "2020 (COVID Hub)" if s == 2020 else "2012-2019 (Baseline)"
    )
    return df


def run_q4_fade_test(qdf: pd.DataFrame) -> None:
    """
    Compare Q4 Output Variance between Baseline (2012-2019) and 2020.
    Prints t-test results to console.
    """
    print(f"\n{SEP}")
    print("  PHASE 2 – Q4 FADE TEST: Within-Game Intensity")
    print(SEP)
    print(
        "  Metric: Q4 Scoring Output - Q1 Scoring Output per match\n"
        "  (positive = teams scored more in Q4 than Q1; late-game fatigue effect)\n"
        "  Hypothesis: In 20-min eras, tired defences lead to higher Q4 scoring.\n"
        "  In 2020's 16-min era, sustained intensity -> Q4~=Q1, variance -> 0.\n"
    )

    baseline = qdf[qdf["era"] == "2012-2019 (Baseline)"]["q4_variance"].dropna()
    covid    = qdf[qdf["era"] == "2020 (COVID Hub)"]["q4_variance"].dropna()

    t, p = stats.ttest_ind(baseline, covid, equal_var=False)
    _, p_mw = stats.mannwhitneyu(baseline, covid, alternative="two-sided")

    print(f"  {'Metric':<35}  {'Baseline (2012-2019)':>20}  {'2020 COVID':>12}")
    print("  " + "-" * 73)
    print(f"  {'N Matches':<35}  {len(baseline):>20d}  {len(covid):>12d}")
    print(f"  {'Mean Q4 Variance':<35}  {baseline.mean():>20.2f}  {covid.mean():>12.2f}")
    print(f"  {'Median Q4 Variance':<35}  {baseline.median():>20.2f}  {covid.median():>12.2f}")
    print(f"  {'Std Deviation':<35}  {baseline.std():>20.2f}  {covid.std():>12.2f}")
    print()
    print(f"  Welch t-test:    t = {t:+.4f}  p = {p:.4e}")
    print(f"  Mann-Whitney U:  p = {p_mw:.4e}")

    direction = "LOWER" if covid.mean() < baseline.mean() else "HIGHER"
    sig = "significantly (p<0.05)" if p < 0.05 else "but NOT significantly (p>=0.05)"
    diff = covid.mean() - baseline.mean()

    print(f"\n  VERDICT: Q4 Variance in 2020 is {direction} than baseline by "
          f"{abs(diff):.2f} points ({sig}).")
    if p < 0.05 and direction == "LOWER":
        print("  This SUPPORTS the hypothesis: 16-min quarters compressed the late-game")
        print("  scoring fade typically caused by defensive fatigue in the standard format.")
    elif p < 0.05 and direction == "HIGHER":
        print("  Unexpectedly, Q4 scoring was HIGHER relative to Q1 in 2020.")
        print("  This may reflect hub scheduling effects on game state dynamics.")
    else:
        print("  The result is not statistically significant. The fade test is inconclusive.")


# ---------------------------------------------------------------------------
# Phase 3 – Visualisation
# ---------------------------------------------------------------------------

def generate_causality_figure(df: pd.DataFrame, qdf: pd.DataFrame,
                               out_path: str = "figure_causality_proof.png") -> None:
    """
    1x2 subplot grid:
      Left:  Bar chart – Forward Efficiency across three eras (V-shape)
      Right: Boxplot  – Q4 Variance: Baseline vs 2020
    """
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.patch.set_facecolor("#0f1117")

    axis_style = dict(facecolor="#0f1117", tick_params=dict(colors="#9ca3af"))

    # --- Left: Bar chart of Forward Efficiency by Era ---
    era_means = (
        df.groupby("era")["Forward_Efficiency"]
        .agg(mean="mean", sem="sem")
        .reindex(ERA_ORDER)
        .reset_index()
    )
    era_labels_clean = [e.replace("\n", " ") for e in ERA_ORDER]
    colors = [ERA_PALETTE[e] for e in ERA_ORDER]

    ax0 = axes[0]
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

    # --- Right: Boxplot of Q4 Variance ---
    ax1 = axes[1]
    ax1.set_facecolor("#0f1117")
    palette_box = {
        "2012-2019 (Baseline)": "#4ade80",
        "2020 (COVID Hub)":     "#f87171",
    }
    order = ["2012-2019 (Baseline)", "2020 (COVID Hub)"]
    sns.boxplot(data=qdf, x="era", y="q4_variance", hue="era",
                order=order, palette=palette_box, ax=ax1,
                showmeans=True, legend=False,
                meanprops={"marker": "o", "markerfacecolor": "white",
                           "markeredgecolor": "black", "markersize": 8})

    ax1.axhline(0, color="#6b7280", lw=1.2, ls="--", alpha=0.6, label="Q4 = Q1")
    ax1.set_title("Q4 Scoring Fade: Q4 Output - Q1 Output\n"
                  "(Positive = More Scoring in Q4 vs Q1)",
                  fontsize=12, color="#f3f4f6", pad=10)
    ax1.set_ylabel("Q4 Output Variance (points)", fontsize=11, color="#9ca3af")
    ax1.set_xlabel("")
    ax1.tick_params(colors="#9ca3af", labelsize=10)
    ax1.grid(True, axis="y", alpha=0.25, color="#374151")
    ax1.spines["bottom"].set_color("#374151")
    ax1.spines["left"].set_color("#374151")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(fontsize=9, framealpha=0.2, facecolor="#1f2937",
               edgecolor="#374151", labelcolor="#e5e7eb")

    fig.suptitle(
        "Quarter Length Causality Proof: V-Shape Reversion & Q4 Fade Compression",
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
    log.info("Parsing Q-by-Q scores from cached HTML files ...")
    qdf = build_quarter_dataset()
    run_q4_fade_test(qdf)

    # Phase 3
    log.info("Generating figure_causality_proof.png ...")
    generate_causality_figure(df, qdf, out_path="figure_causality_proof.png")

    print(f"\n{SEP}")
    print("  Analysis complete.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
