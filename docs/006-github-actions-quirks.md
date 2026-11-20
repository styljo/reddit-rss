# GitHub Actions Pipeline Protections
**Date:** November 2026

## 1. The 60-Day Inactivity Rule
* **The Problem:** GitHub automatically disables scheduled Actions (crons) on repositories that have not had push activity in 60 days. Because an RSS scraper is meant to be set-and-forget, it is highly susceptible to being silently disabled.
* **The Solution:** Implemented `.github/workflows/keepalive.yml`. This workflow runs on the 1st of every month, configures a bot user, and pushes an empty commit (`chore: keepalive`) to the repository. This permanently resets the 60-day inactivity timer. 

## 2. All-or-Nothing Deployment Guard
* **The Problem:** The `feeds.json` array is processed sequentially. If the API is online for the first feed but crashes on the second, generating the GitHub Pages artifact in its current state would overwrite the live site, essentially deleting the second feed's XML file.
* **The Solution:** Added a strict length validation check (`if len(index_links) < len(FEEDS)`). If any feed fails to parse, the script intentionally raises a `RuntimeError` and crashes the job before the deployment step. This ensures GitHub Pages only hosts complete, fully successful builds.
