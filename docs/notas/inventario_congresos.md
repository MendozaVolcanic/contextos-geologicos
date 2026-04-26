# Inventario de actas extraídas

Carpeta: `docs/congresos/Simposios-Congresos/` (879 MB, 554 archivos, **gitignored**)

## Contenido

### Simposios de Geoparques y Geoturismo / Geopatrimonio
- `Simposio I/` — Primer simposio Geopatrimonio (incluye `I_Simposio_Geoparques_Geoturismo_Chile.pdf` y `Primer simposio geopatrimonio.pdf`)
- `Simposio II/` — Acta II Simposio Geoparques y Geoturismo Chile 2014
- `Simposio III/` — Actas III Simposio geoparques y geoturismo Chile
- `Simposio IV/` — vacío en el ZIP

### Congresos Geológicos Chilenos
- `XIV Congreso Geológico Chileno 2015/` — Antofagasta, completo, 5 áreas temáticas (AT1-AT5) con simposios y sesiones técnicas. Incluye **AT4 SIM5 "Geopatrimonio en Chile"** con varios papers de Schilling, Martínez, Urresty, Vega, Rauld, Villa, Rodríguez sobre patrimonio geológico.
- `XV Congreso Geológico Chileno 2018/` — Concepción

### Otros documentos relevantes
- `Anais-VSBPG-2019.pdf` — Anais V Simpósio Brasileiro Patrimônio Geológico
- `Anais_do_III_SImposio_Brasileiro_de_Patr (1).pdf` — III Simpósio Brasileiro
- `GGN18_Abstract_Book_final.pdf` — Global Geoparks Network 2018
- `Fuentes et al 2018b Geopatrimonio y maqueta Villarrica_revMV-FF.docx` — paper de Felipe Fuentes

## Papers más relevantes para el proyecto

Encontrados en `XIV Congreso Geológico Chileno 2015/AT4 Impacto de las Geociencias en la Sociedad/SIM5 Geopatrimonio en Chile/`:

- `At4Sim5_015_Schilling et al_Patrimonio geológico.pdf`
- `At4Sim5_016_Martinez et al_Patrimonio Geológico Chileno.pdf`
- `At4Sim5_019_Schilling et al_Kütralkura.pdf` — Geoparque Kütralkura
- `At4Sim5_009_Urresty et al_Geodiversidad y Geopatrimonio.pdf`
- `At4Sim5_005_Villa_Geositios en la Alta Cordillera.pdf`
- `At4Sim5_006_Rodríguez_Geopatrimonio Quebrada Camiña.pdf`
- `At4Sim5_010_Vega et al_Patrimonio Paleontológico.pdf`
- `At4Sim5_020_Rauld et al_Gestión del Patrimonio.pdf`

Y de Felipe Fuentes específicamente:
- `At1Sim1_003_Fuentes et al_Formación Santa Juana.pdf` (XIV Cong, AT1 SIM1, Triásico)
- `At1St1_049_Fuentes et al_Melange de Chañaral + obs CM.pdf` (XIV Cong, AT1 ST1)
- `At3Sim12_005_Fuentes et al_Evento meteorológico Marzo 2015.pdf` (XIV Cong, aluviones Atacama)

## Pendiente

Los PDFs de actas son **escaneados** (imagen, no texto seleccionable) — `pdftotext` no extrae nada de ellos. Para indexarlos por contenido habría que correr **OCR** (Tesseract). Posibles candidatos a procesar primero si vale la pena el esfuerzo:
- `Primer simposio geopatrimonio.pdf` (II Simposio Geopatrimonio = donde apareció Mourgues 2012)
- Los 8 PDFs de SIM5 listados arriba.

No se commitea al repo por tamaño (879 MB).
