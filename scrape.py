import json
import os
import re
import time
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape
import markdown
from curl_cffi import requests

API_BASE = "https://arctic-shift.photon-reddit.com/api"

with open("feeds.json", "r", encoding="utf-8") as f:
    FEEDS = json.load(f)


def fetch_arctic_shift(url: str) -> tuple[str, list[dict]]:
    comment_match = re.search(r"/comments/([a-z0-9]+)", url, re.IGNORECASE)
    if comment_match:
        kind = "comments"
        endpoint = f"{API_BASE}/comments/search"
        params = {
            "link_id": f"t3_{comment_match.group(1)}",
            "limit": 100,
            "sort": "desc",
            "after": int(time.time()) - 30 * 86400,
        }
    else:
        sub_match = re.search(r"/r/([^/?#]+)", url, re.IGNORECASE)
        if not sub_match:
            raise ValueError(f"Could not parse subreddit or thread ID from URL: {url}")
        kind = "posts"
        endpoint = f"{API_BASE}/posts/search"
        params = {"subreddit": sub_match.group(1), "limit": 100, "sort": "desc"}

    last_exc = None
    for attempt in range(1, 4):
        try:
            resp = requests.get(endpoint, params=params, timeout=40)
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json().get("data", [])
            # If a quiet megathread had no comments in the last 30 days, retry once without 'after'
            if kind == "comments" and not data and "after" in params:
                params.pop("after")
                resp = requests.get(endpoint, params=params, timeout=40)
                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json().get("data", [])
            return kind, data
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                wait = attempt * 5
                print(f"Attempt {attempt} failed for {url} ({exc}), retrying in {wait}s...")
                time.sleep(wait)
    raise last_exc


def render_markdown(text: str) -> str:
    # Wrap bare URLs in <...> so Python-Markdown converts them to <a> tags,
    # while leaving existing [label](url) and <url> links untouched.
    pattern = re.compile(r"(\[[^\]]+\]\([^)]+\)|<https?://[^>]+>)|(https?://[^\s<>\)\]]+)")
    linked = pattern.sub(lambda m: m.group(1) if m.group(1) else f"<{m.group(2)}>", text)
    return markdown.markdown(linked, extensions=["tables", "nl2br"])


def parse_posts(items: list[dict]) -> list[dict]:
    entries = []
    for post in items:
        if post.get("stickied"):
            continue

        title = (post.get("title") or "").strip()
        permalink = post.get("permalink") or ""
        deal_url = post.get("url") or ""
        if not title or not permalink:
            continue

        author = post.get("author") or "[deleted]"
        comments_url = f"https://www.reddit.com{permalink}"
        if deal_url.startswith("/"):
            deal_url = f"https://www.reddit.com{deal_url}"

        created_utc = post.get("created_utc")
        dt = datetime.fromtimestamp(created_utc, tz=timezone.utc) if created_utc else datetime.now(timezone.utc)

        selftext = (post.get("selftext") or "").strip()
        body_html = render_markdown(selftext) if selftext and selftext not in ("[deleted]", "[removed]") else ""

        links = []
        if deal_url and deal_url.rstrip("/") != comments_url.rstrip("/"):
            links.append(f'<a href="{escape(deal_url)}">[link]</a>')
        links.append(f'<a href="{escape(comments_url)}">[comments]</a>')

        meta_html = f'<p>submitted by /u/{escape(author)}<br/>{" ".join(links)}</p>'

        entries.append({
            "title": title,
            "link": comments_url,
            "guid": comments_url,
            "dt": dt,
            "html": f"{meta_html}{body_html}",
        })
    return entries


def parse_comments(items: list[dict]) -> list[dict]:
    entries = []
    for comment in items:
        if comment.get("stickied"):
            continue

        author = comment.get("author") or "[deleted]"
        raw_body = comment.get("body") or ""
        body_text = " ".join(raw_body.split())
        permalink = comment.get("permalink") or ""
        if not body_text or body_text in ("[deleted]", "[removed]") or not permalink:
            continue

        full_permalink = f"https://www.reddit.com{permalink}"
        short_title = f"{author}: {body_text[:90]}{'...' if len(body_text) > 90 else ''}"
        created_utc = comment.get("created_utc")
        dt = datetime.fromtimestamp(created_utc, tz=timezone.utc) if created_utc else datetime.now(timezone.utc)

        entries.append({
            "title": short_title,
            "link": full_permalink,
            "guid": full_permalink,
            "dt": dt,
            "html": f"<p><strong>/u/{escape(author)}</strong></p>{render_markdown(raw_body)}",
        })
    return entries


os.makedirs("public", exist_ok=True)
index_links = []

for idx, feed in enumerate(FEEDS):
    if idx > 0:
        time.sleep(3)

    slug = feed["slug"]
    title = feed["title"]
    url = feed["url"]
    out_path = f"public/{slug}.xml"

    try:
        kind, raw_items = fetch_arctic_shift(url)
        entries = parse_comments(raw_items) if kind == "comments" else parse_posts(raw_items)

        if not entries:
            print(f"Warning: 0 entries parsed for {slug}, skipping overwrite.")
            continue

        newest_dt = max(e["dt"] for e in entries)
        items_xml = []
        for e in entries:
            items_xml.append(
                f"""    <item>
      <title>{escape(e["title"])}</title>
      <link>{escape(e["link"])}</link>
      <guid isPermaLink="true">{escape(e["guid"])}</guid>
      <pubDate>{format_datetime(e["dt"])}</pubDate>
      <description>{escape(e["html"])}</description>
    </item>"""
            )

        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape(title)}</title>
    <link>{escape(url)}</link>
    <description>Generated RSS feed for {escape(title)}</description>
    <lastBuildDate>{format_datetime(newest_dt)}</lastBuildDate>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rss)
        print(f"Wrote {len(entries)} items to {out_path}")
        index_links.append(f'<li><a href="{slug}.xml">{escape(title)}</a> (<code>{slug}.xml</code>)</li>')
    except Exception as exc:
        print(f"Error updating {slug}: {exc}")

if len(index_links) < len(FEEDS):
    raise RuntimeError(
        f"Only {len(index_links)}/{len(FEEDS)} feeds succeeded; aborting to preserve existing GitHub Pages deployment."
    )

with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(f"<!doctype html><html><body><h2>Active RSS Feeds</h2><ul>{''.join(index_links)}</ul></body></html>")
