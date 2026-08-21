# Collectors API — 31 ready-made scrapers you call with a keyword, not a URL

Most scraping APIs hand you a fetcher and leave the parsing to you. The
[QuanticData Collectors](https://quanticdata.io/collectors/) are the other half: **31 versioned
scrapers** with a published input schema, a published output schema, an hourly health probe and
a price per **delivered row**. You send `{"query": "coffee roasters", "location": "Milan, Italy"}`
and get typed rows back — no selectors, no pagination logic, no maintenance when the site
redesigns.

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here

python3 catalog.py                       # list all 31, with your price and health
python3 run_collector.py web_search --input '{"query":"proxy api","country":"us"}'
python3 run_collector.py google_maps_places \
    --input '{"query":"coffee roasters","location":"Milan, Italy","max_results":40}' --csv places.csv
```

## The three endpoints

| Call | What it does |
|---|---|
| `GET /v1/scraper/collectors` | the catalogue: schemas, examples, health, your unit price. Free. |
| `POST /v1/scraper/collectors/{slug}/run` | run one. Short runs answer `200` with the rows; long ones answer `202` + `run_id`. |
| `GET /v1/scraper/collectors/runs/{runId}` | one run and its rows. `?format=csv` streams CSV. Free. |

## The catalogue

| Category | Collectors |
|---|---|
| Search engines | `web_search` `search_images` `search_videos` |
| SEO | `keyword_ideas` |
| E-commerce | `amazon_search` `amazon_product` `ebay_search` `aliexpress_search` `google_shopping` `product_offers` |
| Local | `google_maps_places` `place_reviews` |
| Jobs | `google_jobs` `linkedin_jobs` `indeed_jobs` |
| News | `google_news` |
| Social | `youtube_search` `youtube_channel` `instagram_profile` `tiktok_profile` `tiktok_video` `reddit_posts` |
| Apps | `app_store_apps` `google_play_apps` |
| Real estate | `zillow_search` |
| Companies & leads | `linkedin_profile` `linkedin_company` `company_profile` `site_contacts` `local_business_leads` |
| Travel | `hotels` |

Prices run from **$0.0002 per keyword** (`keyword_ideas`) to **$0.03 per enriched company
profile** — `catalog.py` prints the live list with your tier discount applied.

## Files

| File | What it does |
|---|---|
| [`catalog.py`](catalog.py) | fetch the catalogue, print price/health/units, dump schemas |
| [`run_collector.py`](run_collector.py) | generic CLI runner: sync or async, JSON or CSV out |
| [`async_runs.py`](async_runs.py) | force `async: true`, poll several runs concurrently |
| [`validate_input.py`](validate_input.py) | check your input against the published JSON Schema before spending anything |
| [`pipeline.py`](pipeline.py) | chain collectors: `google_maps_places` → `site_contacts` → enriched CSV |

## Billing, precisely

Pay per **delivered** row at the collector's unit price. Zero results costs zero. A failed run
costs zero. A run that returns fewer rows than `max_results` charges only what it delivered, and
comes back with `partial: true` plus a note explaining why it stopped.

```jsonc
// POST /v1/scraper/collectors/web_search/run  →  200
{ "run_id": "…", "status": "done", "count": 20, "partial": false,
  "results": [ { "rank": 1, "title": "…", "link": "…", "snippet": "…" } ],
  "usage": { "cost_usd": 0.008 } }

// long run  →  202
{ "run_id": "…", "status": "queued", "statusUrl": "/api/v1/scraper/collectors/runs/…" }
```

## Related

- [Collectors overview](https://quanticdata.io/collectors/) · [Documentation](https://quanticdata.io/docs/)
- [Google Search Results API](https://quanticdata.io/collectors/google-search-results-api/) · [Keyword research API](https://quanticdata.io/collectors/keyword-research-api/)
- [Lead scraper API](https://quanticdata.io/collectors/lead-scraper-api/) · [Company data API](https://quanticdata.io/collectors/company-data-api/)
- [MCP server](https://quanticdata.io/mcp-server/) — the same collectors as agent tools

MIT licensed.
