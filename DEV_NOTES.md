# Development History & Technical Notes

This document logs the architectural decisions, pipeline issues, and API experiments for the Reddit RSS scraper. 

## 1. Feed Formatting & HTML Layout
* **Goal:** Create a clean, scannable RSS feed layout optimized for RSS readers (like CommaFeed) without bloated raw URLs.
* **Implementation:** 
  * Replicated the classic Reddit RSS structure: `submitted by /u/[author]`.
  * Added compact `[link] [comments]` hyperlink buttons.
  * Added conditional logic: If a post is text-only (the deal URL matches the comment URL), the script drops the duplicate `[link]` and only outputs `[comments]`.
  * Preserved the original Markdown `selftext` body by compiling it to HTML.

## 2. CI/CD Scheduling & Execution 
* **The Problem:** GitHub Actions native `schedule` (cron) is highly unreliable for frequent executions. Setting the cron to `17,47 * * * *` (every 30 minutes) resulted in an over 90% drop rate, executing only ~3 times in a 24-hour period instead of 48. GitHub prioritizes paid runners and heavily throttles free-tier scheduled workflows.
* **The Solution:** Disabled GitHub's native cron scheduler. Transitioned to using `workflow_dispatch` triggered via an external webhook from **cron-job.org**, authenticated with a GitHub Fine-Grained Personal Access Token (PAT). This forces execution exactly every 30 minutes bypassing GitHub's internal queue.

## 3. API Choice: Arctic Shift (Current Production)
* **Context:** Reddit severely restricted its official API in mid-2023, effectively killing free personal Developer App keys for scraping. We pivoted to third-party databases.
* **Method:** Queries `https://arctic-shift.photon-reddit.com/api` (a Pushshift alternative).
* **Strengths:** 
  * Bypasses Reddit's official API rate limits and IP blocks.
  * Capable of routing standard subreddit posts (`/posts/search`) and specific megathread replies (`/comments/search`) automatically using regex matching in `feeds.json`.
* **Weaknesses (The Megathread Timeout):** 
  * Fails on massive, multi-year megathreads (e.g., the 3-year-old Itch.io thread). The backend database struggles to sort thousands of comments in real-time, timing out and returning a `"data": null` payload.
* **Mitigation:** Built a fail-safe in `scrape.py` to catch empty payloads (`if not entries:`). The script will safely abort the `.xml` overwrite, preserving the previous feed state instead of corrupting it with an empty file during API congestion.

## 4. The Native Reddit JSON Experiment (`test.py`)
* **Goal:** Eliminate Arctic Shift's ingestion lag and megathread timeouts by pulling data directly from Reddit's native JSON feeds (e.g., `.../comments/p0ik3q.json`).
* **Method:** Utilized the `curl_cffi` library to perfectly spoof a Google Chrome 120 TLS fingerprint and bypass Reddit's bot-detection.
* **Result:** `403 Forbidden` (Failed). 
* **Root Cause:** While the browser fingerprinting was successful, GitHub Actions runs on Microsoft Azure cloud servers. Reddit's Web Application Firewall (WAF) aggressively blacklists known data center IP blocks. 
* **Conclusion:** Native JSON scraping is impossible on cloud CI/CD runners without official (and currently unavailable) developer authentication. The `test.py` script is retained in the repo as a diagnostic probe for future network testing.

## 5. Future Fallback Strategies
If Arctic Shift becomes permanently unreliable or goes offline, the remaining options are:
1. **Switch Third-Party Archivers:** Point the script's `API_BASE` to **PullPush** (another Pushshift instance) to test if their backend handles heavy megathread queries better.
2. **Local Execution (Residential IP):** Re-enable native `.json` scraping using `curl_cffi`, but move execution off GitHub Actions. Run the Python script locally on a Windows 11 machine via Task Scheduler. The residential IP inherently bypasses Reddit's data center WAF, and the script can `git push` the XML files up to GitHub Pages automatically.
