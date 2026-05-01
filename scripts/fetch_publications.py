import os
import yaml
import time
from scholarly import scholarly

SCHOLAR_ID = os.environ.get("SCHOLAR_ID")
if not SCHOLAR_ID:
    raise ValueError("SCHOLAR_ID não definido.")

OUTPUT_FILE = "_data/publications.yml"

print(f"Buscando autor com ID: {SCHOLAR_ID}")
author = scholarly.search_author_id(SCHOLAR_ID)
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
            "authors": [a.strip() for a in bib.get("author", "").split(" and ")] if bib.get("author") else [],
        }
        publications.append(entry)
        print(f"  ✓ {entry['title'][:60]}...")
        time.sleep(2)
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        continue

publications.sort(key=lambda x: (x["year"], x["citations"]), reverse=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    yaml.dump(publications, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print(f"\nSalvas {len(publications)} publicações em '{OUTPUT_FILE}'.")
