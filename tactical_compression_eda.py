"""
AFL Tactical Compression - Exploratory Data Analysis
====================================================
Tests the hypothesis that the 2020 COVID season caused a structural 
shift in game-play (tackles, uncontested marks, disposals) resulting in
fewer chaos/combat mechanics.

Dependencies: pandas, numpy, scipy, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

CACHE_FILE = Path("afl_cache/raw_panel.parquet")

def load_and_prep_data():
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"{CACHE_FILE} missing. Run extraction first.")
    
    df = pd.read_parquet(CACHE_FILE)
    
    # Drop rows with missing values
    cols_to_check = ["home_cp", "away_cp", "home_di", "away_di", 
                     "home_tk", "away_tk", "home_mk", "away_mk",
                     "home_cm", "away_cm", "home_fk_for", "away_fk_for", "season"]
    df = df.dropna(subset=[c for c in cols_to_check if c in df.columns])
    
    # Calculate Totals
    df["total_disposals"] = df["home_di"] + df["away_di"]
    df["total_cp"] = df["home_cp"] + df["away_cp"]
    df["total_tackles"] = df["home_tk"] + df["away_tk"]
    df["total_marks"] = df["home_mk"] + df["away_mk"]
    df["total_cm"] = df["home_cm"] + df["away_cm"]
    df["total_uncontested_marks"] = df["total_marks"] - df["total_cm"]
    df["total_fk"] = df["home_fk_for"] + df["away_fk_for"]
    
    # Calculate Rates
    df["CPR"] = df["total_cp"] / df["total_disposals"]
    df["TR"] = df["total_tackles"] / df["total_disposals"]
    df["UMR"] = df["total_uncontested_marks"] / df["total_marks"]
    
    # Filter 0s to avoid divisions
    df["FreeHomePercent"] = np.where(df["away_fk_for"] > 0, 
                                     (df["home_fk_for"] / df["away_fk_for"]) * 100, np.nan)
    df["FreeAwayPercent"] = np.where(df["home_fk_for"] > 0, 
                                     (df["away_fk_for"] / df["home_fk_for"]) * 100, np.nan)
    
    # Period Identifier
    df["period"] = np.where(df["season"] == 2020, "2020 (COVID)", "2012-2019 (Baseline)")
    
    return df

def perform_t_tests(df):
    baseline = df[df["period"] == "2012-2019 (Baseline)"]
    covid = df[df["period"] == "2020 (COVID)"]
    
    metrics = {
        "Contested Possession Rate (CPR)": "CPR",
        "Tackle Rate (TR)": "TR",
        "Uncontested Mark Ratio (UMR)": "UMR",
        "Total Free Kicks": "total_fk"
    }
    
    print("\n" + "="*60)
    print(" " * 15 + "TACTICAL COMPRESSION T-TESTS")
    print("="*60)
    
    for name, col in metrics.items():
        base_val = baseline[col].dropna()
        cov_val = covid[col].dropna()
        
        t_stat, p_val = stats.ttest_ind(base_val, cov_val, equal_var=False)
        base_mean = base_val.mean()
        cov_mean = cov_val.mean()
        
        # Determine movement
        diff = cov_mean - base_mean
        pct_diff = (diff / base_mean) * 100
        
        print(f"--- {name} ---")
        print(f"  Baseline Mean: {base_mean:.4f}")
        print(f"  2020 Mean:     {cov_mean:.4f}  ({pct_diff:+.1f}%)")
        print(f"  T-Stat:        {t_stat:.3f}")
        print(f"  P-Value:       {p_val:.4e}\n")

def plot_kde_comparison(df, metric, title, xlabel, filename):
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    sns.kdeplot(data=df, x=metric, hue="period", fill=True, common_norm=False, alpha=0.5, palette="magma")
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.axvline(df[df["period"] == "2012-2019 (Baseline)"][metric].mean(), color='blue', linestyle='--', alpha=0.7)
    plt.axvline(df[df["period"] == "2020 (COVID)"][metric].mean(), color='orange', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def execute_publications(df):
    log.info("Generating publication visuals...")
    
    # 1. Baseline vs COVID Density - Tackle Rate
    plot_kde_comparison(df, "TR", "Density of Tackle Rate: Baseline vs COVID Season", 
                        "Tackle Rate (Tackles / Disposals)", "figure_baseline_density.png")
                        
    # 2. Baseline vs COVID Density - Uncontested Mark Ratio
    plot_kde_comparison(df, "UMR", "Density of Uncontested Mark Ratio: Baseline vs COVID Season", 
                        "Uncontested Mark Ratio (Uncontested / Total Marks)", "figure_covid_density.png")
    
    # 3. YOY 3-pane line chart
    yearly_stats = df.groupby("season")[["CPR", "TR", "UMR"]].mean().reset_index()
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    sns.set_theme(style="darkgrid")
    
    metrics = [("CPR", "Contested Possession Rate", "coral"), 
               ("TR", "Tackle Rate", "teal"), 
               ("UMR", "Uncontested Mark Ratio", "purple")]
    
    for ax, (col, title, color) in zip(axes, metrics):
        ax.plot(yearly_stats["season"], yearly_stats[col], marker='o', lw=2, color=color)
        ax.axvspan(2019.5, 2020.5, color='yellow', alpha=0.2, label="2020 COVID Season")
        ax.axvline(2019.5, color='black', linestyle='--')
        ax.set_title(f"Year-over-Year: {title}", fontsize=13)
        ax.set_ylabel(title)
        ax.grid(True)
    
    axes[-1].set_xlabel("Season", fontsize=12)
    axes[-1].set_xticks(range(2012, 2021))
    
    plt.tight_layout()
    plt.savefig("figure_game_style_evolution.png", dpi=160)
    plt.close()
    
def main():
    df = load_and_prep_data()
    perform_t_tests(df)
    execute_publications(df)
    log.info("EDA completely executed.")

if __name__ == "__main__":
    main()
