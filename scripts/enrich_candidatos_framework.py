"""
enrich_candidatos_framework.py
==============================

Para cada candidato bibliométrico (de antartica_geositios_propuestos.geojson),
determina el Framework SCAR (F1-F9) cruzando espacialmente con
antartica_frameworks.geojson.

Estrategia
----------
1. Lee los 40 candidatos (puntos en EPSG:4326).
2. Lee los 6 frameworks mapeados (polígonos en EPSG:4326).
3. Spatial join: para cada candidato, framework cuyo polígono lo contenga.
4. Para candidatos fuera de cualquier polígono mapeado, asigna framework por
   regla geográfica blanda (latitud + longitud + nombre):
     - Antarctic Peninsula (-75°S..-60°S, -80°W..-50°W) → F9 Peninsula arc
     - Transantarctic Mountains (cinturón) → F2 Beacon / F3 Ferrar
     - Dry Valleys (-78°S..-77°S, 162°E..164°E) → F6 Glacial geology
     - Mt Erebus / Ross Island (-78°S..-77°S, 166°E..168°E) → F4 Cenozoic volcanism
     - East Antarctica craton (>0°E, <-65°S) → F1 Basement
5. Escribe app/data/antartica_geositios_propuestos.geojson con campo `framework`.

Uso
---
    pip install geopandas shapely pyogrio
    python scripts/enrich_candidatos_framework.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "app" / "data"
PROPUESTOS = APP_DATA / "antartica_geositios_propuestos.geojson"
FRAMEWORKS = APP_DATA / "antartica_frameworks.geojson"


# Reglas blandas para candidatos que no caigan en polígonos mapeados.
# Tuplas (descripción, bbox=(lat_min, lat_max, lon_min, lon_max), framework).
# bbox usa convención (S, N, W, E) en grados decimales con signos.
SOFT_RULES = [
    # Antarctic Peninsula (Tierra Graham + Palmer Land + South Shetlands)
    ("Peninsula arc", (-75.0, -60.0, -80.0, -50.0), "F9 Antarctic Peninsula arc"),
    # Dry Valleys
    ("Dry Valleys", (-78.0, -76.5, 161.0, 164.5), "F6 Glacial geology"),
    # Erebus / Ross Island volcanic province
    ("Ross Island volcanism", (-78.0, -77.0, 165.5, 168.5), "F4 Cenozoic volcanism"),
    # Northern Victoria Land (Terra Nova, Cape Roberts) — Ross Orogen + Beacon
    ("Northern Victoria Land", (-76.5, -71.0, 160.0, 170.0), "F2 Sedimentary basins (Beacon)"),
    # Transantarctic Mountains (cinturón TAM)
    ("Transantarctic Mountains", (-87.0, -78.0, 160.0, 180.0), "F2 Sedimentary basins (Beacon)"),
    # East Antarctic Craton sector Princess Elizabeth-Prydz (Vestfold, Larsemann, Rauer, Grove)
    ("East Antarctic craton (Prydz sector)", (-72.0, -66.0, 70.0, 110.0), "F1 Basement"),
    # Enderby Land (Rayner Complex)
    ("Enderby Land", (-71.0, -65.0, 45.0, 60.0), "F1 Basement"),
    # Dronning Maud Land (Sør Rondane, Yamato)
    ("Dronning Maud Land", (-75.0, -68.0, 0.0, 45.0), "F1 Basement"),
    # Ellsworth-Whitmore (Vinson, Union Glacier)
    ("Ellsworth-Whitmore", (-83.0, -77.0, -90.0, -75.0), "F1 Basement"),
    # West Antarctic Rift (Marie Byrd Land + Amundsen-Bellingshausen)
    ("Marie Byrd Land volcanism", (-80.0, -72.0, -150.0, -100.0), "F4 Cenozoic volcanism"),
]


def load_geojson(path: Path) -> dict:
    if not path.exists():
        print(f"[ERROR] No existe {path}", file=sys.stderr)
        sys.exit(1)
    # Algunos GeoJSON antiguos vienen en latin-1 (con guion largo Word "—" como byte 0x97).
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="latin-1"))


def spatial_join(candidates: dict, frameworks: dict) -> dict[str, str]:
    """Devuelve {codigo_candidato: framework_name} para los que caen DENTRO de polígonos."""
    try:
        import geopandas as gpd
        from shapely.geometry import shape
    except ImportError:
        print("[ERROR] Falta geopandas. pip install geopandas pyogrio shapely",
              file=sys.stderr)
        return {}

    fw_features = frameworks.get("features", [])
    if not fw_features:
        print("[WARN] antartica_frameworks.geojson sin features", file=sys.stderr)
        return {}

    fw_polys = []
    for f in fw_features:
        props = f.get("properties", {})
        name = props.get("nombre") or props.get("framework") or props.get("name") or "?"
        try:
            geom = shape(f["geometry"])
        except Exception:
            continue
        fw_polys.append({"name": name, "geom": geom})

    assigned: dict[str, str] = {}
    for cand in candidates.get("features", []):
        props = cand.get("properties", {})
        codigo = props.get("codigo", "")
        try:
            pt = shape(cand["geometry"])
        except Exception:
            continue
        for fp in fw_polys:
            if fp["geom"].contains(pt):
                assigned[codigo] = fp["name"]
                break
    return assigned


def soft_rule(lat: float, lon: float) -> str | None:
    for desc, (lat_min, lat_max, lon_min, lon_max), fw in SOFT_RULES:
        # Manejo de bbox que cruza el antimeridiano (lon_min > lon_max).
        in_lat = lat_min <= lat <= lat_max
        if lon_min <= lon_max:
            in_lon = lon_min <= lon <= lon_max
        else:
            in_lon = (lon >= lon_min) or (lon <= lon_max)
        if in_lat and in_lon:
            return fw
    return None


def main() -> int:
    candidates = load_geojson(PROPUESTOS)
    frameworks = load_geojson(FRAMEWORKS)
    print(f"[INFO] {len(candidates['features'])} candidatos")
    print(f"[INFO] {len(frameworks['features'])} polígonos de framework")

    # 1) Spatial join estricto
    hard = spatial_join(candidates, frameworks)
    print(f"[INFO] Asignación por polígono: {len(hard)} candidatos")

    # 2) Reglas blandas para el resto
    soft_count = 0
    no_fw = 0
    for feat in candidates["features"]:
        props = feat["properties"]
        codigo = props.get("codigo", "")
        lon, lat = feat["geometry"]["coordinates"]
        if codigo in hard:
            props["framework"] = hard[codigo]
            props["framework_source"] = "spatial-join (antartica_frameworks.geojson)"
        else:
            sr = soft_rule(lat, lon)
            if sr:
                props["framework"] = sr
                props["framework_source"] = "soft-rule (regla geográfica)"
                soft_count += 1
            else:
                props["framework"] = "(sin asignar)"
                props["framework_source"] = "fuera de bboxes conocidos"
                no_fw += 1
    print(f"[INFO] Asignación por regla blanda: {soft_count} candidatos")
    print(f"[INFO] Sin framework: {no_fw} candidatos")

    # 3) Estadísticas
    fw_counts: dict[str, int] = {}
    for feat in candidates["features"]:
        fw = feat["properties"].get("framework", "(sin asignar)")
        fw_counts[fw] = fw_counts.get(fw, 0) + 1
    print("\n[INFO] Distribución por framework:")
    for fw, n in sorted(fw_counts.items(), key=lambda x: -x[1]):
        print(f"  {n:3d}  {fw}")

    # 4) Escribir
    PROPUESTOS.write_text(json.dumps(candidates, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    print(f"\n[OK] {PROPUESTOS} actualizado con campo `framework`")

    # 5) Generar tabla resumen para el INFORME
    out_md = ROOT / "docs" / "notas" / "candidatos_x_framework.md"
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Candidatos bibliométricos por Framework SCAR\n\n")
        f.write("Generado por `scripts/enrich_candidatos_framework.py`.\n\n")
        # Agrupar por framework
        by_fw: dict[str, list[dict]] = {}
        for feat in candidates["features"]:
            fw = feat["properties"].get("framework", "(sin asignar)")
            by_fw.setdefault(fw, []).append(feat["properties"])
        for fw in sorted(by_fw.keys()):
            sites = by_fw[fw]
            f.write(f"## {fw} — {len(sites)} candidatos\n\n")
            f.write("| Sitio | Pubs | Menciones | Fuente asignación |\n")
            f.write("|---|---:|---:|---|\n")
            for s in sorted(sites, key=lambda x: -x.get("pubs_count", 0)):
                f.write(f"| {s.get('nombre','?')} | {s.get('pubs_count','?')} | "
                        f"{s.get('hits_count','?')} | {s.get('framework_source','?')} |\n")
            f.write("\n")
    print(f"[OK] {out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
