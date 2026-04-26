"""
Parser de los 2 informes SERNAGEOMIN (Léxico Estratigráfico) → JSON estructurado.

Estrategia: best-effort regex sobre el texto extraído. Los PDFs son informes con
estructura no perfectamente regular; se extrae lo extraíble y se reporta lo que falle.

Headers de unidad reconocidos (al inicio de línea o tras nueva sección):
- Formación X
- Complejo X
- Grupo X
- Estratos X
- Granito X / Granodiorita X / Tonalita X / Diorita X / Plutón X / Sienogranito X

Campos: Edad: / Litología. / Distribución. / Definición / Espesor

Salida: app/data/lexico.json
"""

import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TXT_FILES = [
    ROOT / "docs/pdfs/lexico1.txt",
    ROOT / "docs/pdfs/lexico2.txt",
]
OUT = ROOT / "app/data/lexico.json"

# Nombre de la unidad: 1-4 palabras, cada una capitalizada. Sin "que", "de", "en", "y" excepto entre palabras.
UNIT_HEADER = re.compile(
    r"^\s*(Formación|Complejo Metamórfico|Complejo Plutónico|Complejo Volcánico|"
    r"Complejo Hipabisal|Complejo|Grupo|Estratos)\s+"
    r"((?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:de|del|de\s+los|de\s+las|el|la|los|las)\s+)?){0,1}"
    r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2})\s*$",
    re.MULTILINE,
)

# Palabras que indican que el "nombre" es ruido (sentence fragment)
NOISE_WORDS = {"que", "donde", "cual", "cuyas", "cuya", "cuyos", "se", "está", "intruido",
               "intruidos", "intruida", "incluye", "fueron", "habría", "tiene", "presenta",
               "corresponde", "corresponden", "constituye", "consiste", "según", "aflora",
               "aflora", "extiende", "subyace"}

FIELD_PATTERNS = {
    "edad": re.compile(r"Edad\s*[:.]\s*(.+?)(?=\n\s*(?:Litología|Distribución|Espesor|Definición|Referencia|$))", re.DOTALL),
    "litologia": re.compile(r"Litología\s*[.:]\s*(.+?)(?=\n\s*(?:Edad|Distribución|Espesor|Definición|Referencia|$))", re.DOTALL),
    "distribucion": re.compile(r"Distribución\s*[.:]\s*(.+?)(?=\n\s*(?:Edad|Litología|Espesor|Definición|Referencia|$))", re.DOTALL),
    "espesor": re.compile(r"Espesor\s*[.:]\s*(.+?)(?=\n\s*(?:Edad|Litología|Distribución|Definición|Referencia|$))", re.DOTALL),
    "definicion": re.compile(r"Definición\s*[.:]\s*(.+?)(?=\n\s*(?:Edad|Litología|Distribución|Espesor|Referencia|$))", re.DOTALL),
}


def slugify(name):
    s = name.lower().replace("ó", "o").replace("á", "a").replace("é", "e").replace("í", "i").replace("ú", "u").replace("ñ", "n")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def clean(text):
    if not text:
        return None
    t = re.sub(r"\s+", " ", text).strip()
    # Cortar si supera límite razonable
    if len(t) > 500:
        t = t[:500].rsplit(" ", 1)[0] + "…"
    return t


def detect_period(edad):
    """Heurística: extraer período principal."""
    if not edad:
        return ""
    e = edad.lower()
    keywords = [
        ("Cuaternario", ["holoceno", "pleistoceno", "cuaternario"]),
        ("Neógeno", ["mioceno", "plioceno", "neógeno", "neogeno"]),
        ("Paleógeno", ["paleoceno", "eoceno", "oligoceno", "paleógeno", "paleogeno"]),
        ("Cretácico", ["cretácico", "cretacico", "albiano", "aptiano", "barremiano", "hauteriviano", "valanginiano", "berriasiano", "maastrichtiano", "campaniano", "santoniano", "coniaciano", "turoniano", "cenomaniano"]),
        ("Jurásico", ["jurásico", "jurasico", "kimmeridgiano", "tithoniano", "oxfordiano", "calloviano", "bathoniano", "bajociano", "aaleniano", "toarciano", "pliensbaquiano", "sinemuriano", "hettangiano"]),
        ("Triásico", ["triásico", "triasico", "rhaetiano", "noriano", "carniano", "ladiniano", "anisiano"]),
        ("Pérmico", ["pérmico", "permico", "lopingiano", "guadalupiano", "cisuraliano"]),
        ("Carbonífero", ["carbonífero", "carbonifero", "pensilvaniano", "misisipiano"]),
        ("Devónico", ["devónico", "devonico"]),
        ("Silúrico", ["silúrico", "silurico"]),
        ("Ordovícico", ["ordovícico", "ordovicico"]),
        ("Cámbrico", ["cámbrico", "cambrico"]),
        ("Precámbrico", ["precámbrico", "precambrico", "neoproterozoico", "mesoproterozoico", "paleoproterozoico"]),
    ]
    for periodo, kws in keywords:
        if any(k in e for k in kws):
            return periodo
    return ""


def parse_file(path):
    text = path.read_text(encoding="utf-8")
    matches = list(UNIT_HEADER.finditer(text))
    print(f"  {path.name}: {len(matches)} headers")
    entries = []
    for i, m in enumerate(matches):
        rango = m.group(1)
        nombre_unidad = m.group(2).strip()
        nombre_completo = f"{rango} {nombre_unidad}"
        # Filtrar nombres muy cortos / falsos positivos
        if len(nombre_unidad) < 3 or nombre_unidad.endswith("("):
            continue
        # Si contiene palabras-ruido, descartar
        words_lower = set(w.lower().strip(".,;:") for w in nombre_unidad.split())
        if words_lower & NOISE_WORDS:
            continue
        # Si el nombre tiene más de 4 palabras significativas, descartar
        sig_words = [w for w in nombre_unidad.split() if w.lower() not in {"de", "del", "la", "los", "las", "el", "y"}]
        if len(sig_words) > 4:
            continue
        # Body = texto desde este header hasta el siguiente
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else min(start + 5000, len(text))
        body = text[start:end]
        if len(body) < 30:
            continue
        # Extraer campos
        fields = {}
        for k, pat in FIELD_PATTERNS.items():
            mm = pat.search(body)
            if mm:
                fields[k] = clean(mm.group(1))
        if not fields:
            continue
        edad = fields.get("edad", "")
        entries.append({
            "id": f"{slugify(rango)}-{slugify(nombre_unidad)}",
            "nombre": nombre_completo,
            "rango": rango,
            "edad": edad or "—",
            "periodo": detect_period(edad),
            "litologia": fields.get("litologia", ""),
            "distribucion": fields.get("distribucion", ""),
            "espesor": fields.get("espesor", ""),
            "definicion": fields.get("definicion", ""),
            "fuente": path.name,
        })
    return entries


def main():
    print("Parsing lexicon PDFs…")
    all_entries = []
    seen = {}
    for f in TXT_FILES:
        if not f.exists():
            print(f"  SKIP (missing): {f}")
            continue
        for e in parse_file(f):
            # Deduplicate por (rango, nombre)
            key = (e["rango"].lower(), e["nombre"].lower())
            if key in seen:
                # Merge fields preferring longer ones
                old = all_entries[seen[key]]
                for k in ("litologia", "distribucion", "espesor", "definicion"):
                    if len(e.get(k, "") or "") > len(old.get(k, "") or ""):
                        old[k] = e[k]
                continue
            seen[key] = len(all_entries)
            all_entries.append(e)

    print(f"\nTotal entradas únicas: {len(all_entries)}")

    # Conteo por período
    from collections import Counter
    periods = Counter(e["periodo"] or "(sin período)" for e in all_entries)
    print("\nPor período:")
    for p, n in periods.most_common():
        print(f"  {p:18} {n}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "_source": "Léxico Estratigráfico de Chile — informes prácticas profesionales SERNAGEOMIN (Arratia, Espinoza, Garrido 2024)",
        "_processing": "Parser regex sobre PDF→texto extraído (scripts/build_lexico.py). Best-effort.",
        "entries": all_entries,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten: {OUT}")
    print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
