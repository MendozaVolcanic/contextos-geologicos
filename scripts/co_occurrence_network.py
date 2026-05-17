"""
co_occurrence_network.py
========================

Construye una red de co-ocurrencia de sitios antárticos a partir del campo
`co_sites_top` de antartica_geositios_propuestos.geojson (generado por
analisis_actas_scar.py).

Idea
----
Dos sitios están "conectados" si aparecen juntos en muchos documentos.
Una red con esa lógica revela:
  - Clusters geográficos (sitios contiguos siempre se citan juntos)
  - Pares no-triviales (e.g. un sitio chileno con uno australiano = misma temática)
  - Candidatos a "frameworks regionales" (clusters densos)

Salidas
-------
- docs/notas/co_occurrence_edges.csv  — lista de aristas con peso
- docs/notas/co_occurrence_network.md — top N pares + clusters detectados
- (opcional con --gephi) app/data/co_occurrence.graphml — para Gephi/Cytoscape

Uso
---
    pip install networkx
    python scripts/co_occurrence_network.py [--min-cooccur 5] [--top-pairs 50]
"""

from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "app" / "data"
NOTES_DIR = ROOT / "docs" / "notas"
GEO_PROP = APP_DATA / "antartica_geositios_propuestos.geojson"
GEO_CAT = APP_DATA / "antartica_geositios.geojson"


def load_propuestos() -> list[dict]:
    if not GEO_PROP.exists():
        print(f"[ERROR] No existe {GEO_PROP}. Corre analisis_actas_scar.py primero.",
              file=sys.stderr)
        sys.exit(1)
    data = json.loads(GEO_PROP.read_text(encoding="utf-8"))
    feats = data.get("features", [])
    print(f"[INFO] {len(feats)} candidatos cargados")
    return feats


def build_edges(feats: list[dict], min_cooccur: int) -> list[tuple[str, str, int]]:
    """Lista de aristas (a, b, peso). El peso es nº de docs compartidos."""
    edges_dict: dict[tuple, int] = {}
    for f in feats:
        a = f["properties"]["nombre"]
        co = f["properties"].get("co_sites_top", {}) or {}
        for b, w in co.items():
            if w < min_cooccur:
                continue
            key = tuple(sorted([a, b]))
            # Conservar el máximo (los dos extremos pueden reportarse distinto)
            if key in edges_dict:
                edges_dict[key] = max(edges_dict[key], w)
            else:
                edges_dict[key] = w
    return sorted(((a, b, w) for (a, b), w in edges_dict.items()),
                  key=lambda x: -x[2])


def detect_clusters(edges: list[tuple[str, str, int]], min_weight: int = 8):
    """Detecta componentes conexas pesadas con networkx."""
    try:
        import networkx as nx
    except ImportError:
        print("[WARN] networkx no instalado. pip install networkx", file=sys.stderr)
        return None, []
    G = nx.Graph()
    for a, b, w in edges:
        if w >= min_weight:
            G.add_edge(a, b, weight=w)
    # Comunidades por Louvain si está disponible
    try:
        communities = list(nx.community.louvain_communities(G, weight="weight", seed=42))
    except Exception:
        communities = [list(c) for c in nx.connected_components(G)]
    return G, communities


def write_edges_csv(edges: list[tuple[str, str, int]]) -> None:
    out = NOTES_DIR / "co_occurrence_edges.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["site_a", "site_b", "shared_docs"])
        for a, b, weight in edges:
            w.writerow([a, b, weight])
    print(f"[OK] {out} ({len(edges)} aristas)")


def write_report(edges: list[tuple[str, str, int]], communities, top_pairs: int) -> None:
    out = NOTES_DIR / "co_occurrence_network.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("# Red de co-ocurrencia — sitios antárticos\n\n")
        f.write("Construida desde el campo `co_sites_top` del GeoJSON de candidatos.\n"
                "Dos sitios están conectados si aparecen mencionados en el mismo "
                "documento del corpus. El peso es el nº de documentos compartidos.\n\n")

        f.write(f"## Top {top_pairs} pares más co-citados\n\n")
        f.write("| Sitio A | Sitio B | Docs compartidos |\n")
        f.write("|---|---|---:|\n")
        for a, b, w in edges[:top_pairs]:
            f.write(f"| {a} | {b} | {w} |\n")
        f.write("\n")

        if communities:
            f.write(f"## Clusters detectados (Louvain communities, min_weight=8)\n\n")
            f.write(f"Total: {len(communities)} clusters\n\n")
            for i, comm in enumerate(sorted(communities, key=lambda c: -len(c)), 1):
                if len(comm) < 2:
                    continue
                f.write(f"### Cluster {i} — {len(comm)} sitios\n\n")
                for site in sorted(comm):
                    f.write(f"- {site}\n")
                f.write("\n")
    print(f"[OK] {out}")


def write_graphml(G, out: Path) -> None:
    if G is None:
        return
    try:
        import networkx as nx
        nx.write_graphml(G, out)
        print(f"[OK] {out} (para Gephi/Cytoscape)")
    except Exception as e:
        print(f"[WARN] graphml: {e}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-cooccur", type=int, default=4,
                    help="Mínimo de docs compartidos para considerar una arista")
    ap.add_argument("--top-pairs", type=int, default=50)
    ap.add_argument("--gephi", action="store_true",
                    help="Exportar .graphml para Gephi/Cytoscape")
    args = ap.parse_args()

    feats = load_propuestos()
    edges = build_edges(feats, args.min_cooccur)
    print(f"[INFO] {len(edges)} aristas con >= {args.min_cooccur} docs compartidos")
    if not edges:
        print("[WARN] sin aristas — bajar --min-cooccur", file=sys.stderr)
        return 1
    G, communities = detect_clusters(edges)
    print(f"[INFO] {len(communities) if communities else 0} clusters detectados")
    write_edges_csv(edges)
    write_report(edges, communities, args.top_pairs)
    if args.gephi:
        write_graphml(G, APP_DATA / "co_occurrence.graphml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
