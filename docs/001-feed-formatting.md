# Feed Formatting & HTML Layout

**Date:** November 2026

## Goal

Create a clean, scannable RSS feed layout optimized for RSS readers (like CommaFeed) without bloated raw URLs.

## Implementation

- **Post Layout:** Replicated the classic Reddit RSS presentation using the format `submitted by /u/[author]` with compact `[link] [comments]` hyperlink buttons directly underneath.
- **Conditional Link Logic:** If a post is text-only (meaning the deal URL exactly matches the Reddit comments URL), the script drops the duplicate `[link]` button and only outputs `[comments]`.
- **Megathread Comment Layout:** Renders `<p><strong>/u/[author]</strong></p>` followed by the comment HTML body, and formats each item `<title>` as `[author]: <snippet>` truncated to 90 characters (`...`).
- **Markdown & Auto-Linking:** Renders post `selftext` and comment bodies with Python `markdown` (`tables` and `nl2br` extensions). A regex pre-pass wraps bare `http(s)://` URLs in `<...>` while leaving existing `[label](url)` and `<url>` links untouched so links stay clickable in RSS readers and detectable by userscripts.
- **Filtering & Deduplication:** Skips `stickied` posts/comments and `[deleted]` / `[removed]` content (omitting deleted `selftext` on posts and dropping deleted/removed comments). Uses the permanent Reddit permalink as `<guid isPermaLink="true">` so RSS readers deduplicate entries across polls.
- **Web Directory:** Automatically generates `public/index.html` as a lightweight frontend directory with clickable links to all active `.xml` feeds.
