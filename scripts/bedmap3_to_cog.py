"""
bedmap3_to_cog.py
=================

Toma el NetCDF consolidado BedMap3 (~2.5 GB) y produce 3 COG GeoTIFFs
DOWNSAMPLEADOS para servir desde GitHub Pages.

Input
-----
- docs/mapas/antartica/bedmap3/bedmap3.nc

Variables esperadas (verificadas con xarray al primer run):
- bed_topography     (bed elevation, m)
- surface_topography (ice surface elevation, m)
- ice_thickness      (m)

Resolución original: 500 m
Resolución de salida: 5000 m (10x downsample) -> cada COG ~10-30 MB -> cabe en repo

Salida
------
- app/data/bedmap3_bed_5km.tif       (m, signed int16, COG)
- app/data/bedmap3_surface_5km.tif   (m, signed int16, COG)
- app/data/bedmap3_thickness_5km.tif (m, signed int16, COG)

Para servir en el dashboard usamos georaster-layer-for-leaflet vía CDN.

Uso
---
    pip install xarray rioxarray netCDF4 rasterio
    python scripts/bedmap3_to_cog.py
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NC_PATH = ROOT / "docs" / "mapas" / "antartica" / "bedmap3" / "bedmap3.nc"
OUT_DIR = ROOT / "app" / "data"

# Variables a extraer (ajustar tras ver xarray ds.variables)
VARS = {
    "bed":       "bed_topography",
    "surface":   "surface_topography",
    "thickness": "ice_thickness",
}

# Factor de downsample (10× -> de 500 m a 5 km)
DOWNSAMPLE = 10


def main() -> int:
    if not NC_PATH.exists():
        print(f"[ERROR] No existe {NC_PATH}", file=sys.stderr)
        return 1

    try:
        import xarray as xr
        import rioxarray  # noqa
        import numpy as np
    except ImportError:
        print("[ERROR] pip install xarray rioxarray netCDF4 rasterio numpy",
              file=sys.stderr)
        return 1

    print(f"[INFO] Abriendo {NC_PATH.name} ({NC_PATH.stat().st_size / 1024**3:.2f} GB)…")
    ds = xr.open_dataset(NC_PATH, chunks={"x": 1024, "y": 1024})
    print(f"[INFO] Variables disponibles: {list(ds.data_vars.keys())}")
    print(f"[INFO] Dimensiones: {dict(ds.sizes)}")
    print(f"[INFO] CRS metadata: {ds.attrs.get('Projection', ds.attrs.get('crs', '?'))}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for label, var_name in VARS.items():
        # Fallback names si los esperados no existen
        if var_name not in ds.data_vars:
            candidates = [v for v in ds.data_vars
                          if label in v.lower() or v.lower() in label]
            if not candidates:
                print(f"[WARN] Variable '{var_name}' no encontrada. Skip.")
                continue
            var_name = candidates[0]
            print(f"[INFO] Usando fallback: {label} -> {var_name}")

        print(f"\n[INFO] Procesando {label} ({var_name})…")
        da = ds[var_name]

        # Downsample con block-mean (coarsen)
        kw = {dim: DOWNSAMPLE for dim in da.dims if dim in ("x", "y")}
        da_small = da.coarsen(boundary="trim", **kw).mean()
        print(f"  Shape original: {da.shape} -> downsampled: {da_small.shape}")

        # CRS: BedMap3 es EPSG:3031 (Antarctic Polar Stereographic, true scale -71)
        if not da_small.rio.crs:
            da_small = da_small.rio.write_crs("EPSG:3031")
        # Convertir a int16 (los rangos de elevación caben: -8000 a +5000 m)
        arr = da_small.values
        nodata = -32768
        arr_int = np.where(np.isnan(arr), nodata, arr).astype("int16")
        da_int = da_small.copy(data=arr_int).rio.write_nodata(nodata)

        out_tif = OUT_DIR / f"bedmap3_{label}_5km.tif"
        da_int.rio.to_raster(
            out_tif,
            driver="COG",
            compress="DEFLATE",
            predictor=2,
            dtype="int16",
        )
        size_mb = out_tif.stat().st_size / 1024**2
        print(f"  [OK] {out_tif.name}: {size_mb:.1f} MB")

    print("\n[DONE] BedMap3 procesado a COGs servibles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
