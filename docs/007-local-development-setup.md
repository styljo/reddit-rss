# Local Development & Environment Setup

**Date:** November 2026

## Goal

Establish an isolated local Python workspace at `C:\Github\reddit-rss` to inspect the codebase, verify syntax and dependencies, and test changes safely before pushing to `origin/main`.

## Prerequisites

- **Python 3.12** recommended (matches `.github/workflows/feed.yml`). **Python 3.9+** is required for built-in generic type annotations used in `scrape.py`.

## Setup Steps (Windows PowerShell)

### 1. Clone the Repository

```powershell
mkdir -Force C:\Github
cd C:\Github
git clone https://github.com/styljo/reddit-rss.git
cd reddit-rss
```

### 2. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is restricted, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first, then run `.\.venv\Scripts\Activate.ps1` again.

### 3. Install Dependencies

Matches `.github/workflows/feed.yml`:

```powershell
python -m pip install --upgrade pip
pip install curl_cffi markdown
```

### 4. Verify Syntax and Imports

```powershell
python -m py_compile scrape.py
python -c "import curl_cffi, markdown; print('Imports OK')"
```

### 5. Run the Scraper Locally

```powershell
python scrape.py
```

Generated RSS feeds (`public/<slug>.xml`) and the directory page (`public/index.html`) are written to `public/`.

## Notes

- Select `.venv\Scripts\python.exe` as the workspace interpreter in Antigravity IDE so terminal sessions and linters use the isolated environment.
- Both `.venv` and `public/` are listed in `.gitignore`; check `git status` before committing so local packages and generated feeds are never staged or pushed.
- Optional API diagnostic scripts live in `debug/` (`python debug/test_reddit_native.py` and `python debug/test_pullpush_api.py`) and are not part of the automated scraping pipeline.
