import os
import yaml
import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SCHOLAR_ID = os.environ.get("SCHOLAR_ID")
OUTPUT_FILE = "_data/publications.yml"

if not SERPAPI_KEY or not SCHOLAR_ID:
    raise ValueError("SERPAPI_KEY e SCHOLAR_ID precisam estar definidos.")

def fetch_publications() -> list[dict]:
    publications = []
    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": SERPAPI_KEY,
        "num": 100,
        "sort": "pubdate",
    }

    print("Buscando publicações via SerpApi (Google Scholar)...")
    r = requests.get("https://serpapi.com/search", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    for article in data.get("articles", []):
        # Venue: periódico ou conferência
        venue = article.get("publication") or ""
        # Remove o ano e volume que às vezes vêm junto na string de venue
        if "," in venue:
            venue = venue.split(",")[0].strip()

        cited_by = 0
        cited_info = article.get("cited_by") or {}
        if isinstance(cited_info, dict):
            cited_by = cited_info.get("value") or 0

        link = article.get("link") or ""

        entry = {
            "title": article.get("title") or "",
            "venue": venue,
            "year": int(article.get("year") or 0),
            "citations": int(cited_by),
            "url": link,
            "authors": [a.strip() for a in (article.get("authors") or "").split(",")],
        }
        publications.append(entry)
        print(f"  ✓ {entry['title'][:70]} ({entry['citations']} cit.)")

    publications.sort(key=lambda x: x["citations"], reverse=True)
    return publications

if __name__ == "__main__":
    pubs = fetch_publications()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(pubs, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"\nSalvas {len(pubs)} publicações em '{OUTPUT_FILE}'.")
