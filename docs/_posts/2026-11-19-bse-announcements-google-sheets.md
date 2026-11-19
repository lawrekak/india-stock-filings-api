---
layout: post
title: "BSE announcements into Google Sheets automatically (no code server)"
description: "A 20-line Apps Script that appends new BSE corporate announcements to a Google Sheet every hour."
---
Want a live log of BSE filings for your portfolio or coverage list without running any servers? Google Sheets plus Apps Script can do it.

## Setup (5 minutes)

1. Open a new Google Sheet → **Extensions → Apps Script**.
2. Paste the script below.
3. **Project Settings → Script properties** → add `APIFY_TOKEN` (free from [apify.com](https://console.apify.com/sign-up)).
4. **Triggers → Add trigger** → `fetchAnnouncements`, time-driven, every hour.

```javascript
function fetchAnnouncements() {
  const token = PropertiesService.getScriptProperties().getProperty('APIFY_TOKEN');
  const url = 'https://api.apify.com/v2/acts/guiltless_baluster~india-corporate-announcements/run-sync-get-dataset-items?token=' + token;
  const input = { exchanges: ['BSE'], daysBack: 1, onlyNew: true, stateKey: 'google-sheet',
                  excludeKeywords: ['trading window', 'newspaper publication'] };
  const res = UrlFetchApp.fetch(url, { method: 'post', contentType: 'application/json',
                                       payload: JSON.stringify(input), muteHttpExceptions: true });
  const items = JSON.parse(res.getContentText());
  const sheet = SpreadsheetApp.getActiveSheet();
  if (sheet.getLastRow() === 0)
    sheet.appendRow(['Time (IST)', 'Company', 'Scrip', 'Category', 'Sub-category', 'Headline', 'PDF']);
  items.forEach(a => sheet.appendRow([a.announcedAt, a.companyName, a.bseScripCode,
                                      a.category, a.subCategory, a.headline, a.attachmentUrl]));
}
```

## Tips

- **Watchlist only:** add `bseScripCodes: ['500325','532540']` to the input.
- **Results season:** add `categories: ['Result']` and switch the trigger to every 15 minutes.
- **Filter view:** use Sheets' filter on the Category column to build a daily "results" or "dividends" tab.

## Cost

All BSE filings for a month is roughly 12,000 rows, about **$24**. A focused watchlist usually costs well under the free $5 credit.

---
*Not affiliated with BSE Ltd. Not investment advice.*
