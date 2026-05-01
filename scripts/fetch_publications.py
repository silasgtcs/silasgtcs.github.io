import os
import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SCHOLAR_ID = os.environ.get("SCHOLAR_ID")

params = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": SERPAPI_KEY,
    "num": 100,
    "sort": "pubdate",
}

r = requests.get("https://serpapi.com/search", params=params, timeout=30)
print("Status:", r.status_code)
print("Chaves na resposta:", list(r.json().keys()))
print("Primeiros 2000 chars:", r.text[:2000])
