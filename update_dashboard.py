#!/usr/bin/env python3
"""
Daily auto-update for ACL Recovery Dashboard.
Updates: lastUpdated, days since injury, days to surgery.
All other data (ROM, sessions, goals, reminders) is updated manually via Cowork.
"""

import re
from datetime import date

# ── Fixed reference dates ──────────────────────────────────────────────────────
INJURY_DATE  = date(2026, 4, 24)
# Surgery date: update this line once confirmed with Mr Punwar
SURGERY_DATE = date(2026, 7, 15)   # placeholder: mid-July 2026

# ── Calculate ──────────────────────────────────────────────────────────────────
today             = date.today()
days_since_injury = (today - INJURY_DATE).days
days_to_surgery   = max(0, (SURGERY_DATE - today).days)

# Format date as "23 May 2026" (no leading zero on day)
today_str = today.strftime("%-d %b %Y")

# ── Load file ──────────────────────────────────────────────────────────────────
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

original = html

# ── Apply updates ──────────────────────────────────────────────────────────────

# 1. lastUpdated
html = re.sub(
    r'lastUpdated:\s*"[^"]*"',
    f'lastUpdated: "{today_str}"',
    html
)

# 2. days since injury stat
html = re.sub(
    r'(n:\s*")[^"]*(",\s*\n\s*l:\s*"days since injury")',
    rf'\g<1>{days_since_injury}\g<2>',
    html
)

# 3. days to surgery stat
html = re.sub(
    r'(n:\s*")[^"]*(",\s*\n\s*l:\s*"days to surgery")',
    rf'\g<1>~{days_to_surgery}\g<2>',
    html
)

# ── Write back only if changed ─────────────────────────────────────────────────
if html != original:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated: {today_str} | {days_since_injury} days since injury | ~{days_to_surgery} days to surgery")
else:
    print("No changes needed.")
