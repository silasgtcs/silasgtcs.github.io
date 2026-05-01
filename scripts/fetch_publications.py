import os
import yaml
import requests
import time

ORCID = os.environ.get("ORCID_ID", "")
AUTHOR_NAME = "Silas Garrido Teixeira"  # fallback caso ORCID não funcione
OUTPUT_FILE = "_data/publications.yml"
BASE_URL = "https://api.openalex.org"

def get_author_id() -> str:
    if ORCID:
        url = f"{BASE_URL}/authors/https://orcid.org/{ORCID}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()["id"]
    else:
        url = f"{BASE_URL}/authors"
        r = requests.get(url, params={"search": AUTHOR_NAME, "per_page": 1}, timeout=30)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            raise ValueError(f"Autor '{AUTHOR_NAME}' não encontrado no OpenAlex.")
        author_id = results[0]["id"]
        print(f"Autor encontrado: {results[0]['display_name']} ({author_id})")
        return author_id

def fetch_publications(author_id: str) -> list[dict]:
    publications = []
    cursor = "*"
    while cursor:
        params = {
            "filter": f"authorships.author.id:{author_id}",
            "fields": "title,publication_year,primary_location,cited_by_count,authorships,doi",
            "per_page": 100,
            "cursor": cursor,
        }
        r = requests.get(f"{BASE_URL}/works", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        for work in data.get("results", []):
            venue = ""
            loc = work.get("primary_location") or {}
            source = loc.get("source") or {}
            venue = source.get("display_name") or ""

            doi = work.get("doi") or ""
            if doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")

            authors = [
                a["author"]["display_name"]
                for a in work.get("authorships", [])
                if a.get("author")
            ]

            entry = {
                "title": work.get("title") or "",
                "venue": venue,
                "year": work.get("publication_year") or 0,
                "citations": work.get("cited_by_count") or 0,
                "url": f"https://doi.org/{doi}" if doi else "",
                "authors": authors,
            }
            publications.append(entry)
            print(f"  ✓ {entry['title'][:70]} ({entry['citations']} cit.)")

        cursor = data.get("meta", {}).get("next_cursor")
        time.sleep(0.5)

    publications.sort(key=lambda x: (x["citations"], x["year"]), reverse=True)
    return publications

if __name__ == "__main__":
    author_id = get_author_id()
    pubs = fetch_publications(author_id)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(pubs, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"\nSalvas {len(pubs)} publicações em '{OUTPUT_FILE}'.")
