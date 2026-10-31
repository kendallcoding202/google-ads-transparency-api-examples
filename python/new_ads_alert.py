"""Alert on competitors' NEW Google ads since the last run (ad spy mode).

Stores the last dataset ID in .last_dataset so you can run it daily from cron.
Prints new ads; swap print() for a Slack webhook / email if you want push alerts.
Usage: APIFY_TOKEN=... python new_ads_alert.py hubspot.com --max-ads 200
"""
import argparse, json, os, pathlib, urllib.request
from apify_client import ApifyClient

p = argparse.ArgumentParser()
p.add_argument("queries", nargs="+"); p.add_argument("--max-ads", type=int, default=200)
p.add_argument("--slack-webhook", default=os.environ.get("SLACK_WEBHOOK_URL"))
a = p.parse_args()
state = pathlib.Path(".last_dataset")
client = ApifyClient(os.environ["APIFY_TOKEN"])
run_input = {"queries": a.queries, "maxAdsPerAdvertiser": a.max_ads}
if state.exists():
    run_input["previousRunDatasetId"] = state.read_text().strip()
run = client.actor("crunchy_galaxy_qcr/google-ads-transparency-scraper").call(run_input=run_input, max_total_charge_usd=1.0)
state.write_text(run.default_dataset_id)
if "previousRunDatasetId" not in run_input:
    print("First run saved as the baseline. Run again tomorrow to see new ads."); raise SystemExit
new = [i for i in client.dataset(run.default_dataset_id).iterate_items() if i.get("change") == "NEW_AD"]
lines = [f"New {n['format']} ad from {n['advertiserName']} (first shown {n['firstShown']}): {n['adUrl']}" for n in new]
print("\n".join(lines) or "No new ads.")
if lines and a.slack_webhook:
    req = urllib.request.Request(a.slack_webhook, json.dumps({"text": "\n".join(lines[:30])}).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(req)
