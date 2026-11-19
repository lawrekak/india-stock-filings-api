---
layout: post
title: "Build a Telegram alert bot for BSE results & order wins in 15 minutes"
description: "Get a Telegram message the moment a company on your watchlist files results, an order win, a dividend or a buyback on BSE."
---
Market-moving filings (an order win, a surprise result, a buyback) hit BSE minutes before most news apps pick them up. Here's how to get them on Telegram for your own watchlist, in about 15 minutes and roughly ₹0 to start.

## 1. Create the bot

1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Send any message to your new bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy your `chat.id`.

## 2. Get an Apify token

Sign up at [apify.com](https://console.apify.com/sign-up) (free $5/month usage) and copy your API token.

## 3. The script

```python
import os, requests
from apify_client import ApifyClient

WATCHLIST = ["500325", "532540", "500209"]          # Reliance, TCS, Infosys
KEYWORDS  = ["result", "order", "dividend", "buyback", "acquisition"]

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("guiltless_baluster/india-corporate-announcements").call(run_input={
    "exchanges": ["BSE"], "daysBack": 1,
    "bseScripCodes": WATCHLIST, "includeKeywords": KEYWORDS,
    "excludeKeywords": ["trading window"],
    "onlyNew": True, "stateKey": "tg-watchlist",
})
for a in client.dataset(run["defaultDatasetId"]).iterate_items():
    requests.post(f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage", json={
        "chat_id": os.environ["TG_CHAT"],
        "text": f"📢 {a['companyName']}\n{a['headline']}\n{a['attachmentUrl'] or ''}",
    })
```

`onlyNew` is the key: the feed remembers what it already sent you, so each run delivers (and bills) only fresh filings.

## 4. Run it every 15 minutes

Pick one:

- **GitHub Actions** (free): a workflow with `schedule: - cron: "*/15 3-11 * * 1-5"` (market hours in UTC).
- **cron** on any server.
- **Apify Schedules**: schedule the actor itself and attach a webhook.

## What it costs

A 20-stock watchlist typically produces 5–30 relevant filings a day. At $2 per 1,000 that's **under ₹100 a month**, well inside Apify's free $5 credit.

## Ideas to extend it

- Run a public Telegram channel for a sector (pharma order wins, PSU results).
- Add `"categories": ["Insider Trading / SAST"]` to track promoter buying.
- Pipe the PDF link into an LLM for a one-line summary.

Full script: [examples/telegram_alert_bot.py](https://github.com/lawrekak/india-stock-filings-api/blob/main/examples/telegram_alert_bot.py).

---
*Not investment advice.*
