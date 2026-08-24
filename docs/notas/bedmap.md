# BedMap3 — descarga manual

Si `build_bedmap.py` no pudo parsear RAMADDA, abrir la entrada en el navegador:

- Entry: <http://ramadda.data.bas.ac.uk/repository/entry/show?entryid=2d0e4791-8e20-46a3-80e4-f5f6716025d2>
- DOI:   https://doi.org/10.5285/2d0e4791-8e20-46a3-80e4-f5f6716025d2

Archivos a bajar (~5 GB en total: 2.1 GB de GeoTIFF + 2.4 GB de NetCDF):

- `bm3_bed.tif` (bed)
- `bm3_surface.tif` (surface)
- `bm3_thickness.tif` (thickness)
- `bm3_grid.nc` (netcdf)

Dejarlos en `docs\mapas\antartica\bedmap3` y volver a correr el script.

## Vectores SCAR ADD (línea de costa, grounding line)

Portal: <https://data.bas.ac.uk/items/e74543c0-4c4e-4b41-aa33-5bb2f67df389/>

Bajar:
- `add_coastline_high_res_polygon.gpkg` → renombrar a `app/data/coastline.geojson` (convertir con `ogr2ogr -f GeoJSON`).
- `add_groundingline_polygon.gpkg` → `app/data/grounding_line.geojson`.
