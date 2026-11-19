"""Push NEW BSE announcements for your watchlist to a Telegram chat.

Run this every 15 minutes (cron, GitHub Actions, or an Apify schedule + webhook).
Alert mode (onlyNew) means you only receive, and only pay for, announcements you haven't seen.

pip install apify-client requests
APIFY_TOKEN=xxx TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=xxx python telegram_alert_bot.py
"""
import os
import requests
from apify_client import ApifyClient

WATCHLIST = ["500325", "532540", "500209", "532174"]  # Reliance, TCS, Infosys, ICICI Bank
KEYWORDS = ["result", "order", "dividend", "buyback", "acquisition", "bonus", "split"]

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("guiltless_baluster/india-corporate-announcements").call(
    run_input={
        "exchanges": ["BSE"],
        "daysBack": 1,
        "bseScripCodes": WATCHLIST,
        "includeKeywords": KEYWORDS,
        "excludeKeywords": ["trading window", "newspaper publication"],
        "onlyNew": True,
        "stateKey": "telegram-watchlist",
    }
)
bot, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
for a in client.dataset(run["defaultDatasetId"]).iterate_items():
    text = f"📢 *{a['companyName']}*\n{a['headline']}\n_{a['category']} · {a['announcedAt'][11:16]} IST_\n{a['attachmentUrl'] or ''}"
    requests.post(f"https://api.telegram.org/bot{bot}/sendMessage",
                  json={"chat_id": chat, "text": text, "parse_mode": "Markdown"}, timeout=20)
