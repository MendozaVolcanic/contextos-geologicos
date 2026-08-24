# Code Review Report — Suite Geopatrimonio

**Proyectos:**
- `C:\Users\nmend\OneDrive\Escritorio\claude\Diversion\Contextos geologicos`
- `C:\Users\nmend\OneDrive\Escritorio\claude\Diversion\Glaciar Antartico`
- `C:\Users\nmend\OneDrive\Escritorio\claude\Diversion\Suite-Geopatrimonio`

**Fecha:** 2026-08-24
**Motivo:** auditoría previa al traspaso a Felipe Fuentes Carrasco
**Código revisado:** 23 scripts Python (~3.700 líneas) + 6 archivos JS (~2.600 líneas)
**Equipo:** correctness · reproducibility · design · domain · performance · security

> **Cómo leer el puntaje.** El rubric está calibrado para paquetes de replicación de
> papers listos para someter. Estos son proyectos de investigación en curso cuyo autor ya
> declara en el README qué heurísticas están pendientes de validación. Un puntaje bajo acá
> significa "quedan cosas por cerrar antes de publicar resultados", no "el código está mal
> hecho". Se aplicó un tope de −25 por categoría para que seis hallazgos de dominio no
> hundan el total.

## Puntaje

| Proyecto | Score | Veredicto |
|---|---:|---|
| Contextos Geológicos | 20 / 100 | Revise (major) |
| Glaciar Antártico | 65 / 100 | Revise |
| Suite-Geopatrimonio | 90 / 100 | Ship with notes |

## Checklist estructural

| # | Categoría | Resultado | Nota |
|---|---|---|---|
| 1 | Reproducibilidad | ❌ Fail | Contextos sin `requirements.txt`; `print()` revienta al redirigir stdout |
| 2 | Estructura de scripts | ✅ Pass | Todos con docstring de cabecera; ninguno supera 500 líneas |
| 3 | Higiene de salida | ✅ Pass | Salida informativa, resultados a archivo |
| 4 | Calidad de funciones | ✅ Pass | Nombres descriptivos, documentadas |
| 5 | Correctitud de dominio | ❌ Fail | Ver P1-1 y P1-2 |
| 6 | Figuras | N/A | No se generan figuras estáticas |
| 7 | Persistencia de datos | ✅ Pass | Derivados commiteados; crudos documentados |
| 8 | Dependencias | ❌ Fail | 13 externas sin declarar en Contextos |
| 9 | Específico de Python | ⚠️ Parcial | Encoding explícito solo tras el fix de hoy |
| 10 | Específico de R | N/A | — |
| 11 | Verificación cross-lenguaje | N/A | — |

**Checklist: 5/8 Pass** (3 N/A)

---

## P1 — Críticos

### P1-1 · Las subdivisiones TAM están etiquetadas F2, y el propio repo dice F3

**`Contextos geologicos/scripts/build_tam_subdivisions.py:52`** · domain · confianza 0.90 · **verificado**

`build_antartica_frameworks.py` define el catálogo canónico de los 9 SCAR Frameworks. Ahí,
**F3 = "Gondwana amalgamation and breakup"**, y su descripción nombra explícitamente
*"secuencias Gondwana, Ferrar LIP"*. Las reglas SIMPCODE del mismo archivo son inequívocas:

```python
if s == 50: return 3, "Beacon Supergroup → F3 Gondwana"
if s == 42: return 3, "Ferrar Igneous Province → F3 Gondwana (LIP)"
```

Pero `build_tam_subdivisions.py`, cuyo propio docstring describe las TAM como *"Beacon
Supergroup + Ferrar dolerite sills"*, las etiqueta:

```python
"framework": "F2 Sedimentary basins (Beacon) — TAM Norte"
```

**F2 real es "Proterozoic orogens & rifted margins"** — basamento pre-Gondwana, sin
relación con Beacon ni Ferrar. Y el nombre *"Sedimentary basins (Beacon)"* no existe en el
catálogo de los 9 frameworks: es inventado. El error se repite en las `SOFT_RULES` de
`enrich_candidatos_framework.py:47-54` y **ya está publicado** en
`app/data/antartica_frameworks.geojson`.

*Arreglo:* cambiar las 4 subdivisiones TAM a F3, reutilizando el nombre exacto del catálogo.

### P1-2 · El corpus de actas SCAR aporta peso cero al ranking bibliométrico

**`Contextos geologicos/scripts/analisis_actas_scar.py:281`** · correctness + domain · confianza 0.98 · **verificado**

Para cada PDF, la metadata se fija a `{"cites": 0}` (línea 265), y el peso se calcula como
`weight = math.log(meta["cites"] + 1)` → **log(1) = 0.0**. Como los candidatos se ordenan
primero por `weighted_score`, las actas SCAR —que le dan el nombre y el propósito al
script— no influyen en qué geositios se proponen. Solo pesa el corpus OpenAlex.

El script hermano `analisis_congresos_chile.py:282` ya tiene el guard:
`... if meta["cites"] > 0 else 1.0`. Acá falta.

*Alcance medido:* el corpus real es 26 PDFs contra 883 TXT, así que el ranking no queda
destruido, pero la fuente primaria declarada queda relegada a criterio de desempate.

*Arreglo:* replicar el `else 1.0` del script hermano.

### P1-3 · Ocho scripts se caen si se redirige la salida a un archivo

**`Contextos geologicos/scripts/` y `Glaciar Antartico/scripts/`** · reproducibility · confianza 1.0 · **reproducido**

En Windows, Python solo usa UTF-8 en consola interactiva (PEP 528). Al redirigir o
pipear —`python scripts/build_chile_contextos.py > log.txt`, lo normal para un batch de
19.000 polígonos— cae al cp1252 local y los `print()` con `→`, `✓` o `≈` lanzan
`UnicodeEncodeError` **abortando el script a medio correr**.

Reproducido en este equipo: exit code 1, traceback en `cp1252.py`, salida vacía.

Scripts afectados: `build_antartica_frameworks`, `build_antartica_geojson`, `build_bedmap`,
`build_chile_contextos`, `build_chile_geologico`, `build_inventario_geositios`,
`build_master_db`, `fetch_itslive`.

*Nota:* `—` y `…` **sí** son válidos en cp1252 y no rompen; solo `→ ✓ ✗ ≥ ≈ ▶`.

*Arreglo:* `sys.stdout.reconfigure(encoding="utf-8")` al inicio, o reemplazar por ASCII.

### P1-4 · Contextos Geológicos no declara ninguna de sus 13 dependencias

**`Contextos geologicos/`** · reproducibility · confianza 0.90 · **verificado**

No hay `requirements.txt`, `pyproject.toml` ni `environment.yml`. Los scripts importan
geopandas, requests, xarray, rioxarray, pypdf, pdfplumber, networkx, flashtext, lxml,
openpyxl, numpy, shapely y pyogrio. El README menciona tres. Quien retome el proyecto debe
deducir el entorno leyendo 18 scripts. Glaciar Antártico sí tiene su `requirements.txt`.

---

## P2 — Mayores

| # | Archivo | Problema | Revisor(es) | Conf. |
|---|---|---|---|---|
| 1 | `extract_long_paths.py:33` | **ZIP slip.** `target = dest_root / name` sin validar contención, y `long_path()` hace `resolve()` que normaliza los `..`, así que una entrada maliciosa escribe fuera del destino. Riesgo real acotado (uso manual sobre ZIPs oficiales), pero se combina con las descargas por HTTP del punto 9. | security | 0.95 |
| 2 | `build_tam_subdivisions.py:59` | **Bboxes TAM-N y TAM-C se solapan** en lat[−76,5 · −76,0] × lon[159 · 170] (0,5° × 11°). El spatial-join asigna por orden de iteración, no por geología — contradice el objetivo declarado del script. Verificado aritméticamente. | domain | 0.80 |
| 3 | `top_acceleration_sites.py:95` | **Un solo umbral fijo para regímenes de hielo incompatibles.** Los mismos cortes (±30, ±10 m/yr) se aplican a glaciares de descarga rápidos (PIG, Thwaites), plataformas flotantes (Ross, Amery, Larsen C) y un sitio de divisoria interior (Kohnen, ~1-2 m/yr). 30 m/yr es ~1% de PIG pero excede la velocidad total de Kohnen. | domain | 0.75 |
| 4 | `top_acceleration_sites.py:37` | **Una ventana de 30 km rotulada como la plataforma completa.** El muestreo es ~3.600 km²; Ross tiene ~500.000 km². El JSON y el visor dicen "Ross Ice Shelf" como si el número caracterizara toda la plataforma, cuando cubre menos del 1%. | domain | 0.72 |
| 5 | `analisis_congresos_chile.py:315` | **El prefijo fuzzy nunca trunca.** `c[:max(8, len(c))]` devuelve la cadena completa, porque el guard ya exige `len(c) >= 8`. Debía ser `min`. El dedup contra geositios ya catalogados casi no filtra. Verificado ejecutando. | correctness | 0.78 |
| 6 | `build_chile_contextos.py:118` | **Volcánico paleozoico → SSPz**, contexto definido como *sedimentario*. 375 polígonos según el propio `mapping_rules_log.md`. La rama Paleozoico no tiene bucket volcánico. | domain | 0.78 |
| 7 | `build_chile_contextos.py:99` | **Cretácico de época ambigua cae por defecto en SMKs** (Superior) en vez de quedar como indeterminado, inflando el conteo de SMKs. | domain | 0.65 |
| 8 | `enrich_candidatos_framework.py:111` | **Fallback silencioso a latin-1.** latin-1 decodifica cualquier byte sin fallar nunca, así que enmascara corrupción futura sin avisar. Es el rastro del bug de encoding corregido hoy. | reproducibility | 0.68 |
| 9 | `build_bedmap.py:57,59` · `build_antartica_geositios.py:54` · `analisis_congresos_chile.py:127` | **Descargas por HTTP sin TLS** (BAS RAMADDA, Quantarctica, GeoNames). Verifiqué que los tres soportan HTTPS hoy. Un MitM podría inyectar un GeoTIFF o un ZIP alterado — y ese ZIP se extrae con el script del punto 1. | security | 0.75 |
| 10 | `analisis_congresos_chile.py:282` | **El peso no es monótono en el borde.** Un paper con 0 citas pesa 1,0 y uno con 1 cita pesa log(2)=0,69 — o sea, el no citado gana. | domain | 0.68 |
| 11 | `enrich_candidatos_framework.py:92,94` | **"F1 Basement" sobre regiones de corteza mixta.** Enderby Land y Dronning Maud contienen tanto el Napier arqueano (F1) como el Rayner proterozoico (F2) dentro del mismo bbox. | domain | 0.62 |

---

## P3 — Menores

| Archivo | Problema | Revisor |
|---|---|---|
| `top_acceleration_sites.py:110` | `-(mean_delta or -9999)`: un `0.0` legítimo es falsy y se ordena al final como si fuera el sitio más desacelerado. Bug latente — hoy ningún sitio da exactamente 0,0. | correctness |
| `build_chile_contextos.py:77` | Metamórficas cenozoicas caen en UNK mientras las paleozoicas y mesozoicas van a TCA. Regla inconsistente, 5 polígonos. | domain |
| 4 scripts `build_*` | Roundtrip JSON por fila para serializar geometrías, donde `shapely.geometry.mapping()` es directo. Datasets chicos (≤149 filas), impacto menor. | performance |
| `analisis_actas_scar.py:188` | `import math` a mitad del módulo. | design |
| `Glaciar/app/app.js:290` | `itsLayer2` y `showCompare` se agregan al `state` fuera de su definición inicial. | design |
| `Glaciar/requirements.txt` | Solo cotas inferiores (`>=`), sin lockfile. rasterio y xarray han roto API entre versiones mayores. | reproducibility |
| `build_lexico.py:24` | `lexico1.txt` y `lexico2.txt` no tienen script de extracción desde sus PDFs. Los regex del parser dependen del layout exacto del extractor usado. | reproducibility |
| `fetch_openalex_*.py` | No registran fecha de consulta; OpenAlex es mutable, así que el corpus no es trazable a un snapshot. | reproducibility |
| Suite (3 dashboards) | Utilidades duplicadas entre los tres dashboards. **Rebajado de P1 a P3**: son repos independientes con deploy propio, y compartir código exigiría submodules o CDN — un acoplamiento peor que la duplicación. | design |

---

## Estado de los arreglos (2026-08-24, mismo día)

Los cuatro P1 fueron **aplicados y verificados**. Los P2 y P3 siguen abiertos.

| # | Hallazgo | Estado | Verificación |
|---|---|---|---|
| P1-1 | TAM etiquetadas F2 en vez de F3 | ✅ Corregido | 4 subdivisiones + 5 SOFT_RULES; GeoJSON regenerado y **confirmado en producción** vía GitHub Pages |
| P1-2 | Actas SCAR con peso cero | ✅ Corregido | Piso de 1.0 igual al script hermano; comportamiento verificado para cites = 0, 1, 2, 10 |
| P1-3 | 8 scripts caían al redirigir stdout | ✅ Corregido | `build_master_db.py` ahora termina en exit 0 con los dos `✓` intactos en el archivo redirigido |
| P1-4 | Sin `requirements.txt` | ✅ Corregido | 16 dependencias con las versiones realmente usadas; sintaxis validada; README actualizado |

Los 11 scripts modificados compilan, las 15 capas GeoJSON siguen siendo UTF-8 válido con
su conteo de features intacto, y ambos deploys de GitHub Pages quedaron en verde.

**Deuda que introduce el arreglo de P1-2:** al replicar el guard del script hermano, se
hereda su no-monotonía (P2-10): un paper con 0 citas pesa 1,0 y uno con 1 cita pesa 0,69.
Se mantuvo así por consistencia entre los dos scripts. La alternativa monótona es
`math.log1p(cites) + 1.0` en ambos, pero cambia todos los pesos ya calculados y es una
decisión de criterio, no un bug mecánico.

---

## Riesgos residuales

- Ninguna revisión ejecutó los pipelines completos: las reglas de mapping se auditaron
  contra `mapping_rules_log.md`, no contra los polígonos reales.
- No se verificó que las coordenadas de `KEY_GLACIERS` caigan sobre el tronco rápido de
  cada glaciar y no sobre un margen o la línea de conexión a tierra.
- Las descripciones F1-F9 se contrastaron entre archivos del repo, no contra el documento
  primario SCAR ATCM XLIII Att. A.
- `build_antartica_*.py` hacen `int(row.SIMPCODE)` sin guard de nulos sobre 99.080
  polígonos; si alguno viniera vacío, el batch cae sin salida parcial.
- No hay configuración de linters (ruff, eslint) ni tests en ninguno de los tres proyectos.

## Prioridad de arreglo

1. **P1-1 (TAM F2→F3)** — es un error geológico publicado y se arregla cambiando 8 strings.
2. **P1-3 (encoding en `print`)** — Felipe lo va a golpear el primer día que corra un batch.
3. **P1-4 (`requirements.txt`)** — sin esto no puede levantar el entorno.
4. **P1-2 (peso cero de las actas SCAR)** — una línea, y le devuelve sentido al ranking.
5. **P2-1 (ZIP slip) y P2-9 (HTTPS)** — van juntos: son el mismo vector de ataque.

## Observaciones positivas

- **La trazabilidad es excepcional.** `mapping_rules_log.md` audita cada decisión de
  asignación y `PENDIENTES_DESCARGA.md` documenta procedencia y bloqueos de cada dataset.
  Es más de lo que trae la mayoría de los paquetes de replicación publicados.
- **La separación entre datos crudos y derivados está bien resuelta**: los derivados
  livianos se versionan para que el visor funcione sin bajar nada, y los 3,6 GB de terceros
  quedan fuera con instrucciones de recuperación.
- **El autor declara sus propias limitaciones** en el README ("lo que requiere validación
  humana"), incluida la advertencia de que la lista de 22 contextos no está refrendada.
  Varios hallazgos de dominio de esta auditoría son refinamientos de límites que él ya
  había identificado.
- **Los docstrings explican el porqué físico**, no solo el qué. `itslive_delta.py` anticipa
  el resultado esperado ("la mayor parte del continente debería estar cerca de 0"), y fue
  justamente ese comentario el que permitió detectar el sesgo entre sensores.
- Todos los scripts tienen cabecera, ninguno pasa las 500 líneas, no hay rutas absolutas
  hardcodeadas y no hay una sola credencial en el código.

## Metadatos

- Revisores lanzados: 6
- Hallazgos antes de dedup: 36
- Hallazgos tras dedup y filtro: 24
- Suprimidos (baja confianza o fuera de alcance): 12
- Coincidencias cross-revisor: 1 (P1-2, correctness + domain → confianza 0.98)
- Hallazgos verificados de forma independiente por el orquestador: 7
- Severidades recalibradas: 3 (alcance de P1-2 acotado con el corpus real; duplicación de
  dashboards de P1 a P3; scripts con encoding roto de 13 a 8)
