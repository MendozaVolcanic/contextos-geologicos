"""
Genera app/data/chile_geologico.geojson — base geológica de Chile simplificada.

Entrada: docs/mapas/chile/Mapa_Geologico_de_Chile.geojson (60 MB, 18.935 polígonos)
Salida: ~5-10 MB, disuelto por código `geo` (86 unidades), simplificado.
"""

import geopandas as gpd
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs/mapas/chile/Mapa_Geologico_de_Chile.geojson"
OUT = ROOT / "app/data/chile_geologico.geojson"

# Paleta por era — coherente con la convención cronoestratigráfica internacional
ERA_COLOR = {
    "PRECAMBRICO": "#f06292",
    "PALEOZOICO": "#80cbc4",
    "MEZOZOICO": "#80deea",
    "MESOZOICO": "#80deea",
    "CENOZOICO": "#fff176",
    "CUATERNARIO": "#ffe082",
}

COMPO_TINT = {
    "Rocas intrusivas": -0.15,            # más oscuro
    "Secuencias volcanicas": -0.05,
    "Secuencias volcanosedimenta": 0.0,
    "Secuencias sedimentarias": 0.10,     # más claro
    "Rocas metamorficas": -0.10,
}

def shade(hexcol, factor):
    h = hexcol.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if factor < 0:
        r, g, b = (int(c * (1 + factor)) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * factor) for c in (r, g, b))
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

print("Loading Chile geological map…")
gdf = gpd.read_file(SRC)
print(f"  {len(gdf)} features (CRS: {gdf.crs})")

# Limpieza mínima
gdf["era"] = gdf["era"].fillna("DESCONOCIDO").astype(str).str.strip()
gdf["periodo"] = gdf["periodo"].fillna("").astype(str).str.strip()
gdf["composicio"] = gdf["composicio"].fillna("").astype(str).str.strip()
gdf["geo"] = gdf["geo"].fillna("?").astype(str).str.strip()

print("Dissolving by `geo` code…")
diss = gdf.dissolve(by="geo", aggfunc={
    "era": "first",
    "periodo": "first",
    "epoca": "first",
    "composicio": "first",
}, as_index=False)
print(f"  → {len(diss)} unique units")

print("Simplifying geometry (tolerance=0.01° ≈ 1 km)…")
diss["geometry"] = diss.geometry.simplify(tolerance=0.01, preserve_topology=True)

print("Building features…")
records = []
for _, row in diss.iterrows():
    base = ERA_COLOR.get(row.era.upper(), "#9e9e9e")
    color = shade(base, COMPO_TINT.get(row.composicio, 0.0))
    geom = json.loads(gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_json())["features"][0]["geometry"]
    props = {
        "geo": row.geo,
        "era": row.era,
        "periodo": row.periodo,
        "epoca": row.epoca,
        "composicio": row.composicio,
        "color": color,
    }
    records.append({"type": "Feature", "properties": props, "geometry": geom})

fc = {
    "type": "FeatureCollection",
    "_source": "SERNAGEOMIN — Mapa Geológico de Chile escala 1:1.000.000",
    "_processing": "Disuelto por código `geo` (86 unidades), simplificado a 0.01°",
    "features": records,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
print(f"\nWritten: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024 / 1024:.2f} MB")
