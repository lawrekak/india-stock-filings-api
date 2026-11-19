"""Fetch today's BSE results & dividend announcements.

pip install apify-client
APIFY_TOKEN=xxx python python_quickstart.py
"""
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("guiltless_baluster/india-corporate-announcements").call(
    run_input={
        "exchanges": ["BSE"],
        "daysBack": 1,
        "categories": ["Result", "Dividend"],
        "maxResults": 200,
    }
)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f'{item["announcedAt"]}  {item["companyName"]:<40} {item["headline"][:70]}')
    print(f'    PDF: {item["attachmentUrl"]}')
