---
layout: post
title: "NSE corporate announcements in Python: what works from the cloud (and what gets blocked)"
description: "How to fetch NSE corporate announcements with Python in 2026, why requests from AWS/GCP servers get blocked, and the reliable alternatives for production."
---
Fetching NSE corporate announcements from your laptop is easy. Fetching them from a server every 15 minutes, reliably, is a different problem. This post walks through what actually works in 2026, with code, and where each approach breaks.

## The NSE endpoint everyone uses

The announcements page on nseindia.com is backed by a JSON endpoint:

```
https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=19-11-2026&to_date=20-11-2026
```

Add `&symbol=INFY` to narrow it to one company. Each row has the symbol, company name, ISIN, a short description, the broadcast time and a link to the attached PDF.

## Attempt 1: plain `requests` (fails)

```python
import requests
r = requests.get("https://www.nseindia.com/api/corporate-announcements",
                 params={"index": "equities", "from_date": "19-11-2026", "to_date": "20-11-2026"})
print(r.status_code)   # 401 or 403, or it hangs
```

NSE expects browser-like headers **and** session cookies that are set when you first load a normal page.

## Attempt 2: warm up a session (works locally)

```python
import requests

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
})
s.get("https://www.nseindia.com/companies-listing/corporate-filings-announcements", timeout=20)  # sets cookies
r = s.get("https://www.nseindia.com/api/corporate-announcements",
          params={"index": "equities", "from_date": "19-11-2026", "to_date": "20-11-2026"}, timeout=20)
rows = r.json()
for a in rows[:5]:
    print(a["an_dt"], a["symbol"], "-", a["desc"], a.get("attchmntFile"))
```

On a home broadband connection in India this usually works. Field names to know: `symbol`, `sm_name` (company), `sm_isin`, `desc`, `an_dt` (e.g. `20-Nov-2026 16:30:01`), `attchmntFile` (PDF), `attchmntText` (summary text).

## Attempt 3: the same script on a cloud server (blocked)

Deploy that script to AWS, GCP, Azure or most VPS providers and it typically starts returning **403s or empty responses**, sometimes after working for a day. NSE sits behind bot protection that scores datacenter IP ranges harshly. Things people try:

| Workaround | Result |
|---|---|
| Rotating user agents | Doesn't help; the IP range is the issue |
| Datacenter proxies | Mostly blocked too |
| Indian residential proxies | Works, but costs per GB and adds latency |
| Headless browser (Playwright) | Works sometimes, heavy and slow, still IP-scored |
| Running from a home Raspberry Pi | Works, until your power or ISP blips |

## The practical answer: use BSE for the feed

Almost every NSE-listed company is **also listed on BSE** and files the same disclosures there under SEBI's LODR rules, usually within the same minute. BSE's announcement API is far friendlier to cloud servers. It has its own quirks (it returns nothing for multi-day ranges across all companies, and rate-limits bursts with HTTP 403), but those are solvable with day-by-day paging and backoff.

If you don't want to maintain that, the [BSE & NSE Corporate Announcements Feed](https://apify.com/guiltless_baluster/india-corporate-announcements?utm_source=blog&utm_medium=nse-python) does it as a hosted API:

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("guiltless_baluster/india-corporate-announcements").call(run_input={
    "exchanges": ["BSE"],
    "daysBack": 1,
    "includeKeywords": ["result", "order", "dividend"],
    "excludeKeywords": ["trading window", "newspaper publication"],
})
for a in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(a["announcedAt"], a["companyName"], "|", a["headline"], "|", a["attachmentUrl"])
```

It costs $2 per 1,000 announcements, and Apify's free tier ($5/month) covers small watchlists. It also supports NSE: set `"exchanges": ["NSE"]` and enable Apify Proxy with Indian residential IPs in the input. That works around the blocking, at the cost of proxy usage.

## Mapping NSE symbols to BSE scrip codes

If your watchlist is in NSE symbols, you'll need BSE scrip codes (e.g. RELIANCE → 500325, TCS → 532540, INFY → 500209). Two ways:

1. Download BSE's list of scrips (Equity segment CSV from bseindia.com) and join on **ISIN**, which is identical on both exchanges.
2. Keep a small hand-made mapping for a short watchlist.

```python
import csv
isin_to_bse = {row["ISIN No"]: row["Security Code"] for row in csv.DictReader(open("bse_scrips.csv"))}
```

## Summary

- From your laptop: the NSE session warm-up works.
- From the cloud: NSE blocks datacenter IPs; use residential proxies or switch to BSE.
- For a maintained feed with PDF links and "only new" alert mode: use the hosted feed above, or see the [BSE API guide]({{ site.baseurl }}{% post_url 2026-11-19-bse-corporate-announcements-api %}) and the [Telegram alert bot]({{ site.baseurl }}{% post_url 2026-11-19-telegram-stock-alert-bot-bse-nse %}).

---
*Not affiliated with NSE or BSE. Not investment advice.*
