"""
fetch_openalex_chile.py
=======================

Descarga abstracts de papers relevantes para Chile/Andes desde OpenAlex.
Análogo a fetch_openalex_abstracts.py pero para el contexto chileno.

Fuentes (OpenAlex source IDs verificados mayo 2026)
----------------------------------------------------
- Andean Geology (SERNAGEOMIN/U. Chile, S78534000) — 866 works
- Geology (GSA, S56162041) — filtrado con "chile" OR "andes"
- EPSL (S119230507) — filtrado con "andes" OR "chil"
- Quaternary Science Reviews (S81424476) — filtrado
- Tectonics (S6410836) — filtrado
- Journal of South American Earth Sciences (búsqueda)
- Tectonophysics (búsqueda)

Salida: docs/biblioteca/chile/papers/openalex_<source>_<year>_<doi>.txt

Uso
---
    python scripts/fetch_openalex_chile.py [--year-min 2010] [--max-per-source 300]
"""

from __future__ import annotations
import argparse
import re
import sys
import time
from pathlib import Path

# Ver nota en analisis_actas_scar.py: el docstring que argparse imprime con
# --help trae "→", que cp1252 no puede representar.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = ROOT / "docs" / "biblioteca" / "chile" / "papers"
PAPERS_DIR.mkdir(parents=True, exist_ok=True)

# Fuentes chilenas — Andean Geology es el journal nacional
SOURCES = {
    "andean_geology":              "S78534000",     # Andean Geology (866 works)
    # Estos los filtramos server-side con "chile" OR "andes" o por país
    "geology_gsa":                 "S56162041",
    "epsl":                        "S119230507",
    "quaternary_sci_rev":          "S81424476",
    "tectonics":                   "S6410836",
}

# Andean Geology cubre toda la cadena andina (toda Sudamérica) → no necesita filtro extra.
# Los otros 4 son globales → exigimos "chile" o "andes" en abstract.
NON_NATIONAL_JOURNALS = {"geology_gsa", "epsl", "quaternary_sci_rev", "tectonics"}
CHILE_KEYWORDS = (
    "chile", "chilean", "andes", "andean", "patagonia", "atacama",
    "magallanes", "antofagasta", "coquimbo", "valparaiso", "araucania",
    "torres del paine", "ojos del salado", "villarrica", "puyehue",
    "easter island", "rapa nui", "altiplano",
)

GEO_KEYWORDS = (
    "geology", "geological", "geomorpholog", "tectonic", "stratigraph",
    "volcan", "metamorph", "intrusiv", "sediment", "glacial",
    "lithosphere", "basement", "pluton", "fossil", "paleo", "palaeo",
    "outcrop", "moraine", "stratovolcano", "ignimbrit", "batholit",
    "rock", "ore", "deposit", "mineral", "subduct", "ophiolit",
)


def reconstruct_abstract(inv_idx: dict | None) -> str:
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


def is_chile_relevant(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in CHILE_KEYWORDS)


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
    is_non_national = label in NON_NATIONAL_JOURNALS
    server_filter = (f"primary_location.source.id:{source_id},"
                     f"publication_year:{year_min}-{year_max}")
    if is_non_national:
        # OR via "search" no aplica con multi-token bien — preguntamos por
        # "andes" como ancla y filtramos en cliente con CHILE_KEYWORDS amplio
        server_filter += ",abstract.search:andes OR chile"

    params = {
        "filter": server_filter,
        "per-page": 200,
        "select": "id,doi,title,publication_year,abstract_inverted_index,cited_by_count",
        "cursor": "*",
    }
    written = 0
    seen = 0
    print(f"\n=== {label} ({source_id}) {year_min}-{year_max} "
          f"{'[+chile/andes filter]' if is_non_national else ''} ===")
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
            if is_non_national and not is_chile_relevant(full):
                continue
            year = w.get("publication_year", "????")
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            cites = w.get("cited_by_count", 0)
            fname = safe_filename(f"openalex_{label}_{year}_{doi or w['id'].split('/')[-1]}.txt")
            out = PAPERS_DIR / fname
            if out.exists():
                continue
            out.write_text(
                f"# {title}\nDOI: {doi}\nYear: {year}\nSource: {label}\n"
                f"CitedByCount: {cites}\n\n{abs_text}\n",
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
        time.sleep(0.3)
    print(f"[OK] {label}: {written} abstracts (de {seen} papers vistos)")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--year-min", type=int, default=2010)
    ap.add_argument("--year-max", type=int, default=2026)
    ap.add_argument("--max-per-source", type=int, default=400)
    ap.add_argument("--sources", nargs="*", default=list(SOURCES.keys()),
                    choices=list(SOURCES.keys()))
    args = ap.parse_args()

    total = 0
    for label in args.sources:
        sid = SOURCES[label]
        total += fetch_one_source(sid, args.year_min, args.year_max,
                                  args.max_per_source, label)
    print(f"\n[DONE] Total abstracts chilenos escritos: {total}")
    print(f"       Carpeta: {PAPERS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
