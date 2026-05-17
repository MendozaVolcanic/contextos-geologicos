"""
fetch_openalex_abstracts.py
===========================

Descarga abstracts de papers Antárticos relevantes desde OpenAlex y los guarda
como .txt en docs/biblioteca/scar/papers/ para alimentar el pipeline
bibliométrico (analisis_actas_scar.py).

Por qué abstracts y no full text
--------------------------------
- OpenAlex provee `abstract_inverted_index` para ~80% de los papers (libre,
  sin auth, sin rate limit estricto).
- Los abstracts antárticos son densos en topónimos (las introducciones suelen
  decir "X site in Y region at Z °S, Y °E").
- Full text requeriría Crossref TDM, ScienceDirect API, Springer SciGraph, etc.
  con autenticación institucional.

Fuentes
-------
- **Antarctic Science** (Cambridge), source ID S939558408 — 464 papers 2018-2026.
- **Polar Science** (Elsevier).
- **Polar Record** (Cambridge).
- **Advances in Polar Science** (CNARC).
- Filtros adicionales: títulos/abstracts con "geology" / "geological" /
  "geomorpholog" / "tectonic" / "stratigraphy" / "volcani".

Uso
---
    pip install requests
    python scripts/fetch_openalex_abstracts.py [--year-min 2015] [--max-papers 500]
"""

from __future__ import annotations
import argparse
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = ROOT / "docs" / "biblioteca" / "scar" / "papers"
PAPERS_DIR.mkdir(parents=True, exist_ok=True)

# Fuentes confirmadas (OpenAlex IDs verificados mayo 2026)
SOURCES = {
    "antarctic_science":     "S939558408",    # Antarctic Science (Cambridge, 2775 works)
    "polar_record":          "S118957039",    # Polar Record (Cambridge, 8370 works)
    "polar_science":         "S14279969",     # Polar Science (Elsevier, 984 works)
    "advances_polar_sci":    "S4210190449",   # Advances in Polar Science (CNARC, 508 works)
}

# Keywords geocientíficas — usamos como FILTRO suave para evitar inflación con
# papers de ecología/biología. Si el abstract NO contiene ninguna, se descarta.
GEO_KEYWORDS = (
    "geology", "geological", "geomorpholog", "tectonic", "stratigraph",
    "volcan", "metamorph", "intrusiv", "sediment", "glacial geo",
    "lithosphere", "basement", "pluton", "fossil", "paleo", "palaeo",
    "outcrop", "nunatak", "moraine", "stratovolcano", "rock",
)


def reconstruct_abstract(inv_idx: dict | None) -> str:
    """Reconstruye el abstract desde `abstract_inverted_index` de OpenAlex."""
    if not inv_idx:
        return ""
    positions = []
    for word, idxs in inv_idx.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def is_geo_relevant(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in GEO_KEYWORDS)


def safe_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
    return s[:120]


def fetch_one_source(source_id: str, year_min: int, year_max: int,
                     max_papers: int, label: str) -> int:
    try:
        import requests
    except ImportError:
        print("[ERROR] pip install requests", file=sys.stderr)
        return 0

    base = "https://api.openalex.org/works"
    params = {
        "filter": f"primary_location.source.id:{source_id},"
                  f"publication_year:{year_min}-{year_max}",
        "per-page": 200,
        "select": "id,doi,title,publication_year,abstract_inverted_index",
        "cursor": "*",
    }
    written = 0
    seen = 0
    print(f"\n=== {label} ({source_id}) {year_min}-{year_max} ===")
    while True:
        try:
            r = requests.get(base, params=params, timeout=60)
            r.raise_for_status()
        except Exception as e:
            print(f"[WARN] OpenAlex query falló: {e}", file=sys.stderr)
            break
        data = r.json()
        works = data.get("results", [])
        if not works:
            break
        for w in works:
            seen += 1
            title = w.get("title") or ""
            abs_text = reconstruct_abstract(w.get("abstract_inverted_index"))
            full = title + "\n\n" + abs_text
            if not is_geo_relevant(full):
                continue
            year = w.get("publication_year", "????")
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            fname = safe_filename(f"openalex_{label}_{year}_{doi or w['id'].split('/')[-1]}.txt")
            out = PAPERS_DIR / fname
            if out.exists():
                continue
            out.write_text(f"# {title}\nDOI: {doi}\nYear: {year}\nSource: {label}\n\n{abs_text}\n",
                           encoding="utf-8")
            written += 1
            if written >= max_papers:
                break
        if written >= max_papers:
            break
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        params["cursor"] = next_cursor
        time.sleep(0.3)  # ser amable con la API
    print(f"[OK] {label}: {written} abstracts (de {seen} papers vistos)")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--year-min", type=int, default=2015)
    ap.add_argument("--year-max", type=int, default=2026)
    ap.add_argument("--max-per-source", type=int, default=300)
    ap.add_argument("--sources", nargs="*", default=list(SOURCES.keys()),
                    choices=list(SOURCES.keys()))
    args = ap.parse_args()

    total = 0
    for label in args.sources:
        sid = SOURCES[label]
        total += fetch_one_source(sid, args.year_min, args.year_max,
                                  args.max_per_source, label)
    print(f"\n[DONE] Total abstracts geo-relevantes escritos: {total}")
    print(f"       Carpeta: {PAPERS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
