"""
Gera dark_mode.svg e light_mode.svg no estilo neofetch.

Edite o bloco CONFIG abaixo para mudar o conteúdo.
- ascii.txt   -> arte ASCII (gerada por ascii_art.py)
- stats.json  -> estatísticas do GitHub (geradas por today.py)
"""
import json
import os
from datetime import date
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------- CONFIG ---
HEADER = "marcelo@marqueti"
CAREER_START = date(2005, 1, 1)  # usado no "Uptime" (ajuste para o ano real)

SECTIONS = [
    [
        ("OS", "macOS, iOS, Linux"),
        ("Uptime", "{uptime}"),
        ("Host", "iFood · Novos Negócios"),
        ("Kernel", "Head of Product (IC)"),
        ("IDE", "Claude Code, VSCode, iTerm2"),
    ],
    [
        ("Languages.Product", "Strategy, Discovery, AI, Marketplaces"),
        ("Languages.Code", "TypeScript, Python, SQL"),
        ("Languages.Real", "Portuguese, Italian, English"),
    ],
    [
        ("Building.Now", "Toqan para Restaurantes, Gomo"),
        ("Company", "Liveshop Sistemas e Consultoria"),
        ("Based", "Campinas, BR · BR/IT citizen"),
    ],
]

CONTACT = [
    ("Website", "restaurantes.toqan.ai"),
    ("LinkedIn", "mmarqueti"),
    ("GitHub", "mmarqueti"),
]

THEMES = {
    "dark": dict(bg="#161b22", text="#c9d1d9", key="#ffa657",
                 value="#a5d6ff", dim="#616e7f", add="#3fb950", border="#30363d"),
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800",
                  value="#0a3069", dim="#c2cfde", add="#1a7f37", border="#d0d7de"),
}
# ---------------------------------------------------------------------------

FONT = 16          # px
LINE = 20          # altura de linha
CHAR = 9.6         # largura aproximada de um caractere monoespaçado em 16px
ART_X = 20
ART_FONT = 8.5   # fonte menor na arte = mais detalhe
ART_LINE = 10
COL_X = 420
RIGHT_X = 965
WIDTH = 985


def uptime(start: date, today: date) -> str:
    y = today.year - start.year
    m = today.month - start.month
    d = today.day - start.day
    if d < 0:
        m -= 1
        d += 30
    if m < 0:
        y -= 1
        m += 12
    s = lambda n, w: f"{n} {w}{'s' if n != 1 else ''}"
    return f"{s(y, 'year')}, {s(m, 'month')}, {s(d, 'day')}"


def load(name, default):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f) if name.endswith(".json") else f.read().splitlines()


def header_line(label, y, c):
    used = len(label) + 1
    dashes = "-" * max(3, int((RIGHT_X - COL_X) / CHAR) - used)
    return (f'<text x="{COL_X}" y="{y}" fill="{c["text"]}">{escape(label)} '
            f'<tspan fill="{c["dim"]}">{dashes}</tspan></text>')


def kv_line(key, value, y, c):
    return (f'<text x="{COL_X}" y="{y}" fill="{c["key"]}">{escape(key)}:</text>'
            f'<text x="{RIGHT_X}" y="{y}" text-anchor="end" fill="{c["value"]}">'
            f'{escape(value)}</text>')


def render(theme: str):
    c = THEMES[theme]
    art = load("ascii.txt", [])
    if theme == "light":
        art = load("ascii_light.txt", art)
    stats = load("stats.json", {})
    up = uptime(CAREER_START, date.today())

    rows = []
    y = 30
    rows.append(header_line(HEADER, y, c))
    for i, section in enumerate(SECTIONS):
        if i:
            y += LINE // 2
        for k, v in section:
            y += LINE
            rows.append(kv_line(k, v.format(uptime=up), y, c))

    y += LINE + LINE // 2
    rows.append(header_line("Contact", y, c))
    for k, v in CONTACT:
        y += LINE
        rows.append(kv_line(k, v, y, c))

    y += LINE + LINE // 2
    rows.append(header_line("GitHub Stats", y, c))
    g = lambda k: f'{stats.get(k, "-"):,}' if isinstance(stats.get(k), int) else "-"
    y += LINE
    rows.append(
        f'<text x="{COL_X}" y="{y}" fill="{c["key"]}">Repos:'
        f'<tspan fill="{c["value"]}"> {g("repos")}</tspan>'
        f'<tspan fill="{c["text"]}"> (Contributed: </tspan>'
        f'<tspan fill="{c["value"]}">{g("contributed")}</tspan>'
        f'<tspan fill="{c["text"]}">)</tspan></text>'
        f'<text x="{RIGHT_X}" y="{y}" text-anchor="end" fill="{c["key"]}">Stars: '
        f'<tspan fill="{c["value"]}">{g("stars")}</tspan></text>')
    y += LINE
    rows.append(
        f'<text x="{COL_X}" y="{y}" fill="{c["key"]}">Commits:'
        f'<tspan fill="{c["value"]}"> {g("commits")}</tspan></text>'
        f'<text x="{RIGHT_X}" y="{y}" text-anchor="end" fill="{c["key"]}">Followers: '
        f'<tspan fill="{c["value"]}">{g("followers")}</tspan></text>')
    if stats.get("updated"):
        y += LINE
        rows.append(f'<text x="{RIGHT_X}" y="{y}" text-anchor="end" '
                    f'fill="{c["dim"]}" font-size="12">updated {escape(stats["updated"])}</text>')

    # arte ASCII centralizada verticalmente na coluna esquerda
    height = max(y + 30, len(art) * ART_LINE + 40)
    art_y = (height - len(art) * ART_LINE) // 2 + 10
    art_svg = "".join(
        f'<tspan x="{ART_X}" y="{art_y + i * ART_LINE}">{escape(line)}</tspan>'
        for i, line in enumerate(art))

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}px" height="{height}px" font-size="{FONT}px">
<style>
text, tspan {{ font-family: "ConsolasFallback", Consolas, "SF Mono", Menlo, "DejaVu Sans Mono", monospace; white-space: pre; }}
</style>
<rect width="{WIDTH}px" height="{height}px" fill="{c["bg"]}" rx="15"/>
<text fill="{c["text"]}" font-size="{ART_FONT}px" xml:space="preserve">{art_svg}</text>
{chr(10).join(rows)}
</svg>
'''
    out = os.path.join(HERE, f"{theme}_mode.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    return out


def build():
    for t in THEMES:
        print("wrote", render(t))


if __name__ == "__main__":
    build()
