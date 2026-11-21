# reddit-rss

> [!WARNING]
> **Project Paused (November 2026):** Development is paused because every free, cloud-hosted path to live comments on the two long-running 2021 megathreads (`itchio-megathread` and `exiled-giveaways-megathread`) is currently blocked at the platform level (Reddit killed native `.rss`, blocks `.json` with `403`, returns `500` on self-service OAuth `prefs/apps`, and removed monotonic comment IDs on October 21, 2026, stopping Arctic Shift from crawling those 2021 threads). `freegamefindings-new.xml` still updates via Arctic Shift. See [`docs/010-megathread-audit-and-options-ruled-out.md`](./docs/010-megathread-audit-and-options-ruled-out.md) for full details.

Automated RSS 2.0 feed generator for Reddit subreddits and megathread comments, built with Python, the Arctic Shift API, GitHub Actions, and GitHub Pages.

## Active Feeds

Subscribe to these URLs in your RSS reader (e.g., CommaFeed, FreshRSS, Miniflux):

- **r/FreeGameFindings (New):** `https://styljo.github.io/reddit-rss/freegamefindings-new.xml`
- **Itch.io Mega Thread (#10):** `https://styljo.github.io/reddit-rss/itchio-megathread.xml` *(stale since Oct 21, 2026)*
- **Exiled Giveaways Mega Thread (#2):** `https://styljo.github.io/reddit-rss/exiled-giveaways-megathread.xml` *(stale since Oct 21, 2026)*

A directory of active feeds is hosted at `https://styljo.github.io/reddit-rss/`.

---

## How It Works

Because Reddit blocks datacenter IP ranges (such as GitHub Actions runners) and restricts unauthenticated scraping, this pipeline queries the [Arctic Shift API](https://arctic-shift.photon-reddit.com) instead of `reddit.com` directly.

```text
feeds.json ──► scrape.py (Arctic Shift API) ──► public/*.xml ──► GitHub Pages ──► RSS Reader
```

1. **Scheduled Execution:** `.github/workflows/feed.yml` runs every 30 minutes via cron, on pushes to `main` touching `feeds.json`, `scrape.py`, or `feed.yml`, or via manual `workflow_dispatch`.
2. **Data Retrieval (`scrape.py`):**
   - Reads target URLs from `feeds.json`.
   - Automatically detects **subreddits** (`/r/<name>`) vs. **comment threads** (`/comments/<id>`).
   - Queries Arctic Shift for the latest **100** posts (`/api/posts/search`) or comments (`/api/comments/search` using the `t3_` link prefix).
   - Bounds comment queries to the last **30 days** (`after` epoch parameter) to reduce `HTTP 422` database timeouts on large megathreads, with an unbounded fallback if a thread returns 0 comments in that window.
   - Retries failed requests up to 3 times with incremental backoff (40s timeout per attempt, 3s delay between feeds).
3. **Parsing & XML Generation:**
   - Strips stickied posts/comments, drops `[deleted]` / `[removed]` comments, and omits `[deleted]` / `[removed]` `selftext` on posts.
   - Converts Reddit Markdown and bare URLs in text posts and comments into real HTML (`<a>` tags, tables, line breaks) so links are clickable in RSS readers and detectable by browser userscripts.
   - Uses the permanent Reddit permalink as `<guid>` so RSS readers deduplicate items across polls.
   - **All-or-Nothing Guard:** If any feed fails to fetch or parses 0 valid entries (`len(index_links) < len(FEEDS)`), the script raises an error and aborts the workflow so GitHub Pages does not overwrite existing live `.xml` files with a partial build.
4. **Deployment:** The workflow splits `build` and `deploy` into separate jobs so feature branches can run CI checks without tripping `github-pages` branch protection rules. Only runs on `main` deploy `public/`.

---

## Repository Structure

| File | Purpose |
| :--- | :--- |
| `feeds.json` | Configuration list defining each feed's output filename (`slug`), display `title`, and Reddit `url`. |
| `scrape.py` | Queries Arctic Shift, renders Markdown to HTML, and generates `public/<slug>.xml` and `public/index.html`. |
| `.github/workflows/feed.yml` | GitHub Actions workflow that validates Python syntax, runs `scrape.py`, and deploys `public/` to GitHub Pages. |
| `.github/workflows/keepalive.yml` | Monthly empty-commit workflow that prevents GitHub from disabling scheduled crons after 60 days of repository inactivity. |
| `debug/test_reddit_native.py` | Diagnostic probe for testing direct Reddit `.json` access with `curl_cffi` TLS impersonation (see [`docs/005-native-json-block.md`](./docs/005-native-json-block.md)). |
| `debug/test_pullpush_api.py` | Diagnostic probe for testing PullPush comment queries (see [`docs/006-pullpush-cloudflare-block.md`](./docs/006-pullpush-cloudflare-block.md)). |
| `docs/` | Chronological architecture notes, troubleshooting history, and local development setup. |

---

## Adding or Updating Feeds

1. Open `feeds.json` and click **Edit**.
2. Add or modify an entry:
   ```json
   {
     "slug": "my-new-feed",
     "title": "Display Title in RSS Reader",
     "url": "https://old.reddit.com/r/SubredditName/new/"
   }
   ```
   - **Subreddit feed:** Any URL containing `/r/<subreddit>`.
   - **Megathread / Comment feed:** Any URL containing `/comments/<thread_id>`.
3. Commit the change to `main`. GitHub Actions will immediately rebuild and publish `https://styljo.github.io/reddit-rss/<slug>.xml`.

---

## Local Testing

Requires **Python 3.9+** (**Python 3.12** recommended to match CI).

```bash
pip install curl_cffi markdown
python scrape.py
```

Generated XML files and `index.html` are written to the local `public/` directory (ignored by Git via `.gitignore`). For a full Windows PowerShell and virtual environment (`.venv`) setup guide, see [`docs/007-local-development-setup.md`](./docs/007-local-development-setup.md).

---

## Operational Notes

- **60-Day Inactivity Rule:** Handled automatically by `.github/workflows/keepalive.yml`, which pushes an empty commit on the 1st of every month. Because `feed.yml` filters pushes by `paths`, the keepalive commit does not trigger an extra scrape.
- **Latency & Cron Reliability:** Arctic Shift ingestion lags live Reddit by a few minutes, and GitHub Actions free-tier cron schedules frequently drift or drop runs under load (see [`docs/003-cron-limitations.md`](./docs/003-cron-limitations.md)).
- **Known Megathread Limitation (Unresolved):** While `freegamefindings-new.xml` stays current, both long-running 2021 megathreads (`itchio-megathread.xml` and `exiled-giveaways-megathread.xml`) still hit intermittent Arctic Shift `HTTP 422` timeouts and have no comments indexed in Arctic Shift after **October 21, 2026** due to Reddit replacing monotonic comment IDs (see [`docs/008-post-revert-hardening-and-audit.md`](./docs/008-post-revert-hardening-and-audit.md) and [`docs/010-megathread-audit-and-options-ruled-out.md`](./docs/010-megathread-audit-and-options-ruled-out.md)).

---

## Architecture & Development Notes

Technical decisions, API limitations, and historical troubleshooting are documented in the [`docs/`](./docs) folder to maintain a strict, chronological architectural record. **These files are append-only once finalized.** To preserve history, do not edit completed files—log new changes by creating the next sequential file (e.g., `011-new-fix.md`) or updating the latest entry.

- [`001-feed-formatting.md`](./docs/001-feed-formatting.md) - Post/comment HTML layout, Markdown auto-linking, and deduplication
- [`002-github-actions-quirks.md`](./docs/002-github-actions-quirks.md) - Keepalive workflow and All-or-Nothing deployment guard
- [`003-cron-limitations.md`](./docs/003-cron-limitations.md) - GitHub Actions cron drop rates and planned external scheduling
- [`004-arctic-shift-api.md`](./docs/004-arctic-shift-api.md) - Arctic Shift API routing, retries, and initial megathread timeout mitigations
- [`005-native-json-block.md`](./docs/005-native-json-block.md) - Reddit WAF `403` blocks on native `.json` scraping
- [`006-pullpush-cloudflare-block.md`](./docs/006-pullpush-cloudflare-block.md) - PullPush Cloudflare JavaScript challenge blocks and revert to Arctic Shift
- [`007-local-development-setup.md`](./docs/007-local-development-setup.md) - Local Windows PowerShell workspace and virtual environment setup
- [`008-post-revert-hardening-and-audit.md`](./docs/008-post-revert-hardening-and-audit.md) - Post-revert CI/scraper hardening, ongoing Arctic Shift megathread timeouts & Oct 21 staleness cutoff, and local probe re-verification
- [`009-reddit-oauth-block.md`](./docs/009-reddit-oauth-block.md) - Reddit `prefs/apps` `HTTP 500` block when attempting to create a personal OAuth `script` app
- [`010-megathread-audit-and-options-ruled-out.md`](./docs/010-megathread-audit-and-options-ruled-out.md) - Live Reddit megathread check, Arctic Shift monotonic-ID root cause (`#53`/`#84`), FGF Discord RSS outage, and ruled-out alternatives

---

## License

Licensed under the [MIT License](./LICENSE).
