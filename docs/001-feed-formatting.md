# Feed Formatting & HTML Layout
**Date:** November 2026

## Goal
Create a clean, scannable RSS feed layout optimized for RSS readers (like CommaFeed) without bloated raw URLs.

## Implementation
* **Layout Structure:** Replicated the classic Reddit RSS presentation using the format: `submitted by /u/[author]`.
* **Navigation Links:** Added compact `[link] [comments]` hyperlink buttons directly under the author line.
* **Conditional Logic:** If a post is text-only (meaning the deal URL exactly matches the Reddit comments URL), the script drops the duplicate `[link]` button and only outputs `[comments]`.
* **Body Rendering:** Preserved the original Markdown `selftext` body by utilizing the Python `markdown` library to compile it into clean HTML for RSS clients.
