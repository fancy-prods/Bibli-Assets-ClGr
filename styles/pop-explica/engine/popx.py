"""popx — motor do estilo "Pop Explica" (vídeo explicativo de produto, 1080x1920, 30fps).

Só depende de pycairo, Pillow, numpy e ffmpeg. Roda igual no Claude e no Codex.
Tudo é função pura de t (segundos): nenhuma cena guarda estado entre frames.
"""
import math, os, random, re, subprocess, json
import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

# ---------------------------------------------------------------- paleta
# Cada tema: (meio, canto). Medidos nos vídeos de referência.
THEMES = {
    "red":    ("#e8727c", "#9d2c3e"),   # problema / alerta
    "orange": ("#f6af6a", "#a9541d"),   # causa / hábito
    "green":  ("#8ed570", "#237442"),   # solução natural / pele
    "teal":   ("#5fc2b4", "#196963"),   # suavidade / cuidado
    "blue":   ("#7ec8e8", "#1f5f8a"),   # mecanismo / água / óleo
    "purple": ("#b49ee8", "#3a227a"),   # solução / produto premium
}
INK = "#1b1015"           # contorno de texto e traço dos desenhos
HL = {"yellow": "#ffd23f", "green": "#7be05a", "red": "#ff5a5f",
      "blue": "#4fc3ff", "orange": "#ff9a3c", "pink": "#ff7eb6", "purple": "#b77bff", "white": "#ffffff"}


def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, d): return clamp((t - t0) / d) if d > 0 else float(t >= t0)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back_out(x, s=1.9):
    x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2


def pop(t, t0, d=0.28):
    """Escala de entrada padrão do estilo: 0 -> ~1.1 -> 1 (overshoot)."""
    if t < t0: return 0.0
    return back_out(prog(t, t0, d))


# ---------------------------------------------------------------- fontes / texto
_font_cache, _sprite_cache = {}, {}


def font(size, weight=900):
    key = (size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(os.path.join(FONT_DIR, "Rubik-VF.ttf"), size)
        f.set_variation_by_axes([weight])
        _font_cache[key] = f
    return _font_cache[key]


def pil_to_surface(img):
    img = img.convert("RGBA")
    a = np.array(img, dtype=np.uint16)
    al = a[..., 3:4]
    rgb = (a[..., :3] * al // 255).astype(np.uint8)
    bgra = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], a[..., 3].astype(np.uint8)])
    bgra = np.ascontiguousarray(bgra)
    surf = cairo.ImageSurface.create_for_data(bytearray(bgra.tobytes()), cairo.FORMAT_ARGB32,
                                              img.width, img.height)
    return surf


def text_sprite(txt, size=104, color="#ffffff", weight=900, stroke=11, stroke_color=INK, shadow=True):
    """Texto no padrão do estilo: caixa alta, Rubik Black, contorno escuro grosso, sombra curta."""
    key = (txt, size, color, weight, stroke, stroke_color, shadow)
    if key in _sprite_cache: return _sprite_cache[key]
    f = font(size, weight)
    bb = f.getbbox(txt, stroke_width=stroke)
    pad = stroke + 14
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = pad - bb[0], pad - bb[1]
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((ox, oy + 7), txt, font=f, fill=(0, 0, 0, 95),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, 95))
        img = Image.alpha_composite(img, sh); d = ImageDraw.Draw(img)
    d.text((ox, oy), txt, font=f, fill=color, stroke_width=stroke, stroke_fill=stroke_color)
    s = (pil_to_surface(img), w, h, ox)  # ox = x da origem do texto dentro do sprite
    _sprite_cache[key] = s
    return s


def blit(ctx, sprite, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    surf, w, h = sprite[0], sprite[1], sprite[2]
    if scale <= 0.001 or alpha <= 0.001: return
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(scale, scale)
    ctx.set_source_surface(surf, -w / 2, -h / 2); ctx.paint_with_alpha(alpha); ctx.restore()


# ---------------------------------------------------------------- formas básicas
def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill(ctx, color, a=1.0):
    c = hex2rgb(color) if isinstance(color, str) else color
    ctx.set_source_rgba(*c, a)


def soft_shadow(ctx, x, y, w, h, r, a=0.22, off=14, steps=6):
    for i in range(steps):
        g = (steps - i) * 4
        rrect(ctx, x - g / 2, y + off - g / 2 + 4, w + g, h + g, r + g / 2)
        ctx.set_source_rgba(0, 0, 0, a / steps); ctx.fill()


def ground_shadow(ctx, cx, cy, rx, ry=None, a=0.22):
    if rx <= 0.5: return
    ry = ry or rx * 0.18
    ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, 0, 0, 0, a); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.fill(); ctx.restore()


# ---------------------------------------------------------------- fundo
def background(ctx, theme, t, center=(540, 1060), seed=1):
    mid, corner = (hex2rgb(c) for c in THEMES[theme])
    ctx.set_source_rgb(*mid); ctx.paint()
    # raios girando devagar (≈5°/s), 20 raios alternados
    n, R = 20, 2600
    rot = math.radians(5 * t)
    cx, cy = center
    ray = mix(mid, (1, 1, 1), 0.30)
    for i in range(0, n, 2):
        a0 = rot + i * 2 * math.pi / n; a1 = a0 + 2 * math.pi / n
        ctx.move_to(cx, cy); ctx.line_to(cx + R * math.cos(a0), cy + R * math.sin(a0))
        ctx.line_to(cx + R * math.cos(a1), cy + R * math.sin(a1)); ctx.close_path()
    ctx.set_source_rgba(*ray, 0.42); ctx.fill()
    # brilho central
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 700)
    hi = mix(mid, (1, 1, 1), 0.30)
    g.add_color_stop_rgba(0, *hi, 0.45); g.add_color_stop_rgba(1, *hi, 0)
    ctx.set_source(g); ctx.paint()
    # vinheta para a cor de canto
    g = cairo.RadialGradient(cx, cy, 380, cx, cy, 1350)
    g.add_color_stop_rgba(0, *corner, 0); g.add_color_stop_rgba(1, *corner, 0.95)
    ctx.set_source(g); ctx.paint()
    # bokeh: círculos suaves subindo
    rnd = random.Random(seed)
    for _ in range(16):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(10, 34); sp = rnd.uniform(18, 45); a = rnd.uniform(0.10, 0.24)
        y = (y0 - sp * t) % (H + 100) - 50
        x = x0 + 18 * math.sin(t * 0.7 + x0)
        gg = cairo.RadialGradient(x, y, 0, x, y, r)
        gg.add_color_stop_rgba(0, 1, 1, 1, a); gg.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(gg); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()


def iris(ctx, t, t0, new_theme_draw, origin=(540, 1060), d=0.42):
    """Transição de tema: círculo com aro branco abrindo a partir de `origin`."""
    p = prog(t, t0, d)
    if p <= 0: return False
    if p >= 1: return True
    e = ease_in_out(p); rmax = math.hypot(W, H)
    r = e * rmax
    ctx.save(); ctx.arc(*origin, r, 0, 2 * math.pi); ctx.clip(); new_theme_draw(ctx); ctx.restore()
    ctx.set_line_width(26 * (1 - e) + 6); ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - e * 0.6))
    ctx.arc(*origin, r, 0, 2 * math.pi); ctx.stroke()
    return False


# ---------------------------------------------------------------- legenda
class Captions:
    """Legenda palavra-a-palavra.
    words: [{"w": "Todo", "s": 0.0, "e": 0.3, "c": "yellow"?}, ...]  (c = cor do destaque, opcional)
    Uma frase = até `max_words` palavras ou até pontuação/largura máxima. A frase é diagramada
    inteira (centralizada) e as palavras aparecem no lugar final, sem recentralizar.
    A palavra falada agora fica colorida; as anteriores ficam brancas.
    """

    def __init__(self, words, y=300, size=104, max_words=3, max_w=960, default_hl="yellow"):
        self.y, self.size, self.default_hl, self.max_w = y, size, default_hl, max_w
        self.phrases = []
        cur = []
        for i, w in enumerate(words):
            cur.append(w)
            end_punct = w["w"].rstrip()[-1:] in ".,!?;:"
            txt = " ".join(x["w"].strip(".,;:").upper() for x in cur)
            too_wide = text_sprite(txt, size)[1] > max_w
            if too_wide and len(cur) > 1:
                cur.pop(); self.phrases.append(cur); cur = [w]
            if len(cur) >= max_words or end_punct:
                self.phrases.append(cur); cur = []
        if cur: self.phrases.append(cur)
        for ph in self.phrases: self._layout(ph)

    def _clean(self, w): return w["w"].strip(".,;:").upper()

    def _layout(self, ph):
        f = font(self.size)
        space = f.getlength(" ") * 0.9 + 2 * 11   # + contorno dos dois lados
        adv = [f.getlength(self._clean(w)) for w in ph]
        total = sum(adv) + space * (len(ph) - 1)
        k = min(1.0, self.max_w / total)          # palavra sozinha larga demais: reduz em vez de sair da tela
        x = W / 2 - total / 2
        for w, a in zip(ph, adv):
            spr = text_sprite(self._clean(w), self.size)
            cx = x - spr[3] + spr[1] / 2   # centro do sprite com a origem do texto em x
            w["_cx"], w["_k"] = W / 2 + (cx - W / 2) * k, k
            x += a + space

    def draw(self, ctx, t):
        for i, ph in enumerate(self.phrases):
            start = ph[0]["s"]
            end = self.phrases[i + 1][0]["s"] if i + 1 < len(self.phrases) else ph[-1]["e"] + 0.6
            if not (start <= t < end): continue
            active = max([j for j, w in enumerate(ph) if w["s"] <= t], default=-1)
            for j, w in enumerate(ph):
                if t < w["s"]: continue
                col = HL[w.get("c", self.default_hl)] if j == active else "#ffffff"
                sc = pop(t, w["s"], 0.22) * w.get("_k", 1.0)
                blit(ctx, text_sprite(self._clean(w), self.size, col), w["_cx"], self.y, sc)


# ---------------------------------------------------------------- componentes
def pill(ctx, t, t0, cx, cy, txt, bg="#ffffff", fg="#2a2238", size=38, icon=None):
    """Etiqueta curta em cápsula (ex.: 'ESCOVAR 2x AO DIA ✓', 'PORO ENTUPIDO')."""
    s = pop(t, t0)
    if s <= 0: return
    spr = text_sprite(txt, size, fg, 800, stroke=0, shadow=False)
    w, h = spr[1] - 28 + 44 + (40 if icon else 0), size + 30
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    soft_shadow(ctx, -w / 2, -h / 2, w, h, h / 2, a=0.18, off=6, steps=4)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2); fill(ctx, bg); ctx.fill()
    blit(ctx, spr, -20 if icon else 0, 0)
    if icon == "check":
        check_badge(ctx, w / 2 - 38, 0, 18)
    ctx.restore()


def check_badge(ctx, cx, cy, r, color="#3cc46b"):
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill(ctx, color); ctx.fill()
    ctx.set_line_width(r * 0.32); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(cx - r * .45, cy + r * .02); ctx.line_to(cx - r * .1, cy + r * .38); ctx.line_to(cx + r * .5, cy - r * .35)
    ctx.set_source_rgb(1, 1, 1); ctx.stroke()


def checklist(ctx, t, items, x=150, y=1340, w=780, h=96, gap=22):
    """items: [(texto, t_entrada)]. Cartões brancos que entram deslizando da esquerda com check verde."""
    for i, (txt, t0) in enumerate(items):
        p = prog(t, t0, 0.32)
        if p <= 0: continue
        e = back_out(p, 1.4)
        yy = y + i * (h + gap); xx = x - (1 - e) * 220
        ctx.save(); ctx.translate(xx + w / 2, yy + h / 2); ctx.scale(0.9 + 0.1 * e, 0.9 + 0.1 * e)
        soft_shadow(ctx, -w / 2, -h / 2, w, h, 22, a=0.2, off=8, steps=4)
        rrect(ctx, -w / 2, -h / 2, w, h, 22); fill(ctx, "#ffffff", min(1, p * 2)); ctx.fill()
        bx = -w / 2 + 26
        rrect(ctx, bx, -24, 48, 48, 10); fill(ctx, "#3cc46b"); ctx.fill()
        cp = prog(t, t0 + 0.15, 0.2)
        if cp > 0:
            ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(1, 1, 1)
            ctx.move_to(bx + 12, 1); ctx.line_to(bx + 21, 11)
            ex, ey = bx + 21 + (16 * cp), 11 - (24 * cp); ctx.line_to(ex, ey); ctx.stroke()
        spr = text_sprite(txt.upper(), 40, "#2a2238", 800, stroke=0, shadow=False)
        blit(ctx, spr, bx + 72 + spr[1] / 2 - 14, 0)
        ctx.restore()


def progress_bar(ctx, t, t0, cx, cy, label, frm, to, d=1.2, color="#ff9a3c", w=640):
    """Barra com rótulo (ex.: ESMALTE caindo, OLEOSIDADE baixando). frm/to em 0..1."""
    s = pop(t, t0)
    if s <= 0: return
    v = frm + (to - frm) * ease_in_out(prog(t, t0 + 0.25, d))
    h = 72
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    soft_shadow(ctx, -w / 2, -h / 2, w, h, 20, a=0.18, off=6, steps=4)
    rrect(ctx, -w / 2, -h / 2, w, h, 20); fill(ctx, "#ffffff"); ctx.fill()
    spr = text_sprite(label.upper(), 30, "#2a2238", 800, stroke=0, shadow=False)
    blit(ctx, spr, -w / 2 + 24 + spr[1] / 2 - 14, 0)
    bx = -w / 2 + 60 + spr[1]; bw = w / 2 - 28 - bx
    rrect(ctx, bx, -14, bw, 28, 14); fill(ctx, "#ece7f2"); ctx.fill()
    if v > 0.01:
        rrect(ctx, bx, -14, bw * v, 28, 14); fill(ctx, color); ctx.fill()
    ctx.restore()


def sparkle(ctx, x, y, r, a=1.0):
    """Estrela branca de 4 pontas com lados côncavos."""
    if r <= 0.5: return
    ctx.save(); ctx.translate(x, y)
    pts = [(0, -r), (r, 0), (0, r), (-r, 0)]
    ctx.move_to(*pts[0])
    for i in range(4):
        p1 = pts[(i + 1) % 4]
        ctx.curve_to(0, 0, 0, 0, *p1)
    ctx.close_path(); ctx.set_source_rgba(1, 1, 1, a); ctx.fill(); ctx.restore()


def sparkles(ctx, t, t0, cx, cy, spread=(300, 380), n=9, seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        x = cx + rnd.uniform(-spread[0], spread[0]); y = cy + rnd.uniform(-spread[1], spread[1])
        ph = rnd.uniform(0, 6.28); sz = rnd.uniform(22, 46)
        appear = pop(t, t0 + i * 0.05, 0.3)
        tw = 0.55 + 0.45 * math.sin(t * 5 + ph)
        sparkle(ctx, x, y, sz * appear * tw, 0.95)


def glow(ctx, cx, cy, r, a=0.55):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()


def product(ctx, t, t0, cx, cy, img=None, h=900, card=False):
    """Foto do produto (PNG recortado). Entra com pop, flutua (±12px, ±2°) com brilho e sparkles.
    card=True coloca dentro de cartão branco arredondado (usado em kits/combos)."""
    s = pop(t, t0, 0.36)
    if s <= 0: return
    fy = 12 * math.sin((t - t0) * 2.2); rot = math.radians(2.2 * math.sin((t - t0) * 1.6))
    glow(ctx, cx, cy, h * 0.62, 0.5 * s)
    ctx.save(); ctx.translate(cx, cy + fy); ctx.rotate(rot); ctx.scale(s, s)
    if img is not None:
        sw, sh = img.get_width(), img.get_height(); k = h / sh
        if card:
            cw, ch = sw * k + 60, h + 60
            soft_shadow(ctx, -cw / 2, -ch / 2, cw, ch, 36); rrect(ctx, -cw / 2, -ch / 2, cw, ch, 36)
            fill(ctx, "#ffffff"); ctx.fill()
        ctx.scale(k, k); ctx.set_source_surface(img, -sw / 2, -sh / 2); ctx.paint()
    else:
        placeholder_tube(ctx, h)
    ctx.restore()


def placeholder_tube(ctx, h):
    w = h * 0.36
    soft_shadow(ctx, -w / 2, -h / 2, w, h * 0.9, 30, a=0.25)
    ctx.move_to(-w / 2, -h / 2 + 20); ctx.line_to(w / 2, -h / 2 + 20)
    ctx.line_to(w / 2 - 6, h * 0.38); ctx.line_to(w * 0.18, h / 2 - 10); ctx.line_to(-w * 0.18, h / 2 - 10)
    ctx.line_to(-w / 2 + 6, h * 0.38); ctx.close_path()
    g = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    g.add_color_stop_rgb(0, .42, .33, .86); g.add_color_stop_rgb(.5, .62, .54, .98); g.add_color_stop_rgb(1, .36, .27, .78)
    ctx.set_source(g); ctx.fill()
    ctx.rectangle(-w / 2 + 2, -h * 0.02, w - 4, h * 0.13); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    blit(ctx, text_sprite("SEU", 34, "#ffffff", 900, 0, False), 0, -h * 0.28)
    blit(ctx, text_sprite("PRODUTO", 34, "#ffffff", 900, 0, False), 0, -h * 0.22)
    ctx.arc(-18, h * 0.045, 22, 0, 6.28); fill(ctx, "#ffd23f"); ctx.fill()
    ctx.arc(18, h * 0.045, 22, 0, 6.28); fill(ctx, "#3a2a9a"); ctx.fill()


def seal(ctx, t, t0, cx, cy, txt_lines=("DERMATOLOGI-", "CAMENTE", "TESTADO"), r=120):
    """Selo circular com check (dermatologicamente testado, Anvisa etc.)."""
    s = pop(t, t0, 0.35)
    if s <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate(math.radians(-6 * (1 - s)))
    ctx.arc(0, 8, r, 0, 6.28); ctx.set_source_rgba(0, 0, 0, .18); ctx.fill()
    ctx.arc(0, 0, r, 0, 6.28); fill(ctx, "#ffffff"); ctx.fill()
    ctx.set_line_width(6); ctx.arc(0, 0, r - 14, 0, 6.28); fill(ctx, "#3cc46b"); ctx.stroke()
    check_badge(ctx, 0, -r * 0.38, r * 0.26)
    for i, ln in enumerate(txt_lines):
        blit(ctx, text_sprite(ln, 22, "#1f5c3a", 900, 0, False), 0, r * 0.08 + i * 26)
    ctx.restore()


def cart_icon(ctx, x, y, s=1.0, color=(1, 1, 1)):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(-22, -18); ctx.line_to(-14, -18); ctx.line_to(-6, 10); ctx.line_to(18, 10); ctx.line_to(24, -10); ctx.line_to(-11, -10)
    ctx.set_source_rgb(*color); ctx.stroke()
    for px in (-2, 14):
        ctx.arc(px, 19, 4.5, 0, 6.28); ctx.fill()
    ctx.restore()


def cta(ctx, t, t0, cx=540, cy=1560, txt="TOCA NO CARRINHO", arrow=True):
    """Botão laranja pulsando + seta amarela apontando. Último beat do vídeo."""
    s = pop(t, t0, 0.32)
    if s <= 0: return
    pulse = 1 + 0.045 * math.sin((t - t0) * 2 * math.pi * 1.4)
    spr = text_sprite(txt, 44, "#ffffff", 900, stroke=0, shadow=False)
    w, h = spr[1] - 28 + 170, 116
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s * pulse, s * pulse)
    rrect(ctx, -w / 2, -h / 2 + 10, w, h, h / 2); fill(ctx, "#c94a00"); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    g = cairo.LinearGradient(0, -h / 2, 0, h / 2); g.add_color_stop_rgb(0, 1, .55, .16); g.add_color_stop_rgb(1, 1, .40, .02)
    ctx.set_source(g); ctx.fill()
    rrect(ctx, -w / 2 + 18, -h / 2 + 10, w - 36, h * 0.3, h * 0.15); ctx.set_source_rgba(1, 1, 1, .18); ctx.fill()
    cart_icon(ctx, -w / 2 + 64, 2, 1.25)
    blit(ctx, spr, 40, 2)
    ctx.restore()
    a = pop(t, t0 + 0.25)
    if arrow and a > 0.001:
        bob = 16 * math.sin((t - t0) * 2 * math.pi * 1.4)
        ctx.save(); ctx.translate(cx - w / 2 + 70 - bob * .6, cy + 150 + bob * .6); ctx.rotate(math.radians(125)); ctx.scale(a, a)
        ctx.move_to(-60, -18); ctx.line_to(10, -18); ctx.line_to(10, -46); ctx.line_to(64, 0); ctx.line_to(10, 46)
        ctx.line_to(10, 18); ctx.line_to(-60, 18); ctx.close_path()
        ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); fill(ctx, INK); ctx.stroke_preserve()
        fill(ctx, "#ffd23f"); ctx.fill(); ctx.restore()


# ---------------------------------------------------------------- personagem exemplo
def tooth(ctx, t, cx, cy, s=1.0, mood="sad", dirt=0.0, shine=False):
    """Personagem-exemplo do estilo: formas arredondadas, traço escuro médio, blush, sombra no chão.
    mood: sad | happy | worried. dirt 0..1 amarela/mancha a cor."""
    if s <= 0.01: return
    ground_shadow(ctx, cx, cy + 250 * s, 170 * s, a=0.25)
    bob = 6 * math.sin(t * 3.0)
    ctx.save(); ctx.translate(cx, cy + bob * s); ctx.scale(s, s)
    def body():
        ctx.move_to(-150, -120)
        ctx.curve_to(-150, -250, -40, -250, 0, -205); ctx.curve_to(40, -250, 150, -250, 150, -120)
        ctx.curve_to(150, -20, 120, 40, 105, 120); ctx.curve_to(95, 200, 80, 240, 55, 240)
        ctx.curve_to(25, 240, 25, 120, 0, 120); ctx.curve_to(-25, 120, -25, 240, -55, 240)
        ctx.curve_to(-80, 240, -95, 200, -105, 120); ctx.curve_to(-120, 40, -150, -20, -150, -120); ctx.close_path()
    clean, yellow = hex2rgb("#fbf6e8"), hex2rgb("#e3c56a")
    body(); ctx.set_source_rgb(*mix(clean, yellow, dirt)); ctx.fill_preserve()
    ctx.set_line_width(9); ctx.set_line_join(cairo.LINE_JOIN_ROUND); fill(ctx, "#6b4a2e"); ctx.stroke()
    # sombra interna lateral (1 tom)
    ctx.save(); body(); ctx.clip()
    g = cairo.LinearGradient(40, 0, 160, 0); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.10)
    ctx.set_source(g); ctx.paint(); ctx.restore()
    if shine:
        ctx.save(); ctx.translate(-80, -150); ctx.rotate(-0.5); ctx.scale(1, 2.2)
        ctx.arc(0, 0, 14, 0, 6.28); ctx.set_source_rgba(1, 1, 1, .9); ctx.fill(); ctx.restore()
    # rosto
    for ex in (-48, 48):
        ctx.arc(ex, -95, 13, 0, 6.28); fill(ctx, "#2b1a12"); ctx.fill()
        ctx.arc(ex + 4, -100, 4, 0, 6.28); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.save(); ctx.translate(ex * 1.55, -55); ctx.scale(1, .6); ctx.arc(0, 0, 20, 0, 6.28)
        ctx.set_source_rgba(1, .45, .5, .45); ctx.fill(); ctx.restore()
    ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND); fill(ctx, "#2b1a12")
    if mood == "happy":
        ctx.arc(0, -62, 30, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
    elif mood == "sad":
        ctx.arc(0, -25, 28, 1.2 * math.pi, 1.8 * math.pi); ctx.stroke()
        ctx.move_to(118, -140); ctx.curve_to(128, -118, 140, -112, 128, -100); ctx.curve_to(116, -100, 112, -118, 118, -140)
        fill(ctx, "#7fd0ff"); ctx.fill()
    else:
        ctx.move_to(-22, -48); ctx.line_to(22, -52); ctx.stroke()
    ctx.restore()


def eyes_pair(ctx, t, t0, x, y, s=1.0):
    """Par de olhinhos 'todo mundo reparou' que surge com pop e pisca."""
    k = pop(t, t0) * s
    if k <= 0: return
    blink = 0.12 if (t * 1.3 + x * 0.01) % 3.0 < 0.12 else 1.0
    for dx in (-38, 38):
        ctx.save(); ctx.translate(x + dx * k, y); ctx.scale(k, k * blink)
        ctx.arc(0, 0, 34, 0, 6.28); fill(ctx, "#ffffff"); ctx.fill_preserve()
        ctx.set_line_width(3); fill(ctx, INK); ctx.stroke()
        ctx.arc(6, 4, 16, 0, 6.28); fill(ctx, INK); ctx.fill(); ctx.restore()


# ---------------------------------------------------------------- render
def render(draw_frame, duration, out_mp4, audio=None, t_from=0.0):
    """draw_frame(ctx, t). Encaminha frames brutos para o ffmpeg."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio: cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((duration - t_from) * FPS))
    for i in range(n):
        ctx = cairo.Context(surf); draw_frame(ctx, t_from + i / FPS)
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait()


def still(draw_frame, t, path, scale=0.5):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf); draw_frame(ctx, t); surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    img = Image.fromarray(a[..., [2, 1, 0]].copy())
    if scale != 1: img = img.resize((int(W * scale), int(H * scale)))
    img.save(path); return path


def words_from_align(path):
    """Converte o JSON do tools/align.py do kit (lista de {word,start,end}) para o formato da legenda."""
    data = json.load(open(path))
    items = data.get("words", data) if isinstance(data, dict) else data
    return [{"w": d.get("word", d.get("w")), "s": d.get("start", d.get("s")), "e": d.get("end", d.get("e"))}
            for d in items]


# ---------------------------------------------------------------- timeline de cenas
def timeline(ctx, t, scenes, d=0.42):
    """scenes: lista ordenada de dicts {"t": início, "theme": "red", "draw": fn(ctx, t), "origin": (x,y)?, "d": s?}.
    Cada cena nova abre com íris por cima da anterior (fundo + elementos), então elementos da cena
    velha somem naturalmente sob o círculo. A primeira cena não tem transição.
    "d": duração da íris só daquela cena; "d": 0 = corte seco (ex.: escondido por um flash branco)."""
    live = [s for s in scenes if s["t"] <= t]
    if not live: return
    # cena-base = última cuja íris já terminou
    base = 0
    for i, s in enumerate(live):
        if i == 0 or t >= s["t"] + s.get("d", d): base = i
    s = live[base]
    background(ctx, s["theme"], t, seed=base + 1); s["draw"](ctx, t)
    for j in range(base + 1, len(live)):
        s = live[j]; o = s.get("origin", (540, 1060))
        p = ease_in_out(prog(t, s["t"], s.get("d", d))); r = p * math.hypot(W, H)
        ctx.save(); ctx.arc(*o, r, 0, 2 * math.pi); ctx.clip()
        background(ctx, s["theme"], t, seed=j + 1); s["draw"](ctx, t); ctx.restore()
        ctx.set_line_width(26 * (1 - p) + 6); ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - p * 0.6))
        ctx.arc(*o, r, 0, 2 * math.pi); ctx.stroke()


# ---------------------------------------------------------------- vídeo real dentro do estilo
class Clip:
    """Trecho de vídeo real (demonstração do produto) para encaixar no estilo.
    Decodifica em streaming durante o render (leitura sequencial) e com seek pontual nos stills.
    src: caminho do mp4. start: segundo do clipe onde começar. w,h: tamanho de exibição (crop centralizado)."""

    def __init__(self, src, w=760, h=1000, start=0.0, speed=1.0):
        self.src, self.w, self.h, self.start, self.speed = src, w, h, start, speed
        self.proc, self.idx, self.last = None, -1, None

    def _open(self, at):
        if self.proc: self.proc.kill()
        vf = (f"fps={FPS},scale={self.w}:{self.h}:force_original_aspect_ratio=increase,"
              f"crop={self.w}:{self.h}")
        self.proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(at), "-i", self.src,
                                      "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgra", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def frame(self, local_t):
        i = int(max(0, local_t) * self.speed * FPS)
        if self.proc is None or i < self.idx or i > self.idx + 90:
            self._open(self.start + i / FPS); self.idx = i - 1; self.last = None
        n = self.w * self.h * 4
        while self.idx < i:
            buf = self.proc.stdout.read(n)
            if len(buf) < n: break          # acabou o clipe: congela no último frame
            self.last = bytearray(buf); self.idx += 1
        if self.last is None: return None
        return cairo.ImageSurface.create_for_data(self.last, cairo.FORMAT_ARGB32, self.w, self.h)


def clip_card(ctx, t, t0, clip, cx=540, cy=1000, border=14, radius=40, tilt=-2.0, label=None):
    """Vídeo real em cartão branco arredondado: entra com pop, flutua de leve.
    label: pílula opcional sobre o canto superior (ex.: 'IPX7', 'TESTE REAL')."""
    s = pop(t, t0, 0.32)
    if s <= 0: return
    surf = clip.frame(t - t0)
    w, h = clip.w, clip.h
    fy = 8 * math.sin((t - t0) * 2.0)
    ctx.save(); ctx.translate(cx, cy + fy); ctx.rotate(math.radians(tilt)); ctx.scale(s, s)
    W2, H2 = w + 2 * border, h + 2 * border
    soft_shadow(ctx, -W2 / 2, -H2 / 2, W2, H2, radius + border, a=0.3)
    rrect(ctx, -W2 / 2, -H2 / 2, W2, H2, radius + border); fill(ctx, "#ffffff"); ctx.fill()
    if surf is not None:
        ctx.save(); rrect(ctx, -w / 2, -h / 2, w, h, radius); ctx.clip()
        ctx.set_source_surface(surf, -w / 2, -h / 2); ctx.paint(); ctx.restore()
    ctx.restore()
    if label:
        pill(ctx, t, t0 + 0.25, cx + w / 2 - 90, cy - h / 2 - 10, label, bg="#ffd23f", fg=INK)


def clip_full(ctx, t, t0, clip, dim=0.25):
    """Vídeo real em tela cheia (clip criado com w=1080, h=1920). Escurece levemente para a legenda ler."""
    surf = clip.frame(t - t0)
    if surf is None: return
    ctx.set_source_surface(surf, 0, 0); ctx.paint()
    g = cairo.LinearGradient(0, 0, 0, 700); g.add_color_stop_rgba(0, 0, 0, 0, dim); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g); ctx.paint()


# ---------------------------------------------------------------- render paralelo + storyboard
def _render_chunk(args):
    module_path, fn_name, i0, i1, out = args
    import importlib.util
    spec = importlib.util.spec_from_file_location("vidmod", module_path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    frame = getattr(mod, fn_name)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        ctx = cairo.Context(surf); frame(ctx, i / FPS); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait()
    return out


def render_parallel(module_path, duration, out_mp4, audio=None, fn_name="frame", workers=None, tmp=None):
    """Divide o vídeo em blocos e renderiza um por CPU; depois concatena e põe o áudio (normalizado -14 LUFS).
    module_path: arquivo .py do vídeo (precisa expor `frame(ctx, t)` em nível de módulo)."""
    import multiprocessing as mp, tempfile
    workers = workers or max(1, mp.cpu_count())
    n = int(round(duration * FPS)); step = math.ceil(n / workers)
    tmp = tmp or tempfile.mkdtemp(prefix="popx_")
    jobs = [(os.path.abspath(module_path), fn_name, i, min(n, i + step), os.path.join(tmp, f"part{k:02d}.mp4"))
            for k, i in enumerate(range(0, n, step))]
    if workers == 1:
        parts = [_render_chunk(j) for j in jobs]
    else:
        with mp.get_context("spawn").Pool(workers) as pool: parts = pool.map(_render_chunk, jobs)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst]
    if audio:
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-c", "copy"]
    subprocess.run(cmd + [out_mp4], check=True)
    return out_mp4


def storyboard(frame, duration, path, n=12, times=None, cols=6, scale=0.25):
    """Contact sheet de n frames espaçados (ou `times`), com o segundo escrito em cada um.
    Olhar ANTES de renderizar: texto sobreposto, coisa cortada, elemento fora da tela."""
    times = times or [round(duration * (i + 0.5) / n, 2) for i in range(n)]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cols = min(cols, len(times)); tw, th = int(W * scale), int(H * scale); rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (tw * cols, th * rows), "black"); d = ImageDraw.Draw(sheet)
    for k, t in enumerate(times):
        ctx = cairo.Context(surf); frame(ctx, t); surf.flush()
        a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
        img = Image.fromarray(a[..., [2, 1, 0]].copy()).resize((tw, th))
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(img, (x, y)); d.rectangle([x, y, x + 64, y + 26], fill="black")
        d.text((x + 6, y + 6), f"{t:.1f}s", fill="white")
    sheet.save(path); return path


def _duration_ffmpeg(path):
    """Sem ffprobe (ex.: ffmpeg avulso no Windows): lê a linha 'Duration:' do ffmpeg -i."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def audio_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout
        return float(out.strip())
    except (FileNotFoundError, ValueError):
        return _duration_ffmpeg(path)
