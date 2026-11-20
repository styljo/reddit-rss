# CI/CD Scheduling & Execution Limits
**Date:** November 2026

## The Problem
GitHub Actions native `schedule` (cron) is highly unreliable for frequent executions. Setting the cron to `17,47 * * * *` (every 30 minutes) results in an over 90% drop rate on the free tier. The pipeline executes only a handful of times in a 24-hour period instead of the expected 48.

## Current State
Currently relying on the native GitHub cron scheduler. As a result, RSS feed updates are heavily delayed by GitHub's internal queue throttling.

## Planned Mitigation
Disable GitHub's native cron scheduler. Transition to using `workflow_dispatch` triggered via an external webhook from **cron-job.org**, authenticated with a GitHub Fine-Grained Personal Access Token (PAT). This will force execution exactly every 30 minutes and bypass GitHub entirely.
