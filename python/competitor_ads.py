"""Download every Google ad your competitors run (Google Ads Transparency Center) to CSV.

Usage:  APIFY_TOKEN=... python competitor_ads.py nike.com HubSpot --max-ads 50 --region US
Weekly monitoring: run it from cron / GitHub Actions and pass --previous-dataset <id from last run>
to get only NEW_AD / STOPPED_AD changes (see new_ads_alert.py).
"""
import argparse, csv, os, sys
from apify_client import ApifyClient

ACTOR = "crunchy_galaxy_qcr/google-ads-transparency-scraper"

p = argparse.ArgumentParser()
p.add_argument("queries", nargs="+", help="brand names, domains or AR... advertiser IDs")
p.add_argument("--max-ads", type=int, default=100)
p.add_argument("--region", default="anywhere")
p.add_argument("--format", default="ALL", choices=["ALL", "TEXT", "IMAGE", "VIDEO"])
p.add_argument("--previous-dataset")
p.add_argument("--out", default="competitor_ads.csv")
p.add_argument("--max-charge-usd", type=float, default=1.0, help="hard spending cap for this run")
a = p.parse_args()

client = ApifyClient(os.environ["APIFY_TOKEN"])
run_input = {
    "queries": [q for q in a.queries if not q.startswith("AR")],
    "advertiserIds": [q for q in a.queries if q.startswith("AR")],
    "maxAdsPerAdvertiser": a.max_ads, "region": a.region, "format": a.format,
}
if a.previous_dataset:
    run_input["previousRunDatasetId"] = a.previous_dataset

run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=a.max_charge_usd)
items = list(client.dataset(run.default_dataset_id).iterate_items())
ads = [i for i in items if i["type"] == "ad"]
cols = ["advertiserName", "format", "firstShown", "lastShown", "daysShown", "adUrl", "imageUrl", "creativeId"]
with open(a.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(ads)

for s in (i for i in items if i["type"] == "advertiserSummary"):
    est = s.get("totalAdsEstimate") or {}
    print(f"{s['advertiserName']}: {s['adsScraped']} ads scraped (Google estimates {est.get('min')}-{est.get('max')} total), "
          f"formats {s['adsByFormat']}, active in last 48h: {s['activeLast48h']}")
changes = [i for i in items if i["type"] == "change"]
if changes:
    print(f"{len(changes)} changes since the previous run")
print(f"Saved {len(ads)} ads to {a.out}. Dataset ID for next week's diff: {run.default_dataset_id}", file=sys.stderr)
