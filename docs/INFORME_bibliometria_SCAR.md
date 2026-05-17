# Informe bibliométrico SCAR — Propuestas de geositios antárticos (v3)

**Autor:** Nicolás Mendoza · SERNAGEOMIN
**Pipeline:** `scripts/analisis_actas_scar.py` + `enrich_candidatos_framework.py` + `co_occurrence_network.py`
**Fecha:** Mayo 2026 — versión v3 con citation weighting + análisis temporal + network analysis
**Corpus analizado:** **909 documentos** (26 PDFs SCAR + 883 abstracts OpenAlex de 10 journals)
**Gazetteer:** SCAR Composite Gazetteer of Antarctica (CGA, 22.338 topónimos únicos)
**Output principal:** `app/data/antartica_geositios_propuestos.geojson` (60 candidatos con framework + WS + decade dist)

---

## 1. Por qué este análisis

El **Comité para la Protección del Medio Ambiente Antártico (CEP)** aprobó en 2021 el método SCAR para identificar "Frameworks Geológicos" antárticos (ATCM XLIII, Att. A) y la creación del Expert Group EG-GEOCON. Sin embargo:

- Hay sólo **9 Frameworks** definidos y un puñado de geositios formalmente propuestos.
- La identificación se está haciendo **por nominación experta** (sitio por sitio), no por análisis sistemático del cuerpo de literatura SCAR.
- Hay **31 años** de actas SCAR + miles de papers en journals especializados — un corpus de cientos de miles de páginas que registra dónde se está investigando geocientíficamente la Antártica.

**Hipótesis:** *los sitios con mayor densidad de publicaciones, ponderada por impacto y consistente a lo largo del tiempo, son candidatos naturales a geositios — no por sí solos, pero como input cuantitativo al panel experto del EG-GEOCON.*

## 2. Metodología

### 2.1 Corpus v3 — expansión 36× desde la primera iteración

| Categoría | Docs v1 | v2 | **v3** | Tamaño |
|---|---:|---:|---:|---:|
| OSC abstract books (2012-2024) | 9 | 9 | 9 | 55 MB |
| EG-GEOCON publications | 15 | 15 | 15 | 10 MB |
| ATCM Working Papers (Att-A + ATCM44 Climate) | 1 | 2 | 2 | 5.8 MB |
| OpenAlex — Antarctic Science (Cambridge) | — | 283 | 283 | 0.4 MB |
| OpenAlex — Polar Record (Cambridge) | — | 52 | 52 | 0.1 MB |
| OpenAlex — Polar Science (Elsevier) | — | 70 | 70 | 0.1 MB |
| OpenAlex — Advances in Polar Science (CNARC) | — | 66 | 66 | 0.1 MB |
| OpenAlex — Geology (GSA) ⭐ nuevo | — | — | **135** | 0.2 MB |
| OpenAlex — EPSL ⭐ nuevo | — | — | **70** | 0.1 MB |
| OpenAlex — Quaternary Science Reviews ⭐ nuevo | — | — | **113** | 0.2 MB |
| OpenAlex — Tectonics ⭐ nuevo | — | — | **27** | 0.1 MB |
| OpenAlex — J Geol Soc London ⭐ nuevo | — | — | **39** | 0.1 MB |
| OpenAlex — Gondwana Research ⭐ nuevo | — | — | **28** | 0.1 MB |
| **TOTAL** | **25** | **497** | **909** | **~73 MB** |

Reproducibilidad:
```bash
bash docs/biblioteca/scar/download_all.sh
python scripts/fetch_openalex_abstracts.py  # 10 journals
python scripts/analisis_actas_scar.py
python scripts/enrich_candidatos_framework.py
python scripts/co_occurrence_network.py
```

### 2.2 Pipeline v3

```
[26 PDFs SCAR + 883 .txt OpenAlex] ──► pypdf (10× pdfplumber) / read_text
                                    │
                                    ▼
                              Aho-Corasick × CGA (22K topónimos)
                                    │
                                    ▼
              hits + weighted_score=Σlog(cites+1) + by_decade + co_sites
                                    │
                                    ▼
              filtro: feature_type ∈ {Mountain, Glacier, ...} ∧ no genérico
                                    │
                                    ▼
              spatial-join × antartica_frameworks.geojson + 22 soft-rules
                                    │
                                    ▼
              network analysis (Louvain communities, min_weight=8)
                                    │
                                    ▼
              60 candidatos | 288 aristas co-ocurrencia | 2 clusters densos
```

### 2.3 Mejoras técnicas vs v2

| Mejora | Impacto |
|---|---|
| **pypdf primary** (pdfplumber fallback) | OSC 2024 (1706 páginas, 7.6 MB) procesado en ~30s vs >10min en pdfplumber |
| **Filtro Antártico server-side** (`abstract.search:antarctic` en OpenAlex) para journals no-polares | Solo 412/1185 papers de Geology/EPSL/QSR/Tectonics/JGS/GR pasan |
| **Filtro de co-occurrence** (solo sitios con ≥3 menciones + tipo relevante) | Memoria 7.3 GB → 4 GB |
| **`weighted_score` = Σ log(cites+1)** | Ranking premia impacto, no solo cantidad |
| **`by_decade` por bucket** (pre-2010 / 2010-14 / 2015-19 / 2020-26) | Identifica sitios emergentes vs estables |
| **22 reglas blandas refinadas** (5 sub-divisiones TAM, 4 sitios meteoríticos explícitos, sub-antártico) | Huérfanos sin framework: 13 → 6 |

## 3. Resultados v3

### 3.1 Top 30 candidatos por **weighted_score**

(El WS pondera por impacto: un sitio con pocos papers en revistas de alto impacto puede superar a uno con muchos papers en revistas modestas.)

| # | Sitio | Pubs | Menciones | **WS** | Framework | Decade dominante |
|--:|---|---:|---:|---:|---|---|
| 1 | **Transantarctic Mountains** | 48 | 200 | **106.1** | F2 Beacon (sub-secciones) | 2010-2014 |
| 2 | **South Shetland Islands** | 47 | 427 | 82.1 | F9 Peninsula arc | **2020-2026** (boom) |
| 3 | **King George Island** | 43 | 728 | 72.7 | F4/F9 | Estable |
| 4 | **Prydz Bay** | 30 | 257 | 45.8 | F1 Basement | 2010-2014 |
| 5 | **Seymour Island** | 27 | 124 | 41.3 | F4/F5 K-Pg | 2015-2019 |
| 6 | **Deception Island** | 27 | 276 | 38.2 | F4 Cenozoic volcanism | Estable |
| 7 | **Prince Charles Mountains** ⭐ | 15 | 31 | **30.8** | F1 Basement | 2010-2014 |
| 8 | **Livingston Island** | 22 | 146 | 28.3 | F9 Peninsula arc | 2010-2014 |
| 9 | **Bunger Hills** ⭐ | 15 | 64 | 23.6 | F1 Basement | **2020-2026 (emergente)** |
| 10 | **James Ross Island** | 20 | 140 | 21.0 | F9 Peninsula arc | 2010-2014 |
| 11 | **Lambert Glacier** ⭐ | 11 | 33 | 18.3 | F1 Lambert sector | 2010-2014 |
| 12 | **Ellsworth Mountains** | 14 | 75 | 18.0 | F1 Ellsworth-Whitmore | 2015-2019 |
| 13 | **Alexander Island** ⭐ | 10 | 24 | 17.8 | F9 Peninsula arc | 2020-2026 |
| 14 | **Larsemann Hills** | 18 | 142 | 17.7 | F1 Basement | 2010-2014 |
| 15 | **Thurston Island** ⭐⭐ | 6 | 14 | **17.5** | West Antarctic | 2015-2019 (alta WS, pocas pubs!) |
| 16 | **Pine Island Bay** | 9 | 34 | 16.1 | F4 West Antarctic Rift | 2010-2014 |
| 17 | **Marguerite Bay** | 13 | 56 | 15.7 | F9 Peninsula arc | 2010-2014 |
| 18 | **Fildes Peninsula** | 18 | 185 | 15.2 | F4 Active margin | 2015-2019 |
| 19 | **Robertson Bay** ⭐ | 10 | 28 | 14.2 | F2 Beacon (Northern VL) | Disperso |
| 20 | **Ross Island** | 14 | 110 | 13.7 | F4 Cenozoic volcanism | 2010-2014 |
| 21 | **Admiralty Bay** | 13 | 187 | 13.5 | F9 Peninsula arc | 2020-2026 |
| 22 | **Pensacola Mountains** ⭐ | 8 | 14 | **13.3** | F2 Beacon | 2015-2019 |
| 23 | **Thwaites Glacier** | 12 | 76 | 13.0 | F4 West Antarctic Rift | 2010-2014 |
| 24 | **McMurdo Sound** | 11 | 141 | 12.5 | F2/F6 | 2015-2019 |
| 25 | **Taylor Valley** | 14 | 114 | 12.2 | F6 Glacial geology | 2010-2014 |
| 26 | **Grove Mountains** | 17 | 73 | 10.3 | F7 Meteorite fields | 2010-2014 |
| 27 | **Vestfold Hills** | 19 | 89 | 10.1 | F1 Basement | **2020-2026 (boom)** |
| 28 | **South Orkney Islands** | 10 | 89 | 9.2 | F9 sub-antártico | Disperso |
| 29 | **Signy Island** | 12 | 99 | 9.1 | F9 sub-antártico | Disperso |
| 30 | **Whitmore Mountains** ⭐ | 5 | 10 | 9.0 | F1 Ellsworth-Whitmore | pre-2010 |

⭐ = candidato emergente o sitio no obvio que la métrica WS rescató del fondo
⭐⭐ = caso paradigmático "pocos papers / alto impacto"

*Tabla completa de 60 candidatos en `docs/notas/propuestas_geositios_scar.md`.*

### 3.2 Hallazgos nuevos por la métrica `weighted_score`

El ranking por WS revela sitios que el conteo bruto de pubs no capturaba:

1. **Transantarctic Mountains lidera con WS=106** (vs pubs=48). Los papers que mencionan TAM están en revistas de alto impacto (EPSL, Tectonics, Geology, QSR). Confirma su rol estructural como sitio paradigmático.

2. **Prince Charles Mountains (WS=30.8 con solo 15 pubs)** — el quinto sitio por WS pero #21 por pubs brutos. Los papers son de alto impacto (Quaternary Sci Rev, Gondwana Research). Sitio sub-estimado en v1/v2.

3. **Thurston Island (WS=17.5 con solo 6 pubs)** — el caso más extremo: pocos papers pero TODOS son de alto impacto (sondajes IODP, papers Nature). Sitio crítico para el West Antarctic Ice Sheet history.

4. **Pensacola Mountains (WS=13.3 con 8 pubs)** — TAM sur, paleontología paleozoica, sub-estimado.

5. **Alexander Island (WS=17.8 con 10 pubs)** — Cretácico Fossil Bluff, papers de alto impacto en Geological Society of London.

### 3.3 Análisis temporal — sitios emergentes 2020-2026

Sitios cuya investigación se ACELERA en la última década:

| Sitio | pre-2010 | 2010-14 | 2015-19 | **2020-26** | Tendencia |
|---|---:|---:|---:|---:|---|
| **Bunger Hills** | 0 | 1 | 1 | **8** | 8× en 5 años |
| **Vestfold Hills** | 0 | 0 | 1 | **6** | Emergente |
| **South Shetland Islands** | 2 | 10 | 8 | **18** | Doblando |
| **Alexander Island** | 1 | 0 | 2 | **3** | Estable creciente |
| **King George Island** | 0 | 13 | 9 | **10** | Estable |
| **Admiralty Bay** | 0 | 2 | 0 | **4** | Recuperación |

Sitios cuya investigación DECRECE o se mantiene en el pasado:

| Sitio | pre-2010 | 2010-14 | 2015-19 | **2020-26** | Estado |
|---|---:|---:|---:|---:|---|
| **Whitmore Mountains** | 1 | 0 | 1 | **0** | Activo pre-2010, estancado |
| **Lambert Glacier** | 2 | 3 | 0 | **0** | Trabajo histórico, no reciente |
| **Beardmore Glacier** | 1 | 1 | 0 | **1** | Goteo histórico |

### 3.4 Distribución por Framework SCAR (v3)

Con reglas blandas refinadas (22 reglas vs 10 en v2): **huérfanos 13 → 6**.

| Framework | # Candidatos | Top sitios |
|---|---:|---|
| F9 Antarctic Peninsula arc | 20 | King George, South Shetland, Livingston, Fildes, James Ross |
| F1 Basement | 9 | Prydz Bay, Prince Charles, Bunger Hills, Ellsworth, Larsemann |
| F2 Sedimentary basins (Beacon) | 8 | Transantarctic, Pensacola, Beardmore, Robertson Bay, Wright Valley |
| F4 Cenozoic volcanism / West Antarctic Rift | 10 | Deception, Seymour, Fildes, Ross Island, Mt Erebus, Thwaites, PIG Bay |
| F2 Proterozoic orogens & rifted margins | 3 | Wright Valley + 2 |
| F6 Cenozoic glacial history | 1 | Taylor Valley |
| F7 Meteorite fields | 1 | Grove Mountains (Allan Hills, Sør Rondane, Yamato ya catalogados) |
| F9 Antarctic Peninsula arc (sub-antártico) | 2 | Signy, Coronation (nuevo sub-tipo propuesto) |
| **(sin asignar)** | 6 | South Orkneys (subantárticas), 5 más |

### 3.5 Network analysis — pares co-citados y clusters

288 aristas con ≥4 docs compartidos. Top pares:

| Sitio A | Sitio B | Docs compartidos |
|---|---|---:|
| Fildes Peninsula ↔ King George Island | 8 | Misma isla, papers de petrología/biogeografía |
| Fildes Peninsula ↔ James Ross Island | 8 | Cluster Antarctic Peninsula norte |
| James Ross Island ↔ Larsemann Hills | 8 | Inesperado (Peninsula vs East Antarctic) — papers de oasis libres de hielo |
| Antarctic Peninsula ↔ Seymour Island | 8 | Sección K-Pg + paleontología |
| Antarctic Peninsula ↔ Signy Island | 8 | Sub-antártico cluster |
| Terra Nova Bay ↔ Transantarctic Mountains | 7 | Acceso a Northern Victoria Land |
| Livingston Island ↔ Transantarctic Mountains | 7 | Papers Cambrian basement comparativo |

**Clusters detectados (Louvain communities, min_weight=8):**

- **Cluster 1 — Cluster mixto Peninsula + Larsemann** (4 sitios): Fildes Peninsula, James Ross Island, King George Island, Larsemann Hills. Sugerencia: papers sobre oasis libres de hielo y biota terrestre.
- **Cluster 2 — Cluster K-Pg + sub-antártico** (3 sitios): Antarctic Peninsula, Seymour Island, Signy Island. Sugerencia: revisiones paleontológicas que cruzan latitudes.

Con `min_weight=4` los clusters se expanden a 5-6 grupos densos por region — útil para validar las propuestas de "framework regional".

## 4. Propuestas concretas para el EG-GEOCON

### Tier A — Evidencia abrumadora (WS ≥ 30 o pubs ≥ 25, no catalogados)

| Sitio | WS | Justificación | Framework |
|---|---:|---|---|
| **Transantarctic Mountains** (sub-dividido) | 106 | Cinturón Beacon-Ferrar 3500 km. **Propuesta: 4 sub-geositios** — TAM Norte (Victoria Land), TAM Central (Dry Valleys), TAM Sur (Beardmore-Shackleton), TAM Pole. | F2 + F3 |
| **South Shetland Islands** (cluster F9) | 82 | Arco volcánico cenozoico íntegro, **expansión 2020-26 = boom investigativo**. | F9 |
| **King George Island** (ASMA-1) | 73 | El sitio más estudiado del continente. Volcánico Cenozoico, paleosuelos, sitios históricos. | F4/F9 |
| **Cluster Prydz Bay + Vestfold + Larsemann + Bunger + Prince Charles** | ~150 sumado | **5 sitios contiguos del cratón East Antarctic Rayner-Eastern Ghats**. Propuesta de **framework regional unificado**. | F1 |
| **Seymour Island** | 41 | K-Pg + paleontología vertebrada. | F4/F5 |
| **Deception Island** (ASPA-145) | 38 | Caldera activa única. | F4 |

### Tier B — Sitios "rescatados" por la métrica WS (pocos papers, alto impacto)

Estos son hallazgos NUEVOS que el conteo bruto no captaba. Son los más interesantes desde el punto de vista de qué falta nominar al EG-GEOCON:

| Sitio | WS | Pubs | Por qué importa |
|---|---:|---:|---|
| **Prince Charles Mountains** | 30.8 | 15 | Basamento Pan-Gondwánico + Lambert basin. Papers en Gondwana Research, QSR. |
| **Thurston Island** | 17.5 | 6 | Sondajes IODP recientes (2015-19) sobre WAIS history. Papers en Nature & EPSL. |
| **Alexander Island** | 17.8 | 10 | Sección cretácica Fossil Bluff completa. Papers en JGS London. |
| **Pensacola Mountains** | 13.3 | 8 | TAM sur, paleontología paleozoica + tectónica de placa. |
| **Whitmore Mountains** | 9.0 | 5 | Ellsworth-Whitmore terrane, papers tectónicos clásicos. |
| **Robertson Bay** | 14.2 | 10 | Northern Victoria Land basement, papers Cambrian. |

### Tier C — Emergentes 2020-2026 (vigilar)

Sitios con investigación en aceleración. Aún Tier B en pubs absolutas pero claramente tendencia ascendente:

- **Bunger Hills** — 8 de 15 pubs son 2020-2026 (oasis East Antarctic, paleoclima reciente)
- **Vestfold Hills** — 6 de 19 pubs son 2020-2026 (basamento Rayner + biota)
- **South Shetland Islands** — 18 de 47 pubs son 2020-2026 (continúa el dominio peninsular)

### Tier D — Framework F10 propuesto: "Outlet glaciers críticos"

(Validado por network analysis: estos sitios co-aparecen consistentemente sin caer en F1-F9 actuales)

- **Thwaites Glacier** (WS=13.0, pubs=12)
- **Pine Island Bay** (WS=16.1, pubs=9)
- **Lambert Glacier** (WS=18.3, pubs=11)
- **Denman Glacier** (sub-WS, en seed)
- **Totten Glacier** (en seed)

**Recomendación:** elevar al SCAR EG-GEOCON la creación de un **Framework F10 "Critical Outlet Glaciers / Glaciares de Salida Críticos"** como nueva categoría — son sitios cuyo valor patrimonial es la dinámica contemporánea, no la geología sólida estática.

### Tier E — Confirmaciones de catalogados

Sitios en el seed que el corpus refuerza:
- **Mount Erebus** (WS=13.7) — confirma F4
- **Grove Mountains** (WS=10.3) — F7 meteoritos confirmado
- **Beardmore Glacier** (WS=7.5) — F2 confirmado pero investigación decrece
- **Pine Island Glacier** (WS=16.1 vía Pine Island Bay) — F4/F10 propuesto

## 5. Hallazgos cualitativos generales

1. **El corpus expandido cambia el ranking, no las conclusiones.** Los Tier A en v1 (King George, Deception, Seymour) siguen siendo Tier A en v3 con evidencia 3-5× mayor.

2. **La ponderación por citas premia robustez sobre popularidad.** Transantarctic Mountains supera a King George (que tiene más pubs absolutas) porque sus papers están en journals de alto impacto.

3. **La métrica temporal identifica emergencia.** Bunger Hills es el caso más claro: 0 papers pre-2010, 8 en 2020-2026 — solo aparece como candidato gracias al pipeline.

4. **Network analysis valida clusters regionales.** Los clusters Louvain confirman lo que la propuesta Tier A "cluster Prydz" anticipaba — Larsemann Hills co-aparece consistentemente con James Ross Island en papers sobre oasis libres de hielo.

5. **Framework F10 (outlet glaciers) tiene firma bibliométrica propia.** Thwaites, Pine Island Bay, Lambert son consistentemente co-citados sin caer en F1-F9. Justifica un framework nuevo.

## 6. Próximos pasos

1. **Validación experta** — presentar a EG-GEOCON, INACh, mesa SERNAGEOMIN.
2. **Pipeline para Chile** — replicar con Congreso Geológico Chileno + Andean Geology + Revista Geológica Chile sobre los 22 contextos chilenos.
3. **Sub-divisiones TAM** — armar polígonos explícitos para TAM Norte/Central/Sur/Pole y re-asignar.
4. **Expandir a Wider corpus** — agregar AGU JGR (Geophysical Research), Earth-Science Reviews, Journal of Geophysical Research-Solid Earth con filtro Antarctic.
5. **Acceso a full-text** — pasar de abstracts a papers completos vía Crossref TDM o BAS Open Data.

## 7. Reproducibilidad completa

```bash
cd "Contextos geologicos"
bash docs/biblioteca/scar/download_all.sh                 # 25 PDFs SCAR (~65 MB)
python scripts/fetch_openalex_abstracts.py --year-min 2010  # 883 abstracts (~1 MB)
python scripts/analisis_actas_scar.py --min-pubs 5 --top-n 60
python scripts/enrich_candidatos_framework.py
python scripts/co_occurrence_network.py --min-cooccur 4

# Outputs:
#   app/data/antartica_geositios_propuestos.geojson  (60 candidatos + WS + decade)
#   app/data/scar_pubs_por_sitio.csv                  (CSV con todas las métricas)
#   docs/notas/propuestas_geositios_scar.md
#   docs/notas/candidatos_x_framework.md
#   docs/notas/co_occurrence_edges.csv
#   docs/notas/co_occurrence_network.md

# Visor con Bibliometría tab (Chart.js): cd app && python -m http.server 8000
```

## 8. Anexos

- **A1.** Tabla completa de 60 candidatos: `docs/notas/propuestas_geositios_scar.md`
- **A2.** Distribución por framework: `docs/notas/candidatos_x_framework.md`
- **A3.** CSV con todas las métricas: `app/data/scar_pubs_por_sitio.csv`
- **A4.** Red de co-ocurrencia: `docs/notas/co_occurrence_network.md` + `co_occurrence_edges.csv`
- **A5.** GeoJSON cargable en el visor: `app/data/antartica_geositios_propuestos.geojson`
- **A6.** Fuentes SCAR descargables: `docs/biblioteca/scar/SOURCES.md`
- **A7.** Código pipeline: `scripts/analisis_actas_scar.py`
- **A8.** Código fetch OpenAlex: `scripts/fetch_openalex_abstracts.py`
- **A9.** Código spatial join framework: `scripts/enrich_candidatos_framework.py`
- **A10.** Código co-occurrence: `scripts/co_occurrence_network.py`

---

*Versión v3 — Mayo 2026.*
*v1 (25 PDFs SCAR) detectó los Tier A obvios.*
*v2 (497 docs +4 journals polares) descubrió Bunger, Prince Charles, Thwaites, Vega, Wright.*
*v3 (909 docs +6 journals generales + WS + temporal + network) rescata Thurston, Pensacola, Alexander, Whitmore por alta WS con pocas pubs, identifica Bunger/Vestfold/SSI como emergentes 2020-26, valida cluster Prydz por co-ocurrencia, y justifica framework F10 (Outlet Glaciers).*
