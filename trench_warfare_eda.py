"""
Trench Warfare / Hub Fatigue EDA
================================
Tests whether the compressed 2020 schedule caused structural
shifts towards stoppage density, lower forward efficiency, and closer margins.
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
log = logging.getLogger(__name__)

CACHE_FILE = Path("afl_cache/raw_panel.parquet")

def load_and_prep_data():
    if not CACHE_FILE.exists():
        raise FileNotFoundError("Cache missing.")
        
    df = pd.read_parquet(CACHE_FILE)
    
    # Required columns for Trench Warfare hypothesis
    cols = ["home_cl", "away_cl", "home_i50", "away_i50", 
            "home_mi50", "away_mi50", "home_gl", "away_gl", 
            "home_bh", "away_bh", "home_di", "away_di", "season"]
            
    df = df.dropna(subset=[c for c in cols if c in df.columns])
    
    df["total_clearances"] = df["home_cl"] + df["away_cl"]
    df["total_disposals"] = df["home_di"] + df["away_di"]
    df["total_i50"] = df["home_i50"] + df["away_i50"]
    df["total_mi50"] = df["home_mi50"] + df["away_mi50"]
    df["total_goals"] = df["home_gl"] + df["away_gl"]
    df["total_behinds"] = df["home_bh"] + df["away_bh"]
    
    # Calculate scores from gl and bh if home_score not explicitly correct or present in index
    df["home_score"] = (df["home_gl"] * 6) + df["home_bh"]
    df["away_score"] = (df["away_gl"] * 6) + df["away_bh"]
    
    # Stoppage Density
    df["Clearance_Rate"] = df["total_clearances"] / df["total_disposals"]
    
    # Standardized Margin
    df["Margin_per_100_Disp"] = (np.abs(df["home_score"] - df["away_score"]) / df["total_disposals"]) * 100
    
    # Forward Efficiency
    df["MI50_Ratio"] = df["total_mi50"] / df["total_i50"]
    
    # Goal Accuracy
    df["Accuracy"] = df["total_goals"] / (df["total_goals"] + df["total_behinds"])
    
    # NOTE: Q-by-Q missing so skipping H2_Scoring_Share
    
    df["period"] = np.where(df["season"] == 2020, "2020 (COVID)", "2012-2019 (Baseline)")
    
    return df

def run_tests_and_plot(df):
    metrics = {
        "Stoppage Density (Clearance Rate)": "Clearance_Rate",
        "Standardized Margin (Margin per 100 Disp)": "Margin_per_100_Disp",
        "Forward Efficiency (MI50 Ratio)": "MI50_Ratio",
        "Goal Accuracy": "Accuracy"
    }
    
    baseline = df[df["period"] == "2012-2019 (Baseline)"]
    covid = df[df["period"] == "2020 (COVID)"]
    
    print("\n=======================================================")
    print("      TRENCH WARFARE / HUB FATIGUE T-TEST RESULTS      ")
    print("=======================================================")
    
    for name, col in metrics.items():
        base_val = baseline[col].dropna()
        cov_val = covid[col].dropna()
        
        t_stat, p_val = stats.ttest_ind(base_val, cov_val, equal_var=False)
        b_mean = base_val.mean()
        c_mean = cov_val.mean()
        pct_diff = ((c_mean - b_mean) / b_mean) * 100
        
        print(f"--- {name} ---")
        print(f"  Baseline Mean: {b_mean:.4f}")
        print(f"  2020 Mean:     {c_mean:.4f}  ({pct_diff:+.1f}%)")
        print(f"  T-Stat:        {t_stat:.3f}")
        print(f"  P-Value:       {p_val:.4e}\n")
        
    # Plotting 2x2 grid
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colors = {"2012-2019 (Baseline)": "royalblue", "2020 (COVID)": "darkorange"}
    
    for i, (name, col) in enumerate(metrics.items()):
        sns.boxplot(data=df, x="period", y=col, ax=axes[i], palette=colors, 
                    showmeans=True, meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
        axes[i].set_title(name, fontsize=13, fontweight='bold')
        axes[i].set_xlabel("")
        axes[i].set_ylabel("Value")
        
    plt.suptitle("Trench Warfare Hypothesis: Era Comparison", fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig("figure_trench_warfare.png", dpi=150, bbox_inches='tight')
    log.info("Saved figure_trench_warfare.png")

if __name__ == "__main__":
    df = load_and_prep_data()
    run_tests_and_plot(df)
