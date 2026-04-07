# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from pathlib import Path

html = Path('afl_cache/season_2012.html').read_text(encoding='utf-8', errors='replace')
soup = BeautifulSoup(html, 'html.parser')
all_links = soup.find_all('a', href=True)

# Find ALL links that contain 'stats' anywhere
stats_links = [a for a in all_links if 'stats' in a['href']]
print(f'Links containing "stats": {len(stats_links)}')
for a in stats_links[:10]:
    print(f'  href={repr(a["href"])} text={repr(a.get_text(strip=True)[:40])}')

# Find links containing 'games'
game_links = [a for a in all_links if 'games' in a['href']]
print(f'\nLinks containing "games": {len(game_links)}')
for a in game_links[:10]:
    print(f'  href={repr(a["href"])} text={repr(a.get_text(strip=True)[:40])}')

# Find links pointing to team pages
team_links = [a for a in all_links if 'teams' in a['href']]
print(f'\nLinks containing "teams": {len(team_links)}')
for a in team_links[:6]:
    print(f'  href={repr(a["href"])} text={repr(a.get_text(strip=True)[:40])}')

# Find links pointing to venue pages
venue_links = [a for a in all_links if 'venues' in a['href']]
print(f'\nLinks containing "venues": {len(venue_links)}')
for a in venue_links[:6]:
    print(f'  href={repr(a["href"])} text={repr(a.get_text(strip=True)[:40])}')
