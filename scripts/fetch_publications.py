import os
import yaml
import time
from scholarly import scholarly, ProxyGenerator

SCHOLAR_ID = os.environ.get("SCHOLAR_ID")
if not SCHOLAR_ID:
    raise ValueError("SCHOLAR_ID não definido. Configure o secret no GitHub.")

OUTPUT_FILE = "_data/publications.yml"


def fetch_publications(author_id: str) -> list[dict]:
    try:
        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg)
        print("Usando proxy rotativo.")
    except Exception:
        print("Proxy não disponível, tentando sem proxy.")

    print(f"Buscando autor com ID: {author_id}")
    author = scholarly.search_author_id(author_id)
    author = scholarly.fill(author, sections=["publications"])

    publications = []
    for pub in author.get("publications", []):
        try:
            filled = scholarly.fill(pub)
            bib = filled.get("bib", {})

            entry = {
                "title": bib.get("title", ""),
                "venue": bib.get("journal") or bib.get("booktitle") or bib.get("publisher") or "",
                "year": int(bib.get("pub_year", 0)),
                "citations": filled.get("num_citations", 0),
                "url": filled.get("pub_url") or "",
                "doi": "",
            }

            authors_raw = bib.get("author", "")
            entry["authors"] = [a.strip() for a in authors_raw.split(" and ")] if authors_raw else []

            publications.append(entry)
            time.sleep(2)

        except Exception as e:
            print(f"Erro ao processar publicação: {e}")
            continue

    publications.sort(key=lambda x: (x["year"], x["citations"]), reverse=True)
    return publications


def save_yaml(publications: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if "/" in path else None
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            publications,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
    print(f"Salvo {len(publications)} publicações em '{path}'.")


if __name__ == "__main__":
    pubs = fetch_publications(SCHOLAR_ID)
    save_yaml(pubs, OUTPUT_FILE)
