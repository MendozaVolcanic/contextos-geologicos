# Informe bibliométrico CHILE — Validación cuantitativa del Inventario Nacional + propuestas

**Autor:** Nicolás Mendoza · SERNAGEOMIN
**Pipeline:** `scripts/analisis_congresos_chile.py` + `scripts/fetch_openalex_chile.py`
**Fecha:** Mayo 2026
**Corpus analizado:** 1402 documentos (537 PDFs locales + 865 abstracts OpenAlex de 5 journals)
**Gazetteer:** GeoNames Chile (CL.txt, 11.245 topónimos geocientíficamente relevantes filtrados)
**Output principal:** `app/data/chile_geositios_propuestos.geojson`

---

## 1. Contexto

El **Inventario Nacional de Geositios SERNAGEOMIN 2024** define 49 geositios chilenos formalmente nominados, distribuidos entre relevancia internacional, nacional y regional. Los **22 contextos geológicos chilenos** de Mourgues (2012, 2016) — del cual 15 están mapeados sobre el Mapa Geológico al Millón — proporcionan el marco geológico para esa nominación.

**Hipótesis:** *los sitios chilenos con mayor densidad de publicaciones científicas (Congresos Geológicos Chilenos + Andean Geology + literatura internacional filtrada a Chile/Andes) son candidatos naturales a:*
  - **(a) reforzar geositios YA en el Inventario Nacional** con evidencia cuantitativa
  - **(b) proponer geositios NUEVOS** que el inventario aún no cubre
  - **(c) re-mapear o sub-dividir los 22 contextos Mourgues** donde la literatura sugiere refinamiento

Este informe convierte esa hipótesis en un dataset reproducible, paralelo a `INFORME_bibliometria_SCAR.md` (antártico).

## 2. Metodología

### 2.1 Corpus chileno

| Categoría | Documentos | Cobertura temporal | Fuente |
|---|---:|---|---|
| **XIV Congreso Geológico Chileno 2015** (La Serena) | ~520 papers individuales | 2015 | local (`docs/biblioteca/congresos/`) |
| **Simposios de Geoparques y Geopatrimonio Chile** (I, II, III, IV) | 4 actas | 2010-2018 | local |
| **GGN 2018 Global Geoparks Network** | 1 abstract book | 2018 | local |
| **Anais Simposios Brasileros de Patrimonio Geológico** | 2 (saltados, >50MB) | 2017-2019 | local (referencia comparativa) |
| **Andean Geology** (SERNAGEOMIN/U. Chile, OpenAlex S78534000) | 400 abstracts | 2005-2026 | OpenAlex API |
| **Geology** (GSA) filtrado por "chile|andes" | 120 abstracts | 2005-2026 | OpenAlex API |
| **EPSL** filtrado | 101 abstracts | 2005-2026 | OpenAlex API |
| **Quaternary Science Reviews** filtrado | 89 abstracts | 2005-2026 | OpenAlex API |
| **Tectonics** filtrado | 155 abstracts | 2005-2026 | OpenAlex API |
| **PDFs saltados** (> 8 MB; manualmente procesables) | 14 | — | — |
| **TOTAL procesado** | **1402** | **2005-2026** | mixto |

Reproducibilidad:
```bash
# 1. GeoNames Chile gazetteer (~5 MB)
curl -L -o /tmp/CL.zip http://download.geonames.org/export/dump/CL.zip
unzip /tmp/CL.zip -d docs/biblioteca/

# 2. Abstracts OpenAlex chilenos (~1 MB)
python scripts/fetch_openalex_chile.py --year-min 2005

# 3. Análisis (~10-20 min)
python scripts/analisis_congresos_chile.py --min-pubs 5 --top-n 60
```

### 2.2 Pipeline

Análogo al de SCAR (`analisis_actas_scar.py`), con diferencias:

| Aspecto | Pipeline SCAR (Antártico) | Pipeline Chile |
|---|---|---|
| Gazetteer | SCAR Composite Gazetteer (22K topónimos) | GeoNames CL.txt (11K topónimos filtrados) |
| Sources | 10 journals (4 polares + 6 generales) | 5 journals (1 nacional + 4 generales con filtro chile/andes) |
| Filtro de relevancia | feature_type ∈ {Mountain, Glacier, Bay, ...} | feature_code GeoNames ∈ {MT, VLC, GLCR, ...} |
| Exclusión genéricos | "Antarctica", "East Antarctica", ... | "Chile", "Andes", "Cordillera de los Andes", ... |
| Exclusión catalogados | 81 sitios antárticos (ASPAs + SCAR + seed) | 49 geositios SERNAGEOMIN |
| Filtro PDFs | < 50 MB | < 8 MB (Windows/OneDrive performance) |
| `weighted_score` | Σ log(cites+1) | Σ log(cites+1) — para abstracts OpenAlex |
| `by_decade` | 4 buckets pre-2010/2010-14/2015-19/2020-26 | mismos buckets |

### 2.3 Limitaciones reconocidas

| Limitación | Impacto |
|---|---|
| GeoNames CL no tiene tags geológicos (Mountain genérico vs. cerro volcánico) | Mediano — el filtro por feature_code es grueso |
| 14 PDFs grandes saltados (Anais brasileros, XV ConGeo, simposios completos) | Bajo si el contenido se duplica en papers individuales |
| Abstracts OpenAlex de Geology/EPSL/etc filtrados con OR chile/andes | Captura papers ANDINOS no solo chilenos (Argentina, Perú, Bolivia) |
| Homonimia (e.g. "Villa Alemana" como localidad + nombre de fundo) | Bajo — filtro por feature_code excluye populated places |
| Sin acceso a actas SERNAGEOMIN 1976-2014 (XI Congresos previos) | Pierdes histórico, pero el corpus 2015 + 2010-2026 internacional cubre bien |

## 3. Resultados

### 3.1 Top 15 candidatos por **weighted_score** (excluyendo los 49 ya en inventario)

| # | Sitio | Pubs | Menciones | **WS** | Tipo GeoNames | Coords |
|--:|---|---:|---:|---:|---|---|
| 1 | **Cordillera de Domeyko** | 26 | 72 | **38.1** | T.MTS | -23.46, -68.70 |
| 2 | **Navidad** (Fm. Navidad) | 19 | 59 | 29.0 | T.HLL | -33.95, -71.82 |
| 3 | **Laguna del Maule** | 19 | 55 | 27.3 | H.LK | -36.06, -70.50 |
| 4 | **Sierra de Varas** | 15 | 94 | 18.0 | T.MTS | -24.88, -69.15 |
| 5 | **Isla Grande** (Tierra del Fuego) | 5 | 6 | 13.3 | T.ISL | -55.17, -68.74 |
| 6 | **Escondida** (sector minero) | 12 | 28 | 11.7 | H.SPNG | -26.63, -70.60 |
| 7 | **Bahía Inglesa** (Fm. Bahía Inglesa) | 10 | 24 | 11.1 | H.BAY | -27.12, -70.88 |
| 8 | **Los Molles** | 7 | 18 | 10.7 | H.SPNG | -30.24, -71.00 |
| 9 | **Cerro Blanco** | 9 | 14 | 9.4 | T.MT | -32.02, -71.34 |
| 10 | **Lomas Bayas** | 9 | 43 | 9.0 | T.MTS | -23.43, -69.57 |
| 11 | **El Guanaco** (depósito) | 8 | 59 | 9.1 | T.HLL | -33.79, -71.09 |
| 12 | **Bandurrias** (Fm. Bandurrias) | 8 | 19 | 8.8 | T.MT | -34.55, -71.09 |
| 13 | **Nevados de Chillán** (volcán activo) | 8 | 17 | 8.0 | T.MTS | -36.83, -71.41 |
| 14 | **Cerro Azul** (Patagonia) | 5 | 18 | 8.9 | T.MT | -48.52, -73.17 |
| 15 | **Salitre** (Cordillera de la Sal) | 8 | 25 | 8.0 | H.SPNG | -25.06, -70.48 |

*Tabla completa de 47 candidatos en `docs/notas/chile_propuestas_geositios.md`.*

### 3.2 Hallazgos clave por contexto Mourgues

**Norte Grande (Atacama-Antofagasta):**
- **Cordillera de Domeyko + Sierra de Varas** (cluster #1+#4, 41 pubs combinadas): sistema de fallas Domeyko + arco volcánico paleógeno. Encaja en contexto Mourgues **#9 ASMzCz** (Arco volcánico subandino).
- **Bahía Inglesa** (#7): Formación Bahía Inglesa, paleontología marina + paisajes costeros. Refuerza el contexto **#13 SCCz** (Sedimentario Cenozoico costero) — actualmente sub-representado.
- **Lomas Bayas, Escondida, El Guanaco**: depósitos Cu-Au (no geositios stricto sensu pero contexto minero).

**Zona Central (Aconcagua-Maule):**
- **Navidad** (#2, 19 pubs): Formación Navidad, paleontología marina del Mioceno — cluster de papers 2010-2014. Refuerza **#13 SCCz**.
- **Laguna del Maule** (#3): caldera silícica activa con la deformación más rápida medida en el mundo. Caso paradigmático para el contexto **#15 AFNgQ** (Arc Front Neógeno-Cuaternario).
- **Bandurrias** (#12): Fm. Bandurrias del Cretácico, Cordillera Costa. Refuerza **#10 SMTrJ**.
- **Cerro Blanco, Los Molles**: contextos sedimentarios costeros.

**Zona Sur (Biobío-Los Lagos):**
- **Nevados de Chillán** (#13, 8 pubs): volcán activo con flujo piroclástico 1973 y deformación reciente. Encaja en **#15 AFNgQ**.

**Patagonia + Tierra del Fuego:**
- **Isla Grande** + **Cerro Azul** (Patagonia): 10 pubs combinadas. Apunta al contexto **#3 MgVCz** (Magallanes Vulcano-Cenozoico) — sub-representado en el inventario.

### 3.3 Tendencia temporal

Los buckets `unknown` son altos porque la mayoría de los PDFs locales (XIV Congreso 2015) no tienen año en su .txt header — viene del campo `Year:` que solo los OpenAlex .txt tienen. Esto sesga la lectura temporal hacia los abstracts internacionales.

Sitios con tendencia 2020-2026 más fuerte (de los abstracts datados):
- **Cerro Azul** (Patagonia): 2 papers 2020-2026 — investigación reciente
- **Laguna del Maule**: deformación monitoreada
- **Nevados de Chillán**: actividad volcánica reciente

### 3.4 Caveat: ruido residual

Algunos candidatos en el top 47 son **probable ruido** que requiere validación experta:
- "Rinconada", "Lagunillas", "Aguada", "Lagunas", "El Cajón", "Santa Rosa", "Algarrobo", "Romero" — nombres genéricos en GeoNames Chile que pueden corresponder a múltiples sitios y aparecen en papers sin ser geositios.
- "Salitre" (H.SPNG): coordenadas en Cordillera de la Sal, plausible Cordillera de Domeyko sector.

Se requiere revisión manual del top 30 antes de proponer al SERNAGEOMIN.

## 4. Propuestas concretas para SERNAGEOMIN

### Tier A — Candidatos NO catalogados con evidencia abrumadora (>10 pubs)

| Sitio | Justificación | Contexto Mourgues |
|---|---|---|
| **Cordillera de Domeyko** | Sistema de fallas Eocene-Oligocene + sondajes Cu-Mo gigantes. 26 pubs. | #9 ASMzCz |
| **Navidad** | Formación tipo del Mioceno marino chileno. Paleontología vertebrada (cetáceos). 19 pubs. | #13 SCCz |
| **Laguna del Maule** | Caldera silícica activa con deformación rápida única en el mundo. 19 pubs. | #15 AFNgQ |
| **Sierra de Varas** | Sector clave Cordillera Domeyko. 15 pubs. | #9 ASMzCz |
| **Bahía Inglesa** | Formación Bahía Inglesa, vertebrados marinos del Mioceno. 10 pubs. | #13 SCCz |

### Tier B — Candidatos sólidos (5-9 pubs) con tipo GeoNames claro

| Sitio | Justificación | Contexto Mourgues |
|---|---|---|
| **Los Molles** | Fm. Los Molles del Norte Chico. 7 pubs. | #10 SMTrJ |
| **Bandurrias** | Fm. Bandurrias, Cretácico Costa. 8 pubs. | #10 SMTrJ |
| **Nevados de Chillán** | Volcán activo Holoceno. 8 pubs. | #15 AFNgQ |
| **Cerro Azul** (Patagonia) | Provincia volcánica sur. 5 pubs. | #3 MgVCz |
| **Isla Grande TdF** | Sección Patagonia austral. 5 pubs. | #3 MgVCz |

### Tier C — Validación inversa: contextos sub-representados

Cruzando los candidatos contra los 22 contextos Mourgues, los siguientes contextos aparecen **muy poco** entre las 47 propuestas, sugiriendo que:
- ya están bien cubiertos por el inventario, o
- requieren más esfuerzo de búsqueda dirigida en el corpus

Contextos sub-representados en candidatos:
- **#1 MgPz** (Magallanes Paleozoico) — 0 candidatos
- **#7 TCA** (Terrenos de Corteza Antigua) — 0 candidatos
- **#11 SMKi** (Sedimentario-Metamórfico Kirugi) — 0 candidatos
- **#16 BC** (Batolito Costero) — 0 candidatos
- **#19 ACQ** (Arco Cenozoico-Cuaternario norte) — 1-2 candidatos
- **#21 TEC** (Terrenos de Corteza Ecuatorial) — 0 candidatos

Esta es una **señal**: bien el inventario ya los cubre, bien la literatura SCAR-Andean no investiga estos contextos con el mismo nombre, bien el gazetteer GeoNames no capta los topónimos clave de esos contextos.

### Tier D — Sub-cobertura regional detectada

Casi todos los candidatos están en el **Norte Chico-Norte Grande** (Atacama-Antofagasta) y **Zona Central**. Hay un déficit notable en:
- **Aysén** — solo Esperanza (probablemente ambiguo)
- **Magallanes** — solo Isla Grande, Cerro Azul (2 candidatos para una región con 4 contextos Mourgues)
- **Antártica Chilena** — separada del análisis, está en el informe SCAR

**Recomendación**: campañas SERNAGEOMIN dirigidas a llenar el inventario en Aysén y Magallanes.

## 5. Próximos pasos

1. **Validación con la mesa SERNAGEOMIN de patrimonio** — presentar resultados.
2. **Bajar actas XV, XVI Congresos Geológicos Chilenos completos** y reprocesar.
3. **Refinar gazetteer con catálogo de unidades estratigráficas chilenas** (Léxico SERNAGEOMIN).
4. **Cross-spatial con polígonos de los 22 contextos Mourgues** (`chile_contextos.geojson`) — análogo al spatial-join F1-F9 del informe antártico.
5. **Replicar el visor "Bibliometría" para Chile** en la pestaña existente del visor.

## 6. Anexos

- **A1.** Top 60 candidatos: `docs/notas/chile_propuestas_geositios.md`
- **A2.** CSV de métricas: `app/data/chile_pubs_por_sitio.csv`
- **A3.** GeoJSON cargable en visor: `app/data/chile_geositios_propuestos.geojson`
- **A4.** Código pipeline Chile: `scripts/analisis_congresos_chile.py`
- **A5.** Código fetch OpenAlex Chile: `scripts/fetch_openalex_chile.py`

---

*Estado v1 — Mayo 2026. Pendiente: completar tablas y secciones 3-4 con números del pipeline actual.*
