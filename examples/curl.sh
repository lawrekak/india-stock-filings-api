#!/usr/bin/env bash
# Today's BSE results & dividend announcements as JSON.
# Usage: APIFY_TOKEN=xxx ./curl.sh
set -euo pipefail
curl -s -X POST \
  "https://api.apify.com/v2/acts/guiltless_baluster~india-corporate-announcements/run-sync-get-dataset-items?token=${APIFY_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"exchanges":["BSE"],"daysBack":1,"categories":["Result","Dividend"],"maxResults":200}'
