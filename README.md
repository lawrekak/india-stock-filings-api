# India Stock Filings API: BSE & NSE Corporate Announcements

**Get every corporate announcement from BSE and NSE as clean JSON, with filing PDF links.**
Quarterly results, board meetings, dividends, order wins, acquisitions, insider trading (SAST), credit ratings, AGMs. No scraping, no proxies, no maintenance on your side.

👉 **Run it now on Apify:** https://apify.com/guiltless_baluster/india-corporate-announcements?utm_source=github&utm_medium=readme

- 📈 ~400–700 BSE filings per trading day, newest first
- 🏷️ Category, sub-category, company name, BSE scrip code, IST timestamp
- 📄 Direct link to the filing PDF on bseindia.com
- 🔔 **Alert mode**: schedule every 15 min and get *only new* announcements
- 💸 **$2 per 1,000 announcements**. No subscription. Filtered-out rows and failed runs are free.

## Example output

```json
{
  "announcedAt": "2026-11-19T18:56:35+05:30",
  "exchange": "BSE",
  "companyName": "Wipro Ltd",
  "bseScripCode": "507685",
  "category": "Company Update",
  "subCategory": "Newspaper Publication",
  "headline": "Announcement under Regulation 30 (LODR)-Newspaper Publication",
  "attachmentUrl": "https://www.bseindia.com/xml-data/corpfiling/AttachLive/....pdf",
  "isCritical": false
}
```

## Quickstart

1. Create a free Apify account (includes $5/month of free usage): https://console.apify.com/sign-up
2. Copy your API token from **Settings → API & Integrations**.
3. Pick an example:

| Example | What it does |
|---|---|
| [`examples/python_quickstart.py`](examples/python_quickstart.py) | Fetch today's results & dividend announcements in Python |
| [`examples/node_quickstart.mjs`](examples/node_quickstart.mjs) | Same in Node.js |
| [`examples/curl.sh`](examples/curl.sh) | One `curl` call, JSON out |
| [`examples/telegram_alert_bot.py`](examples/telegram_alert_bot.py) | Push new order wins / results for your watchlist to Telegram |
| [`examples/google_sheets.gs`](examples/google_sheets.gs) | Auto-fill a Google Sheet every hour |

```bash
export APIFY_TOKEN=your_token
curl -s -X POST "https://api.apify.com/v2/acts/guiltless_baluster~india-corporate-announcements/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"exchanges":["BSE"],"daysBack":1,"categories":["Result","Dividend"]}'
```

## Input options

| Field | Example | Notes |
|---|---|---|
| `exchanges` | `["BSE"]` | BSE is most reliable. NSE needs an Indian residential proxy |
| `daysBack` | `3` | Or use `fromDate` / `toDate` (YYYY-MM-DD, max 92 days) |
| `bseScripCodes` | `["500325","532540"]` | Watchlist (Reliance, TCS) |
| `categories` | `["Result","Board Meeting"]` | Matches category or sub-category |
| `includeKeywords` / `excludeKeywords` | `["order"]` / `["trading window"]` | Case-insensitive |
| `onlyNew` + `stateKey` | `true`, `"my-watchlist"` | Alert mode, returns only rows not seen before |
| `maxResults` | `1000` | Hard stop |

## Use cases

- **Algo trading**: event-driven signals on results, buybacks, order wins, pledges
- **Telegram / WhatsApp stock alert channels**: real-time filings feed
- **Research & IR teams**: watchlist monitoring, competitor tracking
- **Fintech apps**: corporate actions calendar, news feed
- **AI / LLM**: feed filing PDFs into summarisation and RAG pipelines

## Guides

- [How to get BSE corporate announcements via API (2026)](https://lawrekak.github.io/india-stock-filings-api/2026/11/19/bse-corporate-announcements-api.html)
- [Build a Telegram alert bot for BSE results & order wins](https://lawrekak.github.io/india-stock-filings-api/2026/11/19/telegram-stock-alert-bot-bse-nse.html)
- [BSE announcements into Google Sheets automatically](https://lawrekak.github.io/india-stock-filings-api/2026/11/19/bse-announcements-google-sheets.html)
- [NSE corporate announcements in Python: what works from the cloud](https://lawrekak.github.io/india-stock-filings-api/2026/11/20/nse-corporate-announcements-python.html)

## FAQ

**Is this official?** No. The data comes from BSE/NSE public announcement pages. Not affiliated with either exchange.
**How fresh?** As soon as BSE publishes. Schedule every 5–15 minutes for near-real-time alerts.
**Historical data?** Up to 92 days per run; chain runs for longer periods.
**Need a custom field or an exchange we don't cover?** Open an issue.

---
⭐ Star the repo if it saves you a scraper.
