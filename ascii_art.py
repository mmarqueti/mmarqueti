"""
Converte uma foto em arte ASCII e regenera os SVGs.

Uso:
    pip install pillow
    python ascii_art.py minha_foto.jpg            # 76 colunas (padrão)
    python ascii_art.py minha_foto.jpg 38 --invert

Dica: foto de rosto, fundo liso e bem iluminado dá o melhor resultado.
"""
import sys
from PIL import Image, ImageOps, ImageEnhance

import render

# do mais "vazio" ao mais "cheio" (no tema escuro, cheio = mais claro)
RAMP = " .'`:,;-~+=ilcxsoaekdbqpwmhGHXYZ0OQ%8&#B@"


def to_ascii(path, cols=40, invert=False, char_aspect=0.5):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    raw = img.copy()
    w, h = img.size
    rows = max(1, int(h / w * cols * char_aspect))
    img = img.resize((cols, rows))
    bg_mask = raw.resize((cols, rows))   # pixels pretos puros = fundo, ficam vazios nos dois temas
    ramp = RAMP if not invert else RAMP[::-1]
    n = len(ramp) - 1
    lines = []
    for y in range(rows):
        line = "".join(
            " " if bg_mask.getpixel((x, y)) < 12 else ramp[img.getpixel((x, y)) * n // 255]
            for x in range(cols))
        lines.append(line.rstrip())
    return lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cols = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 76
    art = to_ascii(sys.argv[1], cols, invert="--invert" in sys.argv)
    inv = "--invert" in sys.argv
    with open("ascii.txt", "w", encoding="utf-8") as f:      # tema escuro
        f.write("\n".join(art) + "\n")
    light = to_ascii(sys.argv[1], cols, invert=not inv)
    with open("ascii_light.txt", "w", encoding="utf-8") as f: # tema claro
        f.write("\n".join(light) + "\n")
    print("\n".join(art))
    render.build()
