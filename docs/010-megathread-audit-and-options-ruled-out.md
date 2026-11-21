# Megathread Sanity Check & Ruled-Out Alternatives

**Date:** November 2026

## Context

Following the Arctic Shift staleness audit ([`008-post-revert-hardening-and-audit.md`](./008-post-revert-hardening-and-audit.md)) and Reddit OAuth `HTTP 500` block ([`009-reddit-oauth-block.md`](./009-reddit-oauth-block.md)), we verified live activity on Reddit for both 2021 megathreads and evaluated the remaining alternative paths.

## 1. Live Reddit Sanity Check vs. Arctic Shift Proof

- **Live Reddit Activity Confirmed:** Checking both threads directly while logged into Reddit confirmed they are still actively receiving new comments:
  - `Itch.io Mega Thread (#10)` (`p0ik3q`): live comment `19syg3g560kyp` by `Prior-Bandicoot-8701` (posted ~3 hours prior).
  - `Exiled Giveaways Mega Thread (#2)` (`p0ijjx`): live comment `19ss0f9j2bw1x` by `MeguminShiro` (posted ~4 days prior).
  - `r/FreeGameFindings/new`: recent submissions confirmed (~1 day prior).
- **Direct Arctic Shift Lookup Proof:** Querying Arctic Shift's `/api/comments/ids` directly for `19syg3g560kyp,19ss0f9j2bw1x` returned `{"data":[]}` (not present at all). At the same time, querying `/api/comments/search` by author showed Arctic Shift *did* ingest comments by the exact same users on newer posts—including `Prior-Bandicoot-8701` on a newer post (`t3_1y1p7xg`) roughly 30 minutes earlier, and `MeguminShiro` on newer `r/FreeGameFindings` posts up to November 19, 2026.
- **Root Cause Confirmed Upstream ([`ArthurHeitmann/arctic_shift#53`](https://github.com/ArthurHeitmann/arctic_shift/issues/53) & [`#84`](https://github.com/ArthurHeitmann/arctic_shift/issues/84)):** Checking the Arctic Shift GitHub repository revealed why both megathreads froze on the exact date **October 21, 2026**:
  - Reddit completed its rollout replacing sequential (monotonic) comment IDs with non-monotonic 13-character IDs on **October 21, 2026** ([`#53`](https://github.com/ArthurHeitmann/arctic_shift/issues/53): *"Update: As of today all comments have the new ids"*).
  - Because Arctic Shift can no longer enumerate global comment IDs sequentially, it switched to a slower post-based comment ingestion workaround ([`#84`](https://github.com/ArthurHeitmann/arctic_shift/issues/84): *"Posts should be fine. Comments currently have a 1 - 2 day delay"*; [`#53`](https://github.com/ArthurHeitmann/arctic_shift/issues/53): 90–95% completeness). As a structural result, multi-year 2021 megathreads (`p0ik3q`, `p0ijjx`) are no longer crawled for new comments.
  - Additionally, [`#76`](https://github.com/ArthurHeitmann/arctic_shift/issues/76) notes Reddit plans to end remaining public Data API access in **March 2027** in favor of Devvit.

## 2. Alternative Paths Evaluated & Ruled Out

- **Personal Authenticated Reddit RSS Token (`?feed=<token>&user=<user>`):** Tested against both `p0ik3q/.rss` and `new.rss` (`404 Not Found` from `rss.reddit.com`) as well as `p0ik3q/.json` (`403 Forbidden` Reddit WAF block page). Confirms Reddit's global RSS shutdown ([TechCrunch, September 30, 2026](https://techcrunch.com/2026/09/30/reddit-is-killing-rss-feeds-ending-public-api-access-because-of-ai-bots/)) also broke personal token-authenticated feeds.
- **Direct Itch.io Native RSS Feeds:** Tested `https://itch.io/feed/sales.xml` (`200 OK` with an empty channel / 0 items) and `https://itch.io/games/store/on-sale.xml` (`429 Too Many Requests`). Not a viable drop-in.
- **Third-Party Giveaway Aggregators (e.g., GamerPower API):** Ruled out—the goal is specifically to follow the `r/FreeGameFindings` Reddit community threads and comments, not external giveaway aggregators.
- **Paid / Freemium Managed Reddit APIs (e.g., Apify, FetchLayer):** Ruled out—not interested in paid or freemium third-party proxy services.
- **`r/FreeGameFindings` Community Wiki & Official Discord:** The wiki (`r/FreeGameFindings/wiki/rssfeed`) was last revised 4 years ago. On the official `r/FreeGameFindings` Discord (November 19, 2026), moderator **Saulios** confirmed both `@FGF Itch.io Alerts` and `@FGoS Alerts` are currently down due to Reddit globally killing RSS support (with only `free-game-findings-feed` still working) while the mods look for an alternative.
- **Official Reddit API Pre-Approval (OAuth):** Ruled out for now—unlikely to be approved for a personal hobby RSS scraper, or subject to restrictive limits.
- **Filing an Upstream Bug Report to Arctic Shift:** Unnecessary—the October 21 megathread cutoff is already explained as a known structural consequence of Reddit removing monotonic comment IDs (`ArthurHeitmann/arctic_shift#53`, `#84`), not an unreported bug.
- **Disabling/Decoupling Megathreads to Keep Only `freegamefindings-new`:** Ruled out—all 3 feeds are required. External cron setup (`cron-job.org`, [`003-cron-limitations.md`](./003-cron-limitations.md)) remains deferred until all 3 feeds work reliably.
- **Local PC Scheduled Execution:** Ruled out—pipeline must remain cloud-hosted on GitHub Actions.

## Current State

- **Project Paused:** No code changes were applied to `scrape.py` or `feeds.json`, and active development is paused.
- Every free, cloud-hosted path to live comments on the 2021 megathreads (`p0ik3q`, `p0ijjx`) is currently blocked at the platform level (`Arctic Shift` post-Oct 21 structural cutoff, `PullPush` Cloudflare block + Oct 9 cutoff, native `.json` `403`, public/private `.rss` `404`, self-service OAuth `500`). Waiting to see what alternative `r/FreeGameFindings` moderators adopt (e.g., Devvit / Discord Relay or refreshed megathreads).
