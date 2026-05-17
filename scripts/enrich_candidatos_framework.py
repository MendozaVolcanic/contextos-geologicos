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
# Las reglas se evalúan en orden — primer match gana. Orden de específico a genérico.
SOFT_RULES = [
    # --- Sub-divisiones de Transantarctic Mountains (TAM) ---
    # TAM Norte (Victoria Land, Northern): Ross Orogen basement + Beacon + Ferrar
    ("TAM Norte (Northern Victoria Land)", (-76.5, -70.0, 160.0, 170.0), "F2 Sedimentary basins (Beacon)"),
    # TAM Central (sector Dry Valleys-Mawson Glacier): Beacon + Ferrar dominante
    ("TAM Central (Dry Valleys sector)", (-79.5, -76.5, 158.0, 167.0), "F2 Sedimentary basins (Beacon)"),
    # TAM Sur (Beardmore-Shackleton-Darwin Glaciers): Beacon + paleontología
    ("TAM Sur (Beardmore-Shackleton)", (-86.0, -79.5, 150.0, 175.0), "F2 Sedimentary basins (Beacon)"),
    # TAM Pole sector (cinturón polar wraparound)
    ("TAM Pole sector", (-87.0, -79.5, 175.0, 180.0), "F2 Sedimentary basins (Beacon)"),
    ("TAM Pole sector (W)", (-87.0, -79.5, -180.0, -150.0), "F2 Sedimentary basins (Beacon)"),

    # --- Sub-antártico (South Orkney + South Sandwich + South Georgia) ---
    ("South Orkneys (Signy, Coronation)", (-61.5, -60.0, -47.0, -44.0), "F9 Antarctic Peninsula arc (sub-antártico)"),
    ("South Sandwich Islands", (-60.0, -56.0, -29.0, -25.0), "F4 Cenozoic volcanism (sub-antártico)"),

    # --- Antarctic Peninsula (Tierra Graham + Palmer Land + South Shetlands) ---
    ("Peninsula arc", (-75.0, -60.0, -80.0, -50.0), "F9 Antarctic Peninsula arc"),

    # --- Dry Valleys (estricto: solo Taylor/Wright/Beacon Valley) ---
    ("Dry Valleys (estricto)", (-78.0, -76.8, 161.0, 164.5), "F6 Glacial geology"),

    # --- Erebus / Ross Island volcanic province ---
    ("Ross Island volcanism", (-78.0, -77.0, 165.5, 168.5), "F4 Cenozoic volcanism"),

    # --- Campos meteoríticos explícitos ---
    # Allan Hills (ANSMET)
    ("Allan Hills meteorítico", (-76.9, -76.6, 159.0, 160.3), "F7 Meteorite fields"),
    # Grove Mountains (CHINARE meteorítico, Lambert basin)
    ("Grove Mountains meteorítico", (-73.3, -72.3, 74.0, 76.0), "F7 Meteorite fields"),
    # Yamato Mountains (JARE meteorítico, Dronning Maud Land East)
    ("Yamato Mountains meteorítico", (-72.0, -71.0, 35.0, 36.0), "F7 Meteorite fields"),
    # Sør Rondane Mountains (BELARE meteorítico + basamento)
    ("Sør Rondane meteorítico", (-72.5, -71.5, 22.0, 28.0), "F7 Meteorite fields"),

    # --- East Antarctic Craton: cobertura ampliada hasta Wilkes Land ---
    # Windmill Islands (Casey Station area) — Wilkes Land
    ("Windmill Islands (Wilkes Land)", (-67.0, -66.0, 109.5, 111.5), "F1 Basement"),
    # Shackleton Range (gap entre TAM y Ellsworth-Whitmore)
    ("Shackleton Range", (-81.5, -80.0, -35.0, -19.0), "F1 Basement"),
    # Balleny Islands (volcánicas, al norte de Cabo Adare)
    ("Balleny Islands volcanism", (-68.0, -66.0, 162.0, 165.0), "F4 Cenozoic volcanism"),
    # Whitmore Mountains (extender bbox Ellsworth-Whitmore al oeste)
    ("Whitmore Mountains (Ellsworth-Whitmore extension)", (-83.0, -81.0, -106.0, -100.0), "F1 Basement"),

    # --- East Antarctic Craton sector Princess Elizabeth-Prydz ---
    ("East Antarctic craton (Prydz sector)", (-72.0, -66.0, 70.0, 110.0), "F1 Basement"),
    # Enderby Land (Rayner Complex)
    ("Enderby Land", (-71.0, -65.0, 45.0, 60.0), "F1 Basement"),
    # Dronning Maud Land general (Sør Rondane, Yamato regional)
    ("Dronning Maud Land", (-75.0, -68.0, 0.0, 45.0), "F1 Basement"),
    # Ellsworth-Whitmore (Vinson, Union Glacier)
    ("Ellsworth-Whitmore", (-83.0, -77.0, -90.0, -75.0), "F1 Basement"),
    # MacRobertson Land + Prince Charles Mountains + Lambert basin sector
    ("Lambert-PCM sector", (-75.0, -67.0, 60.0, 80.0), "F1 Basement"),

    # --- West Antarctic Rift / Marie Byrd Land ---
    ("Marie Byrd Land volcanism", (-80.0, -72.0, -150.0, -100.0), "F4 Cenozoic volcanism"),
    # Pine Island / Thwaites embayment (Amundsen Sea Embayment)
    ("Amundsen Sea Embayment (PIG/Thwaites)", (-78.0, -73.0, -113.0, -97.0), "F4 Cenozoic volcanism (West Antarctic Rift)"),
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
