# Visor 3D Antártico

Relieve de BedMap3 con la geología de GeoMAP y los 9 Geological Frameworks del
SCAR EG-GEOCON drapeados encima, más los geositios SCAR y los candidatos
bibliométricos posicionados sobre el terreno.

```bash
python -m http.server 8000 --directory app
```

Y abrir <http://localhost:8000/visor3d/>. No hay build: HTML + JS de módulos +
Three.js por CDN, igual que el resto de la Suite.

## Regenerar los datos

Son dos pasos, y el orden importa:

```bash
python scripts/build_antartica_geocon.py
python scripts/build_visor3d_data.py
```

El primero produce `app/data/antartica_geocon.geojson`, que **está gitignorado**
por regenerable y por pesar 15,5 MB. Si clonas limpio y corres solo el segundo,
falla al no encontrarlo.

`build_visor3d_data.py` lee los GeoTIFF y GeoJSON de `app/data/` y escribe
`app/visor3d/data/` (1,9 MB). Necesita `rasterio`, `geopandas` y `Pillow` — todos
en `requirements.txt`.

| Flag | Default | Qué hace |
|---|---:|---|
| `--malla` | 512 | lado de la grilla de elevación. 512² = 262.144 vértices |
| `--textura` | 4096 | lado de las texturas temáticas |
| `--dilatar` | 2 | píxeles de engorde de las clases (ver abajo) |

## Qué mira cada capa

- **Superficie** — altura del hielo. Solo hay dato donde hay hielo o roca, así que
  el océano queda como hueco real en la malla, no como una lámina plana.
- **Lecho rocoso** — topografía bajo el hielo más batimetría. Es la de mayor
  cobertura: 411.704 triángulos contra 161.590 de las otras dos.
- **Espesor de hielo** — no es una elevación. El relieve representa cuánto hielo
  hay encima, así que se lee distinto: los máximos son las cuencas subglaciales.

## Los cuatro niveles de geositio

No todo punto en el mapa es un geositio SCAR, y la diferencia es sustantiva. Los
geositios SCAR **no tienen estatus legal** bajo el Tratado Antártico (presentación
GEOCON, lámina 3); las ASPAs sí. Mezclarlos era un error de categoría.

| Nivel | | Qué es |
|---|---:|---|
| **Aprobado** | 8 | Geositio SCAR formalmente aprobado. 6 de GF1, 1 de GF7 (Yamato) y el K-Pg de isla Marambio. Tres son además IUGS Third 100 |
| **Nominado** | 9 | Propuestos en la convocatoria GF3/GF4 2026-2028, sin resolver. Incluye The Palisades, que la propia presentación dice que no se está considerando por ahora |
| **Potencial** | 68 | Candidatos nuestros, derivados de la bibliografía. **Sin estatus SCAR de ningún tipo** |
| **ASPA** | 72 | Áreas Antárticas Especialmente Protegidas. No son geositios |

Por defecto solo se muestran aprobados y nominados. Se regeneran con
`scripts/build_geositios_geocon.py`, que trae la lista con la lámina de origen de
cada uno y resuelve las coordenadas contra el SCAR Composite Gazetteer.

## Dos cosas que no hay que malinterpretar

**El tamaño de las clases en pantalla no es el área real.** La roca aflorante de
la Antártica es ~0,2% del continente y casi todo afloramiento mide menos que un
píxel de textura. Sin `all_touched` y sin dilatación, la capa de geología quedaba
en 3.772 píxeles de 4,2 millones: invisible. Con los defaults actuales son
295.845 píxeles, o sea unas 3 veces el área rasterizada cruda y bastante más que
el área verdadera. **Las áreas reales están en `docs/notas/geocon_mapping_log.md`**
(y ojo, ese log también advierte que sus km² absolutos vienen de una capa
simplificada a 3 km). Correr con `--dilatar 0` da área fiel y casi nada visible.

**La exageración vertical por defecto es 60×.** La Antártica mide 6.667 km de
ancho y unos 4 km de relieve: a escala 1:1 sería una lámina plana. Cualquier
lectura de pendientes o volúmenes desde esta vista es inválida.

## Cómo están hechos los datos

`meta.json` trae el rango de cada capa, las leyendas y los puntos; las elevaciones
van como int16 crudo (512 KB por capa) que Three.js vuelca directo a un
`BufferAttribute`, sin parsear GeoTIFF en el cliente. Las texturas se rasterizan
sobre la misma grilla del DEM, así que relieve y temática quedan alineados —
verificado comparando el centroide por framework contra el de las geometrías
reales: desvíos de 1 a 94 km contra 650-3.111 km si la textura estuviera volteada.

El remuestreo de los DEM promedia por bloques ignorando el nodata en vez de usar
el resampling bilineal de rasterio, que mezclaba el -32768 con los píxeles del
borde y daba a `surface` un mínimo de -72 m cuando el real es 1 m.

## Depuración

`window.visor3d` expone `{escena, camara, render, controles, dibujar()}`.
`requestAnimationFrame` no dispara con la pestaña oculta, así que `dibujar()` es
la forma de forzar un frame y comprobar que el terreno se dibuja.
