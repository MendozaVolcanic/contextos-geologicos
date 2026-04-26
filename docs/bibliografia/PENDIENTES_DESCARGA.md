# Bibliografía — estado de descarga

Última actualización: 2026-04-25

## ✅ Ya descargado

### Bibliografía core
- **Benado, J.; Hervé, F.; Schilling, M.; Brilha, J. (2019)** — *Geoconservation in Chile: State of the Art and Analysis* (Geoheritage 11:793-807).
  → `docs/bibliografia/01_contextos_geologicos/Benado_Herve_Schilling_Brilha_2019_Geoconservation_in_Chile.pdf`
- **Benado, J.; Andrade, F.; Muñoz, E.; et al. (2020)** — *Geositios de la región de Aysén: contextos geológicos temáticos e inventario* (Aysenología 8:4-19). Contiene los **19 CGT** ya extraídos a `docs/notas/contextos_aysen_benado_2020.md`.
  → `docs/bibliografia/01_contextos_geologicos/Benado_etal_2020_Geositios_Aysen_Contextos_Tematicos.pdf`

### Tesis regionales
- **Sepúlveda V. (2022)** — *Identificación de potenciales geositios y sitios de geodiversidad en la ribera norte del Lago General Carrera, Comuna de Río Ibáñez* (Memoria UNAB).
  → `docs/bibliografia/02_tesis_regionales/Sepulveda_2022_Geositios_Lago_General_Carrera_UNAB.pdf`
- **Gálvez N. (2024)** — *Caracterización del patrimonio geológico de la Reserva de la Biósfera Corredor Biológico Nevados de Chillán – Laguna del Laja* (Memoria UdeC).
  → `docs/bibliografia/02_tesis_regionales/Galvez_2024_Patrimonio_Nevados_de_Chillan_UdeC.pdf`

### Mapas base (PDF)
- **Mapa Geológico de Chile 1:1.000.000** (mirror IPGP)
  → `docs/bibliografia/03_mapas_base/Mapa_Geologico_de_Chile_al_Millon_IPGP.pdf`
- **Mapa Geológico Antártico** (BND Chile)
  → `docs/bibliografia/03_mapas_base/Mapa_Geologico_Antartico_BND_Chile.pdf`

### Datos geoespaciales
- **Mapa Geológico de Chile** — shapefile (15 MB) y GeoJSON completo (60 MB).
  → `docs/mapas/chile/Mapa_Geologico_de_Chile_SHP.zip`
  → `docs/mapas/chile/Mapa_Geologico_de_Chile.geojson`
- **SCAR GeoMAP Antártica v2022.08** — geodatabase ESRI (121 MB) + Google Earth (312 MB).
  → `docs/mapas/antartica/ATA_SCAR_GeoMAP_v2022_08_ESRI.zip`
  → `docs/mapas/antartica/ATA_SCAR_GeoMAP_2022_08_GoogleEarth.zip`

---

## 🔴 Crítico — sigue pendiente

1. **Mourgues, A.; Schilling, M.; Castro, C. (2012)** — *Propuesta de definición de los Contextos Geológicos Chilenos para la caracterización del patrimonio geológico nacional.* Actas XIII Congreso Geológico Chileno, Antofagasta, pp. 890-892.
   - URL: https://catalogobiblioteca.sernageomin.cl/Archivos/14127_pp_890_892.pdf
   - Bloqueo: SSL caducado del catálogo SERNAGEOMIN (curl/PowerShell fallan; el navegador deja aceptar el aviso).
   - Por qué: contiene los **22 contextos a escala nacional**, base para extender lo de Aysén al resto del país.
   - Mientras tanto: estamos usando los 19 CGT de Aysén (Benado 2020) que son derivados de Mourgues 2012.

## 🟡 Útil pero no bloquea

2. **Charrier, R.; Pinto, L.; Rodríguez, M.P. — *The Geology of Chile***
   - https://digital.csic.es/handle/10261/27232 (acceso restringido)

3. **Mourgues et al. — versión completa nacional** si en algún momento aparece publicada con los polígonos georreferenciados.

4. **GNS GeoMAP — página Download oficial** (sólo para metadata, los ZIPs ya los tenemos):
   - https://data.gns.cri.nz/ata_geomap/index.html?content=/mapservice/Content/antarctica/Download.html
   - Bloqueo: certificado SSL no se valida desde nuestras herramientas; abrir desde el navegador.

5. **Durham Repository output 1673488** (404/403 al fetch, sin info)
   - https://durham-repository.worktribe.com/output/1673488

---

## Referencias web de diseño / UX

- BGS Geology Viewer — https://www.bgs.ac.uk/map-viewers/bgs-geology-viewer/
- BGS Lexicon of Named Rock Units — https://webapps.bgs.ac.uk/lexicon/
- SCAR EG-GEOCON — https://scar.org/science/geo/geoconservation (categorías ya en `docs/notas/scar_categorias.md`)
