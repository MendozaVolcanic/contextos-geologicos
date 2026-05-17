"""
analisis_actas_scar.py
======================

Análisis bibliométrico de actas y publicaciones SCAR (Scientific Committee on
Antarctic Research) para *proponer nuevos geositios* basados en intensidad de
investigación geocientífica.

Pipeline
--------
1. Indexa PDFs de actas SCAR (Open Science Conference, ATCM, SALE, GeoMAP).
   Carpeta de entrada: docs/biblioteca/scar/  (los PDFs los pone el usuario;
   el script no descarga porque suelen estar tras login institucional).

2. Extrae texto con `pdfplumber` (fallback `pypdf`).

3. NER de topónimos antárticos contra un gazetteer SCAR Composite Gazetteer
   (CGA) descargado de: https://data.aad.gov.au/aadc/gaz/scar/
   Salida: docs/biblioteca/scar_gazetteer.csv

4. Para cada PDF cuenta menciones por topónimo → DataFrame
   (sitio, lat, lon, pubs, primera_pub, ultima_pub, autores_unicos).

5. Cruza con polígonos de contextos SCAR (app/data/antartica_frameworks.geojson)
   para asignar el `framework` predominante de cada sitio.

6. Cruza con ASPAs + geositios ya catalogados (app/data/antartica_geositios.geojson)
   para marcar cuáles son "nuevos" candidatos.

7. Ranking: sitios con >N publicaciones, no catalogados, diversos en framework
   (representatividad) → propuestos como candidatos a geositios SCAR.

Salida
------
- app/data/antartica_geositios_propuestos.geojson  (capa nueva del visor)
- docs/notas/propuestas_geositios_scar.md          (justificación por sitio)
- app/data/scar_pubs_por_sitio.csv                 (datos crudos para reproducir)

Uso
---
    pip install pdfplumber pypdf pandas geopandas spacy
    python -m spacy download es_core_news_sm  # opcional (NER castellano)
    python scripts/analisis_actas_scar.py [--pdfs-dir docs/biblioteca/scar]
                                          [--min-pubs 5]
                                          [--top-n 20]

Notas
-----
- El gazetteer SCAR CGA es CC-BY y contiene ~38.000 topónimos antárticos. Es
  preferible a usar spaCy NER (que no conoce topónimos antárticos).
- Para análisis de coautoría futura: integrar CrossRef API y OpenAlex en una
  segunda iteración (ver TODO).
"""

from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "app" / "data"
DOCS_BIB = ROOT / "docs" / "biblioteca" / "scar"
GAZETTEER = ROOT / "docs" / "biblioteca" / "scar_gazetteer.csv"
NOTES_OUT = ROOT / "docs" / "notas" / "propuestas_geositios_scar.md"

# El portal SCAR Composite Gazetteer del AADC (data.aad.gov.au/aadc/gaz/scar/) es
# una app ColdFusion: no expone un endpoint de bulk-download estable, hay que
# usar el botón "Download as CSV" del search.cfm (verificado mayo 2026).
# Alternativa práctica: el gazetteer viene empaquetado en Quantarctica 3.x bajo:
#   Quantarctica3/Basemap/Miscellaneous/SCAR_PlaceNames/
# como shapefile + CSV de respaldo.
#
# Pasos para reproducir el CSV:
#   1) https://data.aad.gov.au/aadc/gaz/scar/search.cfm
#   2) Sin filtros (deja "All" en country/feature_type) → Search
#   3) En la página de resultados, click "Download as → CSV"
#   4) Guardar en docs/biblioteca/scar_gazetteer.csv (~39.187 nombres, ~5 MB)
GAZETTEER_PORTAL = "https://data.aad.gov.au/aadc/gaz/scar/search.cfm"
GAZETTEER_URL = GAZETTEER_PORTAL  # informativo solamente


def load_gazetteer(path: Path) -> list[dict]:
    """Lee el CGA (Composite Gazetteer of Antarctica) en formato CSV.

    Columnas reales del WFS aadc:SCAR_CGA_PLACE_NAMES_SIMPLIFIED:
      FID, place_name_mapping, place_name_gazetteer, gaz_id, altitude,
      feature_type_name, narrative, gazetteer, latitude, longitude,
      geometry, scar_common_id, country_name, country_id
    """
    if not path.exists():
        print(f"[WARN] No existe {path}. Bajar con:\n"
              "  curl -L -o docs/biblioteca/scar_gazetteer.csv "
              "'https://data.aad.gov.au/geoserver/aadc/ows?service=WFS&version=1.0.0"
              "&request=GetFeature&typeName=aadc:SCAR_CGA_PLACE_NAMES_SIMPLIFIED"
              "&outputFormat=csv'", file=sys.stderr)
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                name = (r.get("place_name_mapping") or r.get("place_name_gazetteer") or "").strip()
                lat_s = r.get("latitude") or ""
                lon_s = r.get("longitude") or ""
                if not name or not lat_s or not lon_s:
                    continue
                rows.append({
                    "name": name,
                    "lat": float(lat_s),
                    "lon": float(lon_s),
                    "type": (r.get("feature_type_name") or "").strip(),
                })
            except (KeyError, ValueError, TypeError):
                continue
    # Filtra topónimos con >=5 caracteres para evitar matches espurios (e.g. "Foch")
    rows = [r for r in rows if len(r["name"]) >= 5]
    # Dedupe por nombre (varias entradas pueden compartir nombre)
    seen = {}
    for r in rows:
        if r["name"] not in seen:
            seen[r["name"]] = r
    rows = list(seen.values())
    print(f"[INFO] Gazetteer: {len(rows)} topónimos únicos cargados")
    return rows


def extract_text(pdf_path: Path) -> str:
    """Extrae texto con pdfplumber; fallback pypdf."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except ImportError:
        pass
    except Exception as e:
        print(f"[WARN] pdfplumber falló en {pdf_path.name}: {e}", file=sys.stderr)
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception as e:
        print(f"[ERROR] No se pudo extraer {pdf_path.name}: {e}", file=sys.stderr)
        return ""


_KP_CACHE: dict[int, object] = {}


def build_keyword_processor(gazetteer: list[dict]):
    """Construye un KeywordProcessor (Aho-Corasick) UNA SOLA VEZ y lo cachea.

    Es O(N) en el tamaño del texto independiente del número de keywords,
    vs. O(N*K) que sería compilar regex por keyword. Práctico para 20K topónimos.
    """
    key = len(gazetteer)
    if key in _KP_CACHE:
        return _KP_CACHE[key]
    from flashtext import KeywordProcessor
    kp = KeywordProcessor(case_sensitive=False)
    for entry in gazetteer:
        name = entry["name"]
        if len(name) < 5:
            continue
        # flashtext respeta word-boundaries por defecto
        kp.add_keyword(name)
    _KP_CACHE[key] = kp
    return kp


def count_mentions(text: str, gazetteer: list[dict]) -> dict[str, int]:
    """Devuelve {topónimo: nº de menciones en el texto} usando Aho-Corasick."""
    kp = build_keyword_processor(gazetteer)
    counts: dict[str, int] = {}
    for hit in kp.extract_keywords(text):
        counts[hit] = counts.get(hit, 0) + 1
    return counts


def aggregate(pdfs_dir: Path, gazetteer: list[dict]) -> dict[str, dict]:
    """Recorre todos los PDFs y .txt y agrega por sitio."""
    by_site: dict[str, dict] = defaultdict(lambda: {"pubs": 0, "files": set()})
    docs = []
    if pdfs_dir.exists():
        docs = sorted(list(pdfs_dir.glob("**/*.pdf")) +
                      list(pdfs_dir.glob("**/*.txt")))
    if not docs:
        print(f"[WARN] No hay documentos en {pdfs_dir}.", file=sys.stderr)
        return {}
    print(f"[INFO] {len(docs)} documentos encontrados "
          f"({sum(1 for d in docs if d.suffix=='.pdf')} PDF, "
          f"{sum(1 for d in docs if d.suffix=='.txt')} TXT)", flush=True)
    for i, doc in enumerate(docs, 1):
        if i % 25 == 0 or i <= 5 or doc.suffix == ".pdf":
            print(f"[{i}/{len(docs)}] {doc.name}", flush=True)
        if doc.suffix == ".pdf":
            text = extract_text(doc)
        else:
            try:
                text = doc.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"  [WARN] no se pudo leer {doc.name}: {e}", flush=True)
                continue
        if not text:
            continue
        mentions = count_mentions(text, gazetteer)
        if doc.suffix == ".pdf" or i % 50 == 0:
            print(f"  {len(mentions)} topónimos distintos, {sum(mentions.values())} hits", flush=True)
        for name, n in mentions.items():
            by_site[name]["pubs"] += 1
            by_site[name]["hits"] = by_site[name].get("hits", 0) + n
            by_site[name]["files"].add(doc.stem)
    # Enriquecer con coordenadas
    coord = {g["name"]: (g["lat"], g["lon"], g["type"]) for g in gazetteer}
    for name, data in by_site.items():
        if name in coord:
            data["lat"], data["lon"], data["type"] = coord[name]
        data["files"] = sorted(data["files"])
    return dict(by_site)


# Tipos de feature (CGA) que tienen valor como geositio puntual.
# Excluimos: Continent, Station/Base, Pole, Sea, Ocean, Region (demasiado amplios),
# y Cape (suelen ser sitios genéricos sin valor geocientífico singular).
GEOSITE_RELEVANT_TYPES = {
    "Mountain", "Mountain Range", "Massif", "Nunatak", "Range",
    "Glacier", "Ice Shelf", "Ice Stream", "Ice Rise", "Ice Tongue",
    "Bay", "Inlet", "Fjord", "Sound",
    "Island", "Islands", "Archipelago", "Peninsula", "Hill", "Hills",
    "Cliff", "Cliffs", "Bluff", "Peak", "Crag", "Ridge", "Spur",
    "Volcano", "Valley", "Cwm", "Cirque", "Plateau", "Escarpment",
    "Aiguilles", "Tower", "Buttress", "Pinnacle", "Promontory",
    "Lake", "Pond", "Stream", "River",
    "Crater", "Caldera", "Cone",
    "Moraine", "Esker",
}

# Nombres genéricos que aparecen como ruido (regiones extensas, no sitios).
GENERIC_REGION_NAMES = {
    "Antarctica", "The Antarctic", "East Antarctica", "West Antarctica",
    "Antarctic Peninsula", "Antarctic", "South Pole",
    "Princess Elizabeth Land", "Dronning Maud Land", "Queen Maud Land",
    "Mac.Robertson Land", "Wilkes Land", "Victoria Land", "Marie Byrd Land",
    "Enderby Land", "Coats Land", "Palmer Land", "Graham Land",
    "Princess Astrid Coast", "Princess Ragnhild Coast",
    "Ellsworth Land", "George V Land", "Adelie Land", "Oates Land",
    "Ross Sea", "Weddell Sea", "Amundsen Sea", "Bellingshausen Sea",
    "Southern Ocean",
}


def filter_proposals(by_site: dict, catalogados: set[str], min_pubs: int,
                     top_n: int, only_geosite_types: bool = True) -> list[dict]:
    """Filtra sitios no catalogados con >=min_pubs y los rankea.

    Si only_geosite_types=True, descarta sitios cuyo feature_type CGA no
    corresponda a un geositio puntual razonable (Continent, Station, Sea, etc.).
    También descarta los nombres en GENERIC_REGION_NAMES.
    """
    candidates = []
    for name, d in by_site.items():
        if name in catalogados:
            continue
        if name in GENERIC_REGION_NAMES:
            continue
        if d["pubs"] < min_pubs:
            continue
        if "lat" not in d:
            continue
        ftype = (d.get("type") or "").strip()
        if only_geosite_types and ftype not in GEOSITE_RELEVANT_TYPES:
            continue
        candidates.append({"name": name, **d})
    # Ordenar por publicaciones, desempate por hits totales
    candidates.sort(key=lambda c: (-c["pubs"], -c.get("hits", 0)))
    return candidates[:top_n]


def load_catalogados() -> set[str]:
    """Nombres de sitios ya en antartica_geositios.geojson."""
    path = APP_DATA / "antartica_geositios.geojson"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    names = set()
    for f in data.get("features", []):
        n = f.get("properties", {}).get("nombre", "")
        # Quitamos comas y subdivisiones para matching difuso
        names.add(n.split(",")[0].strip())
    return names


def write_outputs(candidates: list[dict]) -> None:
    # GeoJSON propuestos
    features = []
    for c in candidates:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
            "properties": {
                "codigo": f"PROP-{c['name'][:8].upper().replace(' ', '')}",
                "nombre": c["name"],
                "tipo": "candidato",
                "interes": f"Alta densidad de publicaciones SCAR ({c['pubs']} actas, {c.get('hits', 0)} menciones)",
                "fuente": "Bibliometría actas SCAR (analisis_actas_scar.py)",
                "descripcion": f"Tipo gazetteer: {c.get('type','—')}. "
                               f"Aparece en: {', '.join(c['files'][:6])}"
                               + ("…" if len(c["files"]) > 6 else ""),
                "pubs_count": c["pubs"],
                "hits_count": c.get("hits", 0),
                "feature_type": c.get("type", ""),
            }
        })
    out_geo = APP_DATA / "antartica_geositios_propuestos.geojson"
    out_geo.write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {
            "fuente": "Bibliometría actas SCAR",
            "script": "scripts/analisis_actas_scar.py",
        },
        "features": features,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {out_geo} ({len(features)} candidatos)")

    # Notas markdown
    NOTES_OUT.parent.mkdir(parents=True, exist_ok=True)
    with NOTES_OUT.open("w", encoding="utf-8") as f:
        f.write("# Propuestas de geositios SCAR — bibliometría automática\n\n")
        f.write(f"Generado por `scripts/analisis_actas_scar.py`.\n\n")
        f.write("| Sitio | Publicaciones | Menciones | Tipo CGA | Coords |\n")
        f.write("|---|---:|---:|---|---|\n")
        for c in candidates:
            f.write(f"| {c['name']} | {c['pubs']} | {c.get('hits', 0)} | "
                    f"{c.get('type','—')} | {c.get('lat',0):.2f}, {c.get('lon',0):.2f} |\n")
    print(f"[OK] {NOTES_OUT}")

    # CSV crudo
    csv_out = APP_DATA / "scar_pubs_por_sitio.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["site", "pubs", "lat", "lon", "type", "files"])
        for c in candidates:
            w.writerow([c["name"], c["pubs"], c.get("lat"), c.get("lon"),
                        c.get("type", ""), "|".join(c["files"])])
    print(f"[OK] {csv_out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdfs-dir", type=Path, default=DOCS_BIB)
    ap.add_argument("--min-pubs", type=int, default=3,
                    help="Mínimo de publicaciones para considerar un sitio")
    ap.add_argument("--top-n", type=int, default=20,
                    help="Número máximo de candidatos a proponer")
    args = ap.parse_args()

    gazetteer = load_gazetteer(GAZETTEER)
    if not gazetteer:
        return 1
    by_site = aggregate(args.pdfs_dir, gazetteer)
    if not by_site:
        return 1
    catalogados = load_catalogados()
    print(f"[INFO] Ya catalogados: {len(catalogados)}")
    candidates = filter_proposals(by_site, catalogados, args.min_pubs, args.top_n)
    print(f"[INFO] Candidatos: {len(candidates)}")
    write_outputs(candidates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
