# Google Ads Transparency Center API and AI Brand Visibility Tracker: examples

Copy-paste **Python and Node.js examples** for two jobs that have no official API:

1. **Google Ads Transparency Center API**: pull every Google Search, image and YouTube ad a competitor is running, with first/last shown dates, days running, preview images, per-country details and new-ad alerts. This is a **competitor ads scraper** you can automate.
2. **AI brand visibility tracker**: see whether **ChatGPT, Gemini and Perplexity mention and recommend your brand** vs competitors, your rank and sentiment, which sites the AI cites, and how your **share of voice in AI answers** changes over time.

Both run on Apify as pay-per-result Actors, so there are no proxies, captchas or OpenAI keys to manage:

| Actor | Store page | Price |
|---|---|---|
| Google Ads Transparency & Ad Library Scraper | https://apify.com/crunchy_galaxy_qcr/google-ads-transparency-scraper | $1.50 / 1,000 ads |
| AI Search Visibility Tracker: ChatGPT, Gemini & Perplexity | https://apify.com/crunchy_galaxy_qcr/ai-visibility-tracker | $0.04 / AI answer |

New Apify accounts include monthly free credit, which is enough to try both.

## Setup

```bash
export APIFY_TOKEN=...   # Apify Console → Settings → API & Integrations
# Python
pip install -r python/requirements.txt
# Node
cd node && npm install
```

Every example passes a `maxTotalChargeUsd` / `max_total_charge_usd` cap, so a typo can't run up a bill.

---

## 1. Google Ads Transparency Center API (competitor ads)

### Python: competitor ads to CSV
```bash
python python/competitor_ads.py nike.com HubSpot --max-ads 50 --region US
```
```
Hubspot, Inc.: 10 ads scraped (Google estimates 2000-3000 total), formats {'TEXT': 9, 'VIDEO': 1}, active in last 48h: 10
Saved 10 ads to competitor_ads.csv. Dataset ID for next week's diff: CMaAAI5XezPGUthlI
```

### Node.js
```bash
MAX_ADS=10 node node/competitorAds.mjs HubSpot
```

### Minimal code
```python
from apify_client import ApifyClient
client = ApifyClient(TOKEN)
run = client.actor("crunchy_galaxy_qcr/google-ads-transparency-scraper").call(
    run_input={"queries": ["nike.com"], "maxAdsPerAdvertiser": 100, "region": "US"},
    max_total_charge_usd=1.0)
for item in client.dataset(run.default_dataset_id).iterate_items():
    if item["type"] == "ad":
        print(item["advertiserName"], item["format"], item["firstShown"], item["daysShown"], item["adUrl"])
```

### Real output (Oct 31, 2026, trimmed)
| advertiser | format | first shown | last shown | days shown |
|---|---|---|---|---|
| Hubspot, Inc. | TEXT | 2025-05-13 | 2026-10-31 | 502 |
| Hubspot, Inc. | VIDEO | 2025-09-11 | 2026-10-31 | 394 |
| Hubspot, Inc. | TEXT | 2026-04-14 | 2026-10-31 | 200 |
| Hubspot, Inc. | TEXT | 2026-09-10 | 2026-10-31 | 52 |

Each advertiser also gets a summary record: Google's total-ads estimate (HubSpot 2,000–3,000; Nike 50,000–60,000), ads by format, ads active in the last 48h, and the **longest-running ads**. HubSpot's top one had run 1,830 days, and an ad that runs that long is usually a winner. Full samples: [`examples/ads_output_sample.json`](examples/ads_output_sample.json), input: [`examples/ads_input.json`](examples/ads_input.json).

### Input options
`queries` (brand names or domains), `advertiserIds` (`AR…`), `region` (US, GB, DE…), `format` (TEXT/IMAGE/VIDEO), `dateFrom`/`dateTo`, `maxAdsPerAdvertiser`, `extractAdText` (headline/description of text ads), `includeRegionDetails` (per-country dates, EU impression ranges), `previousRunDatasetId` (change tracking).

---

## 2. AI brand visibility tracker (ChatGPT brand mentions)

### Python: share of voice and gap prompts, appended to a history CSV
```bash
python python/ai_visibility.py --brand "Notion | notion.com" \
  --competitor "Confluence | atlassian.com" --competitor "Coda | coda.io" \
  --prompt "What is the best team wiki tool?" --tracking-name notion-weekly
```
```
Brand          Visibility %  Share of voice %  Avg rank
Notion                  100                50         1
Confluence              100                50         2
Report: https://api.apify.com/v2/key-value-stores/<id>/records/REPORT
```

### Node.js
```bash
cd node && node aiVisibility.mjs
```

### Real output (Notion vs Confluence, Coda, ClickUp; 2 prompts × ChatGPT-with-search + Gemini)
| brand | visibility | share of voice | avg rank |
|---|---|---|---|
| Notion | 100% | 40% | 1.0 |
| Confluence | 100% | 40% | 2.25 |
| Coda | 50% | 20% | 2.5 |
| ClickUp | 0% | 0% | – |

Per-answer rows include `brandMentioned`, `brandRank`, `brandSentiment`, a one-line `brandDescription`, `otherBrands` (competitors you didn't list, such as GitBook, Slab and Obsidian here) and `citedDomains` (ChatGPT cited gitbook.com and usewhale.io). Samples: [`examples/tracker_output_sample.json`](examples/tracker_output_sample.json), [`examples/tracker_summary_sample.json`](examples/tracker_summary_sample.json).

---

## Recipes

### Weekly competitor ad monitoring to Google Sheets or CSV
1. Run `competitor_ads.py` weekly from cron or GitHub Actions (`on: schedule`).
2. Import the CSV with Google Sheets `=IMPORTDATA()` from a hosted copy, or skip the script: in Apify Console, create a **Schedule** for the Actor and add the **Google Sheets integration**, which needs no code.

### Alert on competitors' new ads (ad spy)
`python python/new_ads_alert.py hubspot.com` keeps the last run's dataset ID in `.last_dataset` and passes it as `previousRunDatasetId`. The Actor returns `NEW_AD` records only for ads that weren't in the previous run **and** were first shown since then. Set `SLACK_WEBHOOK_URL` to push them to Slack. Run it daily.

### Track brand share of voice in AI answers over time
Run `ai_visibility.py` weekly with the same `--tracking-name`. Each run appends a row to `ai_visibility_history.csv` (date, visibility rate, share of voice, average rank) that you can chart in Sheets. The Actor's HTML **REPORT** also shows the trend since the last run. Use 2–3 `samplesPerPrompt` for stable numbers, because AI answers vary.

### Use from AI agents (MCP)
Both Actors are callable from the [Apify MCP server](https://docs.apify.com/mcp). Try: *"Find all Google ads Nike ran in Germany this month"* or *"How often does ChatGPT recommend Notion vs Confluence?"*

## FAQ
**Is there an official Google Ads Transparency Center API?** No, except a BigQuery dataset that covers only EU/Turkey ads with a delay. The Actor reads the same public data the website shows.

**Why do ChatGPT API answers differ from the ChatGPT app?** The tracker uses OpenAI's model with the web-search tool, which is close to the app with search on, but personalization and sampling still differ. Repeat prompts for stable stats.

## License
MIT. See [LICENSE](LICENSE).

---
Maintained by Kendall Sorenson ([@kendallcoding202](https://github.com/kendallcoding202)), the developer of both Actors. Issues and PRs are welcome.
