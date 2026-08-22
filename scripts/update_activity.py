#!/usr/bin/env python3
"""Update the profile activity SVG from the public GitHub contribution calendar.

The script intentionally avoids inventing totals. If GitHub's contribution HTML
cannot be fetched, it preserves the existing SVG instead of publishing fake data.
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import urllib.request
from pathlib import Path

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER") or os.environ.get("GITHUB_ACTOR")
OUT = Path(__file__).resolve().parents[1] / "assets" / "profile" / "activity.svg"

if not OWNER:
    raise SystemExit("GITHUB_REPOSITORY_OWNER/GITHUB_ACTOR is unavailable; keeping existing activity.svg")

url = f"https://github.com/users/{OWNER}/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "profile-activity-updater/1.0"})

try:
    with urllib.request.urlopen(req, timeout=20) as response:
        source = response.read().decode("utf-8", errors="replace")
except Exception as exc:
    print(f"Contribution fetch failed: {exc}")
    raise SystemExit(0)

cells = {}
for tag in re.findall(r'<td[^>]*class="[^"]*ContributionCalendar-day[^"]*"[^>]*>', source):
    date_m = re.search(r'data-date="([^"]+)"', tag)
    level_m = re.search(r'data-level="([0-4])"', tag)
    if date_m and level_m:
        cells[date_m.group(1)] = int(level_m.group(1))

if not cells:
    print("No contribution cells found; keeping existing activity.svg")
    raise SystemExit(0)

# Last 15 complete-ish weeks ending at the current Sunday.
today = dt.date.today()
end_sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
start = end_sunday - dt.timedelta(weeks=14)

palette = {
    0: ("#0B111B", ""),
    1: ("#164E63", ""),
    2: ("#0E7490", ""),
    3: ("#22D3EE", ""),
    4: ("#A5F3FC", ' class="hot"'),
}

rects = []
for week in range(15):
    for day in range(7):
        date = start + dt.timedelta(days=week * 7 + day)
        level = cells.get(date.isoformat(), 0)
        color, extra = palette[level]
        rects.append(
            f'<rect x="{week*32}" y="{day*32}" width="23" height="23" rx="4" fill="{color}"{extra}/>'
        )

matrix = "\n".join(rects)
new_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="390" viewBox="0 0 900 390" fill="none">
<style>
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}.h{{font-size:11px;font-weight:700;letter-spacing:1.2px;fill:#CBD5E1}}.s{{font-size:8px;fill:#64748B}}@keyframes p{{50%{{opacity:.55}}}}.hot{{animation:p 2s ease-in-out infinite}}
</style>
<rect x="1" y="1" width="898" height="388" rx="12" fill="#05070B" stroke="#fff" stroke-opacity=".1"/>
<text x="25" y="31" class="m h">GITHUB // ACTIVITY CONSOLE</text><text x="720" y="31" class="m s">LIVE SYNC</text>
<text x="25" y="57" class="m s">LAST 15 WEEKS • CONTRIBUTION MATRIX • {html.escape(OWNER)}</text>
<g transform="translate(55 80)">{matrix}</g>
<g class="m s"><text x="25" y="320">LESS</text><rect x="60" y="309" width="15" height="15" rx="3" fill="#0B111B"/><rect x="82" y="309" width="15" height="15" rx="3" fill="#164E63"/><rect x="104" y="309" width="15" height="15" rx="3" fill="#0E7490"/><rect x="126" y="309" width="15" height="15" rx="3" fill="#22D3EE"/><rect x="148" y="309" width="15" height="15" rx="3" fill="#A5F3FC"/><text x="173" y="320">MORE</text></g>
<g transform="translate(535 70)"><rect x="0" y="0" width="330" height="220" rx="9" fill="#080D16" stroke="#fff" stroke-opacity=".06"/><text x="20" y="28" class="m h">PROFILE SIGNALS</text><text x="20" y="58" class="m s">ACCOUNT</text><text x="20" y="80" class="m h">{html.escape(OWNER)}</text><text x="20" y="112" class="m s">SYNC SOURCE</text><text x="20" y="134" class="m h">GITHUB CONTRIBUTIONS</text><text x="20" y="166" class="m s">UPDATE MODE</text><text x="20" y="188" class="m h">GITHUB ACTIONS</text><circle cx="288" cy="29" r="4" fill="#22C55E" class="hot"/></g>
<text x="25" y="365" class="m s">Generated from the public GitHub contribution calendar. No fake contribution totals are embedded.</text>
</svg>'''

OUT.write_text(new_svg, encoding="utf-8")
print(f"Updated {OUT} for {OWNER}")
