// Track ChatGPT brand mentions and AI share of voice vs competitors.
// Usage: APIFY_TOKEN=... node aiVisibility.mjs
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('crunchy_galaxy_qcr/ai-visibility-tracker').call({
    brand: 'Notion | notion.com | notion.so',
    competitors: ['Confluence | atlassian.com', 'Coda | coda.io'],
    prompts: (process.env.PROMPTS || 'What is the best wiki and docs tool for a remote startup team?').split('|'),
    // Options: chatgpt-search, chatgpt-knowledge, gemini-knowledge, perplexity-search
    engines: (process.env.ENGINES || 'chatgpt-search,gemini-knowledge').split(','),
}, { maxTotalChargeUsd: 1 });
const { value: summary } = await client.keyValueStore(run.defaultKeyValueStoreId).getRecord('SUMMARY');
console.table(summary.overall.entities.map(({ name, visibilityRate, shareOfVoice, avgRank }) => ({ name, visibilityRate, shareOfVoice, avgRank })));
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const r of items) console.log(`[${r.engine}] ${r.prompt} -> ${r.brandMentioned ? `mentioned, rank ${r.brandRank}, ${r.brandSentiment}` : 'NOT mentioned'}`);
