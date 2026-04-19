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
        raise FileNotFoundError(f"{CACHE_FILE} missing. Run extraction first.")
    
    df = pd.read_parquet(CACHE_FILE)
    
    # Extract date from match_url (e.g., https://afltables.com/afl/stats/games/2012/03120120331.html)
    df['Date'] = pd.to_datetime(df['match_url'].str.extract(r'(\d{8})\.html')[0], format='%Y%m%d', errors='coerce')
    
    # Calculate Days_Since_Last_Match for every team
    home_df = df[['match_url', 'season', 'Date', 'home_team']].rename(columns={'home_team': 'team'})
    away_df = df[['match_url', 'season', 'Date', 'away_team']].rename(columns={'away_team': 'team'})
    team_matches = pd.concat([home_df, away_df])
    
    # Group by team and sort by date 
    # Grouping by season automatically makes the first game in a season have NaN for prev_match_date
    team_matches = team_matches.sort_values(by=['team', 'Date'])
    team_matches['prev_match_date'] = team_matches.groupby(['team', 'season'])['Date'].shift(1)
    team_matches['Days_Since_Last_Match'] = (team_matches['Date'] - team_matches['prev_match_date']).dt.days
    
    # Join back to calculate rest per team
    df = df.merge(team_matches[['match_url', 'team', 'Days_Since_Last_Match']].rename(
        columns={'team': 'home_team', 'Days_Since_Last_Match': 'Home_Days_Rest'}
    ), on=['match_url', 'home_team'], how='left')
    
    df = df.merge(team_matches[['match_url', 'team', 'Days_Since_Last_Match']].rename(
        columns={'team': 'away_team', 'Days_Since_Last_Match': 'Away_Days_Rest'}
    ), on=['match_url', 'away_team'], how='left')
    
    # Average Match Rest
    df['Average_Match_Rest'] = (df['Home_Days_Rest'] + df['Away_Days_Rest']) / 2
    
    # Create categorical flag
    def categorize_rest(avg_rest):
        if pd.isna(avg_rest):
            return np.nan
        elif avg_rest <= 5:
            return 'Short Rest'
        elif avg_rest >= 7:
            return 'Normal/Long Rest'
        else:
            return 'Moderate Rest'
            
    df['Rest_Category'] = df['Average_Match_Rest'].apply(categorize_rest)
    
    # Require variables for metrics
    cols = ['home_cp', 'away_cp', 'home_di', 'away_di', 'home_tk', 'away_tk', 
            'home_fk_for', 'away_fk_for', 'home_i50', 'away_i50', 'home_mi50', 'away_mi50']
    df = df.dropna(subset=[c for c in cols if c in df.columns])
    
    # Calculate Phase 2 Metrics
    df['total_disposals'] = df['home_di'] + df['away_di']
    df['CPR'] = (df['home_cp'] + df['away_cp']) / df['total_disposals']
    df['Tackle_Rate'] = (df['home_tk'] + df['away_tk']) / df['total_disposals']
    df['total_i50'] = df['home_i50'] + df['away_i50']
    df['total_mi50'] = df['home_mi50'] + df['away_mi50']
    df['Forward_Efficiency'] = df['total_mi50'] / df['total_i50']
    df['Total_Free_Kicks'] = df['home_fk_for'] + df['away_fk_for']
    
    return df

def run_tests_and_summarize(df):
    df_2020 = df[df['season'] == 2020]
    
    # We only care about games that fall into Short / Normal categories
    short_rest = df_2020[df_2020['Rest_Category'] == 'Short Rest']
    long_rest = df_2020[df_2020['Rest_Category'] == 'Normal/Long Rest']
    
    metrics = {
        'Contested Possession Rate (CPR)': 'CPR',
        'Forward Efficiency': 'Forward_Efficiency',
        'Tackle Rate': 'Tackle_Rate',
        'Total Match Free Kicks': 'Total_Free_Kicks'
    }
    
    print("\n" + "="*85)
    print(f"THE 2020 MICRO-CLIMATE: IMPACT OF TURNAROUND TIME")
    print(f"Short Rest (N={len(short_rest)}) vs Normal/Long Rest (N={len(long_rest)})")
    print("="*85)
    print(f"{'Metric':<35} | {'Short Rest Mean':<15} | {'Normal Rest Mean':<16} | {'P-Value'}")
    print("-" * 85)
    
    for name, col in metrics.items():
        sr_vals = short_rest[col].dropna()
        lr_vals = long_rest[col].dropna()
        
        t_stat, p_val = stats.ttest_ind(sr_vals, lr_vals, equal_var=False)
        
        print(f"{name:<35} | {sr_vals.mean():<15.4f} | {lr_vals.mean():<16.4f} | {p_val:.4e}")
    print("="*85 + "\n")

def generate_visualizations(df):
    df_2020 = df[df['season'] == 2020]
    plot_df = df_2020[df_2020['Rest_Category'].isin(['Short Rest', 'Normal/Long Rest'])]
    
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    palette = {"Short Rest": "tomato", "Normal/Long Rest": "steelblue"}
    
    sns.boxplot(data=plot_df, x="Rest_Category", y="CPR", hue="Rest_Category", ax=axes[0], palette=palette, showmeans=True, 
                legend=False, meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
    axes[0].set_title("Contested Possession Rate by Rest Category (2020)", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Rest Category")
    axes[0].set_ylabel("Contested Possession Rate")
    
    sns.boxplot(data=plot_df, x="Rest_Category", y="Forward_Efficiency", hue="Rest_Category", ax=axes[1], palette=palette, showmeans=True,
                legend=False, meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
    axes[1].set_title("Forward Efficiency by Rest Category (2020)", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Rest Category")
    axes[1].set_ylabel("Forward Efficiency\n(Marks Inside 50 / Inside 50s)")
    
    plt.suptitle("The Fatigue vs Intensity Hypothesis: Short Turnarounds in 2020", fontsize=16, y=1.05)
    plt.tight_layout()
    plt.savefig("figure_rest_impact.png", dpi=150, bbox_inches='tight')
    log.info("Saved figure_rest_impact.png")

def main():
    log.info("Loading and prepping data for Fatigue vs Intensity EDA...")
    df = load_and_prep_data()
    
    log.info("Running statistical tests...")
    run_tests_and_summarize(df)
    
    log.info("Generating figure_rest_impact.png...")
    generate_visualizations(df)
    
    log.info("Analysis complete.")

if __name__ == "__main__":
    main()
