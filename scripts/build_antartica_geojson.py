"""
Genera app/data/antartica_simplecode.geojson a partir del SCAR GeoMAP v2022.08.

Estrategia:
- Disolver los 99.080 polígonos por SIMPCODE → 21 multipolígonos.
- Simplificar geometría (tolerance ~3 km en EPSG:3031) para que el GeoJSON pese poco.
- Reproyectar a EPSG:4326 para Leaflet.
- Adjuntar metadatos de cada clase desde docs/notas/contextos_antarticos.md.

Requiere geopandas + fiona.
"""

import geopandas as gpd
from pathlib import Path
import json
import sys

# En Windows, Python solo usa UTF-8 en consola interactiva (PEP 528). Al
# redirigir la salida a un archivo cae a cp1252 y cualquier print() con
# flechas o checks lanza UnicodeEncodeError, abortando el script a medio
# correr. Esto lo fuerza a UTF-8 siempre.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent.parent
GDB = ROOT / "docs/mapas/antartica/ATA_SCAR_GeoMAP_v2022_08_ESRI/Data/ATA_SCAR_GeoMAP_geology.gdb"
OUT = ROOT / "app/data/antartica_simplecode.geojson"

# Metadatos de las 21 clases (Tabla 3, Cox et al. 2023)
SIMPLECODE_META = {
    10: ("OTHER", "Seasonal water and ice", "#a8d8e8"),
    11: ("OTHER", "Unknown or unclassified rock", "#888888"),
    20: ("QUATERNARY-NEOGENE", "Unconsolidated colluvium, talus, alluvium, undifferentiated till", "#fff2b3"),
    21: ("QUATERNARY-NEOGENE", "Youngest glacial gravel, till, supraglacial material (Holocene)", "#ffe082"),
    22: ("QUATERNARY-NEOGENE", "Coastal ice shelf till, beach, or lake deposits", "#fbc02d"),
    23: ("QUATERNARY-NEOGENE", "Older glacial gravel and till (Miocene-Quaternary)", "#f9a825"),
    30: ("CENOZOIC", "Sedimentary rock with interbedded volcanic / volcaniclastic", "#a5d6a7"),
    31: ("CENOZOIC", "Volcanic rock — basalt to rhyolite (lavas y piroclásticos)", "#e57373"),
    32: ("CENOZOIC", "Intrusive rock — granite, granodiorite, gabbro, syenite (Eoc-Olig)", "#ff8a65"),
    40: ("MESOZOIC-CENOZOIC", "Sedimentary and volcanic rocks (Jurásico-Paleógeno)", "#ce93d8"),
    41: ("MESOZOIC-CENOZOIC", "Volcanic rock (Jurásico-Paleógeno)", "#ba68c8"),
    42: ("MESOZOIC", "Ferrar Igneous Province (Jurásico)", "#7e57c2"),
    43: ("MESOZOIC", "Silicic volcanic & continental sedimentary rock (Jurásico)", "#9575cd"),
    44: ("MESOZOIC", "Unmetamorphosed granitoid, gabbro, intrusive rock", "#ffb74d"),
    45: ("MESOZOIC", "Metamorphosed gneiss and migmatite (Triásico-Cretácico)", "#8e24aa"),
    50: ("PALEOZOIC-MESOZOIC", "Beacon Supergroup (sandstone-rich, Devónico-Triásico)", "#d4a373"),
    60: ("PROTEROZOIC-PALEOZOIC", "Intrusive — granitoid, diorite, gabbro, orthogneiss", "#ef6c00"),
    61: ("PROTEROZOIC-PALEOZOIC", "Folded low-grade metasedimentary & metavolcanic", "#6d4c41"),
    62: ("PROTEROZOIC-PALEOZOIC", "Low-medium grade metamorphic — schist, marble", "#5d4037"),
    63: ("PROTEROZOIC-PALEOZOIC", "High-grade metamorphic — orthogneiss, paragneiss, schist, amphibolite", "#4e342e"),
    70: ("ARCHEAN", "Metamorphic & intrusive — schist, gneiss, granulite, migmatite", "#212121"),
}

print("Loading GeoMAP geological_units…")
gdf = gpd.read_file(GDB, layer="ATA_GeoMAP_geological_units", columns=["SIMPCODE", "geometry"])
print(f"  loaded {len(gdf)} features (CRS: {gdf.crs})")

print("Dissolving by SIMPCODE…")
dissolved = gdf.dissolve(by="SIMPCODE", as_index=False)
print(f"  → {len(dissolved)} classes")

print("Simplifying geometry (tolerance=5000m in EPSG:3031)…")
dissolved["geometry"] = dissolved.geometry.simplify(tolerance=5000, preserve_topology=True)

print("Reprojecting to EPSG:4326…")
dissolved = dissolved.to_crs(epsg=4326)

print("Attaching metadata…")
def edad_for(cls):
    return {
        "OTHER": "—",
        "QUATERNARY-NEOGENE": "Cuaternario-Neógeno",
        "CENOZOIC": "Cenozoico",
        "MESOZOIC-CENOZOIC": "Mesozoico-Cenozoico",
        "MESOZOIC": "Mesozoico",
        "PALEOZOIC-MESOZOIC": "Paleozoico-Mesozoico",
        "PROTEROZOIC-PALEOZOIC": "Proterozoico-Paleozoico",
        "ARCHEAN": "Arqueano",
    }.get(cls, cls)

def tipo_for(desc):
    d = desc.lower()
    if "volcanic" in d: return "arco volcanico"
    if "intrusive" in d or "granitoid" in d or "granite" in d: return "intrusivo"
    if "metamorphic" in d or "gneiss" in d or "schist" in d: return "metamorfico"
    if "sedimentary" in d or "till" in d or "alluvi" in d or "gravel" in d or "beacon" in d: return "sedimentario"
    if "ice" in d or "water" in d: return "hielo/agua"
    return "otros"

records = []
for _, row in dissolved.iterrows():
    code = int(row.SIMPCODE)
    cls, desc, color = SIMPLECODE_META.get(code, ("UNKNOWN", "", "#999"))
    geom = json.loads(gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_json())["features"][0]["geometry"]
    props = {
        "id": f"simp-{code}",
        "simplecode": code,
        "nombre": f"[{code}] {desc}",
        "clase": cls,
        "edad": edad_for(cls),
        "tipo": tipo_for(desc),
        "color": color,
        "region": "antartica",
        "descripcion": desc,
        "unidades": [],
    }
    records.append({"type": "Feature", "properties": props, "geometry": geom})

fc = {
    "type": "FeatureCollection",
    "_source": "SCAR/GNS GeoMAP v2022.08 (Cox et al. 2023, doi:10.1038/s41597-023-02152-9)",
    "_processing": "Disuelto por SIMPCODE, simplificado a 3km, reproyectado a EPSG:4326",
    "features": records,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
size_mb = OUT.stat().st_size / 1024 / 1024
print(f"\nWritten: {OUT}")
print(f"Size: {size_mb:.2f} MB")
print(f"Classes present: {sorted(dissolved.SIMPCODE.unique())}")
