# API Choice: Arctic Shift

**Date:** November 2026

## Context

Following Reddit's severe official API restrictions in mid-2023, free personal Developer App keys for scraping became unviable. We pivoted to third-party archival databases.

## Implementation

- **Method:** Queries `https://arctic-shift.photon-reddit.com/api` (a Pushshift alternative).
- **Routing & Query Params:** Dynamically routes standard subreddit posts (`/posts/search` with `subreddit`, `limit=100`, `sort=desc`) and specific megathread replies (`/comments/search` with `link_id=t3_<id>`, `limit=100`, `sort=desc`) using regex matching against URLs in `feeds.json`.
- **Retries & Rate Limiting:** Each feed query retries up to 3 times with a 40s timeout and incremental backoff (`5s`, `10s`). A hardcoded `time.sleep(3)` is enforced between feed queries to avoid triggering rate limits.

## Limitations & Initial Mitigations (Unresolved)

- **The Megathread Timeout (HTTP 422):** The API struggles on massive, multi-year megathreads (e.g., the long-running Itch.io thread `p0ik3q` and Exiled Giveaways thread `p0ijjx`, both active since 2021). Queries frequently time out and return an `HTTP 422` with a `"data": null` payload (`"Timeout. Maybe slow down a bit"`).
- **30-Day Window Mitigation:** From the initial implementation, comment queries were bounded to the last 30 days (`after` parameter) to reduce database load, falling back to an unbounded query if 0 comments are returned. **This did not eliminate the timeouts**, and megathread comment reliability remained poor.
- **Empty-Feed Fail-Safe:** Added a check in `scrape.py` (`if not entries:`). If a feed parses 0 items, the script skips writing that `.xml` file (preserving any existing local file) and omits it from `index_links`. In GitHub Actions—where `public/` starts empty—this triggers the All-or-Nothing guard (`len(index_links) < len(FEEDS)`) from [`002-github-actions-quirks.md`](./002-github-actions-quirks.md), aborting the build before deployment so live GitHub Pages feeds remain intact.
- **Outcome:** Because megathread comment reliability remained unresolved, we moved on to test alternative data sources.
