# Contextos Geológicos Antárticos — fuentes y propuesta

Última actualización: 2026-04-25

## Fuente A — SCAR EG-GEOCON: 9 Geological Frameworks oficiales

SCAR (vía un Action Group, hoy **Expert Group on Geoconservation, EG-GEOCON**) **acordó formalmente 9 Geological Frameworks** para la Antártica. Es el equivalente directo a los Contextos Geológicos Chilenos.

> "A Geological Framework refers to a regional geological feature, geotectonic unit, geological event, stratigraphic series, palaeobiological association, or any geological entity of international relevance. Following extensive expert consultation by a former SCAR Action Group, **nine Geological Frameworks were identified and formally agreed upon for Antarctica**."

— Springer Nature Communities, post EG-GEOCON (https://communities.springernature.com/posts/calling-for-antarctic-geoheritage-proposals-advancing-geological-conservation-through-scar)

### Frameworks identificados por nombre

| # | Framework | Notas |
|---|---|---|
| 3 | **Gondwana Amalgamation and Breakup** | Incluye Early Palaeozoic subduction & Ross Orogeny, orógenos Pan-Africanos y suturas, peneplanicie de Kukri y secuencias de cobertura Gondwana, registros paleoclimáticos/paleontológicos, Ferrar Large Igneous Province |
| 4 | **Geological History of Antarctica's Active Margin and the West Antarctic Rift System** | Zona de subducción activa, márgenes de rift, control tectónico sobre flujo de hielo cenozoico en Antártica Occidental |
| 5 | **Cretaceous–Paleogene (K–Pg) transition** | Único framework con Geosite ya formalmente seleccionado (caso piloto, Isla Marambio/Seymour) |
| 1, 2, 6, 7, 8, 9 | **No publicados en texto en las páginas web** | Listados en Annex 1 / Figura 1.1 del IP SCAR-ATCM "Method for the systematic identification of globally important geological sites in Antarctica" |

**Pendiente:** descargar el documento SCAR-ATCM (versión cacheada parcial: https://docslib.org/doc/4090731/) o pedirlo al ATS Document Archive (https://www.ats.aq) para tener los 9 nombres exactos.

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
