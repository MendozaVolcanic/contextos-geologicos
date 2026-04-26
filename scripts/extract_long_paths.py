"""
Extrae un ZIP a una carpeta destino bypasseando el límite de 260 caracteres
de Windows usando el prefijo \\?\ en las rutas.

Uso: python extract_long_paths.py <zip> <destino>
"""

import sys
import zipfile
from pathlib import Path

def long_path(p):
    p = str(Path(p).resolve())
    if not p.startswith("\\\\?\\"):
        return "\\\\?\\" + p
    return p

def main(zip_path, dest_root):
    dest_root = Path(dest_root).resolve()
    dest_root.mkdir(parents=True, exist_ok=True)
    skipped = []
    written = 0
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        print(f"Total entries: {len(infos)}")
        for info in infos:
            name = info.filename
            # Saltar .DS_Store y __MACOSX
            if name.endswith("/.DS_Store") or name.endswith(".DS_Store"):
                continue
            if "__MACOSX" in name:
                continue
            target = dest_root / name
            try:
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src:
                    data = src.read()
                # Escribir con ruta extendida
                with open(long_path(target), "wb") as out:
                    out.write(data)
                written += 1
                if written % 50 == 0:
                    print(f"  ... {written} archivos extraídos")
            except Exception as e:
                skipped.append((name, str(e)))
    print(f"\nExtraídos: {written}")
    print(f"Saltados / con error: {len(skipped)}")
    for n, e in skipped[:10]:
        print(f"  - {n[:80]}... : {e}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
