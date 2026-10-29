"""Генерирует assets/stack-dark.svg и assets/stack-light.svg: стек с опытом в годах.

Запуск: python3 scripts/gen.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {"bg": "#0d1117", "line": "#30363d", "txt": "#e6edf3", "muted": "#8b949e", "acc": "#ffb547"},
    "light": {"bg": "#ffffff", "line": "#d0d7de", "txt": "#1f2328", "muted": "#656d76", "acc": "#d97f00"},
}

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

# (группа, [(технология, лет)])
GROUPS = [
    ("Frontend", [("Vue", 4), ("Nuxt", 4), ("TypeScript", 4), ("Tailwind", 4)]),
    ("3D и моушн", [("three.js", 3), ("GSAP", 4), ("WebGL", 3), ("Pixi.js", 1)]),
    ("Backend", [("Node.js", 4), ("Python · FastAPI", 4), ("PostgreSQL", 4), ("Go", 2)]),
    ("AI и инфра", [("Docker", 3), ("CI/CD", 3), ("LLM", 2), ("PyTorch", 2)]),
]
MAX_YEARS = 4


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def stack(t):
    w, pad, gap = 900, 28, 28
    colw = (w - pad * 2 - gap * 3) / 4
    h = 236
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Стек и опыт в годах">',
        f"<style>text{{font-family:{FONT}}}</style>",
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>',
    ]
    for gi, (group, items) in enumerate(GROUPS):
        gx = pad + gi * (colw + gap)
        out.append(f'<text x="{gx}" y="44" font-size="13" font-weight="600" fill="{t["acc"]}">{esc(group)}</text>')
        for ii, (name, years) in enumerate(items):
            y = 82 + ii * 40
            out.append(f'<text x="{gx}" y="{y}" font-size="14" fill="{t["txt"]}">{esc(name)}</text>')
            out.append(f'<text x="{gx + colw}" y="{y}" font-size="12" fill="{t["muted"]}" text-anchor="end">{years} г</text>')
            out.append(f'<rect x="{gx}" y="{y + 9}" width="{colw:.1f}" height="4" rx="2" fill="{t["line"]}"/>')
            out.append(f'<rect x="{gx}" y="{y + 9}" width="{colw * years / MAX_YEARS:.1f}" height="4" rx="2" fill="{t["acc"]}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        (OUT / f"stack-{name}.svg").write_text(stack(theme), encoding="utf-8")
        print("ok", name)
