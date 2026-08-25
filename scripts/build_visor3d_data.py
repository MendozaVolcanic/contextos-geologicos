"""
Prepara los datos del visor 3D antártico (app/visor3d/).

El visor necesita dos cosas que el navegador no puede sacar de los archivos
originales sin bajarse decenas de MB:

  1. **Mallas de elevación.** Los GeoTIFF de BedMap3 son 1333x1333 int16 en
     EPSG:3031. Se remuestrean a una grilla cuadrada y se exportan como binario
     int16 crudo, que Three.js lee con un solo fetch y vuelca directo a un
     BufferAttribute. Sin parsear GeoTIFF en el cliente.

  2. **Texturas temáticas.** Las capas de geología (21 clases SIMPCODE) y de
     contextos GEOCON (9 Geological Frameworks) pesan 17 y 16 MB como GeoJSON.
     Dibujarlas como vectores sobre una malla 3D es caro y se ve mal. Se
     rasterizan a PNG sobre la misma grilla del DEM y se aplican como textura.

Todo se reproyecta/rasteriza sobre la grilla de BedMap3, así que las capas
quedan pixel a pixel alineadas con el relieve.

Entradas:  app/data/bedmap3_{surface,bed,thickness}_5km.tif
           app/data/antartica_simplecode.geojson
           app/data/antartica_geocon.geojson
           app/data/antartica_geositios*.geojson
Salidas:   app/visor3d/data/*.bin, *.png, *.json

Uso:
    python scripts/build_visor3d_data.py [--malla 512] [--textura 4096] [--dilatar 2]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
from PIL import Image

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
OUT = ROOT / "app" / "visor3d" / "data"

CAPAS_DEM = ["surface", "bed", "thickness"]

# Paleta de los 9 Geological Frameworks. GF7/8/9 no se asignan desde litología
# (ver docs/notas/geocon_mapping_log.md) pero se dejan definidos para cuando
# lleguen desde otra fuente.
COLORES_GF = {
    1: "#8c2d04",   # Archean cratons
    2: "#cc4c02",   # Proterozoic orogens / Rodinia
    3: "#7f3b08",   # Gondwana amalgamation and breakup
    4: "#d94801",   # margen activo y rift antártico occidental
    5: "#fdae6b",   # tránsito K-Pg
    6: "#4292c6",   # historia glacial cenozoica
    7: "#54278f",   # meteoritos
    8: "#2171b5",   # subglacial
    9: "#969696",   # otros
}


def hex_a_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def remuestrear_dem(nombre, n):
    """Lee un GeoTIFF de BedMap3 y lo remuestrea a n x n promediando por bloques.

    No se usa el resampling de rasterio a propósito. Bilineal mezcla el nodata
    (-32768) con los píxeles válidos del borde y contamina toda la costa: con
    Resampling.bilinear el `surface` daba un mínimo de -72 m cuando el mínimo real
    del dataset es 1 m. Acá cada celda de salida es el promedio de sus píxeles
    válidos, y si no tiene ninguno queda como nodata.
    """
    ruta = DATA / f"bedmap3_{nombre}_5km.tif"
    with rasterio.open(ruta) as src:
        crudo = src.read(1)
        nodata = src.nodata
        bounds = src.bounds
        crs = str(src.crs)

    alto, ancho = crudo.shape
    valido = crudo != np.int16(nodata)
    valores = np.where(valido, crudo, 0).astype(np.float64)

    # Bordes de bloque: reparte 1333 filas en n grupos sin dejar huecos.
    cortes_f = (np.arange(n) * alto) // n
    cortes_c = (np.arange(n) * ancho) // n

    suma = np.add.reduceat(np.add.reduceat(valores, cortes_f, axis=0), cortes_c, axis=1)
    cuenta = np.add.reduceat(np.add.reduceat(valido.astype(np.int32), cortes_f, axis=0),
                             cortes_c, axis=1)

    salida = np.full((n, n), nodata, dtype=np.float64)
    hay = cuenta > 0
    salida[hay] = suma[hay] / cuenta[hay]
    return np.rint(salida).astype(np.int16), nodata, bounds, crs


def dilatar_indices(grilla, veces):
    """Engorda las clases sobre los píxeles vacíos vecinos.

    Hace falta por una razón física: la roca aflorante de la Antártica es ~0,2%
    del continente y casi todos los afloramientos miden menos que un píxel de
    textura. Sin esto, la capa de geología quedaba en 3.772 píxeles de 4,2
    millones — invisible en pantalla.

    Solo se escribe sobre píxeles que valen 0, así que ninguna clase pisa a otra;
    lo que se altera es el tamaño aparente, no la clasificación. **Las áreas
    reales están en docs/notas/geocon_mapping_log.md, no acá.**
    """
    for _ in range(veces):
        salida = grilla.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                vecino = np.roll(np.roll(grilla, dy, axis=0), dx, axis=1)
                salida = np.where(salida == 0, vecino, salida)
        grilla = salida
    return grilla


def rasterizar_capa(ruta_geojson, campo, colores, n, bounds, etiquetas=None, dilatar=0):
    """Rasteriza un GeoJSON sobre la grilla del DEM y devuelve (PNG RGBA, leyenda).

    Se reproyecta a EPSG:3031 antes de rasterizar para que caiga exactamente
    sobre la misma grilla que el relieve.
    """
    gdf = gpd.read_file(ruta_geojson)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs("EPSG:3031")

    transform = rasterio.transform.from_bounds(
        bounds.left, bounds.bottom, bounds.right, bounds.top, n, n)

    valores = sorted(gdf[campo].dropna().unique().tolist())
    # 0 queda reservado para "sin dato", así que los índices parten en 1
    idx = {v: i + 1 for i, v in enumerate(valores)}

    formas = [(geom, idx[val]) for geom, val in zip(gdf.geometry, gdf[campo])
              if geom is not None and val in idx]
    # all_touched=True marca todo píxel que el polígono toque, aunque no cubra su
    # centro. Sin esto, un afloramiento más chico que un píxel desaparece entero.
    grilla = rasterize(formas, out_shape=(n, n), transform=transform,
                       fill=0, dtype=np.uint16, all_touched=True)
    crudos = {i: int((grilla == i).sum()) for i in idx.values()}
    if dilatar:
        grilla = dilatar_indices(grilla, dilatar)

    rgba = np.zeros((n, n, 4), dtype=np.uint8)
    leyenda = []
    for val, i in idx.items():
        color = colores(val, gdf)
        m = grilla == i
        rgba[m, 0], rgba[m, 1], rgba[m, 2] = hex_a_rgb(color)
        rgba[m, 3] = 255
        leyenda.append({
            "valor": val if not isinstance(val, np.integer) else int(val),
            "color": color,
            "etiqueta": etiquetas(val, gdf) if etiquetas else str(val),
            "pixeles": int(m.sum()),
            "pixeles_sin_dilatar": crudos[i],
        })
    leyenda.sort(key=lambda e: -e["pixeles"])
    return Image.fromarray(rgba, "RGBA"), leyenda


def puntos(ruta, campos):
    """Extrae puntos de un GeoJSON como lista de dicts con x/y en EPSG:3031."""
    if not ruta.exists():
        return []
    gdf = gpd.read_file(ruta)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf4326 = gdf.to_crs("EPSG:4326")
    gdf3031 = gdf.to_crs("EPSG:3031")
    salida = []
    for (_, fila), g3031, g4326 in zip(gdf.iterrows(), gdf3031.geometry, gdf4326.geometry):
        if g3031 is None or g3031.geom_type != "Point":
            continue
        p = {"x": round(g3031.x, 1), "y": round(g3031.y, 1),
             "lon": round(g4326.x, 4), "lat": round(g4326.y, 4)}
        for c in campos:
            if c in fila and fila[c] is not None:
                v = fila[c]
                p[c] = int(v) if isinstance(v, np.integer) else (
                    float(v) if isinstance(v, np.floating) else str(v))
        salida.append(p)
    return salida


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--malla", type=int, default=512,
                    help="lado de la grilla de elevación (default 512)")
    ap.add_argument("--textura", type=int, default=4096,
                    help="lado de las texturas temáticas (default 4096)")
    ap.add_argument("--dilatar", type=int, default=2,
                    help="píxeles de engorde de las clases para que se vean "
                         "(default 2). 0 = área fiel pero casi invisible.")
    args = ap.parse_args(argv[1:])

    OUT.mkdir(parents=True, exist_ok=True)
    n, nt, dil = args.malla, args.textura, args.dilatar
    meta = {"malla": n, "textura": nt, "dilatacion": dil, "capas": {}}

    print(f"Mallas de elevación a {n}x{n}:")
    for nombre in CAPAS_DEM:
        datos, nodata, bounds, crs = remuestrear_dem(nombre, n)
        validos = datos != np.int16(nodata)
        datos.tofile(OUT / f"{nombre}.bin")
        meta["capas"][nombre] = {
            "archivo": f"{nombre}.bin",
            "min": int(datos[validos].min()), "max": int(datos[validos].max()),
            "nodata": int(nodata), "validos": int(validos.sum()),
        }
        meta["bounds"] = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        meta["crs"] = crs
        print(f"  {nombre:<10} {datos[validos].min():>7} a {datos[validos].max():>6} m  "
              f"{validos.sum():>9,} px válidos  → {nombre}.bin "
              f"({(OUT / f'{nombre}.bin').stat().st_size/1024:,.0f} KB)")

    with rasterio.open(DATA / "bedmap3_surface_5km.tif") as src:
        bounds = src.bounds

    print(f"\nTexturas temáticas a {nt}x{nt}:")

    # --- Geología: 21 clases SIMPCODE de GeoMAP ---
    img, leyenda = rasterizar_capa(
        DATA / "antartica_simplecode.geojson", "simplecode", n=nt, bounds=bounds, dilatar=dil,
        colores=lambda v, g: g.loc[g.simplecode == v, "color"].iloc[0],
        etiquetas=lambda v, g: f"[{v}] {g.loc[g.simplecode == v, 'descripcion'].iloc[0]}")
    img.save(OUT / "geologia.png", optimize=True)
    meta["geologia"] = leyenda
    print(f"  geologia.png   {len(leyenda)} clases  "
          f"({(OUT / 'geologia.png').stat().st_size/1024:,.0f} KB)")

    # --- Contextos GEOCON: los Geological Frameworks asignados ---
    img, leyenda = rasterizar_capa(
        DATA / "antartica_geocon.geojson", "framework", n=nt, bounds=bounds, dilatar=dil,
        colores=lambda v, g: COLORES_GF[int(v)],
        etiquetas=lambda v, g: f"GF{int(v)} — {g.loc[g.framework == v, 'nombre'].iloc[0]}")
    img.save(OUT / "geocon.png", optimize=True)
    meta["geocon"] = leyenda
    print(f"  geocon.png     {len(leyenda)} frameworks  "
          f"({(OUT / 'geocon.png').stat().st_size/1024:,.0f} KB)")

    # --- Geositios ---
    meta["geositios"] = puntos(DATA / "antartica_geositios.geojson",
                               ["nombre", "name", "framework", "descripcion"])
    meta["candidatos"] = puntos(DATA / "antartica_geositios_propuestos.geojson",
                                ["name", "nombre", "framework", "pubs", "weighted_score"])
    print(f"\nPuntos: {len(meta['geositios'])} geositios SCAR, "
          f"{len(meta['candidatos'])} candidatos bibliométricos")

    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    print(f"\nmeta.json escrito ({(OUT / 'meta.json').stat().st_size/1024:,.0f} KB)")
    total = sum(f.stat().st_size for f in OUT.iterdir() if f.is_file())
    print(f"Total del paquete de datos del visor: {total/1024**2:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
