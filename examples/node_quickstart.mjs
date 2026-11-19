// npm i apify-client
// APIFY_TOKEN=xxx node node_quickstart.mjs
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('guiltless_baluster/india-corporate-announcements').call({
    exchanges: ['BSE'],
    daysBack: 1,
    categories: ['Result', 'Dividend'],
    maxResults: 200,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const a of items) console.log(a.announcedAt, a.companyName, '-', a.headline, '\n  ', a.attachmentUrl);
