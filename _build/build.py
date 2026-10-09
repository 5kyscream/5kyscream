"""Generates the README SVG assets. Fonts are subset + embedded so text stays editable."""
import base64, pathlib

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
OUT = HERE.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

def b64(name):
    return base64.b64encode((FONTS / name).read_bytes()).decode()

FACES = {
    "serif":  ("InstrumentSerif-Regular.woff2", "normal", 400, "Serif"),
    "serifi": ("InstrumentSerif-Italic.woff2", "italic", 400, "Serif"),
    "mono":   ("JBM-400.woff2", "normal", 400, "Mono"),
    "monob":  ("JBM-700.woff2", "normal", 700, "Mono"),
    "type":   ("SpecialElite-Regular.woff2", "normal", 400, "Type"),
}

import re, io, html
from fontTools import subset as fts
from fontTools.ttLib import TTFont
TTF = {"InstrumentSerif-Regular.woff2":"InstrumentSerif-Regular.ttf","InstrumentSerif-Italic.woff2":"InstrumentSerif-Italic.ttf",
       "JBM-400.woff2":"JBM-400.ttf","JBM-700.woff2":"JBM-700.ttf","SpecialElite-Regular.woff2":"SpecialElite-Regular.ttf"}
def fontcss(*keys):
    return "@@FONTS:" + ",".join(keys) + "@@"
def sub_b64(f, chars):
    font = TTFont(FONTS / TTF[f])
    opts = fts.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern"]
    s = fts.Subsetter(opts); s.populate(text=chars + " "); s.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()
def realcss(keys, body):
    chars = html.unescape("".join(re.findall(r">([^<]*)<", body)))
    out = []
    for k in keys:
        f, style, weight, fam = FACES[k]
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                   f"src:url(data:font/woff2;base64,{sub_b64(f, chars)}) format('woff2');}}")
    return "\n".join(out)

# palette — blood red / bone / ink
INK, INK2 = "#070606", "#0d0b0b"
RED, RED2, OXB = "#c1121f", "#e5383b", "#3a0a0e"
BONE, ASH, DUST = "#ece4d4", "#8a817c", "#4a4441"
LAV = "#9d8fd1"  # DsaDojo nod

BASE_CSS = f"""
.serif{{font-family:'Serif',Georgia,serif}}
.mono{{font-family:'Mono',ui-monospace,monospace}}
.type{{font-family:'Type','Courier New',monospace}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""

GRAIN = """
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" result="n"/>
  <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.09 0"/>
</filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000" fill-opacity="0.35"/>
</pattern>
<radialGradient id="vig" cx="50%" cy="50%" r="75%">
  <stop offset="55%" stop-color="#000" stop-opacity="0"/>
  <stop offset="100%" stop-color="#000" stop-opacity="0.75"/>
</radialGradient>
"""

def overlays(w, h, scan=True):
    s = f'<rect width="{w}" height="{h}" filter="url(#grain)"/>'
    if scan:
        s += f'<rect width="{w}" height="{h}" fill="url(#scan)"/>'
    s += f'<rect width="{w}" height="{h}" fill="url(#vig)"/>'
    return s

def svg(name, w, h, body, css, defs=""):
    m = re.search(r"@@FONTS:([a-z,]+)@@", css)
    if m: css = css.replace(m.group(0), realcss(m.group(1).split(","), body))
    doc = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">
<defs>{GRAIN}{defs}</defs>
<style>{css}{BASE_CSS}</style>
{body}
</svg>"""
    (OUT / name).write_text(doc)
    print(f"{name:22s} {len(doc)/1024:6.1f} KB")


# ───────────────────────── HEADER ─────────────────────────
W, H = 1000, 400
corners = ""
for x, y, dx, dy in [(28, 28, 1, 1), (972, 28, -1, 1), (28, 372, 1, -1), (972, 372, -1, -1)]:
    corners += f'<path d="M{x} {y+22*dy}V{y}H{x+22*dx}" fill="none" stroke="{BONE}" stroke-opacity=".55" stroke-width="1.5"/>'

name = '<tspan class="it">Prathmesh</tspan> Raghuvanshi'
header = f"""
<rect width="{W}" height="{H}" fill="{INK}"/>
<ellipse cx="500" cy="225" rx="420" ry="120" fill="{RED}" opacity=".13" filter="url(#blur)"/>
<g class="flicker">
  {corners}
  <g class="mono" font-size="13" letter-spacing="2">
    <circle cx="58" cy="58" r="6" fill="{RED2}" class="blink"/>
    <text x="72" y="63" fill="{BONE}">REC</text>
    <text x="118" y="63" fill="{ASH}">SP</text>
    <text x="942" y="63" fill="{RED2}" text-anchor="end">CASE FILE № 5KY-022</text>
    <text x="58" y="351" fill="{BONE}">▶ PLAY   03:00:00 AM</text>
    <text x="942" y="351" fill="{ASH}" text-anchor="end">CH-03 · SIGNAL ▮▮▮▯▯</text>
  </g>
  <text x="500" y="138" class="mono" font-size="12" letter-spacing="5" fill="{ASH}" text-anchor="middle">THE FOLLOWING TAPE WAS RECOVERED FROM THE PROFILE OF</text>
  <g class="serif" font-size="94" text-anchor="middle">
    <text x="500" y="236" fill="{RED2}" opacity=".85" class="g1">{name}</text>
    <text x="500" y="236" fill="{LAV}" opacity=".55" class="g2">{name}</text>
    <text x="500" y="236" fill="{BONE}" class="main">{name}</text>
  </g>
  <line x1="380" y1="270" x2="620" y2="270" stroke="{RED}" stroke-width="1.2"/>
  <text x="500" y="302" class="mono" font-size="15" letter-spacing="3" fill="{BONE}" fill-opacity=".8" text-anchor="middle">full-stack  ·  ai/ml  ·  systems</text>
</g>
<rect class="track" x="0" y="-60" width="{W}" height="46" fill="{BONE}" opacity=".045"/>
{overlays(W, H)}
"""
header_css = fontcss("serif", "serifi", "mono") + """
.it{font-style:italic}
.flicker{animation:flick 7s infinite}
@keyframes flick{0%,100%{opacity:1}41%{opacity:1}42%{opacity:.72}43%{opacity:1}77%{opacity:1}77.5%{opacity:.5}78.5%{opacity:1}}
.g1,.g2{opacity:0}
.g1{animation:g1 5s infinite steps(1)}
.g2{animation:g2 5s infinite steps(1)}
@keyframes g1{0%,88%{opacity:0;transform:none}89%{opacity:.85;transform:translate(-6px,1px)}91%{opacity:.85;transform:translate(4px,-2px)}93%{opacity:.85;transform:translate(-2px,0)}95%,100%{opacity:0;transform:none}}
@keyframes g2{0%,88%{opacity:0;transform:none}89%{opacity:.6;transform:translate(6px,-1px)}91%{opacity:.6;transform:translate(-5px,2px)}93%{opacity:.6;transform:translate(3px,0)}95%,100%{opacity:0;transform:none}}
.main{animation:jit 5s infinite steps(1)}
@keyframes jit{0%,88%{transform:none}90%{transform:translate(2px,0)}92%{transform:translate(-1px,0)}94%,100%{transform:none}}
.track{animation:track 6.5s linear infinite}
@keyframes track{from{transform:translateY(0)}to{transform:translateY(520px)}}
"""
blur = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'
svg("header.svg", W, H, header, header_css, blur)


# ───────────────────────── ECG DIVIDER ─────────────────────────
W, H = 1000, 64
pts = [(0, 32), (180, 32), (196, 32), (204, 22), (212, 32), (230, 32), (238, 40), (248, 6), (258, 58), (266, 32),
       (290, 32), (306, 26), (322, 32), (470, 32), (480, 30), (488, 32), (496, 12), (504, 52), (510, 24), (516, 40),
       (522, 32), (540, 32), (560, 28), (580, 32), (720, 32), (734, 32), (742, 22), (750, 32), (764, 44), (772, 2),
       (782, 62), (790, 32), (812, 32), (830, 26), (846, 32), (1000, 32)]
d = "M" + " L".join(f"{x} {y}" for x, y in pts)
ecg = f"""
<path d="{d}" fill="none" stroke="{OXB}" stroke-width="1.5"/>
<path d="{d}" fill="none" stroke="{RED2}" stroke-width="2" stroke-linejoin="round" class="beat" filter="url(#glow)"/>
"""
ecg_css = """
.beat{stroke-dasharray:260 1800;animation:beat 3.2s linear infinite}
@keyframes beat{from{stroke-dashoffset:260}to{stroke-dashoffset:-1800}}
"""
glow = '<filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
svg("divider.svg", W, H, ecg, ecg_css, glow)


# ───────────────────────── SECTION TITLES ─────────────────────────
ROMAN = ["I", "II", "III", "IV", "V", "VI"]
sections = [
    ("the subject", "[ who is in the room ]"),
    ("exhibit a", "[ currently under construction ]"),
    ("instruments", "[ tools found at the scene ]"),
    ("surveillance logs", "[ automated · do not edit ]"),
    ("on repeat", "[ the soundtrack to every commit ]"),
    ("leave a message", "[ after the tone ]"),
]
W, H = 1000, 120
for i, (title, note) in enumerate(sections):
    body = f"""
<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{RED}"/><stop offset=".6" stop-color="{RED}" stop-opacity=".25"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
<text x="2" y="34" class="mono" font-size="13" letter-spacing="5" fill="{RED2}">ACT {ROMAN[i]}</text>
<text x="0" y="92" class="serif" font-style="italic" font-size="58" fill="{BONE}">{title}<tspan fill="{RED2}">.</tspan></text>
<text x="998" y="92" class="mono" font-size="12" letter-spacing="2" fill="{ASH}" text-anchor="end">{note}</text>
<rect x="0" y="110" width="1000" height="1.5" fill="url(#ln)"/>
<rect x="0" y="107" width="8" height="8" fill="{RED2}" transform="rotate(45 4 111)"/>
"""
    svg(f"act-{i+1}.svg", W, H, f'<g>{body}</g>', fontcss("serifi", "mono"))


# ───────────────────────── DSADOJO CARD ─────────────────────────
W, H = 1000, 360
card = f"""
<rect width="{W}" height="{H}" fill="#09090b"/>
<polygon points="600,0 1000,0 1000,{H-34} 540,{H-34}" fill="#2b2736"/>
<text x="140" y="250" class="mono" font-weight="700" font-size="200" fill="{BONE}" opacity=".05" letter-spacing="-8">DOJO</text>
<g transform="translate(46 58)">
  <circle cx="0" cy="0" r="12" fill="none" stroke="{RED2}" stroke-width="2.5"/>
  <circle cx="0" cy="0" r="3" fill="{RED2}"/>
  <path d="M0 -17V-8M0 8V17M-17 0H-8M8 0H17" stroke="{RED2}" stroke-width="2.5"/>
</g>
<text x="72" y="69" class="mono" font-weight="700" font-size="30" letter-spacing="4" fill="{RED2}">DSADOJO</text>
<text x="46" y="98" class="mono" font-size="12" letter-spacing="1.5" fill="{ASH}">&gt;_ EST_CONN: 127.0.0.1 | STATUS: IN DEVELOPMENT</text>
<text x="46" y="170" class="serif" font-style="italic" font-size="40" fill="{BONE}">Competitive DSA, one-on-one,</text>
<text x="46" y="214" class="serif" font-style="italic" font-size="40" fill="{BONE}">refereed by an <tspan fill="{RED2}">AI</tspan>.</text>
<text x="46" y="252" class="mono" font-size="13" fill="{ASH}" letter-spacing="1">1v1 matchmaking · live arena · ai insights · workspace</text>
<g class="mono" font-size="13" letter-spacing="2">
  <rect x="46" y="272" width="196" height="34" fill="none" stroke="{RED2}"/>
  <text x="144" y="294" fill="{RED2}" text-anchor="middle">[ ENTER_ARENA → ]</text>
</g>
<!-- insights panel -->
<g transform="translate(640 40)">
  <text x="0" y="26" class="mono" font-weight="700" font-size="24" letter-spacing="3" fill="{RED2}">[ INSIGHTS ]</text>
  <rect x="0" y="40" width="320" height="1.5" fill="{BONE}" opacity=".25"/>
  <rect x="0" y="60" width="320" height="104" fill="#121116"/>
  <rect x="236" y="60" width="84" height="20" fill="{RED}"/>
  <text x="278" y="74" class="mono" font-weight="700" font-size="10" fill="{INK}" text-anchor="middle" letter-spacing="1">BEGINNER</text>
  <text x="18" y="102" class="mono" font-weight="700" font-size="17" letter-spacing="2" fill="{BONE}">GRAPH ALGORITHMS</text>
  <text x="18" y="148" class="mono" font-size="11" fill="{BONE}">WIN_RATE: 58%</text>
  <text x="302" y="148" class="mono" font-size="11" fill="{RED2}" text-anchor="end">AVG_TIME: 14m 20s</text>
  <rect x="0" y="178" width="320" height="86" fill="#121116"/>
  <rect x="216" y="178" width="104" height="20" fill="{LAV}"/>
  <text x="268" y="192" class="mono" font-weight="700" font-size="10" fill="{INK}" text-anchor="middle" letter-spacing="1">PROFICIENCY</text>
  <text x="18" y="222" class="mono" font-weight="700" font-size="17" letter-spacing="2" fill="{LAV}">DYNAMIC PROGRAMMING</text>
  <text x="18" y="248" class="mono" font-size="11" fill="{BONE}" opacity=".7">89th percentile · standby for grandmaster</text>
</g>
<rect x="0" y="{H-34}" width="{W}" height="34" fill="#050505"/>
<rect x="0" y="{H-34}" width="{W}" height="1" fill="{BONE}" opacity=".08"/>
<text x="16" y="{H-12}" class="mono" font-size="11" fill="{BONE}" opacity=".7">[SYSTEM_KERNEL_v4.2.0]</text>
<text x="984" y="{H-12}" class="mono blink" font-size="11" fill="{RED2}" text-anchor="end">CONNECTION_ACTIVE</text>
{overlays(W, H, scan=False)}
"""
svg("dsadojo.svg", W, H, card, fontcss("serifi", "mono", "monob"))


# ───────────────────────── NOW PLAYING ─────────────────────────
W, H = 1000, 220
def reel(cx, cy):
    spokes = "".join(f'<rect x="-2" y="-17" width="4" height="10" fill="{INK}" transform="rotate({a})"/>' for a in (0, 120, 240))
    return (f'<g transform="translate({cx} {cy})"><g class="spin">'
            f'<circle r="19" fill="{BONE}"/><circle r="7" fill="{INK}"/>{spokes}</g></g>')
np_ = f"""
<rect width="{W}" height="{H}" fill="{INK2}" rx="0"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{OXB}"/>
<!-- cassette -->
<g transform="translate(36 34)">
  <rect width="230" height="150" rx="10" fill="#141112" stroke="{DUST}"/>
  <rect x="14" y="12" width="202" height="88" rx="4" fill="{RED}"/>
  <rect x="14" y="12" width="202" height="88" rx="4" fill="url(#scan)"/>
  <text x="26" y="36" class="type" font-size="15" fill="{BONE}">side a</text>
  <text x="204" y="36" class="type" font-size="15" fill="{BONE}" text-anchor="end">C-60</text>
  <rect x="48" y="50" width="134" height="40" rx="20" fill="{INK}"/>
  {reel(70, 70)}{reel(160, 70)}
  <rect x="96" y="62" width="38" height="16" fill="#2a2223"/>
  <path d="M40 150 L56 116 H174 L190 150" fill="#0c0a0a" stroke="{DUST}"/>
  <circle cx="80" cy="134" r="4" fill="{DUST}"/><circle cx="150" cy="134" r="4" fill="{DUST}"/>
</g>
<!-- track info -->
<text x="300" y="58" class="mono" font-size="12" letter-spacing="4" fill="{RED2}"><tspan class="blink">●</tspan> NOW PLAYING — ON REPEAT SINCE FOREVER</text>
<text x="300" y="112" class="serif" font-style="italic" font-size="50" fill="{BONE}">Moodswings In To Order</text>
<text x="300" y="140" class="mono" font-size="14" letter-spacing="3" fill="{ASH}">DPR IAN  ·  favourite album, ever</text>
<rect x="300" y="166" width="560" height="3" fill="{DUST}"/>
<rect x="300" y="166" width="560" height="3" fill="{RED2}" class="prog"/>
<text x="300" y="192" class="mono" font-size="12" fill="{ASH}">01:21</text>
<text x="860" y="192" class="mono" font-size="12" fill="{ASH}" text-anchor="end">03:33</text>
<!-- controls -->
<g fill="{BONE}" transform="translate(900 152)">
  <path d="M0 6 L0 26 L4 26 L4 6Z M6 16 L20 6 L20 26Z"/>
  <path d="M34 2 L58 16 L34 30Z" fill="{RED2}"/>
</g>
{overlays(W, H, scan=False)}
"""
np_css = fontcss("serifi", "mono", "type") + """
.spin{animation:spin 2.4s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.prog{transform-origin:300px 0;animation:prog 14s linear infinite}
@keyframes prog{from{transform:scaleX(.08)}to{transform:scaleX(1)}}
"""
svg("now-playing.svg", W, H, np_, np_css)


# ───────────────────────── FOOTER ─────────────────────────
W, H = 1000, 260
bars = [BONE, "#b8ad97", RED2, RED, "#6b1a1f", OXB, ASH, DUST]
bw = W / len(bars)
barsvg = "".join(f'<rect x="{i*bw:.1f}" y="0" width="{bw+0.5:.1f}" height="70" fill="{c}"/>' for i, c in enumerate(bars))
foot = f"""
<rect width="{W}" height="{H}" fill="{INK}"/>
<g opacity=".9">{barsvg}</g>
<rect y="70" width="{W}" height="10" fill="#000"/>
<text x="500" y="44" class="mono" font-weight="700" font-size="18" letter-spacing="10" fill="{INK}" text-anchor="middle">PLEASE STAND BY</text>
<text x="500" y="160" class="serif" font-style="italic" font-size="54" fill="{BONE}" text-anchor="middle">end of transmission<tspan fill="{RED2}">.</tspan></text>
<text x="500" y="204" class="mono" font-size="14" letter-spacing="2" fill="{ASH}" text-anchor="middle">the tape ends here. the cursor doesn't<tspan class="blink" fill="{RED2}">█</tspan></text>
{overlays(W, H)}
"""
svg("footer.svg", W, H, foot, fontcss("serifi", "mono", "monob"))
