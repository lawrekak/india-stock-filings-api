---
layout: post
title: "Upcoming dividends, bonus & splits in India: build a corporate actions calendar in Python"
description: "Get every upcoming dividend (₹ per share), bonus issue, stock split, rights issue and buyback for BSE-listed companies as JSON, and turn it into a corporate actions calendar with Python."
---
If you hold Indian stocks, run a portfolio tracker or build anything for Indian investors, you eventually need the same thing: **a list of upcoming corporate actions**. Which companies go ex-dividend next week, and for how many rupees per share? Who has a stock split or bonus coming up? Which buybacks have a record date this month?

BSE publishes all of this on its corporate actions page. Getting it into code is harder than it looks. This guide shows how to build a clean corporate actions calendar in a few lines of Python, with real output from this week.

## What the data looks like on BSE

BSE's corporate actions page lists each action with a free-text **purpose** field, for example:

- `Interim Dividend - Rs. - 0.6000`
- `Stock Split From Rs.10/- to Rs.2/-`
- `Bonus issue 1:1`
- `Right Issue of Equity Shares`
- `Income Distribution (InvIT)`

That's fine for reading, not for filtering. To answer "dividends above ₹5 going ex in the next 30 days", you need the amount as a number, the action as a type, and the ex-date as a real date. You also need to handle BSE's habit of blocking scripted traffic from cloud servers.

## The shortcut: a ready-made corporate actions API

The [India Corporate Actions & Results Calendar](https://apify.com/guiltless_baluster/india-corporate-actions-calendar?utm_source=blog&utm_medium=india-corporate-actions-calendar) does the parsing for you. Each record comes back with:

| Field | Example |
|---|---|
| `actionType` | `dividend`, `bonus`, `split`, `rights`, `buyback`, `income_distribution`, `capital_reduction` |
| `dividendType`, `dividendPerShare` | `interim`, `0.6` |
| `splitFromFaceValue`, `splitToFaceValue` | `10`, `2` |
| `bonusRatio` | `1:1` |
| `exDate`, `recordDate`, `paymentDate` | ISO dates |
| `companyName`, `bseScripCode`, `symbol` | for joining with your holdings |

Pricing is **$3 per 1,000 records**. A month of every BSE corporate action is usually a few hundred records, so a full calendar costs well under a dollar. Apify's free plan ($5/month credit) covers it.

## Step 1: fetch the next 30 days

Get an API token from Apify (**Settings → API & Integrations**) and install the client:

```bash
pip install apify-client
export APIFY_TOKEN=your_token
```

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])

run = client.actor("guiltless_baluster/india-corporate-actions-calendar").call(
    run_input={"mode": "corporateActions", "daysAhead": 30}
)
actions = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(len(actions), "upcoming corporate actions")
```

The run takes a few seconds. Here is part of what it returned on 21 Nov 2026:

| Company | Action | Detail | Ex-date |
|---|---|---|---|
| Pashupati Cotspin | dividend | ₹0.02 interim | 2026-11-23 |
| Vraj Iron And Steel | dividend | ₹0.60 interim | 2026-11-25 |
| Zee Entertainment | buyback | Buy Back of Shares | 2026-11-25 |
| Fusion CX | dividend | ₹0.75 final | 2026-11-27 |
| Varvee Global | split | ₹5 → ₹2 | 2026-11-27 |
| Interarch Building Solutions | split | ₹10 → ₹2 | 2026-11-30 |
| Altius Telecom Infrastructure Trust | income_distribution | InvIT distribution | 2026-11-30 |
| S.P. Apparels | split | ₹10 → ₹2 | 2026-12-10 |

Thirteen actions in total, including four rights issues and a capital reduction. November is a quiet month; expect far more around results seasons and the March–September dividend window.

A single record looks like this:

```json
{
  "recordType": "corporate_action",
  "companyName": "Interarch Building Solutions Ltd",
  "bseScripCode": "544232",
  "purpose": "Stock Split From Rs.10/- to Rs.2/-",
  "actionType": "split",
  "splitFromFaceValue": 10,
  "splitToFaceValue": 2,
  "exDate": "2026-11-30",
  "recordDate": "2026-11-30"
}
```

## Step 2: filter server-side

You don't need to download everything and filter locally. The input accepts filters:

```python
# Only dividends of ₹5 or more per share, next 60 days
run_input = {
    "mode": "corporateActions",
    "actionTypes": ["dividend"],
    "minDividendPerShare": 5,
    "daysAhead": 60,
}

# Only splits and bonuses for a whole year (backtesting)
run_input = {
    "mode": "corporateActions",
    "actionTypes": ["split", "bonus"],
    "fromDate": "2025-11-01",
    "toDate": "2026-11-01",
}

# Only your holdings (BSE scrip codes)
run_input = {
    "mode": "corporateActions",
    "bseScripCodes": ["500325", "532540", "500209"],
    "daysAhead": 90,
}
```

You pay only for records returned, so tight filters keep costs near zero.

## Step 3: turn it into a calendar

Group by week with pandas and print something you can paste into a newsletter or Telegram channel:

```python
import pandas as pd

df = pd.DataFrame(actions)
df["exDate"] = pd.to_datetime(df["exDate"])
df["week"] = df["exDate"].dt.to_period("W-SUN").dt.start_time.dt.date

def describe(r):
    if r.actionType == "dividend" and pd.notna(r.dividendPerShare):
        kind = r.dividendType if isinstance(r.dividendType, str) else ""
        return f"₹{r.dividendPerShare:g}/share {kind} dividend".replace("  ", " ")
    if r.actionType == "split":
        return f"split ₹{r.splitFromFaceValue:g} → ₹{r.splitToFaceValue:g}"
    if r.actionType == "bonus":
        return f"bonus {r.bonusRatio}"
    return r.purpose

for week, g in df.sort_values("exDate").groupby("week"):
    print(f"\nWeek of {week}")
    for r in g.itertuples():
        print(f"  {r.exDate:%a %d %b}  {r.companyName:<40} {describe(r)}")
```

Output:

```
Week of 2026-11-23
  Mon 23 Nov  Pashupati Cotspin Ltd                    ₹0.02/share interim dividend
  Wed 25 Nov  Vraj Iron And Steel Ltd                  ₹0.6/share interim dividend
  Wed 25 Nov  Zee Entertainment Enterprises Ltd        Buy Back of Shares
  Fri 27 Nov  Fusion CX Ltd                            ₹0.75/share final dividend
  Fri 27 Nov  Varvee Global Ltd                        split ₹5 → ₹2
  ...
```

Want an `.ics` file so the dates show up in Google Calendar? Use the `ics` package:

```python
from ics import Calendar, Event

cal = Calendar()
for r in df.itertuples():
    e = Event(name=f"{r.companyName}: {describe(r)} (ex-date)", begin=r.exDate.date())
    e.make_all_day()
    cal.events.add(e)
open("corporate_actions.ics", "w").write(cal.serialize())
```

Import the file once, or host it and subscribe to the URL.

## Step 4: schedule it

On Apify, open the actor, save your input as a **task**, and add a **schedule** (for example every weekday at 08:00 IST). Each run writes a fresh dataset you can pull with one URL:

```
https://api.apify.com/v2/actor-tasks/<TASK_ID>/runs/last/dataset/items?token=<TOKEN>&format=csv
```

That URL works directly in Google Sheets (`=IMPORTDATA(...)`), Excel Power Query, n8n or Make.

## Bonus: the results calendar

The same actor has a second mode, `resultsCalendar`, that lists upcoming board meetings to approve quarterly results. Q3 FY27 results start in mid-January 2027, so this is the time to wire it up:

```python
run_input = {"mode": "resultsCalendar", "daysAhead": 14}
```

Use `"mode": "both"` to get actions and results meetings in one dataset.

## Pair it with the announcements feed

A corporate actions calendar tells you **what is scheduled**. The actual filings (the dividend declaration, the board outcome, the results PDF) come through BSE's announcements. For those, use the [BSE & NSE Corporate Announcements Feed](https://apify.com/guiltless_baluster/india-corporate-announcements?utm_source=blog&utm_medium=india-corporate-actions-calendar) with `categories: ["Dividend", "Corp. Action"]` and alert mode, as shown in the [Telegram alert bot guide](https://lawrekak.github.io/india-stock-filings-api/2026/11/19/telegram-stock-alert-bot-bse-nse.html).

## FAQ

**Does this cover NSE-only companies?** Almost every NSE-listed company is also listed on BSE, so the BSE calendar covers practically the whole market.

**How far back can I go?** Use `fromDate` / `toDate` for historical ranges, handy for backtesting split or bonus effects.

**Is it official?** No. Data comes from BSE's public corporate actions and results calendar pages. Not affiliated with BSE Ltd. Not investment advice.

👉 **Try it:** [India Corporate Actions & Results Calendar on Apify](https://apify.com/guiltless_baluster/india-corporate-actions-calendar?utm_source=blog&utm_medium=india-corporate-actions-calendar)
