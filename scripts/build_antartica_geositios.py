"""
build_antartica_geositios.py
============================

Genera app/data/antartica_geositios.geojson combinando:
  1. ASPA (Antarctic Specially Protected Areas) — Antarctic Treaty Secretariat (ATS).
     Source: https://www.ats.aq/devAS/Ats/AtsMeetingMeasures?lang=e (KML/GeoJSON descargables).
  2. SCAR EG-GEOCON Geological Heritage Sites — Antarctic Geoconservation Framework.
     Source: https://scar.org/science/geo/geoconservation
     Lista publicada en SCAR ATCM XLIII (2021), Att. A. Por ahora se inyecta
     manualmente desde docs/notas/scar_geositios.md (curado a mano).
  3. IUGS heritage sites (si los hay en territorio antártico — al 2026 no hay
     IUGS heritage stones designadas en Antártica; mantenemos el slot por si
     entran a futuro vía propuestas SCAR).

Salida: GeoJSON FeatureCollection con propiedades:
    codigo, nombre, tipo, framework, interes, fuente, descripcion

Uso:
    python scripts/build_antartica_geositios.py [--seed-only]

--seed-only mantiene el dataset semilla curado a mano (no descarga nada).
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_OUT = ROOT / "app" / "data" / "antartica_geositios.geojson"
SEED_NOTES = ROOT / "docs" / "notas" / "scar_geositios_seed.md"

# Fuentes verificadas (mayo 2026)
# ----------------------------------------------------------------------------
# ASPAs / ASMAs: el portal ATS APA Database (https://www.ats.aq/devph/en/apa-database)
# es JavaScript-driven y no expone descargas en bulk. La ruta canónica es bajarlo
# desde el paquete Quantarctica (Norsk Polarinstitutt), que empaqueta las capas
# vigentes de ASPAs/ASMAs/HSMs como ESRI Shapefiles en:
#   Quantarctica3/Basemap/ProtectedAreas/
# Página de descarga: http://quantarctica.npolar.no/downloads
#
# Como el paquete completo pesa ~12 GB, lo razonable es:
#   (a) bajar el paquete una vez con el Norwegian Polar Institute Downloader
#       (https://quantarctica.npolar.no) y apuntar --quantarctica al folder, o
#   (b) si solo nos interesan las ASPAs, extraer el sub-folder ProtectedAreas/
#       con `rsync --include='**/ProtectedAreas/***' --exclude='*'` desde el
#       rsync server público (quantarctica.npolar.no::quantarctica).
#
# SCAR EG-GEOCON Geological Heritage Sites: la lista oficial vive en SCAR ATCM XLIII
# Attachment A (PDF). Texto extraído manualmente a docs/notas/scar_geositios_seed.md
# y semilla puesta en app/data/antartica_geositios.geojson.
QUANTARCTICA_DOWNLOAD_PAGE = "http://quantarctica.npolar.no/downloads"
QUANTARCTICA_RSYNC = "rsync://quantarctica.npolar.no/quantarctica"
SCAR_EGGEOCON_LIST = "https://scar.org/science/geo/geoconservation"


def load_seed() -> dict:
    """Devuelve la FeatureCollection actual del seed manual."""
    if not DATA_OUT.exists():
        print(f"[WARN] No existe {DATA_OUT}, devolviendo FeatureCollection vacía", file=sys.stderr)
        return {"type": "FeatureCollection", "features": []}
    return json.loads(DATA_OUT.read_text(encoding="utf-8"))


def fetch_aspas(quantarctica_dir: Path | None) -> list[dict]:
    """Lee las ASPAs/ASMAs desde un Quantarctica desempaquetado localmente.

    Espera que `quantarctica_dir` apunte al folder que contiene
    `Basemap/ProtectedAreas/aspa_polygon.shp` (o similar). Si es None o no
    existe, devuelve [] y deja un INFO.
    """
    if quantarctica_dir is None or not quantarctica_dir.exists():
        print("[INFO] fetch_aspas: pasá --quantarctica /ruta/a/Quantarctica3 para "
              "integrar el shapefile ASPA. Por ahora solo seed manual.")
        return []
    try:
        import geopandas as gpd
    except ImportError:
        print("[ERROR] Falta geopandas. pip install geopandas pyogrio", file=sys.stderr)
        return []
    # El nombre exacto cambia entre versiones — buscamos genérico.
    # Preferimos polygons (más rico que points) y ASPA antes que ASMA.
    candidates = (
        list(quantarctica_dir.glob("**/ASPAs_polygons.shp")) or
        list(quantarctica_dir.glob("**/ASPAs_points.shp")) or
        list(quantarctica_dir.glob("**/ProtectedAreas/*polygon*.shp")) or
        list(quantarctica_dir.glob("**/ASPA*.shp"))
    )
    if not candidates:
        print(f"[WARN] No encontré shapefile ASPA dentro de {quantarctica_dir}",
              file=sys.stderr)
        return []
    shp = candidates[0]
    print(f"[INFO] Leyendo {shp}")
    gdf = gpd.read_file(shp)
    # Reproyectar a WGS84 (EPSG:4326) para almacenar como GeoJSON
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)
    # Heurísticas de columnas (varían entre releases Quantarctica)
    name_col = next((c for c in ("NAME", "Name", "name", "AreaName") if c in gdf.columns), None)
    code_col = next((c for c in ("CODE", "Code", "code", "ASPA_No") if c in gdf.columns), None)
    feats = []
    for _, row in gdf.iterrows():
        # Centroide para el marker (los ASPAs son polígonos)
        c = row.geometry.centroid
        nombre = str(row[name_col]) if name_col else "ASPA sin nombre"
        codigo = f"ASPA-{row[code_col]}" if code_col else ""
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c.x, c.y]},
            "properties": {
                "codigo": codigo,
                "nombre": nombre,
                "tipo": "ASPA",
                "framework": "",
                "interes": "Área Antártica Especialmente Protegida (Annex V Protocolo Madrid)",
                "fuente": f"Quantarctica · {shp.name}",
                "descripcion": "",
            },
        })
    print(f"[OK] {len(feats)} ASPAs leídas de Quantarctica")
    return feats


def fetch_scar_geosites() -> list[dict]:
    """
    TODO: parsear la tabla de geositios propuestos en SCAR ATCM XLIII Att. A.
    Hoy lo dejamos como stub.
    """
    print("[INFO] fetch_scar_geosites: stub — no se descarga (ver TODO en el script)")
    return []


def merge(seed: dict, *extras: list[dict]) -> dict:
    """Une features evitando duplicados por código."""
    by_code = {}
    for feat in seed.get("features", []):
        code = feat.get("properties", {}).get("codigo")
        if code:
            by_code[code] = feat
    for batch in extras:
        for feat in batch:
            code = feat.get("properties", {}).get("codigo")
            if not code:
                continue
            if code in by_code:
                print(f"[SKIP] {code} ya en seed, no se sobreescribe")
                continue
            by_code[code] = feat
    out = dict(seed)
    out["features"] = list(by_code.values())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed-only", action="store_true",
                    help="No descarga nada, solo valida el seed.")
    ap.add_argument("--quantarctica", type=Path, default=None,
                    help="Ruta al folder Quantarctica3 desempaquetado (contiene "
                         "Basemap/ProtectedAreas/*.shp). Bajar de "
                         + QUANTARCTICA_DOWNLOAD_PAGE)
    args = ap.parse_args()

    seed = load_seed()
    print(f"[INFO] Seed cargado: {len(seed['features'])} sitios")

    if args.seed_only:
        print("[INFO] --seed-only: no se hace merge")
        return 0

    extras_aspa = fetch_aspas(args.quantarctica)
    extras_scar = fetch_scar_geosites()
    merged = merge(seed, extras_aspa, extras_scar)
    print(f"[INFO] Tras merge: {len(merged['features'])} sitios "
          f"(+{len(merged['features']) - len(seed['features'])})")

    DATA_OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Escrito {DATA_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
