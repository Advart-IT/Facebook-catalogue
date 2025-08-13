import os
from pathlib import Path

# CSVs live in the project root (the "main folder")
ROOT_DIR = Path(__file__).resolve().parent.parent

# If you want to restrict to known brands, put slugs here (lowercase), e.g.:
# ALLOWED_BRANDS = {"beelittle", "brand2", "brand3", "brand4"}
ALLOWED_BRANDS = set()  # empty = auto-allow any *_facebook_catalog.csv present

# Public cache (Facebook will still revalidate via ETag/Last-Modified)
CACHE_SECONDS = 3600  # 1 hour

# Basic Auth credentials (set via env in production)
FEED_USER = os.getenv("FEED_USER", "meta")
FEED_PASS = os.getenv("FEED_PASS", "super-secret-123")
