# -*- coding: utf-8 -*-
import sys
import pandas as pd
from afl_noise_affirmation_did import clean_data, compute_epi

df = pd.read_parquet("afl_cache/raw_panel.parquet")
print(f"Raw panel shape: {df.shape}")

df_clean = clean_data(df)

# Look at 2012 matches - are attendance and stats valid?
d_2012 = df_clean[df_clean['season'] == 2012]
print(f"Season 2012 matches: {len(d_2012)}")
if not d_2012.empty:
    print(d_2012[['home_team', 'away_team', 'attendance', 'home_fk_diff', 'cp_diff']].head())

print("\n--- Running Feature Engineering ---")
df_eng = compute_epi(df_clean)
epi_info = df_eng[df_eng['season'] < 2020]['epi_z']
print(f"EPI mean: {epi_info.mean()}, std: {epi_info.std()}, NAs: {epi_info.isna().sum()}")

# What caused NAs? Is rolling attendance nan?
print("\nSample of computed attendance columns:")
print(df_eng[['season', 'home_team', 'away_team', 'attendance', 'hist_att', 'travel_mult', 'epi_raw', 'epi_z']].tail(10))

print("\nSample of 2020 matches EPI:")
d_2020 = df_eng[df_eng['season'] == 2020]
print(d_2020[['home_team', 'away_team', 'epi_z', 'travel_mult', 'epi_raw']].head(10))
