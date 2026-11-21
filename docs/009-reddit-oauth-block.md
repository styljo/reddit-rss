# Reddit OAuth App Creation Attempt

**Date:** November 2026

## Goal

After [`008-post-revert-hardening-and-audit.md`](./008-post-revert-hardening-and-audit.md) confirmed that Arctic Shift still hits `HTTP 422` timeouts and stopped indexing comments on both 2021 megathreads (`p0ik3q`, `p0ijjx`) after October 21, 2026, attempted to register a personal Reddit OAuth `script` application to query `https://oauth.reddit.com` via `client_credentials` in GitHub Actions.

## Method

- Logged in and submitted the **create application** form (type: `script`, redirect URI: `http://localhost:8080`, compliant name without the word `"reddit"`).
- Retried across two consecutive days on both `https://www.reddit.com/prefs/apps` and `https://old.reddit.com/prefs/apps`.

## Result

- **Status:** `an error occurred (status: 500)` on every attempt across both `www.reddit.com` and `old.reddit.com`.
- **Root Cause:** Server-side failure / deprecation of Reddit's legacy self-service `prefs/apps` app-creation endpoint alongside Reddit's Responsible Builder Policy requiring manual API pre-approval (consistent with the restriction noted in [`004-arctic-shift-api.md`](./004-arctic-shift-api.md)). Basic input validation (such as rejecting `"reddit"` in the client name) still runs, but creating the OAuth client consistently fails with HTTP `500`.
- **Conclusion:** Self-service official Reddit OAuth credentials are not obtainable right now, closing off authenticated `oauth.reddit.com` access unless pre-approval is granted or Reddit restores `prefs/apps`.
- **Active State:** No changes were applied to `scrape.py`. Arctic Shift remains the active backend (`freegamefindings-new.xml` updates normally; both megathread feeds remain stale at October 21, 2026).
