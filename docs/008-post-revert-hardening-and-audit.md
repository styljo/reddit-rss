# Post-Revert Hardening & Arctic Shift Megathread Audit

**Date:** November 2026

## Context

After reverting from the failed native JSON ([`005-native-json-block.md`](./005-native-json-block.md)) and PullPush ([`006-pullpush-cloudflare-block.md`](./006-pullpush-cloudflare-block.md)) experiments and setting up a local Python workspace ([`007-local-development-setup.md`](./007-local-development-setup.md)), we hardened the repository/CI pipeline and ran a live audit of Arctic Shift and both diagnostic probes locally.

## 1. Repository, Script & CI Hardening

- **Diagnostic Organization:** Moved `test_reddit_native.py` and `test_pullpush_api.py` into `debug/`.
- **Split `build` / `deploy` Jobs & Syntax Gate:** Updated `.github/workflows/feed.yml` (building on [`002-github-actions-quirks.md`](./002-github-actions-quirks.md)) to run `python -m py_compile scrape.py` inside the `build` job and split GitHub Pages deployment into a separate `deploy` job gated by `if: github.ref == 'refs/heads/main'` so feature-branch CI runs do not trip `github-pages` environment branch protection rules.
- **Scraper Hardening (`scrape.py`):**
  - Replaced `resp.json().get("data", [])` with `resp.json().get("data") or []` so `"data": null` responses from Arctic Shift cannot raise a `TypeError`.
  - Replaced in-place `params.pop("after")` with a fresh `fallback_params` dictionary so retries keep the original `after` window on subsequent attempts.
  - Escaped `"` (`&quot;`) when rendering HTML `href` attributes in `parse_posts()`.

## 2. Live Audit of Arctic Shift (Megathread Issue Still Unresolved)

Running `scrape.py` and targeted API probes confirmed that reverting to Arctic Shift ([`004-arctic-shift-api.md`](./004-arctic-shift-api.md)) did **not** solve the megathread comment problem—and revealed a second, more severe ingestion gap:

1. **Intermittent `HTTP 422` Timeouts Persist:**
   - During a live `scrape.py` run, `exiled-giveaways-megathread` (`t3_p0ijjx`) failed twice with `HTTP 422: {"data":null,"error":"Timeout. Maybe slow down a bit"}` before succeeding on Attempt 3.
   - A standalone 7-day comment probe on `itchio-megathread` (`t3_p0ik3q`) also returned `HTTP 422` timeout.
2. **One-Month Megathread Indexing Cutoff (Since October 21, 2026):**
   - Newer `r/FreeGameFindings` submissions (`freegamefindings-new`) and comments on _recent_ threads are indexed up to `November 20, 2026`.
   - However, for both long-running 2021 megathreads—`p0ik3q` (**Itch.io Mega Thread #10**) and `p0ijjx` (**Exiled Giveaways Mega Thread #2**)—Arctic Shift has **zero comments indexed after `October 21, 2026`** (`2026-10-21T17:53:14Z` and `2026-10-21T08:51:59Z`, respectively), even though both threads remain active and unlocked on Reddit.
   - Because the last indexed comment is now more than 30 days old, the 30-day `after` query returns 0 results and `scrape.py` immediately drops `after` on every run, silently republishing the same 100 stale comments from September–October 2026.

## 3. Local Residential-IP Re-Verification of Diagnostic Probes

Testing both probes locally from a residential IP produced two findings:

- **`debug/test_reddit_native.py`:** Returned **`403 Forbidden`** (Reddit's `theme-beta` block page) locally as well, showing that `curl_cffi` (`impersonate="chrome120"`) alone does not bypass Reddit's WAF even from a residential IP ([`005-native-json-block.md`](./005-native-json-block.md)).
- **`debug/test_pullpush_api.py`:** Returned **`200 OK`** locally (confirming Cloudflare's challenge in [`006-pullpush-cloudflare-block.md`](./006-pullpush-cloudflare-block.md) was datacenter-IP-specific), **but** PullPush's index for `p0ik3q` is even staler than Arctic Shift (newest comment `2026-10-09T22:45:52Z`).

## Current Status

- **`freegamefindings-new.xml`:** Working and up to date via Arctic Shift.
- **`itchio-megathread.xml` & `exiled-giveaways-megathread.xml`:** **Unresolved.** Both feeds remain frozen at October 21, 2026 on Arctic Shift and continue to hit intermittent `HTTP 422` timeouts. Fixing them will require a different data source (e.g., authenticated Reddit OAuth API credentials or an alternative feed/scraper).
