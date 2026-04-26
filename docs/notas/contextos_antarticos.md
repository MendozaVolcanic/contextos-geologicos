# Contextos Geológicos Antárticos — fuentes y propuesta

Última actualización: 2026-04-25

## Fuente A — SCAR EG-GEOCON: 9 Geological Frameworks oficiales

SCAR (vía un Action Group, hoy **Expert Group on Geoconservation, EG-GEOCON**) **acordó formalmente 9 Geological Frameworks** para la Antártica. Es el equivalente directo a los Contextos Geológicos Chilenos.

> "A Geological Framework refers to a regional geological feature, geotectonic unit, geological event, stratigraphic series, palaeobiological association, or any geological entity of international relevance. Following extensive expert consultation by a former SCAR Action Group, **nine Geological Frameworks were identified and formally agreed upon for Antarctica**."

— Springer Nature Communities, post EG-GEOCON (https://communities.springernature.com/posts/calling-for-antarctic-geoheritage-proposals-advancing-geological-conservation-through-scar)

### Lista completa (Annex 1, Figura 1.1 del IP SCAR-ATCM XLIII, 2021)

Documento descargado: `docs/bibliografia/01_contextos_geologicos/SCAR_ATCM43_2021_Method_Antarctic_Geosites.pdf`

| # | Framework | Alcance |
|---|---|---|
| 1 | **Archean cratons** | Evidencia de formación y ruptura de supercontinentes; ciclos de dispersión y ensamble; episodios orogénicos, unidades petrológicas y estructurales mayores; primeras formas de vida |
| 2 | **Proterozoic orogens and Neoproterozoic-early Palaeozoic rifted margins** | Formación y ruptura de Rodinia; episodios orogénicos y vida temprana |
| 3 | **Gondwana amalgamation and breakup** | Secuencias sedimentarias y rocas ígneo-metamórficas asociadas; tectónica; subducción del margen Panthalásico (Ross Orogeny); orógenos/suturas Pan-Africanos; peneplanicie de Kukri; secuencias clásicas de cobertura Gondwana; registros paleoclimáticos y paleontológicos; Ferrar Large Igneous Province (Transantarctic Mts.) |
| 4 | **Geological history of Antarctica's active margin and West Antarctic rift system** | Historia de subducción; cuencas y magmatismo de arco; apertura de Tasman y Drake gateways; establecimiento de la Corriente Circumpolar; arco de Scotia; volcanismo y back-arc Bransfield; rift Antártico Occidental |
| 5 | **The Cretaceous-Palaeogene (K-Pg) transition** | Registros paleontológicos y geoquímicos de la extinción masiva K-Pg. **Único framework con Geosite formalmente seleccionado**: K-Pg en Isla Marambio (Seymour), 64°17'15"S 56°44'07"W |
| 6 | **Cenozoic glacial history** | Registros sedimentarios continentales y marinos; formación y comportamiento de los sistemas glaciales antárticos en respuesta al clima; fluctuaciones del hielo; evolución de los ice sheets; cambios de nivel del mar; hielo antiguo y geotermalismo |
| 7 | **Meteorites and evidence of impacts** | Rasgos petrológicos y morfológicos relacionados con impactos meteoríticos |
| 8 | **Subglacial water bodies, deposits and morphological features** | Morfología subglacial, lagos y redes fluviales subglaciales |
| 9 | **Geological features or materials which cannot be included in other frameworks** | Categoría "comodín" — minerales, rocas, fósiles, suelos, permafrost, estructuras o landforms científicamente importantes que no encajan en los 8 anteriores, incluyendo localidades tipo reconocidas internacionalmente |

### Estado del proceso (al 2021)

- **Paso 1 — Generación de Frameworks: COMPLETADO.** Los 9 fueron acordados tras consulta con la comunidad antártica.
- **Paso 2 — Selección de Geosites: en curso.** Solo el Framework 5 (K-Pg) tiene Geosite seleccionado (Isla Marambio).
- **Pendiente:** Geosites para Frameworks 1, 2, 3, 4, 6, 7, 8, 9. SCAR EG-GEOCON está convocando propuestas activamente, en particular para Frameworks 3 y 4.

## Fuente B — Cox et al. 2023, GeoMAP: SIMPLECODE en 21 clases

Paper: **Cox, S.C.; Smith Lyttle, B.; Elkind, S.; et al. (2023).** *A continent-wide detailed geological map dataset of Antarctica.* Scientific Data 10, 250. DOI: [10.1038/s41597-023-02152-9](https://doi.org/10.1038/s41597-023-02152-9). Ya descargado en `docs/bibliografia/03_mapas_base/Cox_etal_2023_Antarctica_GeoMAP_ScientificData.pdf`.

Atributo `SIMPLECODE` del shapefile `ATA_GeoMAP_geological_units` agrupa los 99.080 polígonos en 21 clases litocronológicas (Tabla 3). Es la **clasificación operacional usable como contextos geológicos** para el visor.

### Tabla 3 — SIMPLECODE (21 clases)

| Código | Clase mayor | Descripción |
|---|---|---|
| 10 | OTHER | Seasonal water and ice |
| 11 | OTHER | Unknown or unclassified rock |
| 20 | QUATERNARY-NEOGENE | Unconsolidated colluvium, talus, alluvium, and undifferentiated till |
| 21 | QUATERNARY-NEOGENE | Youngest glacial gravel, till, and supraglacial material (Holocene) |
| 22 | QUATERNARY-NEOGENE | Unconsolidated coastal ice shelf till, beach, or lake deposits |
| 23 | QUATERNARY-NEOGENE | Older glacial gravel and till (Miocene-Quaternary) |
| 30 | CENOZOIC | Sedimentary rock with interbedded volcanic or volcaniclastic rock |
| 31 | CENOZOIC | Volcanic rock — basalt to rhyolite lava flows and pyroclastic material |
| 32 | CENOZOIC | Intrusive rock — granite, granodiorite, gabbro, or syenite (Eocene-Oligocene) |
| 40 | MESOZOIC-CENOZOIC | Sedimentary and volcanic rocks, pyroclastic material (Jurassic to Paleogene) |
| 41 | MESOZOIC-CENOZOIC | Volcanic rock (Jurassic-Paleogene) |
| 42 | MESOZOIC | Ferrar Igneous Province and related volcanic and sedimentary rock (Jurassic) |
| 43 | MESOZOIC | Silicic volcanic and continental sedimentary rock (Jurassic) |
| 44 | MESOZOIC | Unmetamorphosed granitoid, gabbro, and other intrusive rock |
| 45 | MESOZOIC | Metamorphosed gneiss and migmatite (Triassic, Cretaceous) |
| 50 | PALEOZOIC-MESOZOIC | Beacon Supergroup and other sandstone-rich sedimentary rock (Devonian-Triassic) |
| 60 | PROTEROZOIC-PALEOZOIC | Intrusive rock — granitoid, diorite, gabbro, and orthogneiss |
| 61 | PROTEROZOIC-PALEOZOIC | Folded low-grade metasedimentary and metavolcanic rock |
| 62 | PROTEROZOIC-PALEOZOIC | Low to medium-grade metamorphic rock — schist, marble, metavolcanic, metasandstone |
| 63 | PROTEROZOIC-PALEOZOIC | High-grade metamorphic rock — orthogneiss, paragneiss, schist, and amphibolite |
| 70 | ARCHEAN | Metamorphic and intrusive rock — schist, gneiss, granulite, migmatite, and anatectite |

Capa estilizada `Simple Geology` viene en el paquete de descarga (`docs/mapas/antartica/ATA_SCAR_GeoMAP_v2022_08_ESRI.zip`).

## Estrategia para el visor

**Doble nivel:**
1. **Capa base** = SIMPLECODE (21 clases, datos georreferenciados completos del GeoMAP). Cubre el continente completo, observable, granular.
2. **Capa interpretativa** = 9 Geological Frameworks SCAR (cuando tengamos los nombres oficiales). Agrupación temática de alto nivel para geoconservación, análoga a los CGT chilenos.

Ambas se pueden alternar como overlays en el mapa, igual que el visor BGS hace con sus diferentes leyendas.

## Pendiente de adquirir

- Lista textual completa de los 9 SCAR Geological Frameworks (Frameworks 1, 2, 6, 7, 8, 9 sin nombre publicado en HTML).
  → Buscar en ATS archive: https://www.ats.aq → IP SCAR sobre identificación sistemática de geositios antárticos.
  → O contactar a Anne Grunow (grunow.1@osu.edu, EG-GEOCON Chair).
