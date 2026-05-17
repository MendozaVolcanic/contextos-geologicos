"""
build_tam_subdivisions.py
=========================

Construye polígonos GeoJSON para las 4 sub-divisiones de los
**Transantarctic Mountains (TAM)** y los inyecta en
app/data/antartica_frameworks.geojson para que el spatial-join del
pipeline asigne correctamente cada candidato sin usar reglas blandas.

Sub-divisiones (consenso geológico):
  - **TAM Norte (Northern Victoria Land)**: Cape Adare a Mawson Glacier.
    Ross Orogen basement (Wilson, Bowers, Robertson Bay terranes) +
    Beacon Supergroup + Ferrar dolerite sills.
  - **TAM Central (Dry Valleys – Royal Society Range – David Glacier)**:
    Mawson Glacier a Shackleton Glacier. Beacon-Ferrar dominante,
    incluye los Dry Valleys.
  - **TAM Sur (Beardmore-Shackleton-Nimrod)**: Shackleton Glacier a
    Scott Glacier. Beacon paleontológico (Cryolophosaurus en Mt
    Kirkpatrick) + Ferrar.
  - **TAM Pacific (Pensacola-Thiel Mountains)**: Scott Glacier a
    Pensacola Mountains. Beacon paleozoico + basamento Ross Orogen +
    Whitmore terrane.

Coordenadas aproximadas — el cinturón TAM forma un arco curvo que
discurre por el borde de la Antártica Oriental. Cada sub-polígono es
un rectángulo lat/lon que envuelve el sector. Para refinamiento futuro
usar el SCAR ADD outcrop dataset o GeoMAP v2022 filtrado por unidades.

Uso
---
    python scripts/build_tam_subdivisions.py
    # Re-correr enrich:
    python scripts/enrich_candidatos_framework.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS = ROOT / "app" / "data" / "antartica_frameworks.geojson"


# Polígonos sub-TAM como bbox cerrados (cuádruple) en EPSG:4326.
# Las coordenadas siguen el contorno aproximado del cinturón TAM,
# que va de NE (~71°S 170°E) a SW (~84°S -45°W), cruzando el polo.
TAM_SUBDIVISIONS = [
    {
        "codigo": "TAM-N",
        "nombre": "TAM Norte (Northern Victoria Land)",
        "framework": "F2 Sedimentary basins (Beacon) — TAM Norte",
        "descripcion": "Northern Victoria Land. Cape Adare a Mawson Glacier "
                       "(~76°S). Ross Orogen basement (Wilson/Bowers/Robertson "
                       "Bay terranes) + Beacon + Ferrar sills.",
        "color": "#1f77b4",
        # Bbox: [lat_min, lat_max, lon_min, lon_max]
        # ~71°S a 76°S, ~159°E a 173°E
        "bbox": (-76.5, -70.5, 159.0, 173.0),
    },
    {
        "codigo": "TAM-C",
        "nombre": "TAM Central (Dry Valleys – Royal Society Range)",
        "framework": "F2 Sedimentary basins (Beacon) — TAM Central",
        "descripcion": "Mawson Glacier a Shackleton Glacier. Sector Dry "
                       "Valleys + Royal Society Range + David Glacier. "
                       "Beacon paleobotánico + Ferrar dolerite sills.",
        "color": "#ff7f0e",
        # ~76°S a 80°S, ~155°E a 170°E
        "bbox": (-80.0, -76.0, 155.0, 170.0),
    },
    {
        "codigo": "TAM-S",
        "nombre": "TAM Sur (Beardmore-Shackleton-Nimrod)",
        "framework": "F2 Sedimentary basins (Beacon) — TAM Sur",
        "descripcion": "Shackleton Glacier a Scott Glacier (~84°S). "
                       "Beardmore Glacier (Cryolophosaurus en Hanson Fm.). "
                       "Beacon Supergroup + Ferrar.",
        "color": "#2ca02c",
        # ~80°S a 86°S, ~150°E a 180°E
        "bbox": (-86.0, -80.0, 150.0, 180.0),
    },
    {
        "codigo": "TAM-P",
        "nombre": "TAM Pacific (Pensacola-Thiel Mountains)",
        "framework": "F2 Sedimentary basins (Beacon) — TAM Pacific",
        "descripcion": "Scott Glacier a Pensacola Mountains. Sector "
                       "Atlántico/Pacífico del cinturón TAM. Beacon "
                       "paleozoico + basamento Ross Orogen + Whitmore.",
        "color": "#d62728",
        # ~82°S a 87°S, ~-100°W a -30°W (incluye Whitmore + Pensacola)
        "bbox": (-87.0, -82.0, -100.0, -30.0),
    },
]


def bbox_to_polygon(bbox: tuple[float, float, float, float]) -> list[list[list[float]]]:
    """Convierte (lat_min, lat_max, lon_min, lon_max) a un polígono GeoJSON."""
    lat_min, lat_max, lon_min, lon_max = bbox
    return [[
        [lon_min, lat_min],
        [lon_max, lat_min],
        [lon_max, lat_max],
        [lon_min, lat_max],
        [lon_min, lat_min],
    ]]


def main() -> int:
    if not FRAMEWORKS.exists():
        print(f"[ERROR] No existe {FRAMEWORKS}", file=sys.stderr)
        return 1
    try:
        data = json.loads(FRAMEWORKS.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        data = json.loads(FRAMEWORKS.read_text(encoding="latin-1"))

    existing = data.get("features", [])
    print(f"[INFO] Framework dataset actual: {len(existing)} features")

    # Quitar TAM previos si existieran (idempotencia)
    existing = [
        f for f in existing
        if not (f.get("properties", {}).get("codigo", "")).startswith("TAM-")
    ]
    print(f"[INFO] Tras limpiar TAM previos: {len(existing)} features")

    # Agregar sub-divisiones
    for tam in TAM_SUBDIVISIONS:
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": bbox_to_polygon(tam["bbox"]),
            },
            "properties": {
                "codigo": tam["codigo"],
                "nombre": tam["nombre"],
                "framework": tam["framework"],
                "tipo": "Framework SCAR (sub-division)",
                "color": tam["color"],
                "descripcion": tam["descripcion"],
                "fuente": "scripts/build_tam_subdivisions.py — bbox aproximado",
            },
        }
        existing.append(feat)

    data["features"] = existing
    FRAMEWORKS.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] {FRAMEWORKS}: +{len(TAM_SUBDIVISIONS)} sub-TAM (total {len(existing)})")
    print("\n[NEXT] python scripts/enrich_candidatos_framework.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
