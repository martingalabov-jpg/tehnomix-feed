# Tehnomix - OpenAI Ads product feed

`tehnomix-openai-feed.csv` is built from https://www.tehnomix.bg/media/feed/google-new.csv
by `build_openai_feed.py` (OpenAI file-upload product spec, ads feed).

    python3 build_openai_feed.py <google-new.csv> <out.csv>

Refreshed daily by `refresh.ps1`, run from Windows Task Scheduler ("Tehnomix OpenAI feed refresh") on Martin's PC.
It cannot run in GitHub Actions: Cloudflare returns 403 to GitHub's datacenter IPs even with a browser User-Agent.
From the office connection a browser User-Agent passes (curl's default UA gets 403).
The run aborts without publishing if the download is not the feed CSV or yields fewer than 3000 products.
Log: `refresh.log` next to the script (not committed).
Availability is set to in_stock for every row (the source has no stock column).
