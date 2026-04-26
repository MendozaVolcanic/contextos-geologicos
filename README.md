# Contextos Geológicos · Chile & Antártica

Plataforma web para visualizar contextos geológicos chilenos y antárticos, y consultar el léxico estratigráfico de unidades de roca. Inspirada en el [BGS Geology Viewer](https://www.bgs.ac.uk/map-viewers/bgs-geology-viewer/) y el [BGS Lexicon](https://webapps.bgs.ac.uk/lexicon/).

## Estructura

```
.
├── app/                                  # Aplicación web (HTML + Leaflet + JS vanilla, sin build)
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── data/
│       ├── contextos.geojson             # 19 CGT Aysén + 4 antárticos
│       └── lexico.json                   # Léxico estratigráfico (muestra inicial)
├── docs/
│   ├── pdfs/                             # Informes-fuente del léxico SERNAGEOMIN + texto extraído
│   ├── bibliografia/
│   │   ├── 01_contextos_geologicos/      # Benado 2019, Benado et al. 2020
│   │   ├── 02_tesis_regionales/          # Sepúlveda 2022, Gálvez 2024
│   │   ├── 03_mapas_base/                # Mapa al Millón, Mapa Antártico BND
│   │   └── PENDIENTES_DESCARGA.md
│   ├── mapas/                            # Datos geoespaciales
│   │   ├── chile/                        # SHP + GeoJSON Mapa Geológico de Chile
│   │   └── antartica/                    # SCAR GeoMAP v2022.08 (ESRI + Google Earth)
│   └── notas/
│       ├── contextos_aysen_benado_2020.md  # Tabla de los 19 CGT
│       └── scar_categorias.md
└── README.md
```

## Cómo correr

La app es estática pero necesita un servidor HTTP por los `fetch` a `/data`. Desde la carpeta del proyecto:

```bash
cd app
python -m http.server 8000
```

Y abrir http://localhost:8000

## Estado del proyecto

### Hecho
- [x] Estructura del proyecto, bibliografía clasificada en subcarpetas temáticas
- [x] Texto de los dos informes SERNAGEOMIN extraído a `docs/pdfs/lexico*.txt`
- [x] **19 Contextos Geológicos Temáticos de Aysén** (Benado et al. 2020) integrados al mapa, con sus unidades representativas
- [x] 4 contextos antárticos derivados de SCAR EG-GEOCON
- [x] Filtros por región / tipo / edad, panel de detalle, navegación cruzada léxico ↔ mapa
- [x] Léxico con buscador y filtro por período (8 entradas iniciales)
- [x] Bibliografía descargada: Benado 2019 (Geoconservation Chile), Benado 2020 (Aysén), Sepúlveda 2022, Gálvez 2024, Mapa al Millón, Mapa Antártico BND
- [x] Datos geoespaciales descargados: SHP+GeoJSON Mapa Geológico de Chile, SCAR GeoMAP Antártica v2022.08 (ESRI + Google Earth)

### Pendiente
Ver [`docs/bibliografia/PENDIENTES_DESCARGA.md`](docs/bibliografia/PENDIENTES_DESCARGA.md). El único bloqueante real es **Mourgues, Schilling & Castro (2012)** — pero los 19 CGT de Aysén derivan de ese trabajo, así que tenemos buena base mientras tanto.

### Próximos pasos sugeridos
1. **Cargar Mapa Geológico de Chile** como capa base bajo los CGT (el GeoJSON pesa 60 MB; conviene tilear con `tippecanoe` → `pmtiles` o filtrar columnas y simplificar geometría con `mapshaper`).
2. **Parser de los PDFs SERNAGEOMIN** → léxico completo. El texto ya está extraído; campos siguen el patrón `Edad:`, `Litología.`, `Distribución.`, `Definición:`.
3. **Cargar SCAR GeoMAP Antártica** como capa antártica (la geodatabase ESRI requiere convertir a GeoJSON con GDAL/ogr2ogr).
4. **Polígonos georreferenciados reales para los CGT** (no los bounding boxes placeholder actuales).
5. **Carga del SHP del Inventario Nacional de Geositios** como capa de puntos.
6. **Visor 3D de superficies** (idea 5 — desafío Leapfrog-like) — proyecto separado.
