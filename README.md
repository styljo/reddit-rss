# reddit-rss

Automated RSS 2.0 feed generator for Reddit subreddits and megathread comments, built with Python, the Arctic Shift API, GitHub Actions, and GitHub Pages.

## Active Feeds

Subscribe to these URLs in your RSS reader (e.g., CommaFeed, FreshRSS, Miniflux):

* **r/FreeGameFindings (New):** `https://styljo.github.io/reddit-rss/freegamefindings-new.xml`
* **Itch.io Mega Thread (#10):** `https://styljo.github.io/reddit-rss/itchio-megathread.xml`
* **Exiled Giveaways Mega Thread (#2):** `https://styljo.github.io/reddit-rss/exiled-giveaways-megathread.xml`

A directory of active feeds is hosted at `https://styljo.github.io/reddit-rss/`.

---

## How It Works

Because Reddit blocks datacenter IP ranges (such as GitHub Actions runners) and restricts unauthenticated scraping, this pipeline queries the [Arctic Shift API](https://arctic-shift.photon-reddit.com) instead of `reddit.com` directly.

```text
feeds.json ──► scrape.py (Arctic Shift API) ──► public/*.xml ──► GitHub Pages ──► RSS Reader
```

1. **Scheduled Execution:** `.github/workflows/feed.yml` runs every 30 minutes via cron, on pushes to `main`, or via manual `workflow_dispatch`.
2. **Data Retrieval (`scrape.py`):**
   * Reads target URLs from `feeds.json`.
   * Automatically detects **subreddits** (`/r/<name>`) vs. **comment threads** (`/comments/<id>`).
   * Queries Arctic Shift for the latest **100** posts (`/api/posts/search`) or comments (`/api/comments/search` using the `t3_` link prefix).
   * Bounds comment queries to the last **30 days** (`after` epoch parameter) to prevent `HTTP 422` database timeouts on large megathreads, with an unbounded fallback if a thread had 0 comments in that window.
   * Retries failed requests up to 3 times with incremental backoff (40s timeout per attempt, 3s delay between feeds).
3. **Parsing & XML Generation:**
   * Strips stickied posts/comments and `[deleted]` / `[removed]` entries.
   * Converts Reddit Markdown and bare URLs in comments into real HTML (`<a>` tags, tables, line breaks) so links are clickable in RSS readers and detectable by browser userscripts.
   * Uses the permanent Reddit permalink as `<guid>` so RSS readers deduplicate items across polls.
   * **All-or-Nothing Guard:** If any feed fails to fetch (`len(index_links) < len(FEEDS)`), the script raises an error and aborts the workflow so GitHub Pages does not overwrite existing live `.xml` files with a partial build.
4. **Deployment:** The workflow splits `build` and `deploy` into separate jobs so feature branches can run CI checks without tripping `github-pages` branch protection rules. Only runs on `main` deploy `public/`.

---

## Repository Structure

| File | Purpose |
| :--- | :--- |
| `feeds.json` | Configuration list defining each feed's output filename (`slug`), display `title`, and Reddit `url`. |
| `scrape.py` | Queries Arctic Shift, renders Markdown to HTML, and generates `public/<slug>.xml` and `public/index.html`. |
| `.github/workflows/feed.yml` | GitHub Actions workflow that validates Python syntax, runs `scrape.py`, and deploys `public/` to GitHub Pages. |
| `.github/workflows/keepalive.yml` | Monthly empty-commit workflow that prevents GitHub from disabling scheduled crons after 60 days of repository inactivity. |

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
   * **Subreddit feed:** Any URL containing `/r/<subreddit>`.
   * **Megathread / Comment feed:** Any URL containing `/comments/<thread_id>`.
3. Commit the change to `main`. GitHub Actions will immediately rebuild and publish `https://styljo.github.io/reddit-rss/<slug>.xml`.

---

## Local Testing

```bash
pip install curl_cffi markdown
python scrape.py
```

Generated XML files and `index.html` are written to the local `public/` directory (ignored by Git via `.gitignore`).

---

## Operational Notes

* **60-Day Inactivity Rule:** Handled automatically by `.github/workflows/keepalive.yml`, which pushes an empty commit on the 1st of every month. Because `feed.yml` filters pushes by `paths`, the keepalive commit does not trigger an extra scrape.
* **Latency:** Arctic Shift ingestion lags live Reddit by a few minutes, and GitHub Actions cron schedules can drift by 5–20 minutes under load.
