# Traspaso — Contextos Geológicos · Chile & Antártica

**De:** Nicolás Mendoza · **A:** Felipe Fuentes Carrasco · **Fecha:** 2026-08-24

El `README.md` ya explica qué hace el proyecto, cómo está estructurado y en qué estado
está cada pieza. **Léelo primero.** Este documento cubre solo lo que el README no puede
contarte: qué te falta al clonar, qué se arregló en la entrega y qué decisiones quedan
abiertas.

Este es el **repo maestro** de la Suite Geopatrimonio. Si algún dato aparece duplicado
entre repos, el que manda es este.

## 1. Lo primero: el repo pesa 42 MB, el proyecto pesa 5,3 GB

No es un error, es diseño. Los datos de terceros están deliberadamente fuera del control
de versiones, con su procedencia documentada para que cada quien los baje de la fuente.

| Carpeta | Tamaño real | ¿Viene en el clon? |
|---|---:|---|
| `app/data/` (GeoJSON derivados) | 52 MB | ✅ **Sí** — el dashboard funciona sin bajar nada |
| `docs/biblioteca/` (papers, tesis, libros, actas SCAR) | 2.464 MB | ❌ No — copyright de terceros |
| `docs/mapas/` (GeoMAP, Mapa al Millón, BedMap3, Quantarctica) | 1.103 MB | ❌ No — re-descargables de la fuente oficial |
| `docs/bibliografia/**/*.pdf` | 39 MB | ❌ No — copyright |
| `docs/notas/`, `docs/bibliografia/*.md` | < 1 MB | ✅ Sí — acá está todo el razonamiento |

**Consecuencia práctica:** puedes correr el dashboard de inmediato, pero **no** puedes
regenerar las capas hasta bajar los datasets. La guía está en
`docs/bibliografia/PENDIENTES_DESCARGA.md`, que lista qué se bajó, de dónde, y qué sigue
pendiente.

Si quieres la biblioteca completa, pídesela a Nicolás por disco o carpeta compartida: son
2,5 GB de PDFs de terceros que no corresponde redistribuir por el repo.

## 2. Arrancar

Dashboard, sin instalar nada:

```bash
cd app && python -m http.server 8000
```

Pipeline completo (requiere los datasets del punto 1):

```bash
pip install geopandas fiona pyogrio
python scripts/build_chile_geologico.py
python scripts/build_chile_contextos.py
python scripts/build_antartica_geojson.py
python scripts/build_antartica_frameworks.py
```

Cada push a `main` redespliega GitHub Pages solo.

## 3. Arreglado en esta entrega

**Los GeoJSON no eran UTF-8.** `chile_contextos.geojson`, `chile_geologico.geojson` y
`antartica_simplecode.geojson` —las tres capas centrales del visor— estaban escritos en
cp1252. Como el RFC 7946 exige UTF-8, el navegador los decodificaba mal y **9 de los 15
nombres de contexto salían con caracteres de reemplazo en el sitio público**: "Arco
volc**�**nico del Mesozoico", "dep**�**sitos glaciales", "f**�**siles".

La causa raíz estaba en cuatro scripts que llamaban
`Path.write_text(json.dumps(..., ensure_ascii=False))` **sin `encoding="utf-8"`**. En
Windows eso escribe con la codificación local del sistema. Corregidos los cuatro scripts
y convertidos los tres archivos; verificado en navegador que las 185 features de las tres
capas quedan sin un solo carácter corrupto.

Vale la pena tenerlo presente: cualquier script nuevo que escriba texto debe pasar
`encoding="utf-8"` explícito, si no vuelve a pasar.

## 4. Lo que está pendiente de tu criterio

El README lo detalla en "Lo que requiere validación humana". Resumido, y ordenado por lo
que más desbloquea:

1. **Refrendo de la lista de 22 contextos.** Benado et al. 2019 la describe como
   cuestionada por no haber sido validada por la comunidad geológica nacional. Tú ya se
   lo hiciste notar a Nicolás y quedó anotado en
   `docs/notas/contextos_chilenos_22_mourgues.md`. Todo lo demás cuelga de esto.
2. **Reglas de mapping.** `scripts/build_chile_contextos.py`, función `assign_contexto()`:
   son heurísticas de era + período + composición + latitud aplicadas sobre las 149
   unidades del Mapa al Millón. Hoy asignan 15 de los 22 contextos. La auditoría de cada
   decisión está en `docs/notas/mapping_rules_log.md` — ese archivo es el que hay que
   revisar polígono a polígono.
3. **Los 7 contextos no mapeables por reglas** (#6 IO islas oceánicas, #16 BC borde
   costero, #21 TEC estructuras, #22 Lss impactos, entre otros) necesitan información
   espacial que el mapa geológico no tiene. Requieren otra fuente, no mejores reglas.
4. **Mourgues et al. 2012 original** sigue sin conseguirse: el catálogo SERNAGEOMIN tiene
   el SSL caducado y curl falla, aunque el navegador deja aceptar el aviso. Es la fuente
   primaria para validar todo lo anterior.

## 5. Un dato de esquema que conviene saber

- En `chile_contextos.geojson` el campo `edad` **duplica** el valor de `codigo` en las 15
  features, en vez de traer la era o período. Probablemente una asignación equivocada en
  el build. No rompe el visor porque no se usa para pintar, pero no te fíes de ese campo.
- En `antartica_frameworks.geojson` el campo `framework` mezcla dos formatos: números
  sueltos (`'1'`, `'2'`, `'4'`…) para los frameworks SCAR y strings largos
  (`'F2 Sedimentary basins (Beacon) — TAM Central'`) para las cuatro subdivisiones TAM.
  Si vas a filtrar por ese campo, normalízalo primero.

## 7. Pendientes de la auditoría de código

El 2026-08-24 se auditó el código con seis revisores (correctness, reproducibility, design,
domain, performance, security). El informe completo está en
[`reviews/code-review/2026-08-24_CODE-REVIEW-REPORT.md`](reviews/code-review/2026-08-24_CODE-REVIEW-REPORT.md).

**Ya corregido** (no tienes que hacer nada): las subdivisiones TAM estaban etiquetadas F2
cuando el propio repo define Beacon/Ferrar como F3; ocho scripts se caían al redirigir la
salida a un archivo; las actas SCAR pesaban cero en su propio ranking; y no existía
`requirements.txt`.

**Lo que queda abierto.** Ordenado por lo que más conviene atacar primero. Los cuatro
primeros necesitan criterio geológico, no un parche.

### 7.1 · Decisiones que requieren tu criterio

| Dónde | Qué pasa | Por qué importa |
|---|---|---|
| `build_tam_subdivisions.py:59` | **Los bboxes TAM-N y TAM-C se solapan** en lat[−76,5 · −76,0] × lon[159 · 170] — 0,5° de latitud por 11° de longitud. | En la zona de solape el spatial-join asigna según cuál polígono aparezca primero en el GeoJSON, o sea por orden de iteración y no por geología. Contradice el objetivo declarado del script. La salida más simple es que compartan una latitud de borde (−76,0) en vez de rangos que se pisan. |
| `build_chile_contextos.py:118` | **Todo el volcánico paleozoico cae en SSPz**, que Mourgues define como *"Series sedimentarias del Paleozoico"*. Son 375 polígonos según el propio `mapping_rules_log.md`. | La rama Paleozoico no tiene bucket volcánico, así que arcos volcánicos quedan rotulados como cuencas sedimentarias. O se crea un bucket propio, o se mandan a UNK marcados para que los revises uno a uno. |
| `build_chile_contextos.py:99` | **El Cretácico de época ambigua cae por defecto en SMKs** (Superior). Si `periodo == "Cretacico"` pero `epoca` viene en blanco o no reconocida, el catch-all devuelve SMKs. | SMKi y SMKs son contextos distintos, con cuencas y formaciones distintas. Hoy se está dando una respuesta específica donde el dato no alcanza, inflando el conteo de SMKs. Lo honesto sería UNK o un bucket "Cretácico indeterminado". |
| `enrich_candidatos_framework.py:92,94` | **Enderby Land y Dronning Maud Land están rotulados "F1 Basement"** completo. | Ambas regiones mezclan el Napier arqueano (F1 real) con el Rayner proterozoico y el orógeno Este-Africano-Antártico (F2), dentro del mismo bbox. Un candidato en la porción proterozoica queda mal clasificado según las definiciones del propio repo. |

### 7.2 · Bugs mecánicos, arreglo directo

| Dónde | Qué pasa |
|---|---|
| `extract_long_paths.py:33` | **ZIP slip.** `target = dest_root / name` no valida contención, y `long_path()` hace `resolve()`, que normaliza los `..`. Una entrada `../../algo` escribe fuera del destino. Riesgo acotado porque se usa a mano sobre ZIPs oficiales, pero ver el punto siguiente. |
| `build_bedmap.py:57,59` · `build_antartica_geositios.py:54` · `analisis_congresos_chile.py:127` | **Descargas por HTTP sin TLS** (BAS RAMADDA, Quantarctica, GeoNames). Los tres soportan HTTPS hoy — verificado. Va junto con el ZIP slip: son el mismo vector, porque un intermediario podría servir un ZIP alterado que luego se extrae sin validar. |
| `analisis_congresos_chile.py:315` | **El prefijo fuzzy nunca trunca.** `c[:max(8, len(c))]` devuelve la cadena entera, porque el guard ya exige `len(c) >= 8`. Debía ser `min`. El dedup contra geositios ya catalogados casi no filtra, así que entran duplicados a la lista de candidatos nuevos. |
| `analisis_congresos_chile.py:282` y `analisis_actas_scar.py` | **El peso por citas no es monótono en el borde**: 0 citas pesa 1,0 y 1 cita pesa log(2)=0,69, o sea el no citado le gana al citado. Se mantuvo así en ambos scripts por consistencia. La alternativa monótona es `math.log1p(cites) + 1.0` en los dos, pero recalcula todos los pesos ya generados. |
| `enrich_candidatos_framework.py:111` y `build_tam_subdivisions.py:114` | **Fallback silencioso a latin-1** al leer GeoJSON. latin-1 decodifica cualquier byte sin fallar nunca, así que enmascara corrupción futura sin avisar. Era el parche al bug de encoding ya corregido; ahora que los archivos son UTF-8, conviene sacarlo o al menos que imprima un `[WARN]`. |
| `build_chile_contextos.py:77` | Las metamórficas **cenozoicas** caen en UNK, mientras las paleozoicas y mesozoicas van a TCA. Regla inconsistente entre eras; son 5 polígonos. |

### 7.3 · Menores

- Los cuatro `build_*.py` serializan geometrías con un roundtrip JSON por fila donde
  `shapely.geometry.mapping()` es directo. Datasets chicos, impacto bajo.
- `import math` a mitad del módulo en `analisis_actas_scar.py:188`.
- `lexico1.txt` y `lexico2.txt` no tienen script de extracción desde sus PDFs. Los regex de
  `build_lexico.py` dependen del layout exacto que produjo el extractor, así que si hay que
  regenerarlos no se sabe con qué herramienta ni con qué parámetros.
- `fetch_openalex_*.py` no registran fecha de consulta. OpenAlex es mutable, así que el
  corpus no queda trazable a un snapshot y dos corridas distintas dan resultados distintos
  sin manera de saber cuál produjo qué.
- No hay linters (`ruff`, `eslint`) ni tests en el proyecto.
- `build_antartica_*.py` hacen `int(row.SIMPCODE)` sin guard de nulos sobre 99.080
  polígonos: si alguno viniera vacío, el batch cae sin salida parcial.

### 7.4 · Riesgos que no se pudieron verificar

- Las reglas de mapping se auditaron contra `mapping_rules_log.md`, no corriendo el
  pipeline sobre los polígonos reales.
- Las descripciones F1-F9 se contrastaron entre archivos de este repo, **no** contra el
  documento primario SCAR ATCM XLIII Att. A. Si tienes acceso a ese documento, vale la pena
  validarlas de raíz.


## 8. Los repos hermanos

- [georrutas-chile](https://github.com/MendozaVolcanic/georrutas-chile) — rutas geoturísticas
- [apadrina-geositio-chile](https://github.com/MendozaVolcanic/apadrina-geositio-chile) — ciencia ciudadana
- [dashboard-22-contextos](https://github.com/MendozaVolcanic/dashboard-22-contextos) — gestión SGCh
- [glaciar-antartico](https://github.com/MendozaVolcanic/glaciar-antartico) — Proyecto 2 del Visor Antártico

⚠️ Los tres primeros tienen su propio `TRASPASO.md`. El de `dashboard-22-contextos`
importa especialmente: **hasta el 2026-08-24 publicaba los 22 nombres de contexto
equivocados**, corregidos justamente contra la nota de este repo.
