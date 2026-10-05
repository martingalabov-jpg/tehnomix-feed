# Tehnomix - OpenAI Ads product feed

`20261005-Tehnomix-OpenAI-ProductFeed.csv` is built from https://www.tehnomix.bg/media/feed/google-new.csv
by `build_openai_feed.py` (OpenAI file-upload product spec, ads feed).

    python3 build_openai_feed.py <google-new.csv> <out.csv>

The source is behind Cloudflare (403 for scripts); download it from a browser first.
Availability is set to in_stock for every row (the source has no stock column).
