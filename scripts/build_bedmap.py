"""
build_bedmap.py
===============

Descarga BedMap3 (Pritchard et al., 2025) y genera:
  - GeoTIFFs reproyectados/cogificados a EPSG:3031:
      app/data/bedmap3_bed.tif
      app/data/bedmap3_surface.tif
      app/data/bedmap3_thickness.tif
  - Vectores SCAR ADD (línea de costa, grounding line) en EPSG:3031:
      app/data/grounding_line.geojson
      app/data/coastline.geojson
  - Tiles XYZ locales (opcional, si --tiles) en:
      app/data/tiles/bedmap3_{layer}/{z}/{x}/{y}.png

BedMap3
-------
Pritchard, H. D. et al. (2025). Bedmap3 updated ice bed, surface and thickness
gridded datasets for Antarctica. Scientific Data, doi:10.1038/s41597-025-...

Producto NetCDF público en el portal de UK Polar Data Centre:
  https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=BEDMAP3

Vectores SCAR ADD v7.5:
  https://www.add.scar.org/

Uso:
    pip install rasterio xarray netCDF4 geopandas pyogrio rio-cogeo rio-tiler
    python scripts/build_bedmap.py [--layers bed surface thickness] [--tiles]

Si las descargas remotas fallan (red corporativa, SSL, etc.), el script imprime
las URLs exactas para bajar a mano y deja todo apuntado a docs/notas/bedmap.md.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# En Windows, Python solo usa UTF-8 en consola interactiva (PEP 528). Al
# redirigir la salida a un archivo cae a cp1252 y cualquier print() con
# flechas o checks lanza UnicodeEncodeError, abortando el script a medio
# correr. Esto lo fuerza a UTF-8 siempre.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "app" / "data"
RAW_DIR = ROOT / "docs" / "mapas" / "antartica" / "bedmap3"
NOTES = ROOT / "docs" / "notas" / "bedmap.md"

# BedMap3 Gridding Products — Pritchard et al. 2025, Scientific Data 12, 414.
# DOI: 10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2
# Hosted en RAMADDA (BAS PDC): 7 GeoTIFF (2.1 GB total) + 1 NetCDF (2.4 GB).
# Como RAMADDA usa URLs con UUID por archivo (no path estables), no podemos
# hardcodear el endpoint directo de cada GeoTIFF/NetCDF — hay que parsear el
# index de la entrada. Estrategia:
#   1) GET al show de la entrada
#   2) Extraer los hrefs `/repository/entry/get/<filename>?...&entryid=<uuid>`
#   3) Filtrar por nombre (bm3_bed.tif, bm3_surface.tif, bm3_thickness.tif,
#      bm3_grid.nc) y descargar.
RAMADDA_ENTRY_UUID = "2d0e4791-8e20-46a3-80e4-f5f6716025d2"
RAMADDA_ENTRY_URL = (
    f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={RAMADDA_ENTRY_UUID}"
)
RAMADDA_GET_BASE = "https://ramadda.data.bas.ac.uk/repository/entry/get/"
BEDMAP3_FILES = {
    "bed":       "bm3_bed.tif",         # ~700 MB (16-bit signed, 500 m)
    "surface":   "bm3_surface.tif",     # ~700 MB
    "thickness": "bm3_thickness.tif",   # ~700 MB
    "netcdf":    "bm3_grid.nc",         # ~2.4 GB (consolidado, todas las capas)
}

# Antarctic Digital Database (SCAR ADD v7.x) — el portal canónico de
# coastline / grounding line / sea mask / contours. El paquete completo está
# en data.bas.ac.uk/items/e74543c0-4c4e-4b41-aa33-5bb2f67df389 (visor + items).
# Mismo problema que RAMADDA: hay que parsear el índice. Stub por ahora.
SCAR_ADD_VIEWER = "https://add.scar.org/"
SCAR_ADD_DOWNLOAD = "https://data.bas.ac.uk/items/e74543c0-4c4e-4b41-aa33-5bb2f67df389/"
SCAR_ADD_URLS = {
    "grounding_line": "(parse from SCAR_ADD_DOWNLOAD index)",
    "coastline":      "(parse from SCAR_ADD_DOWNLOAD index)",
}


def download(url: str, dest: Path) -> bool:
    """Descarga con requests; devuelve True si OK."""
    try:
        import requests
    except ImportError:
        print("[ERROR] Falta `requests`. pip install requests", file=sys.stderr)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = 100 * done / total
                        print(f"\r  {dest.name}: {pct:5.1f}%", end="", flush=True)
            print()
        return True
    except Exception as e:
        print(f"\n[WARN] Falló descarga {url}: {e}", file=sys.stderr)
        return False


def nc_to_cog(nc_path: Path, var: str, out_tif: Path) -> bool:
    """Convierte una variable NetCDF a Cloud-Optimized GeoTIFF en EPSG:3031."""
    try:
        import xarray as xr
        import rioxarray  # noqa: F401  (registra el accessor .rio)
    except ImportError:
        print("[ERROR] Falta xarray + rioxarray. pip install xarray rioxarray netCDF4", file=sys.stderr)
        return False
    try:
        ds = xr.open_dataset(nc_path)
        da = ds[var]
        # BedMap3 ya viene en EPSG:3031 (Antarctic Polar Stereographic, true scale -71)
        if not da.rio.crs:
            da = da.rio.write_crs("EPSG:3031")
        out_tif.parent.mkdir(parents=True, exist_ok=True)
        da.rio.to_raster(out_tif, driver="COG", compress="DEFLATE", predictor=2)
        print(f"[OK] {out_tif}")
        return True
    except Exception as e:
        print(f"[ERROR] Conversión NetCDF→COG falló: {e}", file=sys.stderr)
        return False


def generate_tiles(tif_path: Path, out_dir: Path, layer_key: str) -> bool:
    """Genera tiles XYZ desde un COG (opcional)."""
    try:
        # gdal2tiles funciona; rio-tiler también pero requiere un server.
        import subprocess
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = ["gdal2tiles.py", "-z", "0-6", "-w", "none", "-r", "bilinear",
               str(tif_path), str(out_dir)]
        subprocess.run(cmd, check=True)
        print(f"[OK] Tiles en {out_dir}")
        return True
    except Exception as e:
        print(f"[WARN] gdal2tiles falló: {e}", file=sys.stderr)
        return False


def write_fallback_notes() -> None:
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(
        "# BedMap3 — descarga manual\n\n"
        "Si `build_bedmap.py` no pudo parsear RAMADDA, abrir la entrada en el navegador:\n\n"
        f"- Entry: <{RAMADDA_ENTRY_URL}>\n"
        f"- DOI:   https://doi.org/10.5285/{RAMADDA_ENTRY_UUID}\n\n"
        f"Archivos a bajar (~5 GB en total: 2.1 GB de GeoTIFF + 2.4 GB de NetCDF):\n\n"
        + "\n".join(f"- `{fname}` ({layer})" for layer, fname in BEDMAP3_FILES.items())
        + f"\n\nDejarlos en `{RAW_DIR.relative_to(ROOT)}` y volver a correr el script.\n\n"
        + "## Vectores SCAR ADD (línea de costa, grounding line)\n\n"
        + f"Portal: <{SCAR_ADD_DOWNLOAD}>\n\n"
        + "Bajar:\n"
        + "- `add_coastline_high_res_polygon.gpkg` → renombrar a "
          "`app/data/coastline.geojson` (convertir con `ogr2ogr -f GeoJSON`).\n"
        + "- `add_groundingline_polygon.gpkg` → `app/data/grounding_line.geojson`.\n",
        encoding="utf-8",
    )


def resolve_ramadda_links() -> dict[str, str]:
    """Parsea el HTML del entry RAMADDA para encontrar las URLs reales por archivo."""
    import re
    try:
        import requests
    except ImportError:
        return {}
    try:
        r = requests.get(RAMADDA_ENTRY_URL, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] No se pudo leer índice RAMADDA: {e}", file=sys.stderr)
        return {}
    # Hrefs del tipo /repository/entry/get/<filename>?...&entryid=<uuid>
    pattern = re.compile(r'href="(/repository/entry/get/([^"?]+)\?[^"]*entryid=' +
                         re.escape(RAMADDA_ENTRY_UUID) + r'[^"]*)"')
    found = {}
    for match in pattern.finditer(r.text):
        href, fname = match.group(1), match.group(2)
        found[fname] = "https://ramadda.data.bas.ac.uk" + href
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layers", nargs="*", default=list(BEDMAP3_FILES.keys()),
                    choices=list(BEDMAP3_FILES.keys()),
                    help="Capas BedMap3 a procesar")
    ap.add_argument("--tiles", action="store_true",
                    help="Generar tiles XYZ locales (requiere gdal2tiles.py)")
    args = ap.parse_args()

    write_fallback_notes()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] Resolviendo URLs reales desde RAMADDA…")
    link_map = resolve_ramadda_links()
    if not link_map:
        print(f"[!] No pudimos parsear RAMADDA. Bajar a mano desde:\n  {RAMADDA_ENTRY_URL}\n"
              f"y dejar los archivos en {RAW_DIR}", file=sys.stderr)

    any_ok = False
    for layer in args.layers:
        fname = BEDMAP3_FILES[layer]
        local = RAW_DIR / fname
        if not local.exists():
            url = link_map.get(fname)
            if not url:
                print(f"[SKIP] {fname}: no se encontró URL ni archivo local", file=sys.stderr)
                continue
            print(f"[INFO] Descargando {fname} ({layer})…")
            if not download(url, local):
                continue
        # Si es GeoTIFF, ya está en formato útil; solo recomprime a COG si --tiles
        # Si es NetCDF, lo descomponemos en 3 COGs
        if layer == "netcdf":
            for sub, var in (("bed", "bed_topography"),
                             ("surface", "surface_topography"),
                             ("thickness", "ice_thickness")):
                out = DATA_DIR / f"bedmap3_{sub}.tif"
                if nc_to_cog(local, var, out):
                    any_ok = True
        else:
            # Copiar el .tif a app/data/ con el nombre que espera app.js
            out = DATA_DIR / f"bedmap3_{layer}.tif"
            if not out.exists():
                import shutil
                shutil.copy2(local, out)
                print(f"[OK] {out}")
            any_ok = True
            if args.tiles:
                generate_tiles(out, DATA_DIR / "tiles" / f"bedmap3_{layer}", layer)

    if not any_ok:
        print(f"\n[!] Nada se generó. Revisa {NOTES}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
