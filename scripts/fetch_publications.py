import os
import yaml
import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SCHOLAR_ID  = os.environ.get("SCHOLAR_ID")
OUTPUT_FILE = "_data/publications.yml"

if not SERPAPI_KEY or not SCHOLAR_ID:
    raise ValueError("SERPAPI_KEY e SCHOLAR_ID precisam estar definidos.")

def serpapi(params: dict) -> dict:
    r = requests.get("https://serpapi.com/search",
                     params={"api_key": SERPAPI_KEY, **params},
                     timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_article_details(citation_id: str) -> dict:
    """Busca detalhes completos de um artigo pelo citation_id."""
    data = serpapi({
        "engine": "google_scholar_author",
        "view_op": "view_citation",
        "citation_for_view": citation_id,
    })
    return data.get("citation", {})

def fetch_publications() -> list[dict]:
    print("Buscando lista de publicações...")
    data = serpapi({
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "num": 100,
        "sort": "pubdate",
    })

    articles = data.get("articles", [])
    print(f"Encontrados {len(articles)} artigos. Buscando detalhes...\n")

    publications = []
    for article in articles:
        citation_id = article.get("citation_id", "")
        title = article.get("title", "")

        # Busca detalhes completos para venue e link corretos
        details = {}
        if citation_id:
            try:
                details = fetch_article_details(citation_id)
            except Exception as e:
                print(f"  ✗ Erro ao buscar detalhes de '{title[:50]}': {e}")

        # Venue: detalhes têm o nome completo; fallback para o resumido
        venue = ""
        for field in ["journal", "conference", "book", "publisher"]:
            venue = details.get(field, "")
            if venue:
                break
        if not venue:
            venue = article.get("publication", "").split(",")[0].strip()

        # Link: preferir DOI/publisher nos detalhes; fallback para link do Scholar
        link = ""
        for field in ["doi", "publisher_url", "link"]:
            link = details.get(field, "")
            if link:
                break
        if not link:
            link = article.get("link", "")

        # Citações
        cited_by = 0
        cited_info = article.get("cited_by") or {}
        if isinstance(cited_info, dict):
            cited_by = int(cited_info.get("value") or 0)

        entry = {
            "title": title,
            "venue": venue,
            "year": int(article.get("year") or 0),
            "citations": cited_by,
            "url": link,
            "authors": [a.strip() for a in (article.get("authors") or "").split(",")],
        }
        publications.append(entry)
        print(f"  ✓ {title[:65]} ({entry['citations']} cit.)")

    publications.sort(key=lambda x: x["citations"], reverse=True)
    return publications

if __name__ == "__main__":
    pubs = fetch_publications()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(pubs, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"\nSalvas {len(pubs)} publicações em '{OUTPUT_FILE}'.")
