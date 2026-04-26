# Contextos Geológicos · Chile & Antártica

Visor interactivo de los **22 Contextos Geológicos Chilenos** (Mourgues, Schilling & Castro 2012/2016) y los **9 SCAR Antarctic Geological Frameworks** (ATCM XLIII, 2021), construido sobre el Mapa Geológico de Chile 1:1.000.000 (SERNAGEOMIN) y el SCAR/GNS GeoMAP v2022.08 (Cox et al. 2023).

🌐 **Dashboard público:** https://mendozavolcanic.github.io/contextos-geologicos/ *(GitHub Pages, redeploya automático en cada push)*

## Qué hace

- **Mapa de contextos** (Leaflet) — cambia entre Chile (Web Mercator) y Antártica (Polar Stereographic EPSG:3031), con mapa geológico base + polígonos de contextos.
- **Globo 3D** (CesiumJS) — vista esférica con todas las capas superpuestas, sin token Ion.
- **Léxico estratigráfico** — 8 entradas hand-curadas (parser automático en TODO).

## Datos

| Capa | Fuente | Procesamiento |
|---|---|---|
| Mapa Geológico de Chile 1:1M | SERNAGEOMIN (18.935 polígonos) | Disuelto por código `geo` → 149 unidades coloreadas por era |
| 22 Contextos Mourgues | Mourgues 2012/2016 + Mapa al Millón | Reglas era+período+composición+latitud → 15 contextos asignados a polígonos del mapa oficial |
| 9 SCAR Frameworks | SCAR ATCM XLIII Att. A (2021) + GeoMAP | Reglas SIMPCODE → Framework → 6 frameworks asignables desde GeoMAP |
| 21 clases SIMPCODE | Cox et al. 2023, Tabla 3 | Disuelto desde 99.080 polígonos |

## Estructura

```
.
├── app/                          # Dashboard estático (sin build)
│   ├── index.html
│   ├── app.js                    # Mapa Leaflet
│   ├── globo.js                  # Globo Cesium
│   ├── styles.css
│   └── data/
│       ├── chile_contextos.geojson      # 22 contextos chilenos (5 MB)
│       ├── chile_geologico.geojson      # Base 1:1M (7 MB)
│       ├── antartica_frameworks.geojson # 9 SCAR Frameworks (16 MB)
│       ├── antartica_simplecode.geojson # 21 SIMPCODE GeoMAP (17 MB)
│       ├── contextos.geojson            # 19 CGT Aysén (Benado 2020)
│       └── lexico.json
├── scripts/                      # Pipelines reproducibles (geopandas)
│   ├── build_chile_contextos.py
│   ├── build_chile_geologico.py
│   ├── build_antartica_frameworks.py
│   ├── build_antartica_geojson.py
│   └── build_lexico.py
├── docs/
│   ├── pdfs/                     # Informes-fuente del léxico SERNAGEOMIN
│   ├── bibliografia/
│   │   ├── 01_contextos_geologicos/  # Benado 2019, Benado 2020, SCAR ATCM43
│   │   ├── 02_tesis_regionales/      # Sepúlveda 2022, Gálvez 2024
│   │   └── 03_mapas_base/            # Cox 2023, Mapa al Millón, Antártico BND
│   ├── mapas/                    # Datasets crudos (gitignored, ver PENDIENTES)
│   └── notas/
│       ├── contextos_chilenos_22_mourgues.md  ← lista oficial 22 contextos
│       ├── contextos_antarticos.md             ← lista oficial 9 frameworks
│       ├── contextos_aysen_benado_2020.md
│       ├── mapping_rules_log.md                ← auditoría del mapping
│       └── scar_categorias.md
├── DEPLOY.md                     # Cómo deployar a Cloudflare Pages / Netlify
└── README.md
```

## Reproducir el procesamiento

Requiere Python 3.12 + geopandas, fiona, pyogrio.

```bash
# 1. Bajar los datasets pesados a docs/mapas/{chile,antartica}/ (ver docs/bibliografia/PENDIENTES_DESCARGA.md)
# 2. Generar las capas
python scripts/build_chile_geologico.py        # → app/data/chile_geologico.geojson
python scripts/build_chile_contextos.py        # → app/data/chile_contextos.geojson
python scripts/build_antartica_geojson.py      # → app/data/antartica_simplecode.geojson
python scripts/build_antartica_frameworks.py   # → app/data/antartica_frameworks.geojson
```

Los GeoJSON resultado están commiteados al repo, así que para solo correr el dashboard:
```bash
cd app && python -m http.server 8000   # → http://localhost:8000
```

## Estado del proyecto

### Lo conseguido
- ✅ Listas oficiales completas de los 22 contextos chilenos y los 9 frameworks SCAR antárticos
- ✅ Polígonos georreferenciados nacionales para 15/22 contextos chilenos (vía mapping algorítmico)
- ✅ Polígonos antárticos para 6/9 frameworks SCAR
- ✅ Capa base geológica (mapa al millón + GeoMAP) bajo los contextos
- ✅ Vista 3D Cesium con todas las capas
- ✅ Proyección polar EPSG:3031 para Antártica
- ✅ Repo público, GitHub Pages auto-deploy

### Lo que requiere validación humana (Felipe / equipo SERNAGEOMIN)
- Validación / refrendo institucional de los 22 contextos chilenos (la lista *no ha sido validada* por la comunidad geológica nacional según Benado et al. 2019)
- Revisión de las **reglas de mapping** en `scripts/build_chile_contextos.py` función `assign_contexto()` — son heurísticas era+período+composición que pueden corregirse polígono-a-polígono
- Contextos chilenos NO mapeables por reglas: #6 IO (islas oceánicas), #16 BC (borde costero), #21 TEC (estructuras), #22 Lss (impactos) — requieren info espacial/estructural adicional
- Frameworks antárticos NO mapeables solo desde SIMPCODE: F5 (K-Pg, sitio puntual), F7 (meteoritos), F8 (subglacial)

### TODO técnico
- Mejorar parser del léxico (`scripts/build_lexico.py`) para extraer las ~500 unidades de los 2 PDFs SERNAGEOMIN
- Cargar el SHP del Inventario Nacional de Geositios (cuando lo tengamos) como capa de puntos
- Dataset Mourgues 2012 original (SSL caducado, ver `docs/bibliografia/PENDIENTES_DESCARGA.md`) para validar nuestras reglas
- Visor 3D de superficies tipo Leapfrog para acuíferos (idea aparte de Felipe)

## Licencias y atribuciones

- **App y código:** MIT
- **Datos:** SERNAGEOMIN (uso académico), SCAR/GNS GeoMAP CC-BY 4.0, Cox et al. 2023 CC-BY 4.0
- **Bibliografía:** PDFs en `docs/bibliografia/` son referenciales — derechos de los autores originales
