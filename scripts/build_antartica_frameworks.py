"""
Mapea las 21 clases SIMPCODE del SCAR/GNS GeoMAP a los 9 SCAR Geological Frameworks
(Annex 1, ATCM XLIII Attachment A 2021).

Estrategia: reglas SIMPCODE → Framework según edad y litología publicada en
Cox et al. 2023 (Tabla 3) y descripción de cada Framework en el documento SCAR.

Salida:
- app/data/antartica_frameworks.geojson — disuelto por framework
"""

import geopandas as gpd
from pathlib import Path
import json
from collections import Counter
import sys

# En Windows, Python solo usa UTF-8 en consola interactiva (PEP 528). Al
# redirigir la salida a un archivo cae a cp1252 y cualquier print() con
# flechas o checks lanza UnicodeEncodeError, abortando el script a medio
# correr. Esto lo fuerza a UTF-8 siempre.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent.parent
GDB = ROOT / "docs/mapas/antartica/ATA_SCAR_GeoMAP_v2022_08_ESRI/Data/ATA_SCAR_GeoMAP_geology.gdb"
OUT = ROOT / "app/data/antartica_frameworks.geojson"

# 9 SCAR Frameworks (ATCM XLIII Attachment A, 2021)
FRAMEWORKS = {
    1: ("Archean cratons", "#212121",
        "Formación y ruptura de supercontinentes; orógenos arqueanos; primeras formas de vida."),
    2: ("Proterozoic orogens & rifted margins", "#5d4037",
        "Formación y ruptura de Rodinia; orógenos proterozoicos; márgenes rifted neoproterozoicos-paleozoicos tempranos."),
    3: ("Gondwana amalgamation and breakup", "#7e57c2",
        "Ross Orogeny, suturas Pan-Africanas, peneplanicie de Kukri, secuencias Gondwana, Ferrar LIP."),
    4: ("Active margin & West Antarctic rift", "#ef6c00",
        "Subducción, arcos magmáticos, apertura de Tasman/Drake, Scotia Arc, Bransfield, rift Antártico Occidental."),
    5: ("Cretaceous-Palaeogene (K-Pg) transition", "#16a085",
        "Registros paleontológicos y geoquímicos de la extinción masiva K-Pg. Sitio piloto: Isla Marambio."),
    6: ("Cenozoic glacial history", "#3498db",
        "Registros de la formación y dinámica del manto de hielo antártico, fluctuaciones, ice sheets."),
    7: ("Meteorites and impacts", "#c0392b",
        "Rasgos petrológicos y morfológicos relacionados con impactos meteoríticos."),
    8: ("Subglacial water bodies & morphology", "#2980b9",
        "Lagos subglaciales, redes fluviales y morfología bajo el hielo."),
    9: ("Other geological features", "#888888",
        "Categoría comodín — minerales, rocas, fósiles, suelos, permafrost o estructuras que no encajan en F1-F8."),
}


def simpcode_to_framework(simpcode):
    """Reglas SIMPCODE → Framework. Felipe: revisar."""
    # Guard de nulos: esto corre sobre 99.080 polígonos y un solo SIMPCODE vacío
    # o no numérico tiraba el batch entero. Va a F9 ("otros"), que es justamente
    # el bucket de lo no clasificable, y queda contado en el resumen de reglas.
    try:
        s = int(simpcode)
    except (TypeError, ValueError):
        return 9, f"SIMPCODE no numérico ({simpcode!r}) → F9 otros"
    # Arqueano
    if s == 70:
        return 1, "Arqueano metamórfico/intrusivo → F1 cratones arqueanos"
    # Proterozoico-Paleozoico (basamento)
    if 60 <= s <= 63:
        return 2, f"SIMPCODE {s} (Proterozoico-Paleozoico) → F2 orógenos proterozoicos"
    # Beacon Supergroup + Ferrar (Gondwana)
    if s == 50:
        return 3, "Beacon Supergroup → F3 Gondwana"
    if s == 42:
        return 3, "Ferrar Igneous Province → F3 Gondwana (LIP)"
    # Mesozoico arco/intrusivo (active margin)
    if s in (43, 44, 45):
        return 4, f"SIMPCODE {s} (Mesozoico magmatismo/metamorfismo) → F4 margen activo"
    if s in (40, 41):
        return 4, f"SIMPCODE {s} (Mesozoico-Paleógeno volcánico/sed.) → F4 margen activo"
    # Cenozoico magmatismo/sed
    if s in (30, 31, 32):
        return 4, f"SIMPCODE {s} (Cenozoico ígneo/sed.) → F4 margen activo"
    # Cuaternario-Neógeno (glacial)
    if 20 <= s <= 23:
        return 6, f"SIMPCODE {s} (Cuaternario-Neógeno glacial/till) → F6 historia glacial cenozoica"
    # Other
    if s in (10, 11):
        return 9, f"SIMPCODE {s} (agua/hielo estacional o sin clasificar) → F9 otros"
    return 9, f"SIMPCODE {s} sin regla → F9"


def main():
    print("Loading GeoMAP geological_units…")
    gdf = gpd.read_file(GDB, layer="ATA_GeoMAP_geological_units", columns=["SIMPCODE", "geometry"])
    print(f"  {len(gdf)} features (CRS: {gdf.crs})")

    print("Applying mapping rules…")
    fws, rules = [], Counter()
    for _, row in gdf.iterrows():
        fw, rule = simpcode_to_framework(row.SIMPCODE)
        fws.append(fw)
        rules[rule] += 1
    gdf["framework"] = fws

    cnt = Counter(fws)
    print("\nDistribución por Framework:")
    for fw, n in sorted(cnt.items()):
        nombre = FRAMEWORKS.get(fw, ("?",))[0]
        print(f"  F{fw}  {n:>6} polígonos · {nombre}")

    print("\nDissolving by framework…")
    diss = gdf.dissolve(by="framework", as_index=False)
    print(f"  → {len(diss)} frameworks representados")

    print("Simplifying (5km in EPSG:3031)…")
    diss["geometry"] = diss.geometry.simplify(tolerance=5000, preserve_topology=True)

    print("Reprojecting to EPSG:4326…")
    diss = diss.to_crs(epsg=4326)

    records = []
    for _, row in diss.iterrows():
        fw = int(row.framework)
        nombre, color, desc = FRAMEWORKS.get(fw, ("?", "#999", ""))
        geom = json.loads(gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_json())["features"][0]["geometry"]
        records.append({
            "type": "Feature",
            "properties": {
                "id": f"scar-f{fw}",
                "framework": fw,
                "nombre": f"F{fw}: {nombre}",
                "tipo": "framework",
                "edad": "—",
                "color": color,
                "region": "antartica",
                "descripcion": desc,
                "n_poligonos_origen": int(cnt[fw]),
                "unidades": [],
            },
            "geometry": geom,
        })

    fc = {
        "type": "FeatureCollection",
        "_source": "SCAR/GNS GeoMAP v2022.08 mapeado a 9 SCAR Frameworks (ATCM XLIII 2021)",
        "features": records,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten: {OUT}")
    print(f"Size: {OUT.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
