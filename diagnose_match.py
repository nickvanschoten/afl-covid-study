# -*- coding: utf-8 -*-
"""Check if stat tables are nested inside outer tables, causing find_all('tr') to span."""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research-bot) Python-requests/2.x"}
url = "https://afltables.com/afl/stats/games/2012/162120120324.html"
resp = requests.get(url, headers=HEADERS, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')
tables = soup.find_all('table')

print(f"Total tables: {len(tables)}")
for i, tbl in enumerate(tables):
    ths = [th.get_text(strip=True) for th in tbl.find_all('th')]
    if 'FF' not in ths or 'HB' not in ths:
        continue
    print(f"\nTable {i}: {len(ths)} headers")
    # Check if this table has child tables
    child_tables = tbl.find_all('table')
    print(f"  Child tables inside: {len(child_tables)}")
    
    # Use find_all with recursive=False to get only DIRECT child rows
    direct_rows = tbl.find_all('tr', recursive=False)
    nested_tbody = tbl.find_all('tbody', recursive=False)
    print(f"  Direct <tr> children: {len(direct_rows)}")
    print(f"  Direct <tbody> children: {len(nested_tbody)}")
    
    # Find totals rows using both methods
    all_rows = tbl.find_all('tr')
    totals_found = []
    for row in all_rows:
        cells = row.find_all('td')
        if cells and cells[0].get_text(strip=True).lower() == 'totals':
            parent_table = row.find_parent('table')
            parent_headers = [th.get_text(strip=True) for th in parent_table.find_all('th', recursive=False)] if parent_table else []
            totals_cells = [c.get_text(strip=True) for c in cells]
            totals_found.append({
                'parent_is_self': parent_table == tbl,
                'totals_row': totals_cells[:5],
            })
    print(f"  Totals rows found by find_all('tr'): {len(totals_found)}")
    for t in totals_found:
        print(f"    parent_is_self={t['parent_is_self']}: {t['totals_row']}")
