---
layout: post
title: "How to get BSE corporate announcements via API (2026 guide)"
description: "Pull every BSE corporate announcement (results, dividends, board meetings, order wins) as JSON with PDF links, in Python, Node or a single curl call."
---
If you've ever tried to pull corporate announcements from BSE programmatically, you know the pain: undocumented endpoints, blocked requests from cloud servers, a page that only shows one day at a time, and PDFs hidden behind odd paths. This guide shows the fastest working route in 2026.

## What you'll get

Each announcement comes back as one JSON row:

| Field | Example |
|---|---|
| `announcedAt` | `2026-11-19T18:56:35+05:30` |
| `companyName` | Wipro Ltd |
| `bseScripCode` | 507685 |
| `category` / `subCategory` | Company Update / Newspaper Publication |
| `headline` | Announcement under Regulation 30 (LODR) |
| `attachmentUrl` | link to the filing PDF |

A normal trading day has **400–700 filings** on BSE alone.

## Option 1: one curl call

```bash
curl -s -X POST "https://api.apify.com/v2/acts/guiltless_baluster~india-corporate-announcements/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"exchanges":["BSE"],"daysBack":1,"categories":["Result"]}'
```

You need a free [Apify account](https://console.apify.com/sign-up) for the token. It comes with $5 of monthly free usage, which covers thousands of announcements.

## Option 2: Python

```python
from apify_client import ApifyClient
client = ApifyClient("YOUR_TOKEN")
run = client.actor("guiltless_baluster/india-corporate-announcements").call(
    run_input={"exchanges": ["BSE"], "daysBack": 1, "categories": ["Result", "Dividend"]})
for a in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(a["companyName"], "|", a["headline"], "|", a["attachmentUrl"])
```

## Filtering that actually helps

- **Watchlist:** `"bseScripCodes": ["500325", "532540"]`
- **Only what matters:** `"categories": ["Result", "Board Meeting", "Dividend"]`
- **Kill the noise:** `"excludeKeywords": ["trading window", "newspaper publication"]` removes roughly a third of daily filings that are pure compliance boilerplate.
- **History:** `"fromDate": "2026-09-01", "toDate": "2026-09-30"` (up to 92 days per run).

## Why not scrape BSE yourself?

You can, and many people do. What usually breaks:

1. BSE's API returns **nothing for multi-day ranges** across all companies, so you have to loop day by day.
2. It **rate-limits** bursts with HTTP 403s; you need backoff and retries.
3. PDF links switch between "live" and "historical" folders depending on a flag.
4. It changes without notice, and your cron job fails silently.

Paying $2 per 1,000 rows is usually cheaper than an hour of fixing a broken scraper.

## Real-time alerts

Turn on `"onlyNew": true` and schedule the run every 15 minutes. Each run returns only announcements you haven't seen, so you don't pay twice. See the [Telegram alert bot guide]({{ site.baseurl }}{% post_url 2026-11-19-telegram-stock-alert-bot-bse-nse %}).

## What about NSE?

NSE's site blocks most cloud IPs. The feed supports NSE through an Indian residential proxy, but almost every NSE-listed company also files on BSE, so BSE alone covers most needs.

---
*Not investment advice. Not affiliated with BSE Ltd.*
