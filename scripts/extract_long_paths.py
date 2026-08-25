r"""
Extrae un ZIP a una carpeta destino bypasseando el límite de 260 caracteres
de Windows usando el prefijo \\?\ en las rutas.

Uso: python extract_long_paths.py <zip> <destino>
"""

import os
import sys
import zipfile
from pathlib import Path

# Sin esto, redirigir la salida a un archivo en Windows la escribe en cp1252 y
# "Extraídos" sale como "Extra?dos". No llega a reventar porque los acentos caben
# en cp1252, pero corrompe el log igual.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")

def dentro_de(dest_root, target):
    """True si target cae dentro de dest_root una vez normalizados los '..'.

    Sin esto un ZIP con una entrada tipo `../../algo` escribe fuera del destino
    (ZIP slip). No basta con mirar el nombre crudo: `long_path()` hace resolve(),
    que colapsa los '..' en silencio, así que la ruta ya llega saneada —y fuera
    de sitio— al open(). Hay que decidir ANTES de escribir.

    Una entrada absoluta ('C:/algo' o '/etc/algo') tampoco pasa: al unirla con
    dest_root reemplaza la base y relative_to() falla.
    """
    try:
        Path(os.path.normpath(target)).relative_to(dest_root)
        return True
    except ValueError:
        return False

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
            if not dentro_de(dest_root, target):
                skipped.append((name, "ruta fuera del destino (ZIP slip) — no se extrae"))
                continue
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
