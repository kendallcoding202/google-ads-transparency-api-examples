"""Is ChatGPT / Gemini / Perplexity recommending your brand? Track AI share of voice over time.

Usage: APIFY_TOKEN=... python ai_visibility.py --brand "Notion | notion.com" \
         --competitor "Confluence | atlassian.com" --competitor "Coda | coda.io" \
         --prompt "What is the best wiki tool for a startup?" --tracking-name notion-weekly
Appends one row per run to ai_visibility_history.csv (open it in Google Sheets for a trend chart).
"""
import argparse, csv, os, pathlib
from apify_client import ApifyClient

p = argparse.ArgumentParser()
p.add_argument("--brand", required=True); p.add_argument("--competitor", action="append", default=[])
p.add_argument("--prompt", action="append", default=[]); p.add_argument("--category")
p.add_argument("--engines", default="chatgpt-search,gemini-knowledge", help="comma list; also: chatgpt-knowledge, perplexity-search"); p.add_argument("--tracking-name")
p.add_argument("--max-charge-usd", type=float, default=1.0)
a = p.parse_args()

client = ApifyClient(os.environ["APIFY_TOKEN"])
run_input = {"brand": a.brand, "competitors": a.competitor, "prompts": a.prompt, "engines": a.engines.split(",")}
if a.category: run_input["category"] = a.category
if a.tracking_name: run_input["trackingName"] = a.tracking_name
run = client.actor("crunchy_galaxy_qcr/ai-visibility-tracker").call(run_input=run_input, max_total_charge_usd=a.max_charge_usd)
summary = client.key_value_store(run.default_key_value_store_id).get_record("SUMMARY")["value"]

print(f"{'Brand':<14}{'Visibility %':>13}{'Share of voice %':>18}{'Avg rank':>10}")
for e in summary["overall"]["entities"]:
    print(f"{e['name']:<14}{e['visibilityRate'] or 0:>13}{e['shareOfVoice'] or 0:>18}{str(e['avgRank'] or '-'):>10}")
for row in client.dataset(run.default_dataset_id).iterate_items():
    if not row["brandMentioned"]:
        print(f"GAP [{row['engine']}]: \"{row['prompt']}\" mentions {', '.join(row['mentionedInOrder']) or 'no tracked brand'}")

hist = pathlib.Path("ai_visibility_history.csv"); new = not hist.exists()
b = summary["overall"]["brand"]
with hist.open("a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["date", "brand", "answers", "visibilityRate", "shareOfVoice", "avgRank"])
    w.writerow([summary["generatedAt"][:10], b["name"], summary["overall"]["answers"], b["visibilityRate"], b["shareOfVoice"], b["avgRank"]])
print(f"Report: https://api.apify.com/v2/key-value-stores/{run.default_key_value_store_id}/records/REPORT")
