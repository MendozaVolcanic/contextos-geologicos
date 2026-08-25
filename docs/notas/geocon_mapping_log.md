# Auditoría del mapping GeoMAP → 9 Geological Frameworks (EG-GEOCON)

Generado por `scripts/build_antartica_geocon.py`. **No editar a mano.**

Fuente normativa de los 9 GF: SCAR ATCM XLIII (2021), Attachment A, Annex 1, págs. 7-8 — `docs/biblioteca/scar/atcm/ATCM43_Att-A_2021_Method_Identification_Antarctic_Geological_Sites.pdf`. Estado del proceso y geositios aprobados: presentación del workshop GEOCON (SCAR ISAES 2025 / OSC 2026).

Partes de polígono procesadas: **92,328**

> **Cómo leer las áreas.** Salen de `antartica_simplecode.geojson`, que está *simplificado a 3 km* y disuelto por SIMPCODE. Muchos afloramientos antárticos miden menos que esa tolerancia, así que los km² absolutos están inflados: acá dan ~33.000 km² de roca (sin contar depósitos glaciales) contra los 21.745 km² de afloramiento real que publican Burton-Johnson et al. (2016). **Las proporciones entre frameworks son el resultado utilizable; los valores absolutos no.** Para áreas reales hay que correr sobre la geodatabase original en `docs/mapas/antartica/`, que necesita geopandas.

## Distribución por Framework

| GF | Nombre | Polígonos | Área km² | % del área clasificada |
|---|---|---:|---:|---:|
| GF1 | Archean cratons | 2,092 | 1,840 | 4.4% |
| GF2 | Proterozoic orogens and Neoproterozoic–early Palaeozoic rifted margins | 7,427 | 3,409 | 8.2% |
| GF3 | Gondwana amalgamation and breakup | 28,257 | 19,987 | 48.3% |
| GF4 | Geological history of Antarctica's active margin and West Antarctic rift system | 39,518 | 7,630 | 18.4% |
| GF5 | The Cretaceous–Palaeogene (K-Pg) transition | 4 | 77 | 0.2% |
| GF6 | Cenozoic glacial history | 7,452 | 8,444 | 20.4% |
| GF7 | Meteorites and evidence of impacts | 0 | 0 | 0.0% |
| GF8 | Subglacial water bodies, deposits and morphological features | 0 | 0 | 0.0% |
| GF9 | Geological features or materials which cannot be included in other frameworks | 0 | 0 | 0.0% |
| — | *excluidas: agua/hielo estacional y roca sin clasificar* | 7,578 | 963 | — |

## Conteo por regla aplicada

| Polígonos | Área km² | Regla |
|---:|---:|---|
| 17,257 | 10,461 | Basamento Pz en corredor TAM → GF3 (orogenia Ross) |
| 14,108 | 1,767 | Sedimentario/volcánico J-Pg en Península Antártica y Shetland del Sur → GF4 (cuencas de arco) |
| 11,279 | 1,246 | Intrusivo/metamórfico mesozoico en Península Antártica y Shetland del Sur → GF4 (arco andino) |
| 7,452 | 8,444 | Depósito glacial Neógeno-Cuaternario → GF6 (historia glacial cenozoica) |
| 6,874 | 3,221 | Basamento Proterozoico-Paleozoico, resto de Antártica Oriental → GF2 |
| 4,725 | 773 | Basamento Pz en Península Antártica y Shetland del Sur → GF4 (basamento del margen activo) |
| 4,197 | 3,616 | Ferrar Igneous Province → GF3 (LIP de ruptura de Gondwana) |
| 4,196 | 345 | Roca desconocida o sin clasificar — sin dato para asignar GF |
| 3,755 | 3,196 | Beacon Supergroup → GF3 (secuencia clásica de cobertura Gondwana) |
| 3,382 | 619 | Agua/hielo estacional — no es unidad geológica, se excluye |
| 2,868 | 2,689 | Basamento en cinturón Pan-Africano (DML/Sør Rondane/Lützow-Holm) → GF3 |
| 2,092 | 1,840 | Arqueano metamórfico/intrusivo → GF1 cratones arqueanos |
| 1,985 | 1,417 | Sedimentario/volcánico J-Pg fuera de región conocida → GF4 (revisar) |
| 1,522 | 455 | Volcanismo silícico jurásico en Península Antártica y Shetland del Sur → GF4 |
| 1,506 | 629 | Ígneo/sedimentario cenozoico en Península Antártica y Shetland del Sur → GF4 |
| 1,377 | 879 | Ígneo/sedimentario cenozoico fuera de región conocida → GF4 (revisar) |
| 822 | 47 | Basamento Pz en Islas Orcadas del Sur (arco de Scotia) → GF4 (basamento del margen activo) |
| 612 | 87 | Ígneo/sedimentario cenozoico en Marie Byrd Land y rift antártico occidental → GF4 |
| 611 | 151 | Basamento Pz en Marie Byrd Land y rift antártico occidental → GF4 (basamento del margen activo) |
| 553 | 188 | Basamento en sector Enderby/Rayner (grenviliano) → GF2 (ciclo Rodinia) |
| 539 | 87 | Intrusivo/metamórfico mesozoico en Marie Byrd Land y rift antártico occidental → GF4 (arco andino) |
| 333 | 81 | Intrusivo/metamórfico mesozoico fuera de región conocida → GF4 (revisar) |
| 143 | 15 | Volcanismo silícico y sedimentario continental jurásico → GF3 (ruptura de Gondwana) |
| 52 | 5 | Sedimentario/volcánico J-Pg en Marie Byrd Land y rift antártico occidental → GF4 (cuencas de arco) |
| 47 | 6 | Sedimentario/volcánico J-Pg en Islas Orcadas del Sur (arco de Scotia) → GF4 (cuencas de arco) |
| 37 | 10 | Intrusivo/metamórfico mesozoico en corredor TAM → GF3 |
| 4 | 77 | Sedimentario J-Pg en isla Marambio/Seymour → GF5 (tránsito K-Pg) |

## Corredor TAM derivado del dato

El cinturón Transantarctic no se dibujó a mano: se derivó de dónde aparecen realmente el Beacon Supergroup (SIMPCODE 50) y el Ferrar (42), que son los marcadores diagnósticos de GF3 según ATCM43. Resultado: **70 celdas** de 2.0°×5.0°, dilatadas a 70 con una holgura de 0 celda(s).

### Sensibilidad a ese corredor

La holgura del corredor es la única decisión paramétrica del mapping, así que conviene ver cuánto depende el resultado de ella:

| Holgura | Celdas | GF1 | GF2 | GF3 | GF4 | GF6 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | 4.4% | 8.2% | 48.3% | 18.4% | 20.4% |
| 1 | 262 | 4.4% | 2.0% | 54.6% | 18.4% | 20.4% |
| 2 | 489 | 4.4% | 1.2% | 55.4% | 18.4% | 20.4% |
| 3 | 722 | 4.4% | 1.2% | 55.4% | 18.3% | 20.4% |

**Lectura:** GF3 es robusto, pero el límite GF2/GF3 no lo es — una sola celda de dilatación se lleva la mayor parte del área de GF2. Por eso el default es holgura 0: solo celdas donde hay Beacon o Ferrar de verdad.

## Lo que NO se puede asignar desde la litología

Tres frameworks no salen de un mapa geológico y necesitan otra fuente:

- **GF5 (tránsito K-Pg)** — es un horizonte estratigráfico, no una clase litológica. Solo se asigna por posición, en isla Marambio/Seymour, que es el único geositio K-Pg formalmente seleccionado (ATCM43, Annex 1, paso 2).
- **GF7 (meteoritos e impactos)** — son campos de hielo azul, no roca aflorante. GeoMAP no los trae. Requiere el inventario de meteorite fields (Yamato, Allan Hills, Miller Range...). La presentación GEOCON ya aprobó Yamato Mountains como geositio GF7 y sitio IUGS.
- **GF8 (cuerpos de agua subglaciales)** — morfología y lagos bajo el hielo. Requiere BedMap3 y el inventario de lagos subglaciales. El repo ya tiene `scripts/build_bedmap.py`, así que es el más alcanzable de los tres.

**GF9** tampoco se asigna por litología, y a propósito: ATCM43 lo define como rasgos de interés científico que no encajan en los otros ocho, no como cajón del dato ausente. Se asigna sitio por sitio, no polígono por polígono.

## Límites regionales — revisar

Los bboxes son aproximaciones de lectura cartográfica, **no contornos publicados**. Están todos juntos al inicio del script. Los que más pesan:

- Cinturón Pan-Africano `(-76.0, -66.0, -15.0, 45.0)` — decide GF3 vs GF2 en Dronning Maud Land. Anclado en los geositios GF3 que GEOCON ya nominó ahí (Trollslottet, Jutulhogget, Sør Rondane, Rundvågshetta/Lützow-Holm).
- Sector Enderby/Rayner `(-71.0, -65.0, 45.0, 60.0)` — se excluye del anterior porque el Complejo Rayner es grenviliano (~990-900 Ma), o sea ciclo Rodinia → GF2.
- Regiones de margen activo → GF4: Península Antártica y Shetland del Sur `(-75.0, -60.0, -85.0, -50.0)`, Islas Orcadas del Sur (arco de Scotia) `(-62.0, -60.0, -47.0, -44.0)`, Islas Sandwich del Sur (arco de Scotia) `(-60.0, -56.0, -29.0, -25.0)`, Marie Byrd Land y rift antártico occidental `(-85.0, -70.0, -160.0, -90.0)`
