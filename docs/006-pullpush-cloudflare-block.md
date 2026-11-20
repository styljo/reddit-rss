# PullPush API Experiment

**Date:** November 2026

## Goal

After direct Reddit JSON scraping failed in [`005-native-json-block.md`](./005-native-json-block.md), attempted to swap Arctic Shift for PullPush (`api.pullpush.io`) to resolve API timeouts when querying the long-running Itch.io megathread (`p0ik3q`, active since 2021).

## Method

- Created a standalone probe (`test_pullpush.py`, renamed `test_pullpush_api.py`) and ran it via `.github/workflows/feed.yml`.
- Switched from standard `requests` to `from curl_cffi import requests` (without browser TLS `impersonate`, unlike `test_reddit_native.py`) because `.github/workflows/feed.yml` installs `curl_cffi` and `markdown` rather than `requests`.

## Result

- **Status:** `403 Forbidden` (Failed on GitHub Actions).
- **Root Cause:** PullPush is protected by Cloudflare. Cloudflare flagged the GitHub Actions Microsoft Azure IP as a bot and returned a JavaScript challenge (`<title>Just a moment...</title>`).
- **Conclusion:** Like Reddit's native JSON, PullPush cannot be queried reliably from GitHub Actions runners due to datacenter IP blocking.
- **Rollback / Active State:** Reverted `.github/workflows/feed.yml` back to `python scrape.py` (Arctic Shift), leaving Arctic Shift's megathread issues unresolved. The probe script was retained in the repository for diagnostic testing.
