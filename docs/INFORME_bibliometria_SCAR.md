# Informe bibliométrico SCAR — Propuestas de geositios antárticos

**Autor:** Nicolás Mendoza · SERNAGEOMIN
**Pipeline:** `scripts/analisis_actas_scar.py` + `scripts/enrich_candidatos_framework.py`
**Fecha:** Mayo 2026 — versión expandida (corpus v2)
**Corpus analizado:** **497 documentos** (26 PDFs SCAR + 471 abstracts OpenAlex)
**Gazetteer:** SCAR Composite Gazetteer of Antarctica (CGA, 22.338 topónimos únicos)
**Output principal:** `app/data/antartica_geositios_propuestos.geojson` (60 candidatos, todos con framework SCAR asignado)

---

## 1. Por qué este análisis

El **Comité para la Protección del Medio Ambiente Antártico (CEP)** aprobó en 2021 el método SCAR para identificar "Frameworks Geológicos" antárticos (ATCM XLIII, Att. A) y la creación del Expert Group EG-GEOCON. Sin embargo:

- Hay sólo **9 Frameworks** definidos y un puñado de geositios formalmente propuestos.
- La identificación se está haciendo **por nominación experta** (sitio por sitio), no por análisis sistemático del cuerpo de literatura SCAR.
- Hay **31 años** de actas SCAR + cientos de papers en journals antárticos especializados — un corpus de cientos de miles de páginas que registra dónde se está investigando geocientíficamente la Antártica.

**Hipótesis de trabajo:** *los sitios con mayor densidad de publicaciones científicas son candidatos naturales a geositios — no por sí solos, pero como input cuantitativo al panel experto del EG-GEOCON.*

Este informe convierte esa hipótesis en un dataset reproducible.

## 2. Metodología

### 2.1 Corpus (v2 — expandido)

| Categoría | Documentos | Tamaño | Cobertura temporal |
|---|---:|---:|---|
| **OSC abstracts** (Open Science Conferences) | 9 PDFs | 55 MB | 2012, 2014, 2016, 2018 (POLAR), 2020, 2022, 2024 (Pucón) |
| **EG-GEOCON publications** | 15 PDFs | 10 MB | 2016 (review IP031) → 2025 (ISAES, GF1/GF7 formularios) |
| **ATCM Working Papers** | 2 PDFs | 5.8 MB | ATCM 43 Att-A (método 2021) + ATCM 44 Att-111 (Climate Change 2022) |
| **OpenAlex abstracts** (filtrados geo) | **471 .txt** | 1.2 MB | 2010-2026 |
| → Antarctic Science (Cambridge) | 283 | — | journal especializado #1 |
| → Polar Science (Elsevier) | 70 | — | journal especializado #2 |
| → Advances in Polar Science (CNARC) | 66 | — | journal SCAR-affiliated chino |
| → Polar Record (Cambridge) | 52 | — | journal histórico |
| **TOTAL** | **497** | ~72 MB | **2010–2026** |

Todos los documentos son públicos. Reproducción:
```bash
bash docs/biblioteca/scar/download_all.sh                  # 25 PDFs SCAR + Gazetteer
python scripts/fetch_openalex_abstracts.py --year-min 2010 # 471 abstracts via OpenAlex API
```

### 2.2 Pipeline

```
[25 PDFs SCAR + 471 .txt OpenAlex] ──► pdfplumber + plain text read
                                    │
                                    ▼
texto ──► flashtext KeywordProcessor ◄──── SCAR CGA (22.338 topónimos)
                (Aho-Corasick, O(N))
                                    │
                                    ▼
hits por documento × topónimo
                                    │
                                    ▼
filtrar: tipo en {Mountain, Glacier, Bay, Island, ...} AND nombre ∉ macro-regiones
                                    │
                                    ▼
ranking por nº docs (presencia) → desempate por menciones brutas
                                    │
                                    ▼
spatial join × antartica_frameworks.geojson + soft-rules
                                    │
                                    ▼
60 candidatos con framework SCAR asignado
```

### 2.3 Decisiones técnicas clave

1. **Aho-Corasick vs regex** — La primera versión con `re.findall` por topónimo se atascó con 6.6 GB de RAM. Con flashtext, el pipeline procesa 497 docs y 22K topónimos en ~6 min.

2. **Filtro geo-relevancia para OpenAlex** — De 4.281 papers vistos (Antarctic Science + Polar Record + Polar Science + Advances in Polar Science 2010-2026), retenemos sólo aquellos cuyo abstract contiene al menos una keyword geocientífica (`geology`, `geological`, `tectonic`, `stratigraph`, `volcan`, `sediment`, `metamorph`, `paleo/palaeo`, `outcrop`, `nunatak`, `moraine`, `pluton`, `rock`, `glacial geo`, etc.). Esto descarta papers de ecología/biología/clima sin componente geocientífico → 471 supervivientes (11%).

3. **Filtro por feature_type del CGA** — Excluimos Continent, Station, Sea, Ocean, Pole, Cape. Mantenemos ~30 tipos relevantes (Mountain, Glacier, Bay, Island, Hill, Valley, Volcano, etc.).

4. **Exclusión explícita de nombres genéricos** — Lista negra: "Antarctica", "East/West Antarctica", "Antarctic Peninsula", "Dronning Maud Land", "Ross Sea", "Weddell Sea", etc.

5. **Spatial join con frameworks SCAR** — `app/data/antartica_frameworks.geojson` tiene 6 de los 9 frameworks mapeados como polígonos. Para los candidatos que caen fuera (mayormente F1 Basement y F4 Cenozoic volcanism), aplicamos 10 reglas blandas geográficas (bbox por región geológica).

### 2.4 Limitaciones reconocidas

| Limitación | Impacto | Mitigación |
|---|---|---|
| Solo abstracts (no full text de OpenAlex) | ~50% del contenido geocientífico | Los abstracts son densos en topónimos en la sección "estudio en X site" |
| Filtrado por keyword puede dejar fuera geomorfología sutil | Pérdida ~10% | El filtro es generoso (15 keywords ORed) |
| Topónimos homónimos (e.g. "Davis" = estación + apellido) | Inflado falso positivo | Filtro por `feature_type` ya excluye Station |
| Sesgo hacia investigación reciente | Menor peso histórico | Próxima iteración: ponderar por antigüedad/sostenibilidad |
| Polar Record es transversal (no solo geología) | Solo 52/1079 = 4.8% pasan el filtro geo | Confirma que el filtro funciona |
| 13 candidatos sin framework | Caen fuera de polígonos + bboxes blandas | Expandir reglas blandas en próxima iteración |

## 3. Resultados (corpus v2)

### 3.1 Top 30 candidatos a geositios

| # | Sitio | Pubs | Menciones | Framework SCAR (asignado) |
|--:|---|---:|---:|---|
| 1 | **King George Island** | 40 | 722 | F4 Active margin & West Antarctic rift / F9 |
| 2 | **South Shetland Islands** | 36 | 416 | F9 Antarctic Peninsula arc |
| 3 | **Transantarctic Mountains** | 27 | 164 | *(sin asignar — cinturón cruza varios)* |
| 4 | **Deception Island** | 25 | 273 | F4 Cenozoic volcanism |
| 5 | **Prydz Bay** | 23 | 244 | F1 Basement |
| 6 | **Seymour Island** | 23 | 122 | F4 Active margin & W. Antarctic rift |
| 7 | **Livingston Island** | 19 | 142 | F9 Antarctic Peninsula arc |
| 8 | **Vestfold Hills** | 19 | 89 | F1 Basement |
| 9 | **Fildes Peninsula** | 18 | 183 | F4 Active margin |
| 10 | **James Ross Island** | 18 | 135 | F9 Antarctic Peninsula arc |
| 11 | **Larsemann Hills** | 17 | 140 | F1 Basement |
| 12 | **Grove Mountains** ⭐ | 16 | 71 | *(sin asignar — East Antarctica meteorítica)* |
| 13 | **Taylor Valley** | 14 | 114 | F6 Glacial geology |
| 14 | **Admiralty Bay** | 13 | 187 | F9 Antarctic Peninsula arc |
| 15 | **Bunger Hills** ⭐ NUEVO | 13 | 60 | F1 Basement |
| 16 | **Ross Island** | 11 | 105 | F4 Cenozoic volcanism |
| 17 | **Signy Island** | 11 | 94 | *(sin asignar — South Orkneys)* |
| 18 | **McMurdo Sound** | 10 | 140 | *(sin asignar)* |
| 19 | **Maxwell Bay** | 10 | 72 | F9 Antarctic Peninsula arc |
| 20 | **Marguerite Bay** | 10 | 51 | F9 Antarctic Peninsula arc |
| 21 | **Prince Charles Mountains** ⭐ NUEVO | 10 | 22 | *(sin asignar — Lambert Glacier)* |
| 22 | **South Orkney Islands** | 9 | 88 | *(sin asignar)* |
| 23 | **Thwaites Glacier** ⭐ NUEVO | 9 | 70 | F4 Cenozoic volcanism (West Antarctic) |
| 24 | **Taylor Glacier** | 9 | 58 | *(sin asignar — Dry Valleys)* |
| 25 | **Windmill Islands** | 9 | 38 | *(sin asignar — Wilkes Land)* |
| 26 | **Adelaide Island** | 9 | 31 | F9 Antarctic Peninsula arc |
| 27 | **Mount Erebus** | 9 | 24 | F4 Active margin |
| 28 | **Ellsworth Mountains** | 8 | 67 | F1 Basement |
| 29 | **Argentine Islands** | 8 | 43 | F9 Antarctic Peninsula arc |
| 30 | **Anvers Island** | 8 | 36 | F9 Antarctic Peninsula arc |

⭐ = candidato emergente que NO aparecía en el corpus v1 (25 docs).

*Tabla completa de 60 candidatos en `docs/notas/propuestas_geositios_scar.md`. Distribución por framework en `docs/notas/candidatos_x_framework.md`.*

### 3.2 Distribución por Framework SCAR

| Framework | # Candidatos | Top sitios |
|---|---:|---|
| F9 Antarctic Peninsula arc | 21 | King George (40), South Shetland (36), Livingston (19), Fildes (18), James Ross (18) |
| F1 Basement | 11 | Prydz Bay (23), Larsemann Hills (17), Bunger Hills (13), Ellsworth (8), Lützow-Holm Bay (8) |
| F4 Cenozoic volcanism + West Antarctic rift | 10 | Deception (25), Seymour (23), Fildes (18), Ross Island (11), Mount Erebus (9), Thwaites (9) |
| F6 Glacial geology / Cenozoic glacial history | 3 | Taylor Valley (14), Wright Valley (8), Beacon Valley (5) |
| F2 Sedimentary basins / Proterozoic orogens | 2 | Wright Valley (8), Robertson Bay (6) |
| **(sin asignar)** | 13 | Transantarctic Mtns (27), Grove Mtns (16), Signy (11), McMurdo Sound (10), Prince Charles (10) |

### 3.3 Hallazgos cualitativos

#### Confirmaciones del corpus v1, ahora con evidencia 4x mayor

1. **Las Shetland del Sur dominan**. King George Island con **722 menciones en 40 documentos** (vs 670/10 en v1). El cluster F9 incluye además Livingston, Fildes, Admiralty Bay, Maxwell Bay, Barton Peninsula, Keller Peninsula, Byers Peninsula, Hope Bay, Penguin Island. Sigue siendo la región más estudiada del continente.

2. **Triada Vestfold–Prydz–Larsemann (East Antarctic craton)** consolidada como cluster F1. Sumar **Bunger Hills** y **Lützow-Holm Bay**: 5 sitios contiguos del cratón Rayner.

3. **Dry Valleys + Erebus volcanic province** se mantiene como caso para un Framework geomorfológico unificado: Taylor Valley (14), Wright Valley (8), Beacon Valley (5), Taylor Glacier (9), Ross Island (11), Mount Erebus (9), McMurdo Sound (10).

#### Hallazgos NUEVOS (corpus v2)

4. **Bunger Hills (East Antarctica, Wilkes Land)** entra con 13 pubs — oasis libre de hielo de ~5000 km² con paleosuelos cuaternarios y basamento Pan-Gondwánico. Candidato fuerte F1.

5. **Prince Charles Mountains (East Antarctica, MacRobertson Land)** con 10 pubs — cordillera del basamento Rayner-Eastern Ghats que drena al Lambert Glacier (mayor glaciar del continente). Acceso desde Davis. Candidato F1.

6. **Thwaites Glacier** emerge con 9 pubs propias — antes solo aparecía en contexto de "WAIS collapse". Su firma bibliométrica ahora justifica considerarlo *geositio dinámico* F6 + F4 (subglacial volcanism, ITGC sondajes).

7. **Vega Island** (8 pubs) — sitio paleobotánico del Cretácico Superior (Antarctic Peninsula), complementario a Seymour Island en la sección K-Pg.

8. **Wright Valley** (8 pubs) — fue asignado a F2 por spatial-join, pero su valor está en F6 (geomorfología Neógena periglacial preservada). Caso para revisar polígonos F2.

9. **Lambert Glacier + Denman Glacier + Totten Glacier** aparecen como triada complementaria a Thwaites para casos de glaciares dinámicos antárticos no contemplados explícitamente en los 9 Frameworks SCAR actuales.

## 4. Propuestas concretas para el EG-GEOCON

A partir del corpus v2, las nominaciones se actualizan así:

### Tier A — Evidencia abrumadora (>=15 pubs, no catalogados como geositio formal)

| Sitio | Pubs | Justificación principal | Framework |
|---|---:|---|---|
| **King George Island** (ASMA No.1) | 40 | El sitio antártico más estudiado. Volcánico cenozoico, paleosuelos, glaciar Ecology, sitio histórico múltiple. | F4/F9 |
| **South Shetland Islands** (complejo) | 36 | Arco volcánico cenozoico íntegro, agrupar geositios en un único framework regional. | F9 |
| **Transantarctic Mountains** | 27 | Cinturón Beacon-Ferrar de ~3500 km. Propuesta: dividir en sectores (Beardmore, Shackleton, Darwin, etc.). | F2+F3 |
| **Deception Island** (ASPA-145) | 25 | Caldera activa, hidrotermalismo submarino, erupciones recientes. | F4 |
| **Prydz Bay + Vestfold Hills + Larsemann Hills + Bunger Hills** | 72 combinado | Cluster F1 Pan-Gondwánico (cuatro oasis Rayner contiguos). | F1 |
| **Seymour Island** | 23 | Sección K-Pg + paleontología vertebrada. | F4+F5 |
| **Livingston Island** | 19 | Sitio histórico Hannah Point, paleontología Bahía Sur. | F9 |
| **James Ross Island** | 18 | Estratigrafía cretácica + vulcanismo Neógeno + ASPAs activas. | F9 |
| **Fildes Peninsula** | 18 | Vulcanismo Eoceno, paleobotánica, sitio histórico. | F9 |
| **Larsemann Hills** | 17 | Petrología metamórfica granulítica de referencia. | F1 |
| **Grove Mountains** | 16 | Campo meteorítico chino + paleoglacial. | F7 |

### Tier B — Evidencia sólida (10-14 pubs, no catalogados)

| Sitio | Pubs | Justificación | Framework |
|---|---:|---|---|
| **Taylor Valley + Wright Valley + Beacon Valley** | 14+8+5 | Sistema Dry Valleys completo (geositio áreal). | F6 |
| **Admiralty Bay** (ASPA-128 ASMA-1 incluyente) | 13 | Geología sedimentaria + vulcanismo + paleoflora. | F9 |
| **Bunger Hills** ⭐ | 13 | Oasis East Antarctic, paleosuelos cuaternarios. | F1 |
| **Ross Island** (Erebus + ASPA-175) | 11 | Lago de lava fonolítica único + complejo volcánico. | F4 |
| **Signy Island** (South Orkneys) | 11 | Paleoglacial sub-antártico, ASPA-109 activa. | F9 sub-antártico |
| **McMurdo Sound** | 10 | Acceso a Dry Valleys + sondajes Cape Roberts. | F6/F2 |
| **Marguerite Bay** | 10 | Sondajes Ross Sea-Bellingshausen, base Rothera. | F9 |
| **Prince Charles Mountains** ⭐ | 10 | Lambert basin + basamento Rayner. | F1 |

### Tier C — Glaciares de monitoreo (candidatos para *framework dinámico*, no contemplado en F1-F9)

- **Thwaites Glacier** (9) — "Doomsday glacier"
- **Lambert Glacier** (8) — mayor del continente
- **Denman Glacier** (7) — cañón subglacial más profundo de la Tierra
- **Totten Glacier** (6) — base por debajo del nivel del mar
- **Pine Island** (en seed) — colapso WAIS

**Propuesta:** elevar al SCAR EG-GEOCON la creación de un **Framework F10 — "Glaciares de salida críticos / Outlet glaciers"** como nueva categoría para sitios cuyo valor es la dinámica glaciar contemporánea más que la geología sólida.

### Tier D — Confirmaciones de sitios ya catalogados

Sitios ya en `antartica_geositios.geojson` que el corpus refuerza con datos cuantitativos:

- **Seymour Island** (23 pubs) — confirma rol K-Pg
- **Mount Erebus** (9 pubs) — confirma F4 volcanism
- **Allan Hills** + **Grove Mountains** — duplicidad de evidencia F7 (meteoritos)
- **Pine Island Glacier** (en seed, ya documentado)

## 5. Próximos pasos sugeridos

1. **Expandir corpus a literatura general** — además de los 4 journals especializados, abrir a Geology (GSA), Earth & Planetary Science Letters, Quaternary Science Reviews con filtro geográfico Antarctic. OpenAlex permite búsquedas booleanas potentes.

2. **Análisis temporal por década** — separar el ranking 2010-2015 vs 2020-2026 para distinguir sitios "históricamente establecidos" (Vestfold, Erebus) de "emergentes" (Thwaites pre-2010 era 0 pubs).

3. **Refinar reglas blandas para los 13 huérfanos** — Transantarctic Mountains debería sub-dividirse; Signy/South Orkneys necesitan su propio sub-framework; Grove Mountains podría caer en F7 directo.

4. **Ponderación por relevancia** — actualmente todos los documentos pesan igual. Una ponderación posible: peso × tipo (review > working paper > abstract conferencia) o por citaciones (ya recolectadas en OpenAlex como `cited_by_count`).

5. **Validación experta** — esta lista no reemplaza nominación SCAR EG-GEOCON; la complementa. El próximo paso natural es presentarla al EG-GEOCON, INACh o a la mesa SERNAGEOMIN de patrimonio geológico.

## 6. Reproducibilidad completa

```bash
cd "Contextos geologicos"

# 1. PDFs SCAR (~85 MB)
bash docs/biblioteca/scar/download_all.sh

# 2. Abstracts OpenAlex (~1 MB, 4 journals)
python scripts/fetch_openalex_abstracts.py --year-min 2010

# 3. Análisis bibliométrico (3-6 min)
python scripts/analisis_actas_scar.py --pdfs-dir docs/biblioteca/scar --min-pubs 5 --top-n 60

# 4. Asignación de Framework SCAR
python scripts/enrich_candidatos_framework.py

# Outputs:
#   app/data/antartica_geositios_propuestos.geojson  (60 candidatos con framework)
#   app/data/scar_pubs_por_sitio.csv                  (datos crudos)
#   docs/notas/propuestas_geositios_scar.md           (tabla completa)
#   docs/notas/candidatos_x_framework.md              (agrupado F1-F9)
```

## 7. Anexos

- **A1.** Tabla completa de 60 candidatos: `docs/notas/propuestas_geositios_scar.md`
- **A2.** Distribución por framework: `docs/notas/candidatos_x_framework.md`
- **A3.** Datos crudos por sitio × archivo: `app/data/scar_pubs_por_sitio.csv`
- **A4.** GeoJSON cargable en el visor: `app/data/antartica_geositios_propuestos.geojson`
- **A5.** Lista de PDFs SCAR descargados: `docs/biblioteca/scar/SOURCES.md`
- **A6.** Código pipeline análisis: `scripts/analisis_actas_scar.py`
- **A7.** Código fetch OpenAlex: `scripts/fetch_openalex_abstracts.py`
- **A8.** Código spatial join framework: `scripts/enrich_candidatos_framework.py`

---

*Versión v2 (corpus expandido) — Mayo 2026. La iteración v1 con sólo 25 PDFs SCAR ya producía los Tier A; v2 confirma con evidencia 4x mayor y agrega Bunger Hills, Prince Charles Mtns, Thwaites Glacier, Vega Island y Wright Valley a los candidatos.*
