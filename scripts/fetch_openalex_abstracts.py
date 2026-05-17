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
    # Journals especializados polares (cobertura alta de papers antárticos)
    "antarctic_science":     "S939558408",    # Antarctic Science (Cambridge, 2775 works)
    "polar_record":          "S118957039",    # Polar Record (Cambridge, 8370 works)
    "polar_science":         "S14279969",     # Polar Science (Elsevier, 984 works)
    "advances_polar_sci":    "S4210190449",   # Advances in Polar Science (CNARC, 508 works)
    # Journals geocientíficos generales (filtramos por "Antarctic" en abstract)
    "geology_gsa":           "S56162041",     # Geology (GSA, 15423 works)
    "epsl":                  "S119230507",    # Earth and Planetary Science Letters (21700 works)
    "quaternary_sci_rev":    "S81424476",     # Quaternary Science Reviews (9829 works)
    "tectonics":             "S6410836",      # Tectonics (AGU, 5013 works)
    "j_geol_soc_london":     "S53451518",     # Journal of the Geological Society of London (5346 works)
    "gondwana_research":     "S158567263",    # Gondwana Research (5185 works)
}

# Para journals NO polares, exigimos también que el abstract mencione Antártica
NON_POLAR_JOURNALS = {
    "geology_gsa", "epsl", "quaternary_sci_rev",
    "tectonics", "j_geol_soc_london", "gondwana_research",
}
ANTARCTIC_KEYWORDS = (
    "antarctic", "antártic", "antartica", "antarctica",
    "south shetland", "ross sea", "weddell sea", "ross ice",
    "transantarctic", "scotia arc", "subglacial", "amundsen",
    "bellingshausen", "south pole", "ellsworth",
)

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


def is_antarctic_relevant(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in ANTARCTIC_KEYWORDS)


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
    # Para journals no polares filtramos en el server con search:antarctic
    is_non_polar = label in NON_POLAR_JOURNALS
    server_filter = (f"primary_location.source.id:{source_id},"
                     f"publication_year:{year_min}-{year_max}")
    if is_non_polar:
        # Filtro server-side por keyword "antarctic" en abstract
        server_filter += ",abstract.search:antarctic"

    params = {
        "filter": server_filter,
        "per-page": 200,
        "select": "id,doi,title,publication_year,abstract_inverted_index,cited_by_count",
        "cursor": "*",
    }
    written = 0
    seen = 0
    print(f"\n=== {label} ({source_id}) {year_min}-{year_max} "
          f"{'[+antarctic filter]' if is_non_polar else ''} ===")
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
            # Para journals no polares, segundo filtro cliente-side
            if is_non_polar and not is_antarctic_relevant(full):
                continue
            year = w.get("publication_year", "????")
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            cites = w.get("cited_by_count", 0)
            fname = safe_filename(f"openalex_{label}_{year}_{doi or w['id'].split('/')[-1]}.txt")
            out = PAPERS_DIR / fname
            if out.exists():
                continue
            # Metadata estructurada en líneas con prefijo, parseables por el pipeline
            out.write_text(
                f"# {title}\n"
                f"DOI: {doi}\n"
                f"Year: {year}\n"
                f"Source: {label}\n"
                f"CitedByCount: {cites}\n"
                f"\n"
                f"{abs_text}\n",
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
