# The Native Reddit JSON Experiment
**Date:** November 2026

## Goal
Attempted to eliminate Arctic Shift's ingestion lag and megathread timeouts by pulling data directly from Reddit's native JSON feeds (e.g., `.../comments/p0ik3q.json`).

## Method
Created a standalone `test.py` script utilizing the `curl_cffi` library to perfectly spoof a Google Chrome 120 TLS fingerprint, attempting to bypass Reddit's bot-detection.

## Result
* **Status:** `403 Forbidden` (Failed).
* **Root Cause:** While browser fingerprinting succeeded locally, GitHub Actions executes on Microsoft Azure cloud servers. Reddit's Web Application Firewall (WAF) aggressively blacklists known data center IP blocks. 
* **Conclusion:** Native JSON scraping is impossible on cloud CI/CD runners without official developer authentication. 
* **Next Steps:** The `test.py` script remains in the repository as a diagnostic probe. Direct JSON scraping remains a viable fallback only if execution is moved to a residential IP (e.g., a local Windows scheduled task pushing to GitHub).
