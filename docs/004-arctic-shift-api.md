# API Choice: Arctic Shift

**Date:** November 2026

## Context

Following Reddit's severe official API restrictions in mid-2023, free personal Developer App keys for scraping became unviable. We pivoted to third-party archival databases.

## Implementation

- **Method:** Queries `https://arctic-shift.photon-reddit.com/api` (a Pushshift alternative).
- **Routing & Query Params:** Dynamically routes standard subreddit posts (`/posts/search` with `subreddit`, `limit=100`, `sort=desc`) and specific megathread replies (`/comments/search` with `link_id=t3_<id>`, `limit=100`, `sort=desc`) using regex matching against URLs in `feeds.json`.
- **Retries & Rate Limiting:** Each feed query retries up to 3 times with a 40s timeout and incremental backoff (`5s`, `10s`). A hardcoded `time.sleep(3)` is enforced between feed queries to prevent spamming the API and triggering rate limits.

## Limitations & Mitigation

- **The Megathread Timeout (HTTP 422):** The API fails on massive, multi-year megathreads (e.g., the long-running Itch.io thread, active since 2021). The backend database struggles to sort thousands of comments in real-time, timing out and returning an HTTP 422 / `"data": null` payload.
- **The 30-Day Window Fix:** To prevent timeouts, comment queries are bounded to the last 30 days (`after` parameter). If a quiet megathread returns 0 comments in that window, the script automatically drops the `after` parameter and retries to fetch the historical comments.
- **Empty-Feed Fail-Safe:** Added a check in `scrape.py` (`if not entries:`). If a feed parses 0 items, the script skips writing that `.xml` file (preserving any existing local file) and omits it from `index_links`. In GitHub Actions—where `public/` starts empty—this triggers the All-or-Nothing guard (`len(index_links) < len(FEEDS)`) from [`002-github-actions-quirks.md`](./002-github-actions-quirks.md), aborting the build before deployment so live GitHub Pages feeds remain intact.
