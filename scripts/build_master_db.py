"""
Consolida los 7 JSONs de _db/ en una base de datos maestra única.
Genera resumen estadístico + índice cruzado por tema y región.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "docs/biblioteca/_db"
OUT = DB_DIR / "_MASTER.json"
SUMMARY = ROOT / "docs/biblioteca/RESUMEN_BIBLIOGRAFIA.md"


def main():
    files = sorted(DB_DIR.glob("*.json"))
    files = [f for f in files if f.name != "_MASTER.json"]
    print(f"Consolidando {len(files)} archivos:")

    master = {"_generado": "scripts/build_master_db.py", "fuentes": {}, "indices": {}}
    by_tema = defaultdict(list)
    by_region = defaultdict(list)
    by_anio = defaultdict(list)
    n_total = 0

    for f in files:
        print(f"  {f.name}")
        data = json.loads(f.read_text(encoding="utf-8"))
        # Cada archivo es array o dict con key 'geositios' o 'entries'
        if isinstance(data, list):
            entries = data
        elif "geositios" in data:
            entries = data["geositios"]
        elif "entries" in data:
            entries = data["entries"]
        else:
            entries = []
        master["fuentes"][f.stem] = {"n": len(entries), "muestras": entries[:3]}
        n_total += len(entries)
        for e in entries:
            tema = e.get("tema_principal") or e.get("tipo") or "—"
            by_tema[tema].append({"_origen": f.stem, **{k: v for k, v in e.items() if k in ("titulo", "nombre", "autores", "autor", "anio")}})
            region = e.get("region_chile") or e.get("REGIÓN") or e.get("alcance_geografico") or "—"
            by_region[region].append({"_origen": f.stem, "titulo": e.get("titulo") or e.get("nombre", "")})
            year = e.get("anio")
            if year:
                by_anio[str(year)].append(e.get("titulo") or e.get("nombre", ""))

    master["indices"] = {
        "por_tema": {k: v[:50] for k, v in by_tema.items()},
        "por_region": {k: v[:50] for k, v in by_region.items()},
        "por_anio": {k: v for k, v in sorted(by_anio.items())},
    }
    master["_estadisticas"] = {
        "total_registros": n_total,
        "n_temas": len(by_tema),
        "n_regiones": len(by_region),
        "rango_anios": [min(by_anio.keys(), default="—"), max(by_anio.keys(), default="—")],
    }

    OUT.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ Maestra: {OUT}")
    print(f"  Total registros: {n_total}")
    print(f"  Temas únicos: {len(by_tema)}")
    print(f"  Regiones: {len(by_region)}")

    # Resumen markdown
    md = ["# Resumen consolidado de la biblioteca\n\n"]
    md.append(f"**Total registros:** {n_total} (papers + tesis + libros + geositios)\n\n")
    md.append("## Por archivo fuente\n\n| Archivo | Registros |\n|---|---:|\n")
    for k, v in master["fuentes"].items():
        md.append(f"| {k} | {v['n']} |\n")
    md.append("\n## Top temas\n\n")
    for t, items in sorted(by_tema.items(), key=lambda x: -len(x[1]))[:20]:
        md.append(f"- **{t}** ({len(items)})\n")
    md.append("\n## Top regiones (Chile)\n\n")
    for r, items in sorted(by_region.items(), key=lambda x: -len(x[1]))[:20]:
        md.append(f"- **{r}** ({len(items)})\n")
    md.append("\n## Distribución temporal\n\n")
    for y in sorted(by_anio.keys()):
        if y and y != "None":
            md.append(f"- {y}: {len(by_anio[y])}\n")

    SUMMARY.write_text("".join(md), encoding="utf-8")
    print(f"✓ Resumen: {SUMMARY}")


if __name__ == "__main__":
    main()
