# Tehnomix - OpenAI Ads product feed

`tehnomix-openai-feed.csv` is built from https://www.tehnomix.bg/media/feed/google-new.csv
by `build_openai_feed.py` (OpenAI file-upload product spec, ads feed).

    python3 build_openai_feed.py <google-new.csv> <out.csv>

Refreshed every 6 hours by the GitHub Actions workflow `.github/workflows/refresh-feed.yml` (cron 00:00, 06:00, 12:00 and 18:00 UTC; GitHub often starts scheduled runs late).
Cloudflare stopped blocking GitHub's runners on 2026-10-14; before that the refresh ran on Martin's PC. `refresh.ps1` is that old Task Scheduler version, kept as a fallback (its task is disabled; `git pull` before re-enabling).
The run aborts without publishing if the download is not the feed CSV, the source has fewer than 3000 products, or fewer than 1500 remain after filtering.
Only products over 50 EUR are published (sale price when lower than list price, else list price); change `MIN_PRICE` in `build_openai_feed.py` to move the threshold.
Availability is set to in_stock for every row (the source has no stock column).
