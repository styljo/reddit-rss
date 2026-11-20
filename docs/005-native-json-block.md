# The Native Reddit JSON Experiment

**Date:** November 2026

## Goal

Attempted to eliminate Arctic Shift's ingestion lag and megathread timeouts ([`004-arctic-shift-api.md`](./004-arctic-shift-api.md)) by pulling data directly from Reddit's native JSON feeds (e.g., `.../comments/p0ik3q.json?sort=new`).

## Method

Created a standalone probe script (`test.py`, renamed `test_reddit_native.py`) utilizing `curl_cffi` to spoof a Google Chrome 120 TLS fingerprint (`impersonate="chrome120"`), and temporarily ran it in `.github/workflows/feed.yml` to test bypassing Reddit's bot detection.

## Result

- **Status:** `403 Forbidden` (Failed).
- **Root Cause:** GitHub Actions executes on Microsoft Azure cloud servers, and Reddit's Web Application Firewall (WAF) aggressively blocks unauthenticated `.json` requests from datacenter IP ranges.
- **Conclusion:** Unauthenticated native JSON scraping with `curl_cffi` is not viable on GitHub Actions.
- **Rollback / Active State:** Reverted `.github/workflows/feed.yml` back to `scrape.py` (no changes were applied to `scrape.py`), keeping Arctic Shift active while evaluating other third-party archives. The probe script was retained in the repository for diagnostic testing.
