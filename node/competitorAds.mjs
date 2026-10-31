// Google Ads Transparency Center "API" in a few lines: every ad a competitor runs, as JSON.
// Usage: APIFY_TOKEN=... node competitorAds.mjs nike.com HubSpot
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const queries = process.argv.slice(2).length ? process.argv.slice(2) : ['nike.com'];
const run = await client.actor('crunchy_galaxy_qcr/google-ads-transparency-scraper').call(
    { queries, maxAdsPerAdvertiser: Number(process.env.MAX_ADS || 50), region: process.env.REGION || 'anywhere' },
    { maxTotalChargeUsd: 1 },
);
const { items } = await client.dataset(run.defaultDatasetId).listItems();
const ads = items.filter((i) => i.type === 'ad');
console.table(ads.slice(0, 10).map(({ advertiserName, format, firstShown, lastShown, daysShown }) => ({ advertiserName, format, firstShown, lastShown, daysShown })));
for (const s of items.filter((i) => i.type === 'advertiserSummary')) console.log(`${s.advertiserName}: ${s.adsScraped} ads, by format ${JSON.stringify(s.adsByFormat)}`);
