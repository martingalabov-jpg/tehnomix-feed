# Tehnomix - OpenAI Ads product feed

`tehnomix-openai-feed.csv` is built from https://www.tehnomix.bg/media/feed/google-new.csv
by `build_openai_feed.py` (OpenAI file-upload product spec, ads feed).

    python3 build_openai_feed.py <google-new.csv> <out.csv>

Refreshed daily at 04:00 UTC by `.github/workflows/refresh-feed.yml` (also runnable by hand from the Actions tab).
Cloudflare returns 403 to curl's default User-Agent; the workflow sends a browser User-Agent, which passes.
The run fails without publishing if the download is not the feed CSV or yields fewer than 3000 products.
Availability is set to in_stock for every row (the source has no stock column).
