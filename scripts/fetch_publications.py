import os
import yaml
import requests
import time

SCHOLAR_ID = os.environ.get("SCHOLAR_ID")
OUTPUT_FILE = "_data/publications.yml"

BASE_URL = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,externalIds,authors,citationCount,url"

def fetch_publications(author_id: str) -> list[dict]:
    print(f"Buscando publicações para autor: {author_id}")
    publications = []
    offset = 0
    limit = 100

    while True:
        url = f"{BASE_URL}/author/{author_id}/papers"
        params = {"fields": FIELDS, "limit": limit, "offset": offset}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        papers = data.get("data", [])
        if not papers:
            break

        for paper in papers:
            doi = (paper.get("externalIds") or {}).get("DOI", "")
            entry = {
                "title": paper.get("title", ""),
                "venue": paper.get("venue") or "",
                "year": paper.get("year") or 0,
                "citations": paper.get("citationCount") or 0,
                "url": f"https://doi.org/{doi}" if doi else (paper.get("url") or ""),
                "authors": [a["name"] for a in paper.get("authors", [])],
            }
            publications.append(entry)
            print(f"  ✓ {entry['title'][:70]}")

        if len(papers) < limit:
            break
        offset += limit
        time.sleep(1)

    publications.sort(key=lambda x: (x["year"], x["citations"]), reverse=True)
    return publications

def save_yaml(publications, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(publications, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"\nSalvas {len(publications)} publicações em '{path}'.")

if __name__ == "__main__":
    if not SCHOLAR_ID:
        raise ValueError("SCHOLAR_ID não definido.")
    pubs = fetch_publications(SCHOLAR_ID)
    save_yaml(pubs, OUTPUT_FILE)
