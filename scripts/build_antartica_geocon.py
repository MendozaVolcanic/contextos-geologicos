"""
Clasifica la geología antártica en los 9 Geological Frameworks del SCAR EG-GEOCON.

Fuentes normativas (ambas ya en el repo, verificadas contra el original):
  - SCAR ATCM XLIII (2021), Attachment A, Annex 1 — la lista de los 9 GF y el
    alcance de cada uno. docs/biblioteca/scar/atcm/ATCM43_Att-A_2021_*.pdf, pág. 7-8.
  - GEOCON workshop presentation (SCAR ISAES 2025 / OSC 2026) — estado del proceso,
    geositios ya aprobados por GF y la convocatoria GF3/GF4 2026-2028.

Por qué existe este script aparte de build_antartica_frameworks.py
------------------------------------------------------------------
Aquel mapea SIMPCODE → Framework con reglas puramente litocronológicas. Eso no
alcanza, porque **tres de los nueve GF son geográficos antes que litológicos**:

  - GF3 se define "primarily in the Transantarctic Mountains" e incluye la orogenia
    Ross y los orógenos Pan-Africanos. Una misma metamorfita proterozoico-paleozoica
    es GF3 en las TAM o en Dronning Maud Land, y GF2 en el cratón de Enderby.
  - GF4 es el margen activo: Península Antártica, arco de Scotia, rift antártico
    occidental. Un granitoide mesozoico es GF4 en la Península y GF3 en las TAM.

Por eso acá la regla es (SIMPCODE, región) → GF, no SIMPCODE → GF.

Entrada:  app/data/antartica_simplecode.geojson  (21 clases ya disueltas, versionado)
Salida:   app/data/antartica_geocon.geojson      (agrupado por GF)
          docs/notas/geocon_mapping_log.md       (auditoría de cada decisión)

No necesita geopandas: trabaja sobre el GeoJSON derivado que ya está en el repo.

Uso:
    python scripts/build_antartica_geocon.py [--sin-geojson]
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "app" / "data" / "antartica_simplecode.geojson"
OUT_GEO = ROOT / "app" / "data" / "antartica_geocon.geojson"
OUT_LOG = ROOT / "docs" / "notas" / "geocon_mapping_log.md"

R_TIERRA_KM = 6371.0

# --------------------------------------------------------------------------
# Los 9 Geological Frameworks, literal de ATCM43 Att. A, Annex 1, pág. 7-8.
# --------------------------------------------------------------------------
GF = {
    1: ("Archean cratons",
        "Formación y ruptura de supercontinentes; ciclos de dispersión y ensamble; "
        "episodios orogénicos, unidades petrológicas y estructurales mayores; vida temprana."),
    2: ("Proterozoic orogens and Neoproterozoic–early Palaeozoic rifted margins",
        "Formación y ruptura de Rodinia; episodios orogénicos y vida temprana."),
    3: ("Gondwana amalgamation and breakup",
        "Secuencias sedimentarias y rocas ígneo-metamórficas asociadas; subducción del "
        "margen Panthalásico (orogenia Ross); orógenos/suturas Pan-Africanos; peneplanicie "
        "de Kukri; secuencias de cobertura Gondwana; Ferrar LIP. Evidencia principalmente "
        "en las Transantarctic Mountains."),
    4: ("Geological history of Antarctica's active margin and West Antarctic rift system",
        "Historia de subducción; cuencas y magmatismo de arco; gateways de Tasman y Drake; "
        "arco de Scotia; volcanismo; back-arc de Bransfield; rift antártico occidental."),
    5: ("The Cretaceous–Palaeogene (K-Pg) transition",
        "Registros paleontológicos y geoquímicos de la extinción masiva K-Pg."),
    6: ("Cenozoic glacial history",
        "Registros sedimentarios continentales y marinos; formación y comportamiento de los "
        "sistemas glaciales; fluctuaciones del hielo; nivel del mar; hielo antiguo."),
    7: ("Meteorites and evidence of impacts",
        "Rasgos petrológicos y morfológicos relacionados con impactos meteoríticos."),
    8: ("Subglacial water bodies, deposits and morphological features",
        "Morfología subglacial, lagos y redes fluviales subglaciales."),
    9: ("Geological features or materials which cannot be included in other frameworks",
        "Minerales, rocas, fósiles, suelos, permafrost, estructuras o landforms de interés "
        "científico que no encajan en los otros ocho, incluidas localidades tipo."),
}

# --------------------------------------------------------------------------
# Regiones. Cada una es (lat_min, lat_max, lon_min, lon_max) en EPSG:4326.
#
# FELIPE: ESTE ES EL BLOQUE A REVISAR. Los límites son aproximaciones de lectura
# cartográfica, no contornos publicados. Cada uno lleva anotado de dónde sale.
# El log de salida dice cuántos polígonos cayó en cada uno, así que se puede medir
# el efecto de mover cualquiera de estos números.
# --------------------------------------------------------------------------

# Cinturón Transantarctic Mountains. No se dibuja a mano: se deriva de dónde
# aparecen realmente el Beacon Supergroup (50) y el Ferrar (42) en el dataset,
# que son los marcadores diagnósticos de GF3. Ver derivar_corredor_tam().
SIMPCODE_DIAGNOSTICOS_TAM = (50, 42)
TAM_BIN_LAT = 2.0      # tamaño de celda para el corredor derivado
TAM_BIN_LON = 5.0

# Celdas de vecindad admitidas alrededor del corredor. Default 0 = solo celdas
# donde hay Beacon o Ferrar de verdad.
#
# Es el parámetro más influyente de todo el mapping y por eso el default es el
# conservador. Medido sobre el dataset actual, al dilatar el corredor GF2 se
# desangra hacia GF3:
#
#     holgura 0 → GF2 3.409 km² (8,2%)   GF3 19.987 km² (48,3%)
#     holgura 1 → GF2   844 km² (2,0%)   GF3 22.579 km² (54,6%)
#     holgura 2 → GF2   513 km² (1,2%)   GF3 22.914 km² (55,4%)
#
# O sea GF3 es robusto (~48-55%) pero el límite GF2/GF3 no lo es: una celda de
# dilatación se lleva tres cuartos del área de GF2. Como las celdas ya miden
# ~222 x 115 km a esas latitudes, dilatar sin evidencia no se justifica.
# Correr con --sensibilidad para recalcular esta tabla.
TAM_HOLGURA = 0

# Orógenos Pan-Africanos de la Antártica Oriental → GF3 según ATCM43
# ("Pan African orogens/sutures"). Anclado en los geositios GF3 que la propia
# presentación GEOCON ya nominó: Rundvågshetta (Lützow-Holm, ~39°E),
# Sør Rondane (~23°E), Trollslottet y Jutulhogget (Dronning Maud central, ~6-12°E).
CINTURON_PANAFRICANO = (-76.0, -66.0, -15.0, 45.0)

# Cratón de Enderby / Complejo Rayner: grenviliano (~990-900 Ma), o sea ciclo
# Rodinia → GF2, no Pan-Africano. Se excluye a propósito del bbox anterior.
# (El Complejo Napier, arqueano, cae solo por SIMPCODE 70 → GF1.)
SECTOR_RAYNER = (-71.0, -65.0, 45.0, 60.0)

# Margen activo → GF4.
REGIONES_MARGEN_ACTIVO = [
    ("Península Antártica y Shetland del Sur", (-75.0, -60.0, -85.0, -50.0)),
    ("Islas Orcadas del Sur (arco de Scotia)", (-62.0, -60.0, -47.0, -44.0)),
    ("Islas Sandwich del Sur (arco de Scotia)", (-60.0, -56.0, -29.0, -25.0)),
    ("Marie Byrd Land y rift antártico occidental", (-85.0, -70.0, -160.0, -90.0)),
]

# GF5: la transición K-Pg tiene un único geositio formalmente seleccionado
# (ATCM43 Annex 1, paso 2): isla Marambio/Seymour, 64°17'15"S 56°44'07"W.
# No es una clase litológica: es un horizonte dentro del SIMPCODE 40.
SEYMOUR_KPG = (-64.5, -64.0, -57.0, -56.3)


def centroide_anillo(anillo):
    """Centroide del anillo exterior por la fórmula del área con signo (shoelace)."""
    n = len(anillo)
    if n < 3:
        return None
    a = cx = cy = 0.0
    for i in range(n - 1):
        x0, y0 = anillo[i][0], anillo[i][1]
        x1, y1 = anillo[i + 1][0], anillo[i + 1][1]
        cruz = x0 * y1 - x1 * y0
        a += cruz
        cx += (x0 + x1) * cruz
        cy += (y0 + y1) * cruz
    if abs(a) < 1e-12:                       # degenerado: promedio simple
        return (sum(p[0] for p in anillo) / n, sum(p[1] for p in anillo) / n)
    a *= 0.5
    return (cx / (6 * a), cy / (6 * a))


def area_esferica_km2(anillo):
    """Área del anillo sobre la esfera. Independiente de la proyección.

    Se usa esto en vez del área plana en EPSG:4326 porque en latitudes antárticas
    un grado de longitud vale una fracción muy chica de un grado de latitud, y el
    área plana sobreestimaría el interior del continente por un factor enorme.
    """
    n = len(anillo)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n - 1):
        lon0, lat0 = math.radians(anillo[i][0]), math.radians(anillo[i][1])
        lon1, lat1 = math.radians(anillo[i + 1][0]), math.radians(anillo[i + 1][1])
        dlon = lon1 - lon0
        # normalizar el cruce del antimeridiano
        if dlon > math.pi:
            dlon -= 2 * math.pi
        elif dlon < -math.pi:
            dlon += 2 * math.pi
        total += dlon * (2 + math.sin(lat0) + math.sin(lat1))
    return abs(total * R_TIERRA_KM ** 2 / 2.0)


def dentro(bbox, lon, lat):
    lat_min, lat_max, lon_min, lon_max = bbox
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def en_margen_activo(lon, lat):
    for nombre, bbox in REGIONES_MARGEN_ACTIVO:
        if dentro(bbox, lon, lat):
            return nombre
    return None


def partes(geom):
    """Itera los anillos exteriores de un Polygon o MultiPolygon."""
    t = geom.get("type")
    if t == "Polygon":
        if geom["coordinates"]:
            yield geom["coordinates"][0], geom["coordinates"]
    elif t == "MultiPolygon":
        for poly in geom["coordinates"]:
            if poly:
                yield poly[0], poly


def derivar_corredor_tam(feats):
    """Celdas que ocupan Beacon (50) y Ferrar (42): el corredor TAM empírico.

    Preferimos derivarlo del dato antes que dibujar bboxes a mano. El Beacon y el
    Ferrar son los marcadores de GF3 por definición de ATCM43, así que dónde están
    ellos está el cinturón donde el basamento subyacente es orogenia Ross.
    """
    celdas = set()
    for f in feats:
        if f["properties"]["simplecode"] not in SIMPCODE_DIAGNOSTICOS_TAM:
            continue
        for anillo, _ in partes(f["geometry"]):
            c = centroide_anillo(anillo)
            if c:
                celdas.add((int(c[1] // TAM_BIN_LAT), int(c[0] // TAM_BIN_LON)))
    # dilatar el corredor en TAM_HOLGURA celdas
    dilatado = set()
    for by, bx in celdas:
        for dy in range(-TAM_HOLGURA, TAM_HOLGURA + 1):
            for dx in range(-TAM_HOLGURA, TAM_HOLGURA + 1):
                dilatado.add((by + dy, bx + dx))
    return celdas, dilatado


def en_corredor_tam(corredor, lon, lat):
    return (int(lat // TAM_BIN_LAT), int(lon // TAM_BIN_LON)) in corredor


def clasificar(simpcode, lon, lat, corredor_tam):
    """(SIMPCODE, posición) → (gf, regla). gf=None significa 'no es geología clasificable'."""
    s = simpcode
    margen = en_margen_activo(lon, lat)

    # --- No son roca: fuera de la clasificación, no a GF9 ---
    # GF9 es "rasgos geológicos de interés que no encajan en los otros ocho", no un
    # cajón para el dato ausente. Mandar agua estacional a GF9 lo vacía de sentido.
    if s == 10:
        return None, "Agua/hielo estacional — no es unidad geológica, se excluye"
    if s == 11:
        return None, "Roca desconocida o sin clasificar — sin dato para asignar GF"

    # --- Arqueano ---
    if s == 70:
        return 1, "Arqueano metamórfico/intrusivo → GF1 cratones arqueanos"

    # --- Basamento Proterozoico-Paleozoico: acá se juega GF2 vs GF3 ---
    if 60 <= s <= 63:
        if margen:
            return 4, f"Basamento Pz en {margen} → GF4 (basamento del margen activo)"
        if en_corredor_tam(corredor_tam, lon, lat):
            return 3, "Basamento Pz en corredor TAM → GF3 (orogenia Ross)"
        if dentro(SECTOR_RAYNER, lon, lat):
            return 2, "Basamento en sector Enderby/Rayner (grenviliano) → GF2 (ciclo Rodinia)"
        if dentro(CINTURON_PANAFRICANO, lon, lat):
            return 3, "Basamento en cinturón Pan-Africano (DML/Sør Rondane/Lützow-Holm) → GF3"
        return 2, "Basamento Proterozoico-Paleozoico, resto de Antártica Oriental → GF2"

    # --- Cobertura Gondwana y LIP ---
    if s == 50:
        return 3, "Beacon Supergroup → GF3 (secuencia clásica de cobertura Gondwana)"
    if s == 42:
        return 3, "Ferrar Igneous Province → GF3 (LIP de ruptura de Gondwana)"

    # --- Magmatismo silícico jurásico: Gondwana en el este, arco en el oeste ---
    if s == 43:
        if margen:
            return 4, f"Volcanismo silícico jurásico en {margen} → GF4"
        return 3, "Volcanismo silícico y sedimentario continental jurásico → GF3 (ruptura de Gondwana)"

    # --- Mesozoico intrusivo / metamórfico ---
    if s in (44, 45):
        if margen:
            return 4, f"Intrusivo/metamórfico mesozoico en {margen} → GF4 (arco andino)"
        if en_corredor_tam(corredor_tam, lon, lat):
            return 3, "Intrusivo/metamórfico mesozoico en corredor TAM → GF3"
        return 4, "Intrusivo/metamórfico mesozoico fuera de región conocida → GF4 (revisar)"

    # --- Mesozoico-Paleógeno sedimentario y volcánico ---
    if s in (40, 41):
        if dentro(SEYMOUR_KPG, lon, lat):
            return 5, "Sedimentario J-Pg en isla Marambio/Seymour → GF5 (tránsito K-Pg)"
        if margen:
            return 4, f"Sedimentario/volcánico J-Pg en {margen} → GF4 (cuencas de arco)"
        return 4, "Sedimentario/volcánico J-Pg fuera de región conocida → GF4 (revisar)"

    # --- Cenozoico ígneo y sedimentario ---
    if s in (30, 31, 32):
        if margen:
            return 4, f"Ígneo/sedimentario cenozoico en {margen} → GF4"
        return 4, "Ígneo/sedimentario cenozoico fuera de región conocida → GF4 (revisar)"

    # --- Cuaternario-Neógeno glacial ---
    if 20 <= s <= 23:
        return 6, "Depósito glacial Neógeno-Cuaternario → GF6 (historia glacial cenozoica)"

    return None, f"SIMPCODE {s} sin regla"


def barrer_sensibilidad(feats, unidades, holguras=(0, 1, 2, 3)):
    """Cómo cambia el reparto por GF al dilatar el corredor TAM.

    El corredor es la única decisión paramétrica del mapping, así que conviene
    publicar cuánto depende el resultado de ella en vez de dar un número solo.
    """
    global TAM_HOLGURA
    guardado = TAM_HOLGURA
    filas = []
    for h in holguras:
        TAM_HOLGURA = h
        _, corredor = derivar_corredor_tam(feats)
        area = defaultdict(float)
        for s, lon, lat, a, _ in unidades:
            gf, _regla = clasificar(s, lon, lat, corredor)
            if gf is not None:
                area[gf] += a
        total = sum(area.values())
        filas.append((h, len(corredor),
                      {g: (area.get(g, 0.0), 100 * area.get(g, 0.0) / total if total else 0)
                       for g in sorted(GF)}))
    TAM_HOLGURA = guardado
    return filas


def main(argv):
    global TAM_HOLGURA

    ap = argparse.ArgumentParser(description="Clasifica GeoMAP en los 9 GF del EG-GEOCON")
    ap.add_argument("--sin-geojson", action="store_true",
                    help="solo calcula y escribe el log, sin generar el GeoJSON (17 MB)")
    ap.add_argument("--holgura", type=int, default=TAM_HOLGURA,
                    help=f"celdas de dilatación del corredor TAM (default {TAM_HOLGURA}). "
                         f"Es el parámetro más influyente del mapping: subirlo manda más "
                         f"basamento a GF3 y menos a GF2.")
    ap.add_argument("--sensibilidad", action="store_true",
                    help="agrega al log cuánto cambia el reparto por GF según la holgura")
    args = ap.parse_args(argv[1:])
    TAM_HOLGURA = args.holgura

    if not SRC.exists():
        print(f"[ERROR] No existe {SRC}", file=sys.stderr)
        return 1

    print(f"Leyendo {SRC.name}...", flush=True)
    data = json.loads(SRC.read_text(encoding="utf-8"))
    feats = data["features"]
    meta = {f["properties"]["simplecode"]: f["properties"] for f in feats}
    print(f"  {len(feats)} clases SIMPCODE")

    celdas, corredor = derivar_corredor_tam(feats)
    print(f"  corredor TAM derivado de Beacon+Ferrar: {len(celdas)} celdas "
          f"({len(corredor)} con holgura de {TAM_HOLGURA})")

    # Una sola pasada geométrica (centroide + área esférica), que es lo caro.
    # Después clasificar es barato, así que el barrido de sensibilidad sale casi gratis.
    print("  calculando centroides y áreas...", flush=True)
    unidades = []          # (simpcode, lon, lat, area_km2, poly)
    total_partes = 0
    for f in feats:
        s = f["properties"]["simplecode"]
        for anillo, poly in partes(f["geometry"]):
            total_partes += 1
            c = centroide_anillo(anillo)
            if c is None:
                continue
            unidades.append((s, c[0], c[1], area_esferica_km2(anillo), poly))

    por_gf_partes = Counter()
    por_gf_area = defaultdict(float)
    por_regla = Counter()
    area_regla = defaultdict(float)
    geoms_por_gf = defaultdict(list)
    excluidas_partes = 0
    excluidas_area = 0.0

    for s, lon, lat, area, poly in unidades:
        gf, regla = clasificar(s, lon, lat, corredor)
        por_regla[regla] += 1
        area_regla[regla] += area
        if gf is None:
            excluidas_partes += 1
            excluidas_area += area
            continue
        por_gf_partes[gf] += 1
        por_gf_area[gf] += area
        if not args.sin_geojson:
            geoms_por_gf[gf].append(poly)

    area_total = sum(por_gf_area.values())

    sensibilidad = barrer_sensibilidad(feats, unidades) if args.sensibilidad else None
    print(f"\n{'='*74}\nDISTRIBUCIÓN POR GEOLOGICAL FRAMEWORK\n{'='*74}")
    print(f"{'GF':<4}{'polígonos':>11}{'área km²':>14}{'%':>7}  nombre")
    for g in sorted(GF):
        n = por_gf_partes.get(g, 0)
        a = por_gf_area.get(g, 0.0)
        pct = 100 * a / area_total if area_total else 0
        marca = "" if n else "   ← sin asignar desde litología"
        print(f"GF{g:<2}{n:>11,}{a:>14,.0f}{pct:>6.1f}%  {GF[g][0][:44]}{marca}")
    print(f"{'—':<4}{excluidas_partes:>11,}{excluidas_area:>14,.0f}{'':>7}  "
          f"excluidas (agua/hielo estacional y roca sin clasificar)")
    print(f"\nPartes procesadas: {total_partes:,}")

    escribir_log(por_gf_partes, por_gf_area, area_total, por_regla, area_regla,
                 excluidas_partes, excluidas_area, celdas, corredor, meta, total_partes,
                 sensibilidad)
    print(f"Log escrito: {OUT_LOG}")

    if not args.sin_geojson:
        feats_out = []
        for g in sorted(geoms_por_gf):
            feats_out.append({
                "type": "Feature",
                "properties": {
                    "id": f"gf-{g}",
                    "framework": g,
                    "nombre": GF[g][0],
                    "descripcion": GF[g][1],
                    "poligonos": por_gf_partes[g],
                    "area_km2": round(por_gf_area[g], 1),
                },
                "geometry": {"type": "MultiPolygon", "coordinates": geoms_por_gf[g]},
            })
        fc = {
            "type": "FeatureCollection",
            "_source": "SCAR/GNS GeoMAP v2022.08 (Cox et al. 2023) reclasificado a los 9 "
                       "Geological Frameworks de SCAR ATCM XLIII (2021) Att. A, Annex 1",
            "_processing": "scripts/build_antartica_geocon.py — reglas (SIMPCODE, región) → GF",
            "_advertencia": "Los límites regionales son aproximaciones de lectura cartográfica, "
                            "no contornos publicados. Ver docs/notas/geocon_mapping_log.md.",
            "features": feats_out,
        }
        OUT_GEO.parent.mkdir(parents=True, exist_ok=True)
        OUT_GEO.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
        print(f"GeoJSON escrito: {OUT_GEO} ({OUT_GEO.stat().st_size/1024**2:.1f} MB)")

    return 0


def escribir_log(por_gf_partes, por_gf_area, area_total, por_regla, area_regla,
                 excl_n, excl_a, celdas, corredor, meta, total_partes,
                 sensibilidad=None):
    L = []
    L.append("# Auditoría del mapping GeoMAP → 9 Geological Frameworks (EG-GEOCON)\n")
    L.append("Generado por `scripts/build_antartica_geocon.py`. **No editar a mano.**\n")
    L.append("Fuente normativa de los 9 GF: SCAR ATCM XLIII (2021), Attachment A, Annex 1, "
             "págs. 7-8 — `docs/biblioteca/scar/atcm/ATCM43_Att-A_2021_Method_Identification_"
             "Antarctic_Geological_Sites.pdf`. Estado del proceso y geositios aprobados: "
             "presentación del workshop GEOCON (SCAR ISAES 2025 / OSC 2026).\n")
    L.append(f"Partes de polígono procesadas: **{total_partes:,}**\n")

    L.append("> **Cómo leer las áreas.** Salen de `antartica_simplecode.geojson`, que está "
             "*simplificado a 3 km* y disuelto por SIMPCODE. Muchos afloramientos antárticos "
             "miden menos que esa tolerancia, así que los km² absolutos están inflados: acá "
             "dan ~33.000 km² de roca (sin contar depósitos glaciales) contra los 21.745 km² "
             "de afloramiento real que publican Burton-Johnson et al. (2016). **Las "
             "proporciones entre frameworks son el resultado utilizable; los valores "
             "absolutos no.** Para áreas reales hay que correr sobre la geodatabase original "
             "en `docs/mapas/antartica/`, que necesita geopandas.\n")

    L.append("## Distribución por Framework\n")
    L.append("| GF | Nombre | Polígonos | Área km² | % del área clasificada |")
    L.append("|---|---|---:|---:|---:|")
    for g in sorted(GF):
        n = por_gf_partes.get(g, 0)
        a = por_gf_area.get(g, 0.0)
        pct = 100 * a / area_total if area_total else 0
        L.append(f"| GF{g} | {GF[g][0]} | {n:,} | {a:,.0f} | {pct:.1f}% |")
    L.append(f"| — | *excluidas: agua/hielo estacional y roca sin clasificar* | "
             f"{excl_n:,} | {excl_a:,.0f} | — |")
    L.append("")

    L.append("## Conteo por regla aplicada\n")
    L.append("| Polígonos | Área km² | Regla |")
    L.append("|---:|---:|---|")
    for regla, n in por_regla.most_common():
        L.append(f"| {n:,} | {area_regla[regla]:,.0f} | {regla} |")
    L.append("")

    L.append("## Corredor TAM derivado del dato\n")
    L.append(f"El cinturón Transantarctic no se dibujó a mano: se derivó de dónde aparecen "
             f"realmente el Beacon Supergroup (SIMPCODE 50) y el Ferrar (42), que son los "
             f"marcadores diagnósticos de GF3 según ATCM43. Resultado: **{len(celdas)} celdas** "
             f"de {TAM_BIN_LAT}°×{TAM_BIN_LON}°, dilatadas a {len(corredor)} con una holgura "
             f"de {TAM_HOLGURA} celda(s).\n")

    if sensibilidad:
        L.append("### Sensibilidad a ese corredor\n")
        L.append("La holgura del corredor es la única decisión paramétrica del mapping, así "
                 "que conviene ver cuánto depende el resultado de ella:\n")
        L.append("| Holgura | Celdas | GF1 | GF2 | GF3 | GF4 | GF6 |")
        L.append("|---:|---:|---:|---:|---:|---:|---:|")
        for h, nceldas, por_g in sensibilidad:
            cols = " | ".join(f"{por_g[g][1]:.1f}%" for g in (1, 2, 3, 4, 6))
            L.append(f"| {h} | {nceldas} | {cols} |")
        L.append("\n**Lectura:** GF3 es robusto, pero el límite GF2/GF3 no lo es — una sola "
                 "celda de dilatación se lleva la mayor parte del área de GF2. Por eso el "
                 "default es holgura 0: solo celdas donde hay Beacon o Ferrar de verdad.\n")

    L.append("## Lo que NO se puede asignar desde la litología\n")
    L.append("Tres frameworks no salen de un mapa geológico y necesitan otra fuente:\n")
    L.append("- **GF5 (tránsito K-Pg)** — es un horizonte estratigráfico, no una clase "
             "litológica. Solo se asigna por posición, en isla Marambio/Seymour, que es el "
             "único geositio K-Pg formalmente seleccionado (ATCM43, Annex 1, paso 2).")
    L.append("- **GF7 (meteoritos e impactos)** — son campos de hielo azul, no roca aflorante. "
             "GeoMAP no los trae. Requiere el inventario de meteorite fields (Yamato, Allan "
             "Hills, Miller Range...). La presentación GEOCON ya aprobó Yamato Mountains como "
             "geositio GF7 y sitio IUGS.")
    L.append("- **GF8 (cuerpos de agua subglaciales)** — morfología y lagos bajo el hielo. "
             "Requiere BedMap3 y el inventario de lagos subglaciales. El repo ya tiene "
             "`scripts/build_bedmap.py`, así que es el más alcanzable de los tres.\n")
    L.append("**GF9** tampoco se asigna por litología, y a propósito: ATCM43 lo define como "
             "rasgos de interés científico que no encajan en los otros ocho, no como cajón "
             "del dato ausente. Se asigna sitio por sitio, no polígono por polígono.\n")

    L.append("## Límites regionales — revisar\n")
    L.append("Los bboxes son aproximaciones de lectura cartográfica, **no contornos "
             "publicados**. Están todos juntos al inicio del script. Los que más pesan:\n")
    L.append(f"- Cinturón Pan-Africano `{CINTURON_PANAFRICANO}` — decide GF3 vs GF2 en "
             "Dronning Maud Land. Anclado en los geositios GF3 que GEOCON ya nominó ahí "
             "(Trollslottet, Jutulhogget, Sør Rondane, Rundvågshetta/Lützow-Holm).")
    L.append(f"- Sector Enderby/Rayner `{SECTOR_RAYNER}` — se excluye del anterior porque el "
             "Complejo Rayner es grenviliano (~990-900 Ma), o sea ciclo Rodinia → GF2.")
    L.append("- Regiones de margen activo → GF4: " +
             ", ".join(f"{n} `{b}`" for n, b in REGIONES_MARGEN_ACTIVO))
    L.append("")

    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOG.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
