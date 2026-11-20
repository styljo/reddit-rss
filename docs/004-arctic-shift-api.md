# API Choice: Arctic Shift
**Date:** November 2026

## Context
Following Reddit's severe official API restrictions in mid-2023, free personal Developer App keys for scraping became unviable. We pivoted to third-party archival databases.

## Implementation
- **Method:** Queries `https://arctic-shift.photon-reddit.com/api` (a Pushshift alternative).
- **Routing:** Dynamically routes standard subreddit posts (`/posts/search`) and specific megathread replies (`/comments/search`) using regex matching against URLs in `feeds.json`.
- **Rate Limiting:** A hardcoded `time.sleep(3)` is enforced between feed queries to prevent spamming the API and triggering rate limits.

## Limitations & Mitigation
- **The Megathread Timeout (HTTP 422):** The API fails on massive, multi-year megathreads (e.g., the 3-year-old Itch.io thread). The backend database struggles to sort thousands of comments in real-time, timing out and returning a `"data": null` payload.
- **The 30-Day Window Fix:** To prevent timeouts, comment queries are bounded to the last 30 days (`after` parameter). If a quiet megathread returns 0 comments in that window, the script automatically drops the `after` parameter and retries to fetch the historical comments.
- **Write Fail-Safe:** Added a check in `scrape.py` (`if not entries:`). If the API returns an empty payload due to congestion, the script safely aborts the `.xml` file overwrite, preserving the previous feed state instead of corrupting it with an empty file.
