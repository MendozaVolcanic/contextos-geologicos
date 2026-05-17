"""
analisis_congresos_chile.py
===========================

Análogo a analisis_actas_scar.py pero para el contexto **chileno**.

Hipótesis: los sitios chilenos con más densidad de publicaciones en
Congresos Geológicos Chilenos + Andean Geology + literatura geológica
internacional (filtrada a Chile/Andes) son candidatos a:
  (a) reforzar geositios YA en el Inventario Nacional SERNAGEOMIN
      (validación cuantitativa)
  (b) proponer geositios NUEVOS al inventario
  (c) re-mapear/refinar los 22 contextos geológicos Mourgues

Pipeline:
  - Corpus local: docs/biblioteca/congresos/ (XIV Cong Geol Chileno 2015,
    Simposios I-IV Geoparques/Geopatrimonio, GGN18) = 551 PDFs
  - Corpus OpenAlex: docs/biblioteca/chile/papers/ = 865 abstracts
  - Gazetteer: GeoNames Chile (CL.txt, ~46K topónimos)
  - Filtros: feature class T/H + ciertas L; excluir sitios ya en
    geositios_inventario_nacional.geojson (49 sitios)

Salidas:
  - app/data/chile_geositios_propuestos.geojson (nuevos candidatos)
  - app/data/chile_pubs_por_sitio.csv (datos crudos)
  - docs/notas/chile_propuestas_geositios.md (tabla narrativa)

Uso:
    python scripts/analisis_congresos_chile.py [--min-pubs 5] [--top-n 60]
"""

from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "app" / "data"
DOCS_PDF = ROOT / "docs" / "biblioteca" / "congresos"
DOCS_TXT = ROOT / "docs" / "biblioteca" / "chile" / "papers"
GAZ_CL = ROOT / "docs" / "biblioteca" / "CL.txt"
GEOSITIOS_NAC = APP_DATA / "geositios_inventario_nacional.geojson"
NOTES_OUT = ROOT / "docs" / "notas" / "chile_propuestas_geositios.md"


# Feature codes ESTRICTOS — solo lo que tiene valor patrimonio geológico real.
# Excluimos islotes pequeños (ISLT), streams (STM), beaches genéricas (BCH).
GEONAMES_RELEVANT_CODES = {
    # T - mountain (alto valor geocientífico)
    "MT", "MTS", "PK", "PKS",                 # cerros, picos
    "VLC", "VLCS",                            # volcanes (KEY para Chile)
    "RDGE", "CAPE",                           # ridges, cabos
    "VAL", "VALS", "CNYN", "CNYNS",          # valles, cañones
    "CRTR",                                   # cráteres
    "CLF", "CLFS",                            # acantilados
    "GLCR",                                   # glaciares
    "DUNE",                                   # dunas
    "PEN", "PENS",                            # penínsulas
    "PLAT", "PLATS", "MESA", "BUTE",         # mesetas
    "ESCRP",                                  # escarpas
    "HLL", "HLLS",                            # colinas
    "RK", "RKS", "PLDR",                     # rocas notables
    "SDL",                                    # silla
    # H - hydrographic (geomorfo selectivo)
    "LK", "LKS", "LGN", "LGNS",              # lagos
    "BAY", "BAYS", "GULF", "STRT",           # bahías
    "FJD", "FJDS", "INLT",                   # fiordos
    "SPNG", "SPNS",                          # fuentes
    # L - localities (cordilleras, sierras)
    "CDOR", "AREA",
    # Islas grandes solamente (filtramos por nombre tipo "Isla Grande" o Tierra)
    "ISL",                                    # incluye Isla de Pascua, Chiloé, etc.
}

# Nombres genéricos a excluir + homónimos con ciudades/personas conocidas que
# inflan el ranking sin valor geocientífico.
GENERIC_NAMES = {
    # Macro-regiones
    "Chile", "Andes", "Andean", "Cordillera de los Andes",
    "Cordillera de la Costa", "Cordillera Principal",
    "Depresión Intermedia", "Valle Central",
    "Norte Grande", "Norte Chico", "Zona Sur", "Zona Central",
    "Patagonia", "Tierra del Fuego", "Magallanes",
    "Antártica Chilena", "Antártica",
    "Sudamérica", "South America", "Pacific Ocean", "Pacífico",
    "Atlantic Ocean", "Atlántico",
    # Homónimos con ciudades argentinas/uruguayas/etc. que aparecen como
    # topónimos en CL pero los papers se refieren a la otra entidad
    "Buenos Aires", "La Plata", "Vaca Muerta", "Mendoza", "Salta", "Jujuy",
    "Bariloche", "Ushuaia", "Rio Gallegos", "Río Gallegos",
    "Asunción", "Lima", "La Paz", "Quito", "Bogotá",
    # Palabras genéricas con homónimos confusos
    "Valdivia",       # ciudad — papers sobre el terremoto 1960 dominan
    "Concepción",     # ciudad
    "Antofagasta",    # ciudad/región
    "Coquimbo",       # ciudad/región
    "Iquique",        # ciudad
    "Talca",          # ciudad
    "Temuco",         # ciudad
    "Osorno",         # ciudad/volcán — ambiguo
    "Punta Arenas",   # ciudad
    "Santiago",       # ciudad
    "Valparaíso",     # ciudad/región
    # Nombres muy comunes que son apellidos o sustantivos genéricos
    "Martínez", "Rivera", "Vásquez", "Escobar", "Pizarro",
    "Grande", "Colorado", "Las Minas", "Cerro Colorado", "Cerro Negro",
    "Minas", "Estancia", "Caleta", "Portezuelo", "Centinela", "Esperanza",
    "Rivera", "El Alto", "La Cruz", "La Caldera", "La Laguna", "La Isla",
    "Los Pozos", "Punta Negra", "El Volcán", "San Pedro", "San Antonio",
    "San Luis", "La Gloria", "Los Colorados", "Farellones",  # éste sí es real pero domina con sus reuniones de homenaje
    "Infiernillo",
}


def load_geonames_cl(path: Path) -> list[dict]:
    """Carga GeoNames Chile CSV TSV.

    Formato: geonameid, name, asciiname, alternatenames, latitude, longitude,
              feature_class, feature_code, country, ...
    """
    if not path.exists():
        print(f"[ERROR] No existe {path}.\nBajar:\n"
              "  curl -L -o /tmp/CL.zip http://download.geonames.org/export/dump/CL.zip\n"
              "  unzip /tmp/CL.zip -d docs/biblioteca/",
              file=sys.stderr)
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            try:
                name = parts[1].strip()
                lat = float(parts[4])
                lon = float(parts[5])
                fc = parts[6]  # feature class
                code = parts[7]  # feature code
                if code not in GEONAMES_RELEVANT_CODES:
                    continue
                if len(name) < 5:
                    continue
                rows.append({"name": name, "lat": lat, "lon": lon,
                             "type": f"{fc}.{code}"})
            except (ValueError, IndexError):
                continue
    # Dedup
    seen = {}
    for r in rows:
        if r["name"] not in seen:
            seen[r["name"]] = r
    rows = list(seen.values())
    print(f"[INFO] GeoNames CL: {len(rows)} topónimos relevantes")
    return rows


def load_catalogados() -> set[str]:
    """Nombres de geositios ya en geositios_inventario_nacional.geojson."""
    if not GEOSITIOS_NAC.exists():
        return set()
    data = json.loads(GEOSITIOS_NAC.read_text(encoding="utf-8"))
    names = set()
    for f in data.get("features", []):
        n = (f.get("properties", {}).get("NOMBRE") or
             f.get("properties", {}).get("nombre", ""))
        if n:
            # Normalización para matching difuso
            names.add(n.strip().lower())
            names.add(n.split(",")[0].strip().lower())
    return names


def extract_text_pdf(p: Path) -> str:
    try:
        from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(p).pages)
    except Exception as e:
        print(f"[WARN] pypdf falló {p.name}: {e}", file=sys.stderr)
        try:
            import pdfplumber
            with pdfplumber.open(p) as pdf:
                return "\n".join((pg.extract_text() or "") for pg in pdf.pages)
        except Exception:
            return ""


def parse_txt_meta(text: str) -> dict:
    meta = {"year": None, "cites": 0, "source": "local"}
    head = text[:600]
    for line in head.splitlines():
        if line.startswith("Year:"):
            try: meta["year"] = int(line.split(":", 1)[1].strip())
            except ValueError: pass
        elif line.startswith("CitedByCount:"):
            try: meta["cites"] = int(line.split(":", 1)[1].strip())
            except ValueError: pass
        elif line.startswith("Source:"):
            meta["source"] = line.split(":", 1)[1].strip()
    return meta


def decade_bucket(year: int | None) -> str:
    if year is None: return "unknown"
    if year < 2010: return "pre-2010"
    if year < 2015: return "2010-2014"
    if year < 2020: return "2015-2019"
    return "2020-2026"


def build_kp(gazetteer: list[dict]):
    from flashtext import KeywordProcessor
    kp = KeywordProcessor(case_sensitive=False)
    for g in gazetteer:
        if len(g["name"]) >= 5:
            kp.add_keyword(g["name"])
    return kp


def aggregate(gazetteer: list[dict], skip_pdf: bool = False) -> dict[str, dict]:
    # NO trackeamos `files` set para Chile (1414 docs × 5K sitios = explosión).
    # Solo guardamos un sample de los primeros 6 nombres de archivo por sitio.
    by_site = defaultdict(lambda: {"pubs": 0, "hits": 0, "weighted_score": 0.0,
                                    "by_decade": defaultdict(int),
                                    "files_sample": []})
    kp = build_kp(gazetteer)
    gaz_types = {g["name"]: g["type"] for g in gazetteer}
    gaz_coords = {g["name"]: (g["lat"], g["lon"]) for g in gazetteer}

    # Filtros:
    #   - PDFs > 8 MB se saltan (Simposios completos cuelgan pypdf en Windows/OneDrive)
    #   - PDFs > 200 páginas se saltan (compilatorios)
    # Si querés incluirlos, descomprimir y procesar a mano.
    MAX_PDF_MB = 8
    docs = []
    skipped = []
    if not skip_pdf and DOCS_PDF.exists():
        for p in sorted(DOCS_PDF.glob("**/*.pdf")):
            size_mb = p.stat().st_size / (1024 * 1024)
            if size_mb > MAX_PDF_MB:
                skipped.append((p.name, size_mb))
            else:
                docs.append(p)
    elif skip_pdf:
        print("[INFO] --skip-pdf: solo procesando .txt", flush=True)
    if DOCS_TXT.exists():
        docs += sorted(DOCS_TXT.glob("**/*.txt"))
    if skipped:
        print(f"[INFO] {len(skipped)} PDFs saltados por tamano > {MAX_PDF_MB} MB:",
              flush=True)
        for n, s in skipped[:5]:
            safe_name = n.encode("ascii", "replace").decode("ascii")
            print(f"       - {safe_name} ({s:.0f} MB)", flush=True)
    print(f"[INFO] {len(docs)} documentos "
          f"({sum(1 for d in docs if d.suffix=='.pdf')} PDF, "
          f"{sum(1 for d in docs if d.suffix=='.txt')} TXT)", flush=True)

    for i, doc in enumerate(docs, 1):
        if i % 100 == 0 or i <= 5:
            safe_name = doc.name.encode("ascii", "replace").decode("ascii")
            print(f"[{i}/{len(docs)}] {safe_name}", flush=True)
        if doc.suffix == ".pdf":
            text = extract_text_pdf(doc)
            meta = {"year": None, "cites": 0, "source": "local_pdf"}
        else:
            try:
                text = doc.read_text(encoding="utf-8", errors="replace")
                meta = parse_txt_meta(text)
            except Exception:
                continue
        if not text:
            continue
        hits = kp.extract_keywords(text)
        if not hits:
            continue
        mentions: dict[str, int] = {}
        for h in hits:
            mentions[h] = mentions.get(h, 0) + 1
        weight = math.log(meta["cites"] + 1) if meta["cites"] > 0 else 1.0
        bucket = decade_bucket(meta["year"])
        for name, n in mentions.items():
            s = by_site[name]
            s["pubs"] += 1
            s["hits"] += n
            s["weighted_score"] += weight
            s["by_decade"][bucket] += 1
            if len(s["files_sample"]) < 6:
                s["files_sample"].append(doc.stem)

    # Enriquecer con coords/type
    for name, d in by_site.items():
        if name in gaz_coords:
            d["lat"], d["lon"] = gaz_coords[name]
            d["type"] = gaz_types[name]
        d["by_decade"] = dict(d["by_decade"])
        d["files"] = d.pop("files_sample")
    return dict(by_site)


def filter_props(by_site: dict, catalogados: set[str], min_pubs: int, top_n: int):
    out = []
    for name, d in by_site.items():
        if d["pubs"] < min_pubs:
            continue
        if "lat" not in d:
            continue
        # Excluir genéricos
        if name in GENERIC_NAMES:
            continue
        # Excluir catalogados (fuzzy by lowercased prefix)
        nl = name.lower()
        if nl in catalogados or any(nl.startswith(c[:max(8, len(c))]) for c in catalogados if len(c) >= 8):
            continue
        out.append({"name": name, **d})
    out.sort(key=lambda c: (-c.get("weighted_score", 0), -c["pubs"], -c.get("hits", 0)))
    return out[:top_n]


def write_outputs(candidates: list[dict]) -> None:
    # GeoJSON
    feats = []
    for c in candidates:
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
            "properties": {
                "codigo": f"PROP-CL-{c['name'][:8].upper().replace(' ', '')}",
                "nombre": c["name"],
                "tipo": "candidato-chile",
                "interes": f"{c['pubs']} pubs · {c.get('hits', 0)} menciones · "
                           f"WS={round(c.get('weighted_score',0),1)}",
                "fuente": "Bibliometría Congreso Geológico Chileno + Andean Geology + lit. internacional",
                "feature_type": c.get("type", ""),
                "pubs_count": c["pubs"],
                "hits_count": c.get("hits", 0),
                "weighted_score": round(c.get("weighted_score", 0), 2),
                "by_decade": c.get("by_decade", {}),
            },
        })
    out = APP_DATA / "chile_geositios_propuestos.geojson"
    out.write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {
            "fuente": "Bibliometría chilena (analisis_congresos_chile.py)",
            "corpus": "551 PDFs Congreso Geol Chileno + Simposios + 865 abstracts OpenAlex",
        },
        "features": feats,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {out} ({len(feats)} candidatos)")

    # Markdown
    NOTES_OUT.parent.mkdir(parents=True, exist_ok=True)
    with NOTES_OUT.open("w", encoding="utf-8") as f:
        f.write("# Propuestas de geositios CHILE — bibliometría automática\n\n")
        f.write(f"Generado por `scripts/analisis_congresos_chile.py`. "
                f"Excluye los 49 geositios ya en Inventario Nacional SERNAGEOMIN.\n\n")
        f.write("| Sitio | Pubs | Menciones | WS | Tipo GeoNames | Decade | Coords |\n")
        f.write("|---|---:|---:|---:|---|---|---|\n")
        for c in candidates:
            dec = c.get("by_decade", {})
            dec_str = " ".join(f"{k}:{v}" for k, v in sorted(dec.items()) if v > 0)
            f.write(f"| {c['name']} | {c['pubs']} | {c.get('hits', 0)} | "
                    f"{round(c.get('weighted_score',0),1)} | {c.get('type','—')} | "
                    f"{dec_str} | {c.get('lat',0):.2f}, {c.get('lon',0):.2f} |\n")
    print(f"[OK] {NOTES_OUT}")

    # CSV
    csv_out = APP_DATA / "chile_pubs_por_sitio.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["site", "pubs", "hits", "weighted_score",
                    "pre-2010", "2010-2014", "2015-2019", "2020-2026",
                    "lat", "lon", "feature_type", "files"])
        for c in candidates:
            dec = c.get("by_decade", {})
            w.writerow([c["name"], c["pubs"], c.get("hits", 0),
                        round(c.get("weighted_score", 0), 2),
                        dec.get("pre-2010", 0), dec.get("2010-2014", 0),
                        dec.get("2015-2019", 0), dec.get("2020-2026", 0),
                        c.get("lat"), c.get("lon"),
                        c.get("type", ""), "|".join(c["files"][:20])])
    print(f"[OK] {csv_out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-pubs", type=int, default=5)
    ap.add_argument("--top-n", type=int, default=60)
    ap.add_argument("--skip-pdf", action="store_true",
                    help="Solo procesar .txt OpenAlex (rápido, evita pypdf hangs)")
    args = ap.parse_args()
    gaz = load_geonames_cl(GAZ_CL)
    if not gaz:
        return 1
    by_site = aggregate(gaz, skip_pdf=args.skip_pdf)
    if not by_site:
        return 1
    cat = load_catalogados()
    print(f"[INFO] Ya catalogados: {len(cat)} nombres")
    cands = filter_props(by_site, cat, args.min_pubs, args.top_n)
    print(f"[INFO] Candidatos: {len(cands)}")
    write_outputs(cands)
    return 0


if __name__ == "__main__":
    sys.exit(main())
