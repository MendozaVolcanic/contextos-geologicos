"""
Separa geositios SCAR oficiales, nominaciones y potenciales.

Por qué hace falta
------------------
`app/data/antartica_geositios.geojson` traía 81 puntos rotulados como "geositios
SCAR", pero solo uno lo era de verdad. La composición real era:

  72  ASPAs — Areas Antarticas Especialmente Protegidas, bajadas de Quantarctica.
      Son otra figura: tienen estatus legal bajo el Tratado Antartico, mientras
      que los geositios SCAR explicitamente NO lo tienen (presentacion GEOCON,
      lamina 3). Mezclarlos era un error de categoria.
   7  marcados "SCAR-geosite", de los cuales solo Seymour esta aprobado; el resto
      eran semillas inferidas de la bibliografia.
   2  candidatos.

Este script asigna un campo `estatus` a cada punto y agrega los geositios que la
presentacion GEOCON nombra explicitamente:

  aprobado   Geositio SCAR formalmente aprobado.
  nominado   Propuesto en la convocatoria GF3/GF4 2026-2028, sin resolver.
  potencial  Candidato nuestro, sacado de la bibliografia. No tiene estatus SCAR.
  aspa       Area protegida del Tratado. No es un geositio.

Fuentes normativas
------------------
- Presentacion del workshop GEOCON (SCAR ISAES 2025 / OSC 2026), laminas 5-23.
- SCAR ATCM XLIII (2021) Att. A, Annex 1, para el geositio K-Pg y sus coordenadas.
- Coordenadas: SCAR Composite Gazetteer (docs/biblioteca/scar_gazetteer.csv,
  33.495 entradas). Se resuelven por nombre y se deja anotado cual se uso, porque
  varios topónimos se repiten en la Antartica.

Uso:
    python scripts/build_geositios_geocon.py [--dry-run]
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
GEOSITIOS = DATA / "antartica_geositios.geojson"
GAZETTEER = ROOT / "docs" / "biblioteca" / "scar_gazetteer.csv"

csv.field_size_limit(10_000_000)

# ---------------------------------------------------------------------------
# Geositios SCAR aprobados. Lamina de la presentacion entre parentesis.
#
# `gazetteer` es el topónimo exacto con que se resuelve la coordenada. Donde el
# geositio no coincide con un topónimo (el complejo lleva un nombre compuesto que
# el gazetteer no registra), se usa el rasgo geografico que lo contiene y queda
# dicho en `nota_ubicacion`.
# ---------------------------------------------------------------------------
APROBADOS = [
    {
        "codigo": "GEOCON-GF5-01",
        "nombre": "Transición Cretácico-Paleógeno (K-Pg), isla Marambio (Seymour)",
        "framework": 5,
        "coords": (-64.2875, -56.7353),   # 64°17'15\"S 56°44'07\"W, ATCM43 Att. A
        "fuente": "SCAR ATCM XLIII (2021) Att. A, Annex 1",
        "nota_ubicacion": "Coordenada oficial del centro del geositio, no del gazetteer.",
        "iugs": False,
        "descripcion": "Uno de los mejores registros del límite K-Pg del planeta y el "
                       "único aflorante confirmado en la Antártica. Primer geositio "
                       "seleccionado por el método SCAR.",
    },
    {
        "codigo": "GEOCON-GF1-01",
        "nombre": "Complejo estratificado Torckler-Tang Øy, islas Rauer",
        "framework": 1, "gazetteer": "Torckler Island",
        "fuente": "Presentación GEOCON, lámina 6",
        "iugs": False,
        "descripcion": "Intrusión máfica-ultramáfica de 3280-3300 Ma, uno de los complejos "
                       "ígneos estratificados más antiguos conocidos. Conserva estructuras "
                       "sin-magmáticas: bandeamiento gradado y rítmico, cumulados piroxeníticos.",
    },
    {
        "codigo": "GEOCON-GF1-02",
        "nombre": "Paragneis de Taynaya, Vestfold Hills",
        "framework": 1, "gazetteer": "Taynaya Bay",
        "fuente": "Presentación GEOCON, lámina 7",
        "iugs": False,
        "descripcion": "Metasedimentos químicos ultra-magnesianos del Arqueano tardío: "
                       "safirina-espinela-enstatita casi puros, prácticamente sin hierro.",
    },
    {
        "codigo": "GEOCON-GF1-03",
        "nombre": "Complejo estratificado Shcherbinina, islas Rauer",
        "framework": 1, "gazetteer": "Shcherbinina Island",
        "fuente": "Presentación GEOCON, lámina 8",
        "iugs": False,
        "descripcion": "Complejo máfico estratificado de 2840 Ma (diorita-ferrodiorita-"
                       "ferrogabro) metamorfizado en facies granulita, con bandeamiento "
                       "ígneo gradado y texturas ofíticas remanentes.",
    },
    {
        "codigo": "GEOCON-GF1-04",
        "nombre": "Ortogneis tonalítico de Mount Sones, Enderby Land",
        "framework": 1, "gazetteer": "Mount Sones",
        "fuente": "Presentación GEOCON, lámina 9",
        "iugs": True,
        "descripcion": "Litología eoarqueana datada en ~3850 Ma. Sus dataciones U-Pb en "
                       "circón impulsaron la investigación sobre el comportamiento del Pb "
                       "a nanoescala. Aprobado como IUGS Third 100 junto a Mount Riiser-Larsen.",
    },
    {
        "codigo": "GEOCON-GF1-05",
        "nombre": "Metamorfismo UHT de Mount Riiser-Larsen, Enderby Land",
        "framework": 1, "gazetteer": "Mount Riiser-Larsen",
        "fuente": "Presentación GEOCON, lámina 10",
        "iugs": True,
        "descripcion": "Asociación UHT definitoria safirina + ortopiroxeno + cuarzo, con "
                       "osumilita y plegamiento isoclinal por deformación UHT. Aprobado "
                       "como IUGS Third 100 junto a Mount Sones.",
    },
    {
        "codigo": "GEOCON-GF1-06",
        "nombre": "Pegmatitas de berilio de Casey Bay, Enderby Land",
        "framework": 1, "gazetteer": "Christmas Point",
        "fuente": "Presentación GEOCON, lámina 11",
        "nota_ubicacion": "Localidad de las pegmatitas dentro de Casey Bay.",
        "iugs": False,
        "descripcion": "Única ocurrencia conocida en el mundo de mineralización de berilio "
                       "a alta temperatura.",
    },
    {
        "codigo": "GEOCON-GF7-01",
        "nombre": "Campos de meteoritos de las montañas Yamato",
        "framework": 7, "gazetteer": "Yamato Sanmyaku",
        "fuente": "Presentación GEOCON, lámina 12",
        "iugs": True,
        "descripcion": "~14.000 meteoritos recuperados de los campos de hielo azul, una de "
                       "las principales fuentes mundiales. Colección curada en el NIPR. "
                       "Aprobado como IUGS Third 100.",
    },
]

# ---------------------------------------------------------------------------
# Nominaciones de la convocatoria GF3/GF4 2026-2028. Propuestas, sin resolver.
# ---------------------------------------------------------------------------
NOMINADOS = [
    {
        "codigo": "GEOCON-GF3-N1", "framework": 3, "gazetteer": "Rundvågshetta",
        "nombre": "Rundvågshetta, complejo de Lützow-Holm",
        "fuente": "Presentación GEOCON, lámina 15",
        "descripcion": "Granulitas pelíticas y máficas de alta a ultra-alta temperatura; "
                       "registro de eventos del Neoproterozoico tardío (~600 a ~530 Ma) "
                       "durante la amalgamación de Gondwana.",
    },
    {
        "codigo": "GEOCON-GF3-N2", "framework": 3, "gazetteer": "Sør Rondane Mountains",
        "nombre": "Montañas Sør Rondane",
        "fuente": "Presentación GEOCON, lámina 16",
        "descripcion": "Registro de dos eventos metamórficos neoproterozoicos (~600 y "
                       "~550 Ma), historia colisional multi-etapa. Localidad tipo del "
                       "mineral dissakisita-Ce.",
    },
    {
        "codigo": "GEOCON-GF3-N3", "framework": 3, "gazetteer": "Trollslottet",
        "nombre": "Complejo intrusivo Trollslottet, Filchnerfjella (Dronning Maud central)",
        "fuente": "Presentación GEOCON, lámina 17",
        "descripcion": "Infiltración de fluidos tardi-magmáticos en la fase final del "
                       "orógeno Pan-Africano. Las zonas de alteración se extienden por "
                       "cientos de km: ejemplo de libro a escala global.",
    },
    {
        "codigo": "GEOCON-GF3-N4", "framework": 3, "gazetteer": "Jutulhogget",
        "nombre": "Gneis de Jutulhogget (Dronning Maud central)",
        "fuente": "Presentación GEOCON, lámina 18",
        "descripcion": "Evolución tectonometamórfica polifásica del cinturón Maud, desde "
                       "el Mesoproterozoico hasta la orogenia Ediacárico-Cámbrico. Permite "
                       "trazar fundidos anatécticos desde la fuente hasta el dique.",
    },
    {
        "codigo": "GEOCON-GF3-N5", "framework": 3, "gazetteer": "Fremouw Peak",
        "nombre": "Turba silicificada de Fremouw Peak",
        "fuente": "Presentación GEOCON, lámina 19",
        "descripcion": "Turba permineralizada del Triásico medio-tardío con flora, hongos "
                       "y una cianobacteria. La permineralización preserva anatomía a nivel "
                       "celular, algo raro en el registro vegetal mundial.",
    },
    {
        "codigo": "GEOCON-GF3-N6", "framework": 3, "gazetteer": "Skaar Ridge",
        "nombre": "Turba silicificada de Skaar Ridge, glaciar Beardmore",
        "fuente": "Presentación GEOCON, lámina 20",
        "descripcion": "Turba del Pérmico superior con flora de Glossopteris permineralizada. "
                       "Los anillos de crecimiento fósiles aportan datos paleoclimáticos.",
    },
    {
        "codigo": "GEOCON-GF3-N7", "framework": 3, "gazetteer": "The Palisades",
        "nombre": "The Palisades",
        "fuente": "Presentación GEOCON, lámina 21",
        "en_espera": True,
        "descripcion": "Contacto entre la Formación Goldie neoproterozoica plegada y la "
                       "Caliza Shackleton cámbrica suprayacente. ATENCIÓN: la presentación "
                       "dice que se pidió justificación geológica adicional y que NO se está "
                       "considerando como nominación por ahora.",
    },
    {
        "codigo": "GEOCON-GF4-N1", "framework": 4, "gazetteer": "Hope Bay",
        "nombre": "Registro Pérmico-Mesozoico de Hope Bay",
        "fuente": "Presentación GEOCON, lámina 22",
        "descripcion": "Al menos cuatro unidades sedimentarias, volcánicas y plutónicas que "
                       "componen un registro muy completo del margen activo de la Península "
                       "Antártica, del Permo-Triásico al Cretácico.",
    },
    {
        "codigo": "GEOCON-GF4-N2", "framework": 4, "gazetteer": "Dufek Massif",
        "nombre": "Intrusión máfica estratificada de Dufek",
        "fuente": "Presentación GEOCON, lámina 23",
        "nota_ubicacion": "Resuelto al Dufek Massif (Pensacola), no a Dufek Coast ni "
                          "Dufekfjellet, que son otros rasgos homónimos.",
        "descripcion": "Una de las mayores intrusiones máficas estratificadas del mundo: "
                       ">6.600 km² expuestos y 8-9 km de espesor. Emplazada hacia los 183 Ma "
                       "durante la ruptura de Gondwana; probable conducto de los basaltos Ferrar.",
    },
]

NOMBRES_GF = {
    1: "Archean cratons",
    3: "Gondwana amalgamation and breakup",
    4: "Active margin & West Antarctic rift system",
    5: "Cretaceous-Palaeogene (K-Pg) transition",
    7: "Meteorites and evidence of impacts",
}


def cargar_gazetteer():
    """{nombre en minúsculas: (lat, lon, tipo)} del SCAR Composite Gazetteer."""
    if not GAZETTEER.exists():
        print(f"[ERROR] Falta {GAZETTEER}.\n"
              "        Es parte de los datos pesados; ver docs/bibliografia/PENDIENTES_DESCARGA.md",
              file=sys.stderr)
        return None
    idx = {}
    with GAZETTEER.open(encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            nombre = (fila.get("place_name_mapping") or "").strip()
            if not nombre:
                continue
            try:
                lat, lon = float(fila["latitude"]), float(fila["longitude"])
            except (TypeError, ValueError, KeyError):
                continue
            idx.setdefault(nombre.lower(), (lat, lon, fila.get("feature_type_name", "")))
    return idx


def resolver(entrada, gaz):
    """Coordenada explícita si la trae; si no, la del gazetteer."""
    if "coords" in entrada:
        return entrada["coords"], "coordenada oficial del documento"
    clave = entrada["gazetteer"].lower()
    if clave not in gaz:
        return None, f"NO se encontró '{entrada['gazetteer']}' en el gazetteer"
    lat, lon, tipo = gaz[clave]
    return (lat, lon), f"SCAR Composite Gazetteer · {entrada['gazetteer']} ({tipo})"


def construir(entrada, estatus, gaz):
    coords, origen = resolver(entrada, gaz)
    if coords is None:
        print(f"  [WARN] {entrada['nombre'][:50]}: {origen}", file=sys.stderr)
        return None
    lat, lon = coords
    gf = entrada["framework"]
    props = {
        "codigo": entrada["codigo"],
        "nombre": entrada["nombre"],
        "estatus": estatus,
        "tipo": "geositio SCAR",
        "framework": f"GF{gf} — {NOMBRES_GF.get(gf, '?')}",
        "framework_n": gf,
        "fuente": entrada["fuente"],
        "origen_coordenada": origen,
        "descripcion": entrada.get("descripcion", ""),
    }
    if entrada.get("iugs"):
        props["iugs_third_100"] = True
    if entrada.get("en_espera"):
        props["en_espera"] = True
    if entrada.get("nota_ubicacion"):
        props["nota_ubicacion"] = entrada["nota_ubicacion"]
    return {"type": "Feature",
            "properties": props,
            "geometry": {"type": "Point", "coordinates": [round(lon, 4), round(lat, 4)]}}


def clasificar_existente(props):
    """Estatus para los puntos que ya estaban en el archivo."""
    tipo = (props.get("tipo") or "").lower()
    if tipo == "aspa":
        return "aspa"
    # Los 'SCAR-geosite' que no son ninguno de los aprobados eran semillas
    # inferidas de la bibliografía, no designaciones. Pasan a potenciales.
    return "potencial"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = ap.parse_args(argv[1:])

    gaz = cargar_gazetteer()
    if gaz is None:
        return 1
    print(f"Gazetteer SCAR: {len(gaz):,} topónimos\n")

    fc = json.loads(GEOSITIOS.read_text(encoding="utf-8"))
    previos = fc["features"]
    print(f"{GEOSITIOS.name}: {len(previos)} puntos previos")

    # Nombres de los oficiales, para no duplicar las semillas que los anticipaban
    oficiales = APROBADOS + NOMINADOS
    claves = set()
    for e in oficiales:
        claves.add(e["nombre"].lower())
        if "gazetteer" in e:
            claves.add(e["gazetteer"].lower())

    def duplica(props):
        """Solo deduplica semillas, nunca ASPAs.

        Una ASPA que comparte topónimo con un geositio no es el mismo objeto: la
        ASPA 119 'Davis Valley and Forlidas Pond' está en el Dufek Massif pero no
        es la intrusión estratificada de Dufek, y la ASPA 148 'Mount Flora' está
        en Hope Bay pero no es el registro Pérmico-Mesozoico completo. Son figuras
        distintas con límites distintos, así que las dos entradas deben coexistir.
        """
        if (props.get("tipo") or "").lower() == "aspa":
            return False
        n = (props.get("nombre") or "").lower()
        return any(k in n or n in k for k in claves if len(k) > 6)

    conservados, descartados = [], []
    for f in previos:
        if duplica(f["properties"]):
            descartados.append(f["properties"].get("nombre"))
            continue
        f["properties"]["estatus"] = clasificar_existente(f["properties"])
        conservados.append(f)

    nuevos = []
    print("\nGeositios SCAR aprobados:")
    for e in APROBADOS:
        f = construir(e, "aprobado", gaz)
        if f:
            nuevos.append(f)
            lon, lat = f["geometry"]["coordinates"]
            iugs = "  [IUGS Third 100]" if f["properties"].get("iugs_third_100") else ""
            print(f"  GF{e['framework']}  {e['nombre'][:52]:<52} {lat:>8.3f} {lon:>9.3f}{iugs}")

    print("\nNominaciones GF3/GF4 (convocatoria 2026-2028):")
    for e in NOMINADOS:
        f = construir(e, "nominado", gaz)
        if f:
            nuevos.append(f)
            lon, lat = f["geometry"]["coordinates"]
            espera = "  [no se considera por ahora]" if f["properties"].get("en_espera") else ""
            print(f"  GF{e['framework']}  {e['nombre'][:52]:<52} {lat:>8.3f} {lon:>9.3f}{espera}")

    if descartados:
        print(f"\nSemillas reemplazadas por la entrada oficial ({len(descartados)}):")
        for n in descartados:
            print(f"  - {n}")

    fc["features"] = nuevos + conservados
    fc["_source"] = ("Geositios SCAR: presentación del workshop GEOCON (SCAR ISAES 2025 / "
                     "OSC 2026) y ATCM XLIII (2021) Att. A. ASPAs: Quantarctica / ATS. "
                     "Coordenadas: SCAR Composite Gazetteer.")
    fc["_processing"] = "scripts/build_geositios_geocon.py"
    fc["_estatus"] = {
        "aprobado": "Geositio SCAR formalmente aprobado por el EG-GEOCON.",
        "nominado": "Propuesto en la convocatoria GF3/GF4 2026-2028; sin resolver.",
        "potencial": "Candidato propio, derivado de la bibliografía. Sin estatus SCAR.",
        "aspa": "Área Antártica Especialmente Protegida. Es otra figura, con estatus "
                "legal bajo el Tratado Antártico; los geositios SCAR no lo tienen.",
    }

    resumen = {}
    for f in fc["features"]:
        e = f["properties"].get("estatus", "?")
        resumen[e] = resumen.get(e, 0) + 1
    print("\nResultado:")
    for e in ("aprobado", "nominado", "potencial", "aspa"):
        if e in resumen:
            print(f"  {resumen[e]:>4}  {e}")
    print(f"  {len(fc['features']):>4}  total")

    if args.dry_run:
        print("\n[dry-run] no se escribió nada")
        return 0
    GEOSITIOS.write_text(json.dumps(fc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {GEOSITIOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
