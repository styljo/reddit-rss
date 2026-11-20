# CI/CD Scheduling & Execution Limits
**Date:** November 2026

## The Problem
GitHub Actions native `schedule` (cron) proved highly unreliable for frequent executions. Setting the cron to `17,47 * * * *` (every 30 minutes) resulted in an over 90% drop rate on the free tier. The pipeline executed only ~3 times in a 24-hour period instead of the expected 48.

## The Solution
Disabled GitHub's native cron scheduler by removing it from the workflow file. 

Transitioned to using `workflow_dispatch` triggered via an external webhook from **cron-job.org**. This webhook is authenticated using a GitHub Fine-Grained Personal Access Token (PAT) with Actions Read/Write permissions, forcing execution exactly every 30 minutes and bypassing GitHub's internal queue throttling.
