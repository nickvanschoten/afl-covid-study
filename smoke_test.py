# -*- coding: utf-8 -*-
"""
Verify parse_match_stats against known values from alignment_check.txt
GWS vs Sydney, Rd1 2012:  https://afltables.com/afl/stats/games/2012/162120120324.html
Expected:
  Home (GWS) Totals: KI=210, MK=96, HB=157, DI=367, FF=24, FA=16, CP=139
  Away (Sydney) Totals: KI=224, MK=107, HB=164, DI=388, FF=24, FA=6, CP=155
  Wait - Totals row for GWS: ['Totals','210','96','157','367','5','7','37','63','51','28','40','53','24','16','','139','220','12','9','56','3','3','']
  => FF=cells[14]='24', FA=cells[15]='16', CP=cells[17]... wait let me recount
  headers[2:] = ['Player','KI','MK','HB','DI','GL','BH','HO','TK','RB','IF','CL','CG','FF','FA','BR','CP','UP','CM','MI','1%','BO','GA','%P']
  stat_headers.index('FF') = 13
  totals_row[13+1] = totals_row[14] = '24' (GWS FF)  <-- correct per alignment_check.txt
"""
import sys
sys.path.insert(0, '.')

# Delete the cached file so we re-fetch
from pathlib import Path
cached = Path('afl_cache') / 'match_2012_162120120324_html'
if cached.exists():
    cached.unlink()

from afl_noise_affirmation_did import parse_match_stats

match_info = {
    'match_url': 'https://afltables.com/afl/stats/games/2012/162120120324.html',
    'home_team': 'Greater Western Sydney',
    'away_team': 'Sydney',
    'season': 2012,
    'venue': 'Stadium Australia',
}

stats = parse_match_stats(match_info)
print(f"Result: {stats}")
print()

if stats:
    # From alignment_check.txt known values:
    # GWS Totals row: FF=24, CP=139, KI=210, HB=157
    # Sydney Totals row: FF=24, CP=155, KI=224, HB=164
    checks = [
        ('home_fk_for', 24),
        ('home_fk_agt', 16),
        ('home_cp',     139),
        ('home_kicks',  210),
        ('home_hb',     157),
        ('away_fk_for', 24),
        ('away_fk_agt', 6),
        ('away_cp',     155),
        ('away_kicks',  224),
        ('away_hb',     164),
    ]
    all_ok = True
    for key, expected in checks:
        actual = stats.get(key)
        ok = abs(actual - expected) < 0.5 if actual is not None and expected is not None else False
        status = 'OK' if ok else 'FAIL'
        if not ok:
            all_ok = False
        print(f"  {status}: {key} = {actual} (expected {expected})")
    print()
    if all_ok:
        print("ALL CHECKS PASSED - parser is correct!")
    else:
        print("SOME CHECKS FAILED")
        sys.exit(1)
else:
    print("ERROR: parse_match_stats returned None")
    sys.exit(1)
