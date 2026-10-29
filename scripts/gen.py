"""Генерирует SVG для профильного README: шапка-терминал и стек.

Запуск: python3 scripts/gen.py  (пишет в assets/, иконки берёт со skillicons.dev)
Цвета и шрифты те же, что на hunadev.
"""
import base64
import math
import random
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

BG = "#0b0b0d"
SURFACE = "#121215"
LINE = "#26262b"
TXT = "#efeeea"
MUTED = "#8e8d96"
FAINT = "#5a5961"
ACC = "#ffb547"
GREEN = "#7ee787"
BLUE = "#79c0ff"
RED = "#ff7b72"
VIOLET = "#d2a8ff"

MONO = "ui-monospace,'JetBrains Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CH = 0.6  # ширина символа моноширинного шрифта в em

# (группа, [(название, лет, иконка skillicons или None)])
STACK = [
    ("frontend", [("Vue", 4, "vue"), ("Nuxt", 4, "nuxtjs"), ("TypeScript", 4, "ts"), ("Tailwind", 4, "tailwind")]),
    ("3d и моушн", [("three.js", 3, "threejs"), ("GSAP", 4, None), ("WebGL", 3, None), ("Pixi.js", 1, None)]),
    ("backend", [("Node.js", 4, "nodejs"), ("Go", 2, "go"), ("FastAPI", 4, "fastapi"), ("PostgreSQL", 4, "postgres")]),
    ("ии и инфра", [("LLM", 2, None), ("PyTorch", 2, "pytorch"), ("Docker", 3, "docker"), ("CI/CD", 3, "githubactions")]),
]
MORE_ICONS = ["py", "django", "express", "redis", "kafka", "mongodb", "rust", "tauri", "electron", "nginx", "linux"]
MORE_TEXT = "aiogram · grammY · Telegram Mini Apps"
# буквы на плашке для технологий без иконки
MONOGRAMS = {"GSAP": "GS", "WebGL": "GL", "Pixi.js": "Px", "LLM": "AI"}

_icons = {}


def icon(name):
    if name not in _icons:
        req = urllib.request.Request(f"https://skillicons.dev/icons?i={name}&theme=dark", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            _icons[name] = base64.b64encode(r.read()).decode()
    return _icons[name]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(w, h, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<style>
  text {{ font-family: {MONO}; }}
  .blink {{ animation: blink 1.05s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .tw {{ animation: tw 3.2s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
</style>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<rect x="0.5" y="0.5" width="{w-1}" height="34" rx="12" fill="{SURFACE}"/>
<rect x="0.5" y="22" width="{w-1}" height="13" fill="{SURFACE}"/>
<line x1="0" y1="35" x2="{w}" y2="35" stroke="{LINE}"/>
<circle cx="20" cy="18" r="5.5" fill="{RED}"/>
<circle cx="38" cy="18" r="5.5" fill="{ACC}"/>
<circle cx="56" cy="18" r="5.5" fill="{GREEN}"/>
<text x="{w/2}" y="22.5" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(title)}</text>
{body}
</svg>
"""


def appear(inner, begin, dur=0.25):
    return f"""<g opacity="0">{inner}<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/></g>"""


def typed(x, y, cmd, begin, size=15, speed=0.045):
    """Строка `~ $ cmd`, команда печатается по символу. Возвращает (svg, время окончания)."""
    cid = f"type-{y}"
    cw = size * CH
    px = x + cw * 4  # после "~ $ "
    n = len(cmd)
    steps = ";".join(f"{i * cw:.1f}" for i in range(n + 1))
    times = ";".join(f"{i / n:.4f}" for i in range(n)) + ";1"
    dur = n * speed
    prompt = f'<text x="{x}" y="{y}" font-size="{size}"><tspan fill="{BLUE}">~</tspan><tspan fill="{ACC}"> $ </tspan></text>'
    svg = f"""<clipPath id="{cid}"><rect x="{px}" y="{y - size}" width="0" height="{size * 1.5}">
  <animate attributeName="width" values="{steps}" keyTimes="{times}" calcMode="discrete" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>
</rect></clipPath>
{appear(prompt, begin - 0.25, 0.1)}
<text x="{px}" y="{y}" font-size="{size}" fill="{TXT}" clip-path="url(#{cid})">{esc(cmd)}</text>"""
    return svg, begin + dur


def point_cloud(cx, cy, r, n=260, seed=7):
    """Сфера Фибоначчи с наклоном, как облако частиц на сайте."""
    random.seed(seed)
    golden = math.pi * (3 - math.sqrt(5))
    tilt = 0.45
    pts = []
    for i in range(n):
        yy = 1 - (i / (n - 1)) * 2
        rad = math.sqrt(1 - yy * yy)
        th = golden * i
        x, z = math.cos(th) * rad, math.sin(th) * rad
        pts.append((x, yy * math.cos(tilt) - z * math.sin(tilt), yy * math.sin(tilt) + z * math.cos(tilt)))
    pts.sort(key=lambda p: p[2])
    out = []
    for x, y, z in pts:
        depth = (z + 1) / 2
        cls = ' class="tw"' if random.random() < 0.22 else ""
        style = f' style="animation-delay:-{random.random() * 3.2:.2f}s"' if cls else ""
        color = ACC if depth > 0.35 else MUTED
        out.append(f'<circle cx="{cx + x * r:.1f}" cy="{cy + y * r:.1f}" r="{0.8 + 1.6 * depth:.2f}" fill="{color}" opacity="{0.12 + 0.88 * depth:.2f}"{cls}{style}/>')
    return "\n".join(out)


def header():
    w, h = 900, 330
    x = 32
    body = [
        f'<text x="{x}" y="86" font-size="40" font-weight="700" fill="{ACC}" letter-spacing="1">hunadev<tspan class="blink">_</tspan></text>',
        f'<text x="{x}" y="114" font-size="14" fill="{MUTED}">Марк · фронтенд-разработчик</text>',
    ]
    lines = [
        ("whoami", [(TXT, "Делаю сайты, сервисы и Telegram-ботов.")]),
        ("cat stack --main", [(GREEN, "Vue · Nuxt · TypeScript · three.js · Go · FastAPI")]),
        ("./contact --telegram", [(BLUE, "→ t.me/hunamuna123")]),
    ]
    t, y = 0.7, 158
    for cmd, out in lines:
        svg, t = typed(x, y, cmd, t)
        body.append(svg)
        spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for c, s in out)
        body.append(appear(f'<text x="{x}" y="{y + 24}" font-size="15">{spans}</text>', t + 0.15))
        t += 0.55
        y += 52
    body.append(appear(f'<text x="{x}" y="{y}" font-size="15"><tspan fill="{BLUE}">~</tspan><tspan fill="{ACC}"> $ </tspan><tspan fill="{ACC}" class="blink">▋</tspan></text>', t))
    body.append(point_cloud(735, 176, 112))
    body.append(f'<text x="735" y="312" text-anchor="middle" font-size="11" fill="{FAINT}">render://hunadev.point_cloud <tspan fill="{GREEN}" class="blink">●</tspan> <tspan fill="{GREEN}">LIVE</tspan></text>')
    return frame(w, h, "hunadev@github: ~", "\n".join(body))


def tile(x, y, size, name, label):
    """Иконка skillicons или янтарная плашка с буквами, если иконки нет."""
    if name:
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{icon(name)}"/>'
    mono = MONOGRAMS.get(label) or "".join(c for c in label if c.isalnum())[:2]
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.22:.1f}" fill="{SURFACE}" stroke="{ACC}" stroke-opacity=".55"/>'
            f'<text x="{x + size / 2}" y="{y + size * 0.68:.1f}" text-anchor="middle" font-size="{size * 0.42:.1f}" font-weight="700" fill="{ACC}">{esc(mono)}</text>')


def stack():
    w, h = 900, 400
    gap = 24
    colw = (w - 64 - gap * 3) / 4
    body = [f'<text x="32" y="64" font-size="13" fill="{MUTED}"><tspan fill="{ACC}">$</tspan> ls ~/stack <tspan fill="{FAINT}"># цифра справа: сколько лет пользуюсь</tspan></text>']
    for gi, (group, items) in enumerate(STACK):
        gx = 32 + gi * (colw + gap)
        body.append(f'<text x="{gx}" y="100" font-size="12" fill="{VIOLET}">{esc(group)}/</text>')
        body.append(f'<line x1="{gx}" y1="110" x2="{gx + colw}" y2="110" stroke="{LINE}"/>')
        for ii, (name, years, ic) in enumerate(items):
            y = 126 + ii * 46
            b = 0.3 + gi * 0.12 + ii * 0.08
            row = (tile(gx, y, 24, ic, name)
                   + f'<text x="{gx + 34}" y="{y + 17}" font-size="14" fill="{TXT}">{esc(name)}</text>'
                   + f'<text x="{gx + colw}" y="{y + 17}" font-size="12" fill="{MUTED}" text-anchor="end">{years} г</text>')
            body.append(appear(row, b, 0.3))
            seg = colw / 4
            for s in range(4):
                sx = gx + s * seg
                body.append(f'<rect x="{sx:.1f}" y="{y + 31}" width="{seg - 3:.1f}" height="4" rx="2" fill="{LINE}"/>')
                if s < years:
                    body.append(appear(f'<rect x="{sx:.1f}" y="{y + 31}" width="{seg - 3:.1f}" height="4" rx="2" fill="{ACC}"/>', b + 0.15 + s * 0.09, 0.2))
    body.append(f'<line x1="32" y1="318" x2="{w - 32}" y2="318" stroke="{LINE}" stroke-dasharray="3 4"/>')
    body.append(f'<text x="32" y="344" font-size="12" fill="{FAINT}">+ ещё пользовался</text>')
    ix = 32
    for i, ic in enumerate(MORE_ICONS):
        body.append(appear(tile(ix, 356, 26, ic, ic), 1.2 + i * 0.05, 0.3))
        ix += 34
    body.append(appear(f'<text x="{ix + 10}" y="374" font-size="12.5" fill="{MUTED}">{esc(MORE_TEXT)}</text>', 1.8, 0.4))
    return frame(w, h, "~/stack", "\n".join(body))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in [("header", header), ("stack", stack)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("ok", name)
