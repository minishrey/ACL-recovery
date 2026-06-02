#!/usr/bin/env python3
"""
Daily auto-update for ACL Recovery Dashboard.
Updates: lastUpdated, days since injury, days to surgery,
         appointment statuses (done / next / upcoming) and daysTo tag.
All other data (ROM, sessions, goals, reminders) is updated manually via Cowork.
"""

import re
from datetime import date, datetime

# ── Fixed reference dates ──────────────────────────────────────────────────────
INJURY_DATE  = date(2026, 4, 24)
# Surgery date: update this line once confirmed with Mr Punwar
SURGERY_DATE = date(2026, 7, 15)   # placeholder: mid-July 2026

# ── Appointment dates (update list when bookings change) ───────────────────────
# Format: (date_obj, "Display string", "HH:MM AM/PM display")
APPOINTMENTS = [
    (date(2026, 5, 20), "Wed 20 May", "3:30 PM"),
    (date(2026, 5, 27), "Wed 27 May", "11:00 AM"),
    (date(2026, 5, 29), "Fri 29 May", "2:30 PM"),
    (date(2026,  6,  1), "Mon 1 Jun",  "3:30 PM"),
                 (date(2026, 6, 15), "Mon 15 Jun", "4:30 PM"),
]

# ── Calculate ──────────────────────────────────────────────────────────────────
today             = date.today()
days_since_injury = (today - INJURY_DATE).days
days_to_surgery   = max(0, (SURGERY_DATE - today).days)

# Format date as "23 May 2026" (no leading zero on day)
today_str = today.strftime("%-d %b %Y")

# Work out which appointment is next
next_appt = None
for appt_date, display, time in APPOINTMENTS:
    if appt_date >= today:
        next_appt = (appt_date, display, time)
        break

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

# 4. Appointment statuses
# For each appointment, set status based on whether it's past, next, or upcoming
for appt_date, display, time in APPOINTMENTS:
    if appt_date < today:
        new_status = 'status: "done"'
        # Remove daysTo if present
        html = re.sub(
            rf'(date: "{re.escape(display)}",\s*\n\s*time: "{re.escape(time)}",\s*\n\s*who: "Oliver Wu",\s*\n\s*where: "[^"]*",\s*\n\s*)status: "[^"]*"(?:,\s*\n\s*daysTo: \d+)?',
            rf'\g<1>status: "done"',
            html
        )
    elif next_appt and appt_date == next_appt[0]:
        days_to_next = (appt_date - today).days
        html = re.sub(
            rf'(date: "{re.escape(display)}",\s*\n\s*time: "{re.escape(time)}",\s*\n\s*who: "Oliver Wu",\s*\n\s*where: "[^"]*",\s*\n\s*)status: "[^"]*"(?:,\s*\n\s*daysTo: \d+)?',
            rf'\g<1>status: "next",\n    daysTo: {days_to_next}',
            html
        )
    else:
        html = re.sub(
            rf'(date: "{re.escape(display)}",\s*\n\s*time: "{re.escape(time)}",\s*\n\s*who: "Oliver Wu",\s*\n\s*where: "[^"]*",\s*\n\s*)status: "[^"]*"(?:,\s*\n\s*daysTo: \d+)?',
            rf'\g<1>status: "upcoming"',
            html
        )

# ── Write back only if changed ─────────────────────────────────────────────────
if html != original:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    next_str = f"{next_appt[1]} in {(next_appt[0]-today).days}d" if next_appt else "no upcoming"
    print(f"✓ Updated: {today_str} | {days_since_injury}d since injury | ~{days_to_surgery}d to surgery | next: {next_str}")
else:
    print("No changes needed.")
