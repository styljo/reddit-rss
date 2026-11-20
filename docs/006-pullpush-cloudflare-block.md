# PullPush API Experiment
**Date:** November 2026

## Goal
Attempted to swap Arctic Shift for PullPush (`api.pullpush.io`) to resolve API timeouts when querying the massive 3-year-old Itch.io megathread.

## Result
* **Status:** `403 Forbidden` (Failed).
* **Root Cause:** PullPush is protected by Cloudflare. Cloudflare flagged the GitHub Actions Microsoft Azure IP as a bot and returned a JavaScript challenge (`<title>Just a moment...</title>`). 
* **Conclusion:** Like Reddit's native JSON, PullPush cannot be used on cloud CI/CD runners due to data center IP blacklisting. Arctic Shift remains the only viable API for cloud execution, despite its megathread limitations.
