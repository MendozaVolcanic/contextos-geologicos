"""
Mapea las 18.935 unidades del Mapa Geológico de Chile 1:1.000.000 (SERNAGEOMIN)
a uno de los 22 Contextos Geológicos Chilenos (Mourgues et al. 2012/2016).

Estrategia: reglas explícitas era+período+composición+latitud → código de contexto.
Las reglas son las mejores que se pueden inferir sin facies info ni clasificación
unidad-por-unidad. Felipe debería revisarlas y corregir según su criterio.

Salida:
- app/data/chile_contextos.geojson — polígonos del mapa al millón etiquetados
- docs/notas/mapping_rules_log.md — auditoría de cuántas unidades fueron a cada contexto
"""

import geopandas as gpd
from pathlib import Path
import json
from collections import Counter
import sys

# En Windows, Python solo usa UTF-8 en consola interactiva (PEP 528). Al
# redirigir la salida a un archivo cae a cp1252 y cualquier print() con
# flechas o checks lanza UnicodeEncodeError, abortando el script a medio
# correr. Esto lo fuerza a UTF-8 siempre.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs/mapas/chile/Mapa_Geologico_de_Chile.geojson"
OUT_GEOJSON = ROOT / "app/data/chile_contextos.geojson"
OUT_LOG = ROOT / "docs/notas/mapping_rules_log.md"

# Los 22 contextos de Mourgues 2012/2016 — código → (nombre completo, color)
CONTEXTOS = {
    "MgPz":  ("Magmatismo Paleozoico", "#ff8a65"),
    "MgMz":  ("Magmatismo Mesozoico", "#ef6c00"),
    "MgVCz": ("Magmatismo y vulcanismo Cenozoico", "#d35400"),
    "AcMz":  ("Arco volcánico del Mesozoico", "#c0392b"),
    "VNgsQ": ("Volcanismo Neógeno sup-Cuaternario y campos geotermales", "#e74c3c"),
    "IO":    ("Islas y piso oceánicos", "#1abc9c"),
    "TCA":   ("Terrenos exóticos y complejos de acreción", "#5b3a8a"),
    "SSPz":  ("Series sedimentarias del Paleozoico", "#7f8c8d"),
    "SCMz":  ("Series continentales mesozoicas y sus fósiles", "#9b59b6"),
    "SMTrJ": ("Cuencas marinas Triásico-Jurásico-Cretácico basal", "#3498db"),
    "SMKi":  ("Cuencas marinas del Cretácico Inferior", "#2980b9"),
    "SMKs":  ("Cretácico Superior marino de Magallanes y Chile central", "#21618c"),
    "SCCz":  ("Series continentales cenozoicas y sus fósiles", "#27ae60"),
    "SMCz":  ("Series marinas cenozoicas y sus fósiles", "#48c9b0"),
    "AFNgQ": ("Ambientes fluvioaluviales del Neógeno-Cuaternario", "#f1c40f"),
    "BC":    ("Borde costero", "#5dade2"),
    "PGGl":  ("Procesos, geoformas y depósitos glaciales del centro y sur", "#85c1e9"),
    "DA":    ("Desierto de Atacama", "#fad7a0"),
    "ACQ":   ("Cuaternario continental, megafauna y primeros habitantes", "#dc7633"),
    "CHA":   ("Campos de hielo e inlandsis antártico", "#aed6f1"),
    "TEC":   ("Mega estructuras, tectónica andina y neotectónica", "#7d6608"),
    "Lss":   ("Geoformas por impactos y materiales del sistema solar", "#34495e"),
}


def assign_contexto(props, lat):
    """
    Reglas Mourgues. Devuelve (codigo, regla_aplicada).

    Felipe: revisa este bloque. Cada `if` corresponde a un mapping; los comentarios
    indican el razonamiento. Si quieres cambiar una regla, edita acá y vuelve a correr
    el script.
    """
    era = (props.get("era") or "").strip().upper()
    composicio = (props.get("composicio") or "").strip()
    periodo = (props.get("periodo") or "").strip()
    epoca = (props.get("epoca") or "").strip().lower()
    geo = (props.get("geo") or "").strip()

    # Cuaternario y casos por edad/composición
    if "CUATERNARIO" in era or periodo == "Cuaternario" or "holoceno" in epoca or "pleistoceno" in epoca:
        if composicio in ("Secuencias volcanicas", "Secuencias volcanosedimenta"):
            return "VNgsQ", "Cuaternario volcánico → VNgsQ"
        # Sedimentario cuaternario por latitud
        if lat > -28:
            return "DA", "Cuaternario sedimentario lat>-28°S → Desierto de Atacama"
        if lat < -41:
            return "PGGl", "Cuaternario sedimentario lat<-41°S → Glaciales centro-sur"
        return "AFNgQ", "Cuaternario sedimentario −41 a −28 → Fluvioaluvial"

    # Cenozoico (no cuaternario)
    if "CENOZOICO" in era or "CENOZOICA" in era:
        if composicio == "Rocas intrusivas":
            return "MgVCz", "Intrusivo cenozoico → Magmatismo y vulcanismo Cenozoico"
        if composicio in ("Secuencias volcanicas", "Secuencias volcanosedimenta"):
            if any(t in epoca for t in ("mioceno", "plioceno")):
                return "VNgsQ", "Volcánico Mioceno-Plioceno → VNgsQ"
            return "MgVCz", "Volcánico cenozoico (pre-Mioceno) → MgVCz"
        if composicio == "Secuencias sedimentarias":
            # Distinguir marinas/continentales por keywords en epoca
            if any(t in epoca for t in ("miocen", "neogen")):
                return "AFNgQ", "Sedimentario neógeno → AFNgQ"
            return "SCCz", "Sedimentario cenozoico → Series continentales cenozoicas"

    # Mesozoico
    if "MESOZOICO" in era or "MEZOZOICO" in era:
        if composicio == "Rocas intrusivas":
            return "MgMz", "Intrusivo mesozoico → Magmatismo Mesozoico"
        if composicio in ("Secuencias volcanicas", "Secuencias volcanosedimenta"):
            return "AcMz", "Volcánico mesozoico → Arco volcánico Mesozoico"
        if composicio == "Secuencias sedimentarias":
            if periodo == "Triasico" or "tri" in epoca or "jurasico" in epoca:
                return "SMTrJ", "Sedimentario Tr-J → Cuencas marinas Tr-J"
            if periodo == "Cretacico" or "cret" in epoca:
                # Inferior vs superior por epoca
                if any(t in epoca for t in ("inferior", "temprano", "berriasiano",
                                              "valanginiano", "hauteriviano",
                                              "barremiano", "aptiano", "albiano")):
                    return "SMKi", "Cretácico inferior marino → SMKi"
                return "SMKs", "Cretácico superior marino → SMKs"
            return "SCMz", "Sedimentario mesozoico s.l. → Series continentales mesozoicas"
        if composicio == "Rocas metamorficas":
            return "TCA", "Metamórfico mesozoico → Terrenos exóticos y complejos de acreción"

    # Paleozoico
    if "PALEOZOICO" in era:
        if composicio == "Rocas intrusivas":
            return "MgPz", "Intrusivo paleozoico → Magmatismo Paleozoico"
        if composicio == "Rocas metamorficas":
            return "TCA", "Metamórfico paleozoico → Terrenos exóticos y complejos de acreción"
        if composicio == "Secuencias sedimentarias":
            return "SSPz", "Sedimentario paleozoico → Series sedimentarias Pz"
        if composicio in ("Secuencias volcanicas", "Secuencias volcanosedimenta"):
            return "SSPz", "Volcánico paleozoico → SSPz (default)"

    # Precámbrico
    if "PRECAMBRICO" in era or "PRE" in era:
        if composicio == "Rocas metamorficas":
            return "TCA", "Metamórfico precámbrico → TCA"
        return "TCA", "Precámbrico s.l. → TCA"

    # Sin información
    return None, f"sin clasificar (era={era}, comp={composicio}, periodo={periodo})"


def main():
    print("Loading Chile geological map…")
    gdf = gpd.read_file(SRC)
    print(f"  {len(gdf)} features")

    # Reproyectar a un CRS proyectado para calcular centroides en metros
    gdf_proj = gdf.to_crs(epsg=32719)  # UTM zone 19S, decente para Chile central
    centroids = gdf_proj.geometry.centroid.to_crs(epsg=4326)
    gdf["_lat"] = centroids.y
    gdf["_lon"] = centroids.x

    # Aplicar reglas
    print("Applying mapping rules…")
    codigos = []
    rule_log = Counter()
    for _, row in gdf.iterrows():
        cod, rule = assign_contexto(row, row["_lat"])
        codigos.append(cod or "UNK")
        rule_log[rule] += 1

    gdf["contexto"] = codigos

    # Conteo por contexto
    cnt = Counter(codigos)
    print("\nDistribución por contexto:")
    for cod, n in cnt.most_common():
        nombre = CONTEXTOS.get(cod, ("?", ""))[0]
        print(f"  {cod:7} {n:>6} polígonos · {nombre}")

    # Disolver por contexto
    print("\nDissolving by contexto…")
    diss = gdf.dissolve(by="contexto", as_index=False)
    print(f"  → {len(diss)} contextos representados")

    # Simplificar geometría
    print("Simplifying (tolerance=0.015°)…")
    diss["geometry"] = diss.geometry.simplify(tolerance=0.015, preserve_topology=True)

    # Construir features
    records = []
    for _, row in diss.iterrows():
        cod = row.contexto
        nombre, color = CONTEXTOS.get(cod, (f"({cod})", "#999"))
        geom = json.loads(gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_json())["features"][0]["geometry"]
        props = {
            "id": f"ctx-{cod}",
            "codigo": cod,
            "nombre": nombre,
            "tipo": "contexto",
            "edad": cod,
            "color": color,
            "region": "chile",
            "descripcion": nombre,
            "n_poligonos_origen": int(cnt[cod]),
            "unidades": [],
        }
        records.append({"type": "Feature", "properties": props, "geometry": geom})

    fc = {
        "type": "FeatureCollection",
        "_source": "SERNAGEOMIN Mapa Geológico 1:1M, mapeado a 22 contextos Mourgues 2012/2016 mediante reglas era+período+composición+latitud (scripts/build_chile_contextos.py)",
        "features": records,
    }

    OUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_GEOJSON.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    size_mb = OUT_GEOJSON.stat().st_size / 1024 / 1024
    print(f"\nWritten: {OUT_GEOJSON}")
    print(f"Size: {size_mb:.2f} MB")

    # Audit log
    log = ["# Auditoría del mapping mapa al millón → 22 contextos chilenos\n"]
    log.append(f"\nTotal polígonos procesados: **{len(gdf)}**\n")
    log.append("\n## Distribución por contexto\n\n| Código | n polígonos | Contexto |\n|---|---:|---|\n")
    for cod, n in cnt.most_common():
        nombre = CONTEXTOS.get(cod, ("?", ""))[0]
        log.append(f"| {cod} | {n} | {nombre} |\n")
    log.append("\n## Conteo por regla aplicada\n\n| n | Regla |\n|---:|---|\n")
    for rule, n in rule_log.most_common():
        log.append(f"| {n} | {rule} |\n")
    log.append("\n## Limitaciones conocidas\n")
    log.append("- Las reglas no distinguen marino/continental con suficiente precisión sin facies info.\n")
    log.append("- Contextos #6 IO (islas oceánicas), #16 BC (borde costero), #21 TEC (estructuras), #22 Lss (impactos) no se asignan automáticamente — requieren información geográfica/estructural adicional.\n")
    log.append("- Contexto #20 CHA (hielo antártico) está mapeado en el procesamiento antártico aparte.\n")
    log.append("- Felipe: revisar reglas en `scripts/build_chile_contextos.py` función `assign_contexto()`.\n")

    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOG.write_text("".join(log), encoding="utf-8")
    print(f"Audit log: {OUT_LOG}")


if __name__ == "__main__":
    main()
