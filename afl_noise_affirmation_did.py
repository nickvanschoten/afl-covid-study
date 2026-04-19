"""
AFL "Noise of Affirmation" Analysis
=====================================
Continuous Treatment Difference-in-Differences study examining whether the
absence of home crowds during the 2020 COVID-19 season affected the home
team's free kick (penalty) differential.

Data source: AFL Tables (https://afltables.com) via requests + BeautifulSoup.
Econometric framework: linearmodels PanelOLS with entity × time fixed effects.

Author: Generated for research purposes
Python: 3.9+
Dependencies: requests, beautifulsoup4, pandas, numpy, scikit-learn,
              linearmodels, matplotlib, seaborn, scipy
"""

# ---------------------------------------------------------------------------
# Standard Library
# ---------------------------------------------------------------------------
import time
import re
import logging
import warnings
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from linearmodels.panel import PanelOLS
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://afltables.com"
SEASONS = list(range(2012, 2021))          # 2012–2020 inclusive
REQUEST_DELAY = 0.2                         # seconds between HTTP calls
CACHE_DIR = Path("afl_cache")              # local cache directory
CACHE_DIR.mkdir(exist_ok=True)

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (research-bot; AFL noise-of-affirmation study) "
        "Python-requests/2.x"
    )
}

# ---------------------------------------------------------------------------
# Team Metadata  (state, same-city-derby groups)
# ---------------------------------------------------------------------------
# State codes for interstate/same-state/same-city categorisation
TEAM_STATE: dict[str, str] = {
    "Adelaide":            "SA",
    "Brisbane Lions":      "QLD",
    "Carlton":             "VIC",
    "Collingwood":         "VIC",
    "Essendon":            "VIC",
    "Fremantle":           "WA",
    "Geelong":             "VIC",   # Geelong is its own city, not Melbourne
    "Gold Coast":          "QLD",
    "Greater Western Sydney": "NSW",
    "Hawthorn":            "VIC",
    "Melbourne":           "VIC",
    "North Melbourne":     "VIC",
    "Port Adelaide":       "SA",
    "Richmond":            "VIC",
    "St Kilda":            "VIC",
    "Sydney":              "NSW",
    "West Coast":          "WA",
    "Western Bulldogs":    "VIC",
}

VENUE_STATE: dict[str, str] = {
    # VIC venues
    "MCG": "VIC", 
    "Marvel Stadium": "VIC", 
    "GMHBA Stadium": "VIC",
    "Kardinia Park": "VIC",
    "Docklands": "VIC",
    "Eureka Stadium": "VIC",
    "Mars Stadium": "VIC",
    
    # NSW venues
    "SCG": "NSW", 
    "Giants Stadium": "NSW", 
    "Sydney Showground": "NSW",
    "Stadium Australia": "NSW",
    "Blacktown": "NSW",
    
    # QLD venues
    "Gabba": "QLD", 
    "Heritage Bank Stadium": "QLD",
    "Carrara": "QLD",
    "Riverway Stadium": "QLD",
    "Cazaly's Stadium": "QLD",
    
    # SA venues
    "Adelaide Oval": "SA",
    "Football Park": "SA",
    
    # WA venues
    "Optus Stadium": "WA",
    "Perth Stadium": "WA",
    "Subiaco": "WA",
    
    # ACT / TAS / NT / Overseas
    "Manuka Oval": "ACT",
    "UTAS Stadium": "TAS", 
    "Aurora Stadium": "TAS",
    "Blundstone Arena": "TAS",
    "Bellerive Oval": "TAS",
    "York Park": "TAS",
    "TIO Stadium": "NT", 
    "Marrara Oval": "NT",
    "TIO Traeger Park": "NT",
    "Traeger Park": "NT",
    "China Game Venue": "OS",
    "Jiangwan Stadium": "OS",
    "Wellington": "OS"
}

VENUE_CAPACITY: dict[str, int] = {
    "MCG": 100024,
    "Marvel Stadium": 53359, "Docklands": 53359,
    "Optus Stadium": 60000, "Perth Stadium": 60000, "Subiaco": 43500,
    "Adelaide Oval": 53500, "Football Park": 51000,
    "SCG": 48000, "Giants Stadium": 23500, "Sydney Showground": 23500, "Stadium Australia": 82000, "Blacktown": 10000,
    "Gabba": 36000, "Heritage Bank Stadium": 25000, "Carrara": 25000, "Cazaly's Stadium": 13500, "Riverway Stadium": 10000,
    "GMHBA Stadium": 36000, "Kardinia Park": 36000,
    "Eureka Stadium": 11000, "Mars Stadium": 11000,
    "Manuka Oval": 13500,
    "Blundstone Arena": 19500, "Bellerive Oval": 19500, "UTAS Stadium": 19000, "Aurora Stadium": 19000, "York Park": 19000,
    "TIO Stadium": 12500, "Marrara Oval": 12500, "TIO Traeger Park": 7000, "Traeger Park": 7000,
    "Jiangwan Stadium": 11000, "China Game Venue": 11000,
    "Wellington": 34500
}

CLUB_MEMBERSHIPS: dict[str, int] = {
    "Richmond": 95000, "Collingwood": 85000, "West Coast": 80000, "Essendon": 80000,
    "Hawthorn": 75000, "Adelaide": 65000, "Geelong": 60000, "Sydney": 60000,
    "Port Adelaide": 55000, "Carlton": 55000, "Fremantle": 50000,
    "Melbourne": 45000, "Western Bulldogs": 45000, "St Kilda": 45000, "North Melbourne": 40000,
    "Brisbane Lions": 25000, "Greater Western Sydney": 25000, "Gold Coast": 15000
}

NON_VIC_DERBIES: set[tuple[str, str]] = {
    ("West Coast", "Fremantle"), ("Fremantle", "West Coast"),
    ("Adelaide", "Port Adelaide"), ("Port Adelaide", "Adelaide"),
    ("Sydney", "Greater Western Sydney"), ("Greater Western Sydney", "Sydney"),
    ("Brisbane Lions", "Gold Coast"), ("Gold Coast", "Brisbane Lions")
}

# City groups for derby detection: teams that share a city/major venue cluster.
# A derby is when *both* home and away teams are in the same group.
CITY_GROUPS: dict[str, str] = {
    # Greater Melbourne MCG precinct
    "Carlton":          "Melbourne",
    "Collingwood":      "Melbourne",
    "Essendon":         "Melbourne",
    "Hawthorn":         "Melbourne",
    "Melbourne":        "Melbourne",
    "North Melbourne":  "Melbourne",
    "Richmond":         "Melbourne",
    "St Kilda":         "Melbourne",
    "Western Bulldogs": "Melbourne",
    # Geelong - own city
    "Geelong":          "Geelong",
    # Adelaide
    "Adelaide":         "Adelaide",
    "Port Adelaide":    "Adelaide",
    # Perth
    "West Coast":       "Perth",
    "Fremantle":        "Perth",
    # Brisbane metro
    "Brisbane Lions":   "Brisbane",
    "Gold Coast":       "Brisbane",  # Gold Coast is SE-QLD metro area
    # Sydney metro
    "Sydney":           "Sydney",
    "Greater Western Sydney": "Sydney",
}


def fan_split_multiplier(home_team: str, away_team: str, venue: str) -> float:
    """
    Return the fan split ratio (0.1 to 1.0) based on derby/membership rules.
    """
    home_state = TEAM_STATE.get(home_team)
    away_state = TEAM_STATE.get(away_team)
    venue_state = VENUE_STATE.get(venue)
    
    # 1. Hub Override
    if home_state and venue_state and home_state != venue_state:
        return 0.1

    # 2. Non-Victorian Derbies
    if (home_team, away_team) in NON_VIC_DERBIES:
        return 0.85

    # 3. Interstate Matches
    if home_state and away_state and home_state != away_state:
        return 1.0

    # 4. Victorian Derbies (both in Melbourne cluster)
    home_city = CITY_GROUPS.get(home_team)
    away_city = CITY_GROUPS.get(away_team)
    if home_city == "Melbourne" and away_city == "Melbourne":
        return 0.50

    # 5. Same-State (Calculate proportional split)
    home_mems = CLUB_MEMBERSHIPS.get(home_team, 40000)
    away_mems = CLUB_MEMBERSHIPS.get(away_team, 40000)
    return home_mems / (home_mems + away_mems)


# ---------------------------------------------------------------------------
# Phase 1 – Data Ingestion
# ---------------------------------------------------------------------------

def _cached_get(url: str, cache_file: Path) -> str:
    """
    Fetch URL content with local file-system caching.
    Returns the raw HTML string.
    """
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")

    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as exc:
        log.warning("HTTP error fetching %s: %s", url, exc)
        return ""

    cache_file.write_text(html, encoding="utf-8", errors="replace")
    return html


def get_match_stat_urls(season: int) -> list[dict]:
    """
    Parse the AFL Tables season summary page for a given year and return a
    list of dicts: {season, home_team, away_team, venue, match_url}.

    AFL Tables uses *relative* hrefs (e.g. '../stats/games/2012/…') so we
    resolve them with urljoin against the season page base URL.
    """
    season_url = f"{BASE_URL}/afl/seas/{season}.html"
    cache_f = CACHE_DIR / f"season_{season}.html"
    html = _cached_get(season_url, cache_f)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    all_links = soup.find_all("a")

    records: list[dict] = []
    # Walk through all <a> tags; match-stats links follow a predictable
    # sibling pattern on the page:  Team - Venue - Team - [Match stats]
    # AFL Tables hrefs are relative, e.g. '../stats/games/2012/XXXXXX.html'
    game_token = f"stats/games/{season}/"

    # Track whether we have passed the Finals section header.
    # The season page has a 'Finals' anchor; games after that are finals
    # (neutral-venue), which we exclude from the home-advantage analysis.
    in_finals = False

    i = 0
    while i < len(all_links):
        link = all_links[i]
        
        # Detect entry into the Finals section (the actual anchor tag)
        if link.get("name") == "fin":
            in_finals = True

        href = link.get("href")
        if not href:
            i += 1
            continue

        if game_token in href and not in_finals:
            # Resolve the relative href to a full URL
            full_url = urljoin(season_url, href)

            # Look back up to 8 links to find home_team, venue, away_team
            window = all_links[max(0, i - 8): i]
            teams_found = []
            venue_found = None
            for prev in window:
                ph = prev.get("href", "")
                if "teams/" in ph:
                    teams_found.append(prev.get_text(strip=True))
                elif "venues/" in ph:
                    venue_found = prev.get_text(strip=True)

            if len(teams_found) >= 2:
                home = teams_found[-2]
                away = teams_found[-1]
                records.append({
                    "season":    season,
                    "home_team": home,
                    "away_team": away,
                    "venue":     venue_found or "Unknown",
                    "match_url": full_url,
                })
        i += 1

    log.info("Season %d: found %d matches", season, len(records))
    return records


def parse_match_stats(match_info: dict) -> Optional[dict]:
    """
    Scrape a single match stats page and return a dict with:
      home_fk, away_fk, home_cp, away_cp, home_kicks, away_kicks,
      home_handballs, away_handballs, attendance.

    AFL Tables match stats pages list player rows for each team.
    The *last* row per team contains team totals (including Totals label).
    Column abbreviations: FF = Free Kicks For,  CP = Contested Possessions
                          K  = Kicks,            HB = Handballs
    """
    url = match_info["match_url"]
    # Build a safe cache filename from the game-specific portion of the URL
    game_part = url.split("stats/games/")[-1]   # e.g. '2012/162120120324.html'
    fname = re.sub(r"[^a-z0-9]", "_", game_part.lower()).strip("_")
    cache_f = CACHE_DIR / f"match_{fname}"

    html = _cached_get(url, cache_f)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # --- Date / Primetime, Attendance & Game Time ---------------------
    attendance = np.nan
    is_primetime = 0
    game_time_mins = np.nan
    for b_tag in soup.find_all("b"):
        text = b_tag.get_text(strip=True).lower()
        if "date:" in text:
            parent_text = b_tag.parent.get_text()
            if "Thu" in parent_text or "Fri" in parent_text:
                is_primetime = 1
        elif text == "attendance:":
            nxt = b_tag.next_sibling
            if nxt and isinstance(nxt, str):
                m = re.search(r"([\d,]+)", nxt)
                if m:
                    attendance = int(m.group(1).replace(",", ""))

    # Game time: appears as plain text "Game time:125m 18s" in the page body.
    # Use the raw HTML string (faster than navigating the parsed tree).
    gt_m = re.search(r"Game time:\s*(\d+)m\s*(\d+)s", html)
    if gt_m:
        game_time_mins = int(gt_m.group(1)) + int(gt_m.group(2)) / 60.0

    result = {"attendance": attendance, "is_primetime": is_primetime,
              "game_time_mins": game_time_mins}

    # --- Parse stat tables --------------------------------------------
    # AFL Tables pages have two stat tables: one per team.
    # Identify them by presence of both 'FF' and 'HB' in header row.
    tables = soup.find_all("table")
    stat_tables = []
    for tbl in tables:
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
        if "FF" in headers and "HB" in headers:
            stat_tables.append((headers, tbl))

    if len(stat_tables) < 2:
        log.debug("Could not find two stat tables at %s (found %d)",
                  url, len(stat_tables))
        return None

    for idx, (headers, tbl) in enumerate(stat_tables[:2]):

        prefix = "home" if idx == 0 else "away"
        rows = tbl.find_all("tr")
        if not rows:
            continue

        # AFL Tables labels the team's own aggregate row as 'Totals'.
        # The 'Opposition' row below it shows the opposing team's stats
        # (mirrored).  We want the 'Totals' row for this team.
        # Structure: ['Totals', KI, MK, HB, DI, GL, BH, HO, TK, RB, IF,
        #             CL, CG, FF, FA, BR, CP, UP, CM, MI, 1%, BO, GA, '%P']
        totals_row = None

        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            first_cell = cells[0].get_text(strip=True).lower()
            if first_cell == "totals":
                totals_row = cells
                break   # take the first (and only) Totals row

        if totals_row is None:
            # Fallback: last row with >=10 cells that isn't 'Opposition'
            for row in reversed(rows):
                cells = row.find_all("td")
                if len(cells) < 10:
                    continue
                first_cell = cells[0].get_text(strip=True).lower()
                if first_cell != "opposition":
                    totals_row = cells
                    break

        if totals_row is None:
            continue

        # Column alignment:
        # headers[0]  = team name (wide <th>: 'Greater Western Sydney...')
        # headers[1:] = stat column names: '#', 'Player', 'KI', 'MK', etc.
        # totals_row[0] = 'Totals' label
        # totals_row[1:] aligns with headers[2:] (skipping '#' and 'Player'
        #   columns which are collapsed in the totals row).
        # Empirically: Totals row has 24 cells for a 26-header table.
        # headers[1:] has 25 entries; totals_row has 24 cells.
        # We skip 'Player' col (no player name in total), so
        stat_headers = headers[2:]   # skip team-name AND '#' column headers

        # Totals row cell layout (verified against AFL Tables HTML):
        #   cell[0]  = 'Totals' label  (maps to: team-name, '#', 'Player' all collapsed)
        #   cell[1]  = KI value        (stat_headers[1] = 'KI')
        #   cell[2]  = MK value        (stat_headers[2] = 'MK')
        #   ...
        #   cell[13] = FF value        (stat_headers[13] = 'FF')
        #   cell[14] = FA value        (stat_headers[14] = 'FA')
        #   cell[16] = CP value        (stat_headers[16] = 'CP')
        # Note: stat_headers[0]='Player' is absorbed into the 'Totals' label,
        # so col_idx directly corresponds to totals_row[col_idx].

        def _val(col_name: str) -> float:
            """Extract numeric value for a given column header name."""
            try:
                col_idx = stat_headers.index(col_name)
                raw = totals_row[col_idx].get_text(strip=True)
                raw = raw.replace(",", "")
                return float(raw) if raw.lstrip("-").replace(".", "", 1).isdigit() else np.nan
            except (ValueError, IndexError):
                return np.nan

        result[f"{prefix}_score"]   = (_val("GL") * 6) + _val("BH")
        result[f"{prefix}_fk_for"]  = _val("FF")
        result[f"{prefix}_fk_agt"]  = _val("FA")
        result[f"{prefix}_cp"]      = _val("CP")
        result[f"{prefix}_kicks"]   = _val("KI")
        result[f"{prefix}_hb"]      = _val("HB")
        result[f"{prefix}_cl"]      = _val("CL")
        result[f"{prefix}_tk"]      = _val("TK")
        result[f"{prefix}_di"]      = _val("DI")
        result[f"{prefix}_mk"]      = _val("MK")
        result[f"{prefix}_cm"]      = _val("CM")
        result[f"{prefix}_i50"]     = _val("IF")
        result[f"{prefix}_mi50"]    = _val("MI")
        result[f"{prefix}_gl"]      = _val("GL")
        result[f"{prefix}_bh"]      = _val("BH")

    return result


def ingest_all_seasons(seasons: list[int]) -> pd.DataFrame:
    """
    Orchestrate ingestion across all seasons.
    Returns a raw match-level DataFrame.
    """
    all_records: list[dict] = []

    for season in seasons:
        log.info("--- Ingesting season %d ---", season)
        match_infos = get_match_stat_urls(season)

        for info in match_infos:
            stats = parse_match_stats(info)
            if stats is None:
                continue
            record = {**info, **stats}
            all_records.append(record)

    df = pd.DataFrame(all_records)
    log.info("Raw ingestion complete: %d rows × %d cols", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Phase 2 – Feature Engineering
# ---------------------------------------------------------------------------

# Venue name normalisations (AFL Tables uses inconsistent names)
VENUE_ALIASES: dict[str, str] = {
    "M.C.G.":              "MCG",
    "Docklands":           "Marvel Stadium",
    "S.C.G.":              "SCG",
    "Perth Stadium":       "Optus Stadium",
    "Sydney Showground":   "Giants Stadium",
    "Kardinia Park":       "GMHBA Stadium",
    "Adelaide Oval":       "Adelaide Oval",
    "Gabba":               "Gabba",
    "Carrara":             "Heritage Bank Stadium",
    "York Park":           "UTAS Stadium",
    "Bellerive Oval":      "Blundstone Arena",
    "Marrara Oval":        "TIO Stadium",
    "Manuka Oval":         "Manuka Oval",
    "Traeger Park":        "TIO Traeger Park",
    "Eureka Stadium":      "Marvel Stadium",   # same venue, old name
    "Jiangwan Stadium":    "China Game Venue",
    "Riverway Stadium":    "Riverway Stadium",
    "Aurora Stadium":      "UTAS Stadium",
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise team names, venue names, and derive primary outcome variables.
    """
    # Normalise venue names
    df["venue"] = df["venue"].map(VENUE_ALIASES).fillna(df["venue"])

    # Consistent team name mapping (AFL Tables can be inconsistent)
    TEAM_ALIASES = {
        "Grt Western Sydney": "Greater Western Sydney",
        "GWS":                "Greater Western Sydney",
        "GWS Giants":         "Greater Western Sydney",
        "Brisbane":           "Brisbane Lions",
        "Western Bulldogs":   "Western Bulldogs",
        "Bulldogs":           "Western Bulldogs",
    }
    df["home_team"] = df["home_team"].replace(TEAM_ALIASES)
    df["away_team"] = df["away_team"].replace(TEAM_ALIASES)

    # Drop matches with missing free kick data
    fk_cols = ["home_fk_for", "away_fk_for"]
    df = df.dropna(subset=fk_cols).copy()

    # --- Primary outcome variable ---
    # Home team's *received* free kick advantage:
    #   home_fk_for (frees awarded TO the home team) -
    #   away_fk_for (frees awarded TO the away team)
    df["home_fk_diff"] = df["home_fk_for"] - df["away_fk_for"]

    # --- Game-state controls (differentials) ---
    df["cp_diff"]    = df["home_cp"]    - df["away_cp"]
    df["kicks_diff"] = df["home_kicks"] - df["away_kicks"]
    df["hb_diff"]    = df["home_hb"]    - df["away_hb"]
    df["clearance_diff"] = df["home_cl"] - df["away_cl"]

    # --- COVID indicator ---
    df["covid_season"] = (df["season"] == 2020).astype(int)

    # --- Matchup ID (order-independent, alphabetical) ---
    df["matchup_id"] = (
        df[["home_team", "away_team"]]
        .apply(lambda r: "_vs_".join(sorted([r["home_team"], r["away_team"]])), axis=1)
    )

    # --- Matchup Directed ID (order-dependent) ---
    df["matchup_directed_id"] = df["home_team"] + "_vs_" + df["away_team"]

    # --- Date Parsing & Days Rest Calc ---
    df['Date'] = pd.to_datetime(df['match_url'].str.extract(r'(\d{8})\.html', expand=False), format='%Y%m%d', errors='coerce')
    
    # Calculate days rest for home and away
    home_df = df[['match_url', 'season', 'Date', 'home_team']].rename(columns={'home_team': 'team'})
    away_df = df[['match_url', 'season', 'Date', 'away_team']].rename(columns={'away_team': 'team'})
    team_matches = pd.concat([home_df, away_df]).sort_values(by=['team', 'Date'])
    
    # Calculate days since last match
    team_matches['prev_match_date'] = team_matches.groupby(['team', 'season'])['Date'].shift(1)
    team_matches['Days_Since_Last_Match'] = (team_matches['Date'] - team_matches['prev_match_date']).dt.days
    
    # Merge back to compute rest_diff
    df = df.merge(team_matches[['match_url', 'team', 'Days_Since_Last_Match']].rename(
        columns={'team': 'home_team', 'Days_Since_Last_Match': 'Home_Days_Rest'}
    ), on=['match_url', 'home_team'], how='left')
    
    df = df.merge(team_matches[['match_url', 'team', 'Days_Since_Last_Match']].rename(
        columns={'team': 'away_team', 'Days_Since_Last_Match': 'Away_Days_Rest'}
    ), on=['match_url', 'away_team'], how='left')
    
    # Fill NA rest (e.g. first game of season) with 7 days
    df['days_rest_diff'] = df['Home_Days_Rest'].fillna(7) - df['Away_Days_Rest'].fillna(7)

    # --- Hub Location Control ---
    # Determine if 'home' team is playing outside their home state in 2020
    df['home_interstate_2020'] = df.apply(
        lambda r: 1 if (r['covid_season'] == 1 and TEAM_STATE.get(r['home_team'], 'VIC') != VENUE_STATE.get(r['venue'], 'VIC')) else 0,
        axis=1
    )

    return df


def compute_epi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Expected Partisanship Index (EPI) for every match.

    EPI = Historical_Base_Attendance × Travel_Multiplier

    Historical_Base: rolling 5-year average attendance for that
    (home_team, away_team, venue) triplet using pre-2020 data.
    2020 games use the 2015–2019 average.
    """
    df = df.copy()

    # --- Step 1: Fan Split multiplier (vectorised) ---
    df["fan_split"] = df.apply(
        lambda r: fan_split_multiplier(r["home_team"], r["away_team"], r["venue"]), axis=1
    )

    # --- Step 2: Historical average attendance ---
    # Sort by season so rolling windows are chronologically correct
    df = df.sort_values(["home_team", "away_team", "venue", "season"])

    # For the pre-2020 seasons, compute a 5-year rolling mean of attendance
    # per (home_team, away_team, venue) group.
    # We use a minimum of 1 observation to avoid NaN for rare matchups.
    pre2020 = df[df["season"] < 2020].copy()

    # Vectorised rolling: groupby then transform with a lambda on sorted data
    def _rolling_hist_att(group: pd.Series) -> pd.Series:
        return (
            group
            .shift(1)                        # don't leak current-year attendance
            .rolling(window=5, min_periods=1)
            .mean()
        )

    pre2020["hist_att"] = (
        pre2020
        .groupby(["home_team", "away_team", "venue"])["attendance"]
        .transform(_rolling_hist_att)
    )

    # Where attendance is NaN (no previous matchup at this venue),
    # backfill with the venue-level average or the global average.
    venue_avg = pre2020.groupby("venue")["attendance"].mean()
    global_avg = pre2020["attendance"].mean()

    pre2020["hist_att"] = pre2020["hist_att"].fillna(
        pre2020["venue"].map(venue_avg)
    ).fillna(global_avg)

    # --- Step 3: For 2020 matches, use the 2015–2019 average ---
    last5_avg = (
        df[df["season"].between(2015, 2019)]
        .groupby(["home_team", "away_team", "venue"])["attendance"]
        .mean()
        .rename("hist_att")
        .reset_index()
    )

    covid_rows = df[df["season"] == 2020].copy()
    covid_rows = covid_rows.merge(
        last5_avg, on=["home_team", "away_team", "venue"], how="left"
    )
    # Fallback chain: venue 2015-2019 avg → global 2015-2019 avg
    venue_avg_covid = (
        df[df["season"].between(2015, 2019)]
        .groupby("venue")["attendance"]
        .mean()
    )
    global_avg_covid = df[df["season"].between(2015, 2019)]["attendance"].mean()
    covid_rows["hist_att"] = (
        covid_rows["hist_att"]
        .fillna(covid_rows["venue"].map(venue_avg_covid))
        .fillna(global_avg_covid)
    )

    # --- Step 4: Combine pre-2020 and 2020 rows ---
    combined = pd.concat([pre2020, covid_rows], ignore_index=True)
    combined = combined.sort_values(["season", "home_team", "away_team"])

    # --- Step 5: Calculate EPI (Net Partisan Hostility) ---
    # Density = expected_attendance / venue_capacity (capped at 1.0)
    venue_caps = combined["venue"].map(VENUE_CAPACITY)
    default_cap = pd.Series(VENUE_CAPACITY).mean()
    combined["density"] = (combined["hist_att"] / venue_caps.fillna(default_cap)).clip(0.0, 1.0)
    
    combined["epi_raw"] = combined["hist_att"] * combined["density"] * combined["fan_split"]

    # --- Step 6: Standardise EPI using pre-2020 fit ---
    scaler = StandardScaler()
    pre2020_epi = combined[combined["season"] < 2020]["epi_raw"].values.reshape(-1, 1)
    scaler.fit(pre2020_epi)
    combined["epi_z"] = scaler.transform(
        combined["epi_raw"].values.reshape(-1, 1)
    ).ravel()

    # --- Step 7: Fuzzy DiD Treatment Variable (Deficit Ratio) ---
    combined["expected_attendance"] = combined["hist_att"]
    
    # Pre-2020 missing attendance -> match expected attendance (0 deficit)
    # 2020 missing attendance -> assumed empty (1 deficit)
    actual_att = np.where(
        combined["season"] == 2020,
        combined["attendance"].fillna(0.0),
        combined["attendance"].fillna(combined["expected_attendance"])
    )
    
    # Calculate ratio (Expected - Actual) / Expected
    combined["deficit_ratio"] = (combined["expected_attendance"] - actual_att) / combined["expected_attendance"]
    combined["deficit_ratio"] = combined["deficit_ratio"].replace([np.inf, -np.inf], 0.0)
    
    # Bound between 0.0 (normal) and 1.0 (empty), fill any remaining NaNs
    combined["deficit_ratio"] = combined["deficit_ratio"].clip(0.0, 1.0).fillna(0.0)

    # Main continuous interaction parameter
    combined["deficit_x_epi"] = combined["deficit_ratio"] * combined["epi_z"]

    log.info(
        "EPI computed. Mean EPI (pre-2020): %.1f  |  Std: %.1f",
        pre2020_epi.mean(), pre2020_epi.std()
    )
    return combined


def calculate_cpi_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Club Prestige Index (CPI) and merge as cpi_diff.
    """
    df = df.copy()
    
    # 1. Isolate Team-Seasons
    home = df[["season", "home_team", "home_score", "away_score", "is_primetime"]].rename(
        columns={"home_team": "team", "home_score": "pts_for", "away_score": "pts_against"}
    )
    home["is_win"] = (home["pts_for"] > home["pts_against"]).astype(int)
    
    away = df[["season", "away_team", "away_score", "home_score", "is_primetime"]].rename(
        columns={"away_team": "team", "away_score": "pts_for", "home_score": "pts_against"}
    )
    away["is_win"] = (away["pts_for"] > away["pts_against"]).astype(int)
    
    team_games = pd.concat([home, away], ignore_index=True)
    
    season_stats = team_games.groupby(["season", "team"]).agg(
        win_pct=("is_win", "mean"),
        primetime_pct=("is_primetime", "mean")
    ).reset_index()
    
    # 2. Lag the variables (DO NOT BACKFILL 2012)
    season_stats = season_stats.sort_values(["team", "season"])
    season_stats["prev_win_pct"] = season_stats.groupby("team")["win_pct"].shift(1)
    season_stats["prev_primetime_pct"] = season_stats.groupby("team")["primetime_pct"].shift(1)
    
    # 3. Memberships Anchor
    season_stats["memberships"] = season_stats["team"].map(CLUB_MEMBERSHIPS).fillna(40000)
    
    # 4. Intra-Season Standardisation
    def z_score(x):
        return (x - x.mean()) / x.std() if x.std() > 0 else 0
        
    season_stats["mem_z"] = season_stats.groupby("season")["memberships"].transform(z_score)
    season_stats["win_z"] = season_stats.groupby("season")["prev_win_pct"].transform(z_score)
    season_stats["prime_z"] = season_stats.groupby("season")["prev_primetime_pct"].transform(z_score)
    
    # 5. Composite Assembly
    season_stats["cpi_raw"] = (season_stats["mem_z"] + season_stats["win_z"] + season_stats["prime_z"]) / 3
    season_stats["cpi_score"] = season_stats.groupby("season")["cpi_raw"].transform(z_score)
    
    # 6. Merge to Matchups
    team_cpi_map = season_stats.set_index(["season", "team"])["cpi_score"]
    
    df = df.set_index(["season", "home_team"])
    df["home_cpi"] = team_cpi_map
    df = df.reset_index().set_index(["season", "away_team"])
    df["away_cpi"] = team_cpi_map
    df = df.reset_index()
    
    df["cpi_diff"] = df["home_cpi"] - df["away_cpi"]
    
    return df


def build_panel(df: pd.DataFrame, entity_col: str = "matchup_id") -> pd.DataFrame:
    """
    Create the panel DataFrame with a proper MultiIndex for linearmodels.

    Entity = entity_col  (e.g., matchup_id or matchup_directed_id)
    Time   = season
    """
    df = df.copy()

    # Each (entity_col, season) pair should be unique or we take the mean
    # (handles neutral venue edge cases or finals with the same matchup)
    agg_dict = {
        "home_fk_diff":   "mean",
        "home_fk_for":    "mean",
        "away_fk_for":    "mean",
        "home_cp":        "mean",
        "away_cp":        "mean",
        "home_cl":        "mean",
        "away_cl":        "mean",
        "home_tk":        "mean",
        "away_tk":        "mean",
        "home_di":        "mean",
        "away_di":        "mean",
        "home_mk":        "mean",
        "away_mk":        "mean",
        "home_cm":        "mean",
        "away_cm":        "mean",
        "home_i50":       "mean",
        "away_i50":       "mean",
        "home_mi50":      "mean",
        "away_mi50":      "mean",
        "home_gl":        "mean",
        "away_gl":        "mean",
        "home_bh":        "mean",
        "away_bh":        "mean",
        "covid_season":   "first",
        "deficit_ratio":  "mean",
        "epi_z":          "mean",
        "deficit_x_epi":  "mean",
        "cp_diff":        "mean",
        "kicks_diff":     "mean",
        "hb_diff":        "mean",
        "clearance_diff": "mean",
        "home_team":      "first",
        "away_team":      "first",
        "venue":          "first",
        "fan_split":      "first",
        "epi_raw":        "mean",
        "attendance":     "mean",
        "cpi_diff":       "mean",
        "game_time_mins": "mean",
        "days_rest_diff": "mean",
        "home_interstate_2020": "mean",
        "matchup_id":     "first",
        "matchup_directed_id": "first",
    }
    # Keep only columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    # Remove the entity col from agg_dict to prevent index collision on reset_index
    if entity_col in agg_dict:
        del agg_dict[entity_col]

    panel = (
        df
        .groupby([entity_col, "season"])
        .agg(agg_dict)
        .reset_index()
    )

    panel = panel.set_index([entity_col, "season"])

    log.info(
        "Panel built: %d entity-year observations  |  %d unique %s",
        len(panel),
        panel.index.get_level_values(entity_col).nunique(),
        entity_col
    )
    return panel


# ---------------------------------------------------------------------------
# Phase 3 – Econometric Modelling
# ---------------------------------------------------------------------------

def run_models(panel_undirected: pd.DataFrame, panel_directed: pd.DataFrame) -> dict:
    """
    Estimate five PanelOLS specifications separating causal effect from mediation.

    Returns a dict of {label: fitted_result}.
    """
    results = {}

    def clean(df, extra_vars=None):
        base_vars = ["home_fk_diff", "deficit_ratio", "epi_z", "deficit_x_epi", "cpi_diff", 
                     "days_rest_diff", "home_interstate_2020", "cp_diff", "kicks_diff", "clearance_diff"]
        return df.dropna(subset=base_vars)

    panel_u = clean(panel_undirected)
    panel_d = clean(panel_directed)

    # --- Model 1: Baseline (Undirected FEs, No Controls) ---
    log.info("Fitting Model 1: Baseline (Undirected FEs) …")
    m1 = PanelOLS.from_formula(
        formula="home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi + EntityEffects + TimeEffects",
        data=panel_u,
        drop_absorbed=True,
    )
    results["Model 1: Baseline (Undirected FEs)"] = m1.fit(
        cov_type="clustered", cluster_entity=True, cluster_time=True
    )

    # --- Model 2: Main Causal Spec (Directed FEs, No Controls) ---
    log.info("Fitting Model 2: Main Causal (Directed FEs) …")
    m2 = PanelOLS.from_formula(
        formula="home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi + EntityEffects + TimeEffects",
        data=panel_d,
        drop_absorbed=True,
    )
    results["Model 2: Main Causal (Directed FEs)"] = m2.fit(
        cov_type="clustered", cluster_entity=True, cluster_time=True
    )

    # --- Model 3: Hub Travel Robustness (Directed + Rest/Interstate Controls) ---
    log.info("Fitting Model 3: Hub Travel Robustness …")
    m3 = PanelOLS.from_formula(
        formula=(
            "home_fk_diff ~ deficit_ratio + epi_z + deficit_x_epi "
            "+ days_rest_diff + home_interstate_2020 "
            "+ EntityEffects + TimeEffects"
        ),
        data=panel_d,
        drop_absorbed=True,
    )
    results["Model 3: Hub Robustness"] = m3.fit(
        cov_type="clustered", cluster_entity=True, cluster_time=True
    )

    # --- Model 4: Brand Bias (Directed, Hub Controls + CPI) ---
    log.info("Fitting Model 4: Brand Bias …")
    m4 = PanelOLS.from_formula(
        formula=(
            "home_fk_diff ~ cpi_diff + days_rest_diff + home_interstate_2020 "
            "+ EntityEffects + TimeEffects"
        ),
        data=panel_d,
        drop_absorbed=True,
    )
    results["Model 4: Brand Bias Baseline"] = m4.fit(
        cov_type="clustered", cluster_entity=True, cluster_time=True
    )

    # --- Model 5: Mediation Specification (M3 + Post-Treatment Game State Controls) ---
    log.info("Fitting Model 5: Mediation Specification …")
    m5 = PanelOLS.from_formula(
        formula=(
            "home_fk_diff ~ deficit_x_epi + days_rest_diff + home_interstate_2020 "
            "+ cp_diff + kicks_diff + clearance_diff "
            "+ EntityEffects + TimeEffects"
        ),
        data=panel_d,
        drop_absorbed=True,
    )
    results["Model 5: Mediation Spec (Game-State Controls)"] = m5.fit(
        cov_type="clustered", cluster_entity=True, cluster_time=True
    )

    return results


def print_tables(results: dict) -> None:
    """Pretty-print summary tables for each fitted model."""
    separator = "=" * 80
    for label, res in results.items():
        print(f"\n{separator}")
        print(f"  {label}")
        print(separator)
        print(res.summary)

    # Compact coefficient comparison across models
    print(f"\n{'-'*80}")
    print("  COEFFICIENT COMPARISON  (cluster-robust SEs in parentheses)")
    print(f"{'-'*80}")

    params_of_interest = ["deficit_ratio", "epi_z", "deficit_x_epi", "cpi_diff",
                          "cp_diff", "kicks_diff", "clearance_diff"]
    rows = []
    for label, res in results.items():
        row = {"Model": label}
        for p in params_of_interest:
            if p in res.params.index:
                coef = res.params[p]
                se   = res.std_errors[p]
                pval = res.pvalues[p]
                stars = (
                    "***" if pval < 0.01 else
                    "**"  if pval < 0.05 else
                    "*"   if pval < 0.10 else ""
                )
                row[p] = f"{coef:+.3f}{stars}\n({se:.3f})"
            else:
                row[p] = "-"
        rows.append(row)

    comp_df = pd.DataFrame(rows).set_index("Model")
    print(comp_df.to_string())
    print("\n  Significance: *** p<0.01  ** p<0.05  * p<0.10")
    print(f"{'-'*80}")


# ---------------------------------------------------------------------------
# Phase 4 – Visualisation
# ---------------------------------------------------------------------------

def _setup_style() -> None:
    """Configure a premium dark-mode Matplotlib style."""
    plt.style.use("dark_background")
    matplotlib.rcParams.update({
        "font.family":        "sans-serif",
        "font.sans-serif":    ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "axes.facecolor":     "#0f1117",
        "figure.facecolor":   "#0f1117",
        "axes.edgecolor":     "#2d3139",
        "axes.labelcolor":    "#e0e0e0",
        "text.color":         "#e0e0e0",
        "xtick.color":        "#9ca3af",
        "ytick.color":        "#9ca3af",
        "grid.color":         "#1f2937",
        "grid.linestyle":     "--",
        "grid.alpha":         0.6,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
    })


ACCENT_COVID   = "#f472b6"   # Pink − COVID 2020
ACCENT_NORMAL  = "#60a5fa"   # Blue − Normal seasons
ACCENT_EFFECT  = "#34d399"   # Teal − treatment effect
ACCENT_CI      = "#fbbf24"   # Amber − confidence interval


def plot_marginal_effect(
    panel: pd.DataFrame,
    model3_result,
    out_path: str = "figure_marginal_effect.png",
) -> None:
    """
    Plot the marginal effect of the COVID season on the home free kick
    differential across the range of standardised EPI.

    Uses Model 3 coefficients to draw fitted lines separately for
    COVID (2020) and non-COVID seasons, with 95% CI shading.
    """
    _setup_style()

    panel_reset = panel.reset_index()
    panel_reset = panel_reset.dropna(
        subset=["epi_z", "home_fk_diff", "covid_season"]
    )

    epi_grid = np.linspace(
        panel_reset["epi_z"].quantile(0.02),
        panel_reset["epi_z"].quantile(0.98),
        300,
    )

    # Retrieve coefficients from Model 3
    params = model3_result.params
    cov    = model3_result.cov

    beta_intercept = 0.0          # absorbed by FE; we plot deviation from mean
    beta_covid     = params.get("deficit_ratio", 0.0)
    beta_epi       = params.get("epi_z",        0.0)
    beta_interact  = params.get("deficit_x_epi",  0.0)

    # Predicted home_fk_diff (ignoring absorbed FE effects -> relative shift)
    y_normal = beta_epi * epi_grid
    y_covid  = (beta_covid + beta_epi * epi_grid
                + beta_interact * epi_grid)

    # 95% CI for COVID line via delta method
    # d(y_covid)/d(params) w.r.t. [deficit_ratio, epi_z, deficit_x_epi]
    coef_names = list(params.index)

    def _ci(line_vals: np.ndarray, x_grid: np.ndarray,
            covid_flag: int) -> tuple[np.ndarray, np.ndarray]:
        """Return lower and upper 95% CI bands."""
        se_band = np.zeros(len(x_grid))
        for j, x in enumerate(x_grid):
            # Gradient vector
            grad = np.zeros(len(coef_names))
            for k, name in enumerate(coef_names):
                if name == "deficit_ratio":
                    grad[k] = covid_flag
                elif name == "epi_z":
                    grad[k] = x
                elif name == "deficit_x_epi":
                    grad[k] = covid_flag * x
            var = grad @ np.array(cov) @ grad
            se_band[j] = np.sqrt(max(var, 0))
        z95 = 1.96
        return line_vals - z95 * se_band, line_vals + z95 * se_band

    ci_n_lo, ci_n_hi = _ci(y_normal, epi_grid, covid_flag=0)
    ci_c_lo, ci_c_hi = _ci(y_covid,  epi_grid, covid_flag=1)

    fig, axes = plt.subplots(
        1, 2, figsize=(16, 7),
        gridspec_kw={"width_ratios": [3, 1]}
    )

    # -- Left panel: conditional regression lines -----------------------
    ax = axes[0]
    ax.set_facecolor("#0f1117")

    # Scatter: actual data points
    mask_covid  = panel_reset["covid_season"] == 1
    mask_normal = ~mask_covid

    ax.scatter(
        panel_reset.loc[mask_normal, "epi_z"],
        panel_reset.loc[mask_normal, "home_fk_diff"],
        color=ACCENT_NORMAL, alpha=0.18, s=18, zorder=2, label="_nolegend_",
    )
    ax.scatter(
        panel_reset.loc[mask_covid, "epi_z"],
        panel_reset.loc[mask_covid, "home_fk_diff"],
        color=ACCENT_COVID, alpha=0.55, s=35, zorder=3,
        marker="D", label="_nolegend_",
    )

    # Regression lines
    ax.plot(epi_grid, y_normal, color=ACCENT_NORMAL, lw=2.5,
            label="Non-COVID seasons (2012–2019)")
    ax.fill_between(epi_grid, ci_n_lo, ci_n_hi,
                    color=ACCENT_NORMAL, alpha=0.15)

    ax.plot(epi_grid, y_covid, color=ACCENT_COVID, lw=2.5, ls="--",
            label="COVID season (2020 - no crowds)")
    ax.fill_between(epi_grid, ci_c_lo, ci_c_hi,
                    color=ACCENT_COVID, alpha=0.20)

    # Treatment effect band (difference between the two lines)
    ax.fill_between(epi_grid, y_covid, y_normal,
                    where=(y_normal > y_covid),
                    color=ACCENT_EFFECT, alpha=0.12,
                    label="Estimated crowd advantage lost")

    ax.axhline(0, color="#4b5563", lw=1, ls=":")
    ax.axvline(0, color="#4b5563", lw=1, ls=":", label="EPI = 0 (mean)")

    # Annotations
    ax.set_xlabel("Expected Partisanship Index (std. dev.)", fontsize=13)
    ax.set_ylabel("Home Free Kick Differential", fontsize=13)
    ax.set_title(
        "Marginal Effect of COVID Season on Home Free Kick Differential\n"
        "across Expected Partisanship Index (Model 3 - with controls)",
        fontsize=14, pad=18, color="#f3f4f6",
    )
    ax.legend(
        frameon=True, framealpha=0.25, facecolor="#1f2937",
        edgecolor="#374151", fontsize=10.5,
    )
    ax.grid(True)

    # Annotation: coefficient value
    high_epi = epi_grid[-1]
    diff_at_high = y_covid[-1] - y_normal[-1]
    ax.annotate(
        f"Additional COVID effect\nat high EPI: {diff_at_high:+.2f} frees",
        xy=(high_epi, y_covid[-1]),
        xytext=(high_epi - 0.9, y_covid[-1] + 1.2),
        arrowprops=dict(arrowstyle="->", color="#fbbf24", lw=1.5),
        color="#fbbf24", fontsize=9.5,
    )

    # -- Right panel: distribution of EPI by COVID status ---------------
    ax2 = axes[1]
    ax2.set_facecolor("#0f1117")

    epi_normal = panel_reset.loc[mask_normal, "epi_z"].dropna()
    epi_covid  = panel_reset.loc[mask_covid,  "epi_z"].dropna()

    ax2.hist(epi_normal, bins=25, orientation="horizontal",
             color=ACCENT_NORMAL, alpha=0.55, density=True,
             label="2012–2019")
    ax2.hist(epi_covid, bins=15, orientation="horizontal",
             color=ACCENT_COVID, alpha=0.70, density=True,
             label="2020")
    ax2.set_xlabel("Density", fontsize=11)
    ax2.set_ylabel("")
    ax2.set_title("EPI distribution", fontsize=11, color="#d1d5db")
    ax2.legend(fontsize=9.5, framealpha=0.2, facecolor="#1f2937",
               edgecolor="#374151")
    ax2.grid(True, axis="x")

    plt.tight_layout(pad=2.0)
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="#0f1117")
    log.info("Figure saved → %s", out_path)
    # plt.show() removed to prevent hanging


def plot_coef_forest(results: dict,
                     out_path: str = "figure_coefficient_forest.png") -> None:
    """
    Forest plot of key coefficients across the three models,
    showing point estimates and 95% CIs.
    """
    _setup_style()

    key_params = {
        "deficit_ratio": "Deficit Ratio\n(Base effect)",
        "epi_z":         "EPI\n(Std.)",
        "deficit_x_epi": "Deficit × EPI\n(Causal parameter)",
        "cpi_diff":      "CPI\nDifferential",
        "cp_diff":       "CP\nDifferential",
        "kicks_diff":    "Kicks\nDifferential",
        "clearance_diff":"Clearance\nDifferential",
    }
    model_labels  = list(results.keys())
    model_colours = [ACCENT_NORMAL, ACCENT_EFFECT, ACCENT_COVID, "#10b981", "#ec4899"]
    n_models      = len(model_labels)

    fig, axes = plt.subplots(
        1, len(key_params), figsize=(18, 5), sharey=False
    )
    fig.patch.set_facecolor("#0f1117")

    for ax_idx, (pname, plabel) in enumerate(key_params.items()):
        ax = axes[ax_idx]
        ax.set_facecolor("#0f1117")

        ax.axvline(0, color="#6b7280", lw=1.2, ls="--")

        y_positions = []
        for m_idx, (label, res) in enumerate(results.items()):
            if pname not in res.params.index:
                continue
            coef   = res.params[pname]
            lo, hi = res.conf_int().loc[pname].values
            y_pos  = float(m_idx)
            y_positions.append(y_pos)

            colour = model_colours[m_idx % len(model_colours)]
            ax.plot([lo, hi], [y_pos, y_pos], color=colour, lw=2.5, alpha=0.8)
            ax.plot(coef, y_pos, "o", color=colour, ms=8, zorder=5)

            # p-value star
            pval = res.pvalues[pname]
            stars = (
                "***" if pval < 0.01 else
                "**"  if pval < 0.05 else
                "*"   if pval < 0.10 else ""
            )
            ax.text(
                coef, y_pos + 0.18, stars,
                ha="center", va="bottom", color=colour, fontsize=9,
            )

        ax.set_yticks(list(range(n_models)))
        ax.set_yticklabels(
            [f"M{i+1}" for i in range(n_models)],
            fontsize=9, color="#9ca3af",
        )
        ax.set_xlabel("Estimate (95% CI)", fontsize=9.5, color="#9ca3af")
        ax.set_title(plabel, fontsize=10.5, color="#e5e7eb", pad=8)
        ax.grid(True, axis="x", alpha=0.4)

    # Legend
    patches = [
        mpatches.Patch(color=c, label=l)
        for c, l in zip(model_colours, [f"M{i+1}" for i in range(n_models)])
    ]
    fig.legend(
        handles=patches,
        labels=[f"M{i+1}: {l}" for i, l in enumerate(model_labels)],
        loc="upper center", bbox_to_anchor=(0.5, 0.02),
        ncol=3, fontsize=9, framealpha=0.2,
        facecolor="#1f2937", edgecolor="#374151",
    )

    fig.suptitle(
        "AFL Noise of Affirmation - Coefficient Forest Plot\n"
        "(Cluster-robust 95% CI; entity + time fixed effects)",
        fontsize=13, color="#f9fafb", y=1.02,
    )
    plt.tight_layout(pad=1.5)
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="#0f1117")
    log.info("Forest plot saved → %s", out_path)
    # plt.show() removed to prevent hanging


def plot_free_kick_trend(
    df: pd.DataFrame,
    out_path: str = "figure_free_kick_trend.png",
) -> None:
    """
    Plot the season-level mean home free kick differential over time,
    split by high vs. low EPI matches, to visually motivate the study.
    """
    _setup_style()

    df_plot = df.copy()
    df_plot["epi_group"] = pd.qcut(
        df_plot["epi_z"], q=3,
        labels=["Low EPI\n(neutral crowds)", "Mid EPI", "High EPI\n(partisan crowds)"],
    )

    season_means = (
        df_plot
        .groupby(["season", "epi_group"])["home_fk_diff"]
        .agg(["mean", "sem"])
        .reset_index()
    )
    season_means.columns = ["season", "epi_group", "mean_fk", "se_fk"]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor("#0f1117")

    palette = {
        "Low EPI\n(neutral crowds)":  ACCENT_NORMAL,
        "Mid EPI":                    "#a78bfa",
        "High EPI\n(partisan crowds)": ACCENT_COVID,
    }

    for grp, colour in palette.items():
        sub = season_means[season_means["epi_group"] == grp]
        ax.plot(sub["season"], sub["mean_fk"], "o-", color=colour,
                lw=2.2, ms=7, label=grp)
        ax.fill_between(
            sub["season"],
            sub["mean_fk"] - 1.96 * sub["se_fk"],
            sub["mean_fk"] + 1.96 * sub["se_fk"],
            color=colour, alpha=0.15,
        )

    # Shade 2020
    ax.axvspan(2019.5, 2020.5, color="#fbbf24", alpha=0.08,
               label="COVID-19 season (2020)")
    ax.axhline(0, color="#4b5563", lw=1, ls=":")
    ax.set_xticks(SEASONS)
    ax.set_xlabel("Season", fontsize=12)
    ax.set_ylabel("Mean Home Free Kick Differential", fontsize=12)
    ax.set_title(
        "Home Free Kick Advantage by Season & Expected Partisanship Index\n"
        "(2012–2020 - 95% CI bands)",
        fontsize=13.5, pad=15, color="#f3f4f6",
    )
    ax.legend(
        frameon=True, framealpha=0.25, facecolor="#1f2937",
        edgecolor="#374151", fontsize=10,
    )
    ax.grid(True)

    plt.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="#0f1117")
    log.info("Trend plot saved → %s", out_path)
    plt.show()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("======================================================")
    log.info("  AFL 'Noise of Affirmation' - DiD Analysis Pipeline")
    log.info("======================================================")

    # -- 1. Ingestion ---------------------------------------------------
    raw_cache = CACHE_DIR / "raw_panel.parquet"
    if raw_cache.exists():
        log.info("Loading raw panel from cache: %s", raw_cache)
        raw_df = pd.read_parquet(raw_cache)
    else:
        raw_df = ingest_all_seasons(SEASONS)
        raw_df.to_parquet(raw_cache, index=False)
        log.info("Raw panel cached → %s", raw_cache)

    # -- 2. Clean -------------------------------------------------------
    cleaned = clean_data(raw_df)
    log.info("After cleaning: %d rows", len(cleaned))

    # -- 3. CPI & EPI feature engineering ------------------------------
    featured = compute_epi(cleaned)
    featured = calculate_cpi_metrics(featured)

    # -- 4. Build panels ------------------------------------------------
    panel_u = build_panel(featured, entity_col="matchup_id")
    panel_d = build_panel(featured, entity_col="matchup_directed_id")

    print("\n" + "-" * 60)
    print("      AFL 'Noise of Affirmation' - DiD Analysis Pipeline")
    print("-" * 60 + "\n")
    desc_cols = [
        "home_fk_diff", "epi_z", "covid_x_epi", "home_interstate_2020", "days_rest_diff",
        "cp_diff", "kicks_diff",
    ]
    desc_cols = [c for c in desc_cols if c in panel_d.columns]
    print(panel_d[desc_cols].describe().round(3).to_string())

    print("\n  Season-level mean free kick differential:")
    print(
        panel_d
        .reset_index()
        .groupby("season")["home_fk_diff"]
        .mean()
        .round(3)
        .to_string()
    )

    # Parallel trends check: correlation of FKdiff with EPI pre-2020
    pre2020_panel = panel_d[panel_d.index.get_level_values("season") < 2020]
    corr, pval = stats.pearsonr(
        pre2020_panel["epi_z"].dropna(),
        pre2020_panel["home_fk_diff"].reindex(
            pre2020_panel["epi_z"].dropna().index
        ).dropna(),
    )
    print(f"\n  Pre-2020 EPI vs FK Diff: Pearson r = {corr:.3f}  (p={pval:.4f})")
    print("  (Should be positive if EPI captures crowd partisanship)")

    # -- 6. Models ----------------------------------------------------
    fitted = run_models(panel_u, panel_d)
    print_tables(fitted)

    # -- 7. Visualisations ---------------------------------------------
    log.info("Generating visualisations …")
    plot_free_kick_trend(featured, out_path="figure_free_kick_trend.png")
    plot_marginal_effect(
        panel_d,
        fitted["Model 2: Main Causal (Directed FEs)"],
        out_path="figure_marginal_effect.png",
    )
    plot_coef_forest(fitted, out_path="figure_coefficient_forest.png")

    log.info("=" * 54)
    log.info("  Analysis complete.")
    log.info("=" * 54)


if __name__ == "__main__":
    main()
