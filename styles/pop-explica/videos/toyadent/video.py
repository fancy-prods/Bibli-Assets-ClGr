"""Toyadent Ultravioleta — Pop Explica (roteiro v2: "é falta de... roxo?").

    python video.py stills            -> storyboard.jpg (12 frames)
    python video.py stills 1.2 5 9.4  -> storyboard nos segundos pedidos
    python video.py audio             -> mix.wav (narração + SFX) e o relatório dos eventos
    python video.py render            -> out/toyadent.mp4 (4 workers, prioridade baixa)

Edição pedida pelo Arthur: riser + flash branco na passagem do hook ("roxo?") para a explicação.
O riser tem o pico exatamente no branco e corte seco; a íris para o azul termina por baixo do branco.
"""
import sys, os, json, math, random, shutil
VDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(VDIR, "..", "..", "engine"))

# ffmpeg avulso do projeto (o PC não tem ffmpeg instalado; ver ferramentas/bin)
_BIN = os.path.abspath(os.path.join(VDIR, *[".."] * 5, "ferramentas", "bin"))
if not shutil.which("ffmpeg") and os.path.isdir(_BIN):
    os.environ["PATH"] = _BIN + os.pathsep + os.environ.get("PATH", "")

from popx import *

SLUG = os.path.basename(VDIR)
AUDIO = os.path.join(VDIR, "narracao.mp3")
MIX = os.path.join(VDIR, "mix.wav")
WORDS = json.load(open(os.path.join(VDIR, "words.json"), encoding="utf-8"))
DUR = audio_duration(AUDIO) + 0.6

HIGHLIGHT = {
    "amarelado": "yellow", "amarelo": "yellow", "escovar": "red", "roxo": "purple", "toyadent": "purple",
    "ultravioleta": "purple", "branco": "white", "azul": "blue", "neutralizado": "green", "carrinho": "yellow",
    "zero": "green", "clinicamente": "green",
}
for w in WORDS:
    c = HIGHLIGHT.get(w["w"].strip(".,!?;:").lower())
    if c: w["c"] = c
cap = Captions(WORDS)


def _k(w): return w["w"].strip(".,!?;:").lower()


def T(word, n=1):
    hits = [w["s"] for w in WORDS if _k(w) == word.lower()]
    if len(hits) < n: raise KeyError(f"palavra '{word}' (ocorrência {n}) não está no words.json")
    return hits[n - 1]


def E(word, n=1):
    hits = [w["e"] for w in WORDS if _k(w) == word.lower()]
    return hits[n - 1]


def A(name): return os.path.join(VDIR, "assets", name)


PRODUTO = pil_to_surface(Image.open(A("produto.png")))
DEMO = Clip(A("demo.mp4"), w=500, h=410, start=8.0)

PURPLE, PURPLE_HI, PURPLE_DK = "#7b3fe4", "#a57cff", "#4b1fa8"

# ---------------------------------------------------------------- tempos (todos ancorados na narração)
T_AMAR = T("amarelado")
T_ESC = T("escovar")
T_FALTA2 = T("falta", 2)
T_ROXO = T("roxo", 1)                       # "roxo?"
T_STOP = T_ROXO - 0.30                      # roleta para na janela roxa ainda na pausa de "de..."
T_FLASH = (E("roxo", 1) + T("sabe")) / 2    # pico do branco (entre "roxo?" e "Sabe")
T_SH, T_LOIRO, T_POIS = T("shampoo"), T("loiro"), T("pois")
T_CIRC, T_ROXO3, T_AM = T("círculo"), T("roxo", 3), T("amarelo")
T_ENC, T_TOM, T_NEU, T_BR = T("encontram"), T("tom"), T("neutralizado"), T("branco")
T_TOY, T_ZERO, T_SEM, T_FLU, T_NANO = T("toyadent"), T("zero"), T("sem"), T("flúor"), T("nano-hidroxiapatita")
T_VOCE2, T_ESPUMA, T_MUDA, T_AZUL = T("você", 2), T("espuma"), T("muda"), T("azul")
T_TEST, T_MAIS, T_TUBO = T("testada"), T("mais"), T("tubo")
T_TOCA, T_CARR = T("toca"), T("carrinho")


# ---------------------------------------------------------------- utilidades locais
def out_k(t, t1, d=0.25):
    """Escala de saída: 1 até t1, depois encolhe até 0 em d segundos."""
    return 1.0 - ease_in_out(prog(t, t1, d))


def scaled(ctx, cx, cy, k, fn):
    if k <= 0.001: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k); ctx.translate(-cx, -cy); fn(); ctx.restore()


def stroke_ink(ctx, w=8):
    ctx.set_line_width(w); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    fill(ctx, INK); ctx.stroke()


def toothbrush(ctx, x, y, rot=0.0, s=1.0, alpha=1.0):
    """Escova genérica deitada: cabeça (cerdas) no ponto (x, y), cabo para a direita."""
    if s <= 0.001 or alpha <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.push_group()
    rrect(ctx, 40, -24, 420, 48, 24); fill(ctx, "#45c4b0"); ctx.fill_preserve(); stroke_ink(ctx, 7)
    rrect(ctx, 120, -9, 260, 14, 7); ctx.set_source_rgba(1, 1, 1, .5); ctx.fill()
    rrect(ctx, -80, -30, 150, 60, 22); fill(ctx, "#ffffff"); ctx.fill_preserve(); stroke_ink(ctx, 7)
    for i in range(6):                               # cerdas
        bx = -66 + i * 22
        rrect(ctx, bx, -78, 16, 52, 6); fill(ctx, "#7fd0ff" if i % 2 else "#ffffff"); ctx.fill_preserve(); stroke_ink(ctx, 4)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha); ctx.restore()


def red_x(ctx, cx, cy, k):
    if k <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    for a in (1, -1):
        ctx.move_to(-70, -70 * a); ctx.line_to(70, 70 * a)
    ctx.set_line_width(40); ctx.set_line_cap(cairo.LINE_CAP_ROUND); fill(ctx, INK); ctx.stroke_preserve()
    ctx.set_line_width(26); fill(ctx, "#ff3b47"); ctx.stroke()
    ctx.restore()


def surprised_eyes(ctx, t, cx, cy, s, k):
    """Olhos arregalados + boca em 'o' por cima do dente do motor (mesma geometria do tooth())."""
    if k <= 0: return
    bob = 6 * math.sin(t * 3.0)
    ctx.save(); ctx.translate(cx, cy + bob * s); ctx.scale(s, s)
    for ex in (-48, 48):
        ctx.arc(ex, -100, 20 + 14 * k, 0, 6.28); fill(ctx, "#ffffff"); ctx.fill_preserve(); stroke_ink(ctx, 6)
        ctx.arc(ex + 3, -98, 11, 0, 6.28); fill(ctx, "#2b1a12"); ctx.fill()
        ctx.arc(ex + 7, -103, 4, 0, 6.28); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.rectangle(-40, -70, 80, 40); fill(ctx, mix(hex2rgb("#fbf6e8"), hex2rgb("#e3c56a"), 0.85)); ctx.fill()
    ctx.save(); ctx.translate(0, -48); ctx.scale(1, 1.25); ctx.arc(0, 0, 13 * k, 0, 6.28); ctx.restore()
    fill(ctx, "#2b1a12"); ctx.fill()
    ctx.restore()


def splat(ctx, t, t0, cx, cy, r=330, color=PURPLE, seed=7):
    """Respingo de tinta (blob com lóbulos + gotas que voam)."""
    k = pop(t, t0, 0.22)
    if k <= 0: return
    rnd = random.Random(seed)
    lobes = [(rnd.uniform(0.75, 1.15), rnd.uniform(0.0, 6.28)) for _ in range(11)]
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    n = 90
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        rr = r * (0.82 + sum(0.07 * m * math.cos(3 * a + ph * (j + 1)) for j, (m, ph) in enumerate(lobes[:4])))
        x, y = rr * math.cos(a), rr * math.sin(a)
        ctx.line_to(x, y) if i else ctx.move_to(x, y)
    ctx.close_path(); fill(ctx, color); ctx.fill_preserve(); stroke_ink(ctx, 8)
    ctx.arc(-r * .35, -r * .35, r * .18, 0, 6.28); fill(ctx, PURPLE_HI, .55); ctx.fill()
    ctx.restore()
    d = t - t0
    for i, (m, ph) in enumerate(lobes):                 # gotas
        dist = r * (1.05 + 0.5 * m) * ease_out(clamp(d / 0.35)) * 1.0
        x, y = cx + dist * math.cos(ph), cy + dist * math.sin(ph) + 120 * d * d
        ctx.arc(x, y, (14 + 10 * m) * k, 0, 6.28); fill(ctx, color); ctx.fill_preserve(); stroke_ink(ctx, 5)


# ---------------------------------------------------------------- roleta (caça-níquel)
REEL = ["ESCOVA NOVA", "BICARBONATO", "CARVÃO", "CLAREAMENTO"] * 3 + ["#ROXO"]
REEL_STEP = 190


def reel_pos(t):
    n = len(REEL) - 1
    if t <= T_FALTA2: return 0.0
    if t < T_STOP:
        x = prog(t, T_FALTA2, T_STOP - T_FALTA2)
        return n * (1 - (1 - x) ** 3.2)
    d = t - T_STOP
    return n - 0.10 * math.sin(d * 22) * math.exp(-d * 9)


def reel_ticks():
    """Instantes em que um item passa pelo centro (para o clique da roleta)."""
    out, prev, t = [], 0, T_FALTA2
    while t < T_STOP:
        p = int(reel_pos(t))
        if p > prev: out.append(t); prev = p
        t += 1 / 240
    return out


def slot_machine(ctx, t, cx, cy, k):
    if k <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    bw, bh = 840, 400
    soft_shadow(ctx, -bw / 2, -bh / 2, bw, bh, 50, a=0.3)
    rrect(ctx, -bw / 2, -bh / 2, bw, bh, 50); fill(ctx, "#2a2238"); ctx.fill_preserve(); stroke_ink(ctx, 9)
    rrect(ctx, -bw / 2 + 16, -bh / 2 + 16, bw - 32, bh - 32, 38); ctx.set_line_width(6); fill(ctx, "#ffd23f"); ctx.stroke()
    for i in range(14):                                 # luzinhas piscando
        x = -bw / 2 + 60 + i * (bw - 120) / 13
        on = (int(t * 10) + i) % 2 == 0
        for y in (-bh / 2 + 16, bh / 2 - 16):
            ctx.arc(x, y, 10, 0, 6.28); fill(ctx, "#ffd23f" if on else "#8a6a12"); ctx.fill()
    # janela
    ww, wh = 700, 210
    rrect(ctx, -ww / 2, -wh / 2, ww, wh, 26); fill(ctx, "#ffffff"); ctx.fill()
    ctx.save(); rrect(ctx, -ww / 2, -wh / 2, ww, wh, 26); ctx.clip()
    pos = reel_pos(t)
    speed = abs(reel_pos(t + 1 / 60) - pos) * 60
    for i, item in enumerate(REEL):
        y = (i - pos) * REEL_STEP
        if abs(y) > wh: continue
        if item == "#ROXO":
            rrect(ctx, -ww / 2 + 40, y - 80, ww - 80, 160, 30); fill(ctx, PURPLE); ctx.fill()
            for j, dx in enumerate((-180, -40, 120, 230)):    # escorridos
                ctx.arc(dx, y + 80 + 18 + 10 * j % 3, 20, 0, 6.28); fill(ctx, PURPLE); ctx.fill()
            ctx.arc(-200, y - 30, 26, 0, 6.28); fill(ctx, PURPLE_HI, .6); ctx.fill()
        else:
            spr = text_sprite(item, 72, INK, 900, stroke=0, shadow=False)
            ghosts = 3 if speed > 6 else 1
            for gidx in range(ghosts):
                blit(ctx, spr, 0, y + gidx * min(40, speed * 1.2), 1.0, 1.0 if gidx == 0 else 0.25)
    # sombras de cilindro em cima e embaixo
    g = cairo.LinearGradient(0, -wh / 2, 0, wh / 2)
    g.add_color_stop_rgba(0, 0, 0, 0, .35); g.add_color_stop_rgba(.3, 0, 0, 0, 0)
    g.add_color_stop_rgba(.7, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .35)
    ctx.set_source(g); ctx.paint()
    ctx.restore()
    rrect(ctx, -ww / 2, -wh / 2, ww, wh, 26); stroke_ink(ctx, 8)
    # alavanca
    pull = math.sin(math.pi * prog(t, T_FALTA2 - 0.25, 0.45))
    ang = math.radians(-20 + 75 * pull)
    ctx.save(); ctx.translate(bw / 2 + 4, -10)
    rrect(ctx, -6, -30, 40, 60, 14); fill(ctx, "#8a8aa0"); ctx.fill_preserve(); stroke_ink(ctx, 6)
    ctx.translate(18, 0); ctx.rotate(ang)
    ctx.move_to(0, 0); ctx.line_to(0, -180); ctx.set_line_width(18); fill(ctx, INK); ctx.stroke()
    ctx.move_to(0, 0); ctx.line_to(0, -180); ctx.set_line_width(10); fill(ctx, "#c9c9d6"); ctx.stroke()
    ctx.arc(0, -190, 32, 0, 6.28); fill(ctx, "#ff3b47"); ctx.fill_preserve(); stroke_ink(ctx, 7)
    ctx.restore()
    ctx.restore()


# ---------------------------------------------------------------- cena 1: hook (dor + quebra)
def hook(ctx, t):
    punch = 1 + 0.07 * math.exp(-max(0, t - T_ROXO) * 7) if t >= T_ROXO else 1.0
    ctx.save(); ctx.translate(540, 1000); ctx.scale(punch, punch); ctx.translate(-540, -1000)
    # dente: centro -> embaixo quando a roleta entra
    m = ease_in_out(prog(t, T_FALTA2 - 0.3, 0.35))
    tx, ty, ts = 540, 1080 + 440 * m, 1.2 - 0.6 * m
    tooth(ctx, t, tx, ty, ts, mood="sad", dirt=0.85)
    if t >= T_ROXO: surprised_eyes(ctx, t, tx, ty, ts, pop(t, T_ROXO, 0.2))
    # escova esfregando, X em "escovar", sai voando
    if 0.1 <= t < T_ESC + 0.8:
        k_in = pop(t, 0.1, 0.25)
        fly = prog(t, T_ESC + 0.3, 0.45)
        bx = 540 + 110 * math.sin(t * 17) * (1 - fly) + 700 * ease_in_out(fly)
        by = 1120 - 600 * ease_in_out(fly)
        toothbrush(ctx, bx, by, rot=-0.15 + 1.2 * fly, s=k_in, alpha=1 - fly)
        if t >= T_ESC:
            red_x(ctx, 560, 1100 - 600 * ease_in_out(fly), pop(t, T_ESC, 0.22) * (1 - fly))
    # pílula "AMARELADO" tremendo
    pk = out_k(t, T_FALTA2 - 0.45, 0.2)
    if t >= T_AMAR and pk > 0:
        sh = 9 * math.sin(t * 45) * math.exp(-(t - T_AMAR) * 3)
        scaled(ctx, 540, 1500, pk, lambda: pill(ctx, t, T_AMAR, 540 + sh, 1500, "AMARELADO", bg="#ffd23f", fg=INK, size=48))
    # roleta
    if t >= T_FALTA2 - 0.35:
        slot_machine(ctx, t, 540, 930, pop(t, T_FALTA2 - 0.35, 0.3))
    splat(ctx, t, T_ROXO + 0.05, 540, 930)
    ctx.restore()


# ---------------------------------------------------------------- cena 2: mecanismo (matizador + círculo)
HAIR_Y, HAIR_P = hex2rgb("#e5bf55"), hex2rgb("#f3f0e8")


def blonde(ctx, t, cx, cy, k):
    if k <= 0: return
    hp = ease_in_out(prog(t, T_SH + 0.15, T_LOIRO - T_SH))
    sweep = cx - 260 + 520 * hp
    bob = 6 * math.sin(t * 3)
    ctx.save(); ctx.translate(cx, cy + bob); ctx.scale(k, k); ctx.translate(-cx, -cy)
    ground_shadow(ctx, cx, cy + 420, 230, a=0.22)

    def hair_back(col):
        # topo volumoso + duas mechas longas que descem atrás dos ombros (pescoço livre no meio)
        ctx.move_to(cx - 120, cy + 330)
        ctx.curve_to(cx - 250, cy + 250, cx - 235, cy + 60, cx - 215, cy - 60)
        ctx.curve_to(cx - 200, cy - 250, cx + 200, cy - 250, cx + 215, cy - 60)
        ctx.curve_to(cx + 235, cy + 60, cx + 250, cy + 250, cx + 120, cy + 330)
        ctx.curve_to(cx + 140, cy + 230, cx + 120, cy + 160, cx + 70, cy + 150)
        ctx.line_to(cx - 70, cy + 150)
        ctx.curve_to(cx - 120, cy + 160, cx - 140, cy + 230, cx - 120, cy + 330); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill_preserve(); stroke_ink(ctx, 9)

    def strands(col):
        # mechas da frente caindo sobre os ombros, com fios
        for sgn in (-1, 1):
            ctx.move_to(cx + sgn * 150, cy - 40)
            ctx.curve_to(cx + sgn * 200, cy + 60, cx + sgn * 205, cy + 200, cx + sgn * 175, cy + 330)
            ctx.curve_to(cx + sgn * 150, cy + 290, cx + sgn * 130, cy + 300, cx + sgn * 118, cy + 320)
            ctx.curve_to(cx + sgn * 140, cy + 200, cx + sgn * 150, cy + 80, cx + sgn * 120, cy + 10); ctx.close_path()
            ctx.set_source_rgb(*col); ctx.fill_preserve(); stroke_ink(ctx, 8)
            ctx.move_to(cx + sgn * 160, cy + 40); ctx.curve_to(cx + sgn * 175, cy + 140, cx + sgn * 172, cy + 220, cx + sgn * 158, cy + 290)
            ctx.set_line_width(4); fill(ctx, INK, .35); ctx.stroke()

    def hair_front(col):
        # franja de lado (não cobre a testa toda)
        ctx.move_to(cx - 165, cy - 10)
        ctx.curve_to(cx - 185, cy - 200, cx + 10, cy - 250, cx + 140, cy - 150)
        ctx.curve_to(cx + 175, cy - 115, cx + 175, cy - 60, cx + 160, cy - 30)
        ctx.curve_to(cx + 120, cy - 110, cx + 40, cy - 130, cx - 30, cy - 95)
        ctx.curve_to(cx - 90, cy - 70, cx - 130, cy - 40, cx - 165, cy - 10); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill_preserve(); stroke_ink(ctx, 9)
        ctx.move_to(cx - 90, cy - 170); ctx.curve_to(cx - 30, cy - 200, cx + 40, cy - 200, cx + 100, cy - 165)
        ctx.set_line_width(14); ctx.set_source_rgba(1, 1, 1, .45); ctx.stroke()
        ctx.move_to(cx - 20, cy - 205); ctx.curve_to(cx - 60, cy - 150, cx - 100, cy - 90, cx - 150, cy - 40)
        ctx.set_line_width(4); fill(ctx, INK, .35); ctx.stroke()

    def layer(fn):
        fn(HAIR_Y)
        ctx.save(); ctx.rectangle(0, 0, sweep, H); ctx.clip(); fn(HAIR_P); ctx.restore()

    layer(hair_back)
    # tronco e pescoço por cima do cabelo de trás
    ctx.move_to(cx - 230, cy + 420); ctx.curve_to(cx - 230, cy + 250, cx - 150, cy + 200, cx, cy + 200)
    ctx.curve_to(cx + 150, cy + 200, cx + 230, cy + 250, cx + 230, cy + 420); ctx.close_path()
    fill(ctx, "#5fc2b4"); ctx.fill_preserve(); stroke_ink(ctx, 9)
    rrect(ctx, cx - 45, cy + 120, 90, 110, 30); fill(ctx, "#efc3a4"); ctx.fill_preserve(); stroke_ink(ctx, 8)
    ctx.arc(cx, cy, 165, 0, 6.28); fill(ctx, "#f7d2b6"); ctx.fill_preserve(); stroke_ink(ctx, 9)
    for ex in (-58, 58):
        ctx.arc(cx + ex, cy + 10, 14, 0, 6.28); fill(ctx, "#2b1a12"); ctx.fill()
        ctx.arc(cx + ex + 4, cy + 5, 4.5, 0, 6.28); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.save(); ctx.translate(cx + ex * 1.5, cy + 55); ctx.scale(1, .6); ctx.arc(0, 0, 22, 0, 6.28)
        ctx.set_source_rgba(1, .45, .5, .45); ctx.fill(); ctx.restore()
    ctx.arc(cx, cy + 55, 34, 0.15 * math.pi, 0.85 * math.pi); stroke_ink(ctx, 8)
    layer(strands)
    layer(hair_front)
    ctx.restore()
    # frasco genérico (sem marca) passando pelo cabelo
    bk = pop(t, T_SH - 0.15, 0.25) * out_k(t, T_LOIRO + 0.25, 0.25)
    if bk > 0:
        bx, by = sweep + 40, cy - 250 + 14 * math.sin(t * 9)
        ctx.save(); ctx.translate(bx, by); ctx.rotate(math.radians(-35)); ctx.scale(bk, bk)
        rrect(ctx, -30, -205, 60, 50, 12); fill(ctx, "#2a2238"); ctx.fill_preserve(); stroke_ink(ctx, 7)
        rrect(ctx, -70, -160, 140, 280, 42); fill(ctx, PURPLE); ctx.fill_preserve(); stroke_ink(ctx, 8)
        rrect(ctx, -45, -70, 90, 110, 16); fill(ctx, "#ffffff", .9); ctx.fill()
        rrect(ctx, -52, -140, 22, 200, 11); ctx.set_source_rgba(1, 1, 1, .35); ctx.fill()
        ctx.restore()
        for i in range(5):                              # gotinhas roxas caindo
            ph = (t * 2.2 + i * 0.2) % 1
            ctx.arc(bx - 60 + i * 18, by + 120 + 160 * ph, 9 * (1 - ph), 0, 6.28); fill(ctx, PURPLE_HI); ctx.fill()
    if t >= T_LOIRO:
        sparkles(ctx, t, T_LOIRO, cx, cy - 60, spread=(230, 220), n=7, seed=5)


RYB = ["#ffe135", "#ffc21a", "#ff9a1f", "#ff6a1f", "#f0372d", "#c8246e", "#8e2bbf", "#5a3ad1",
       "#2f6fe0", "#1fa6a0", "#45c255", "#a6d93a"]          # amarelo (0) oposto ao violeta (6)


def color_wheel(ctx, t, cx, cy, r, k, hi_purple, hi_yellow):
    if k <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    rot = math.radians(3 * math.sin(t * 1.2))
    for i, col in enumerate(RYB):
        a0 = math.pi + i * math.pi / 6 - math.pi / 12 + rot
        bump = 1 + 0.12 * (hi_yellow if i == 0 else hi_purple if i == 6 else 0)
        ro, ri = r * bump, r * 0.52
        ctx.arc(0, 0, ro, a0, a0 + math.pi / 6); ctx.arc_negative(0, 0, ri, a0 + math.pi / 6, a0); ctx.close_path()
        fill(ctx, col); ctx.fill_preserve(); stroke_ink(ctx, 5)
    # seta dupla "lado oposto"
    pa = min(hi_purple, hi_yellow)
    if pa > 0:
        ctx.set_line_width(10); fill(ctx, INK, pa)
        ctx.move_to(-r * 0.36, 0); ctx.line_to(r * 0.36, 0); ctx.stroke()
        for sgn in (-1, 1):
            ctx.move_to(sgn * r * 0.42, 0); ctx.line_to(sgn * r * 0.28, -16); ctx.line_to(sgn * r * 0.28, 16); ctx.close_path(); ctx.fill()
    ctx.restore()


def venn(ctx, t, cx, cy, r, k, slide, lens):
    if k <= 0: return
    d = 260 - 170 * slide
    lx, rx = cx - d * k, cx + d * k
    rr = r * k
    ctx.arc(lx, cy, rr, 0, 6.28); fill(ctx, "#ffe135"); ctx.fill_preserve(); stroke_ink(ctx, 7)
    ctx.arc(rx, cy, rr, 0, 6.28); fill(ctx, PURPLE); ctx.fill_preserve(); stroke_ink(ctx, 7)
    if lens > 0:
        ctx.save(); ctx.arc(lx, cy, rr, 0, 6.28); ctx.clip()
        ctx.arc(rx, cy, rr, 0, 6.28); ctx.set_source_rgba(1, 1, 1, lens); ctx.fill_preserve()
        ctx.set_line_width(7); fill(ctx, INK, lens); ctx.stroke(); ctx.restore()
        glow(ctx, cx, cy, 160 * k, 0.55 * lens)


def purple_rain(ctx, t, t0, t1, cx, top, bottom, n=22, seed=11):
    if not (t0 <= t < t1 + 0.4): return
    rnd = random.Random(seed)
    for i in range(n):
        x = cx + rnd.uniform(-130, 130); ph = rnd.uniform(0, 1)
        p = ((t - t0) * 1.6 + ph) % 1
        y = top + (bottom - top) * p
        a = (1 - p) * (1 - prog(t, t1, 0.4))
        ctx.arc(x, y, rnd.uniform(6, 13), 0, 6.28); fill(ctx, PURPLE_HI, a); ctx.fill()


def mecanismo(ctx, t):
    blonde(ctx, t, 540, 1020, (1 if t >= T_FLASH - 0.05 else 0) * out_k(t, T_POIS, 0.3))
    if t < T_CIRC - 0.15: return
    ck = pop(t, T_CIRC - 0.15, 0.3)
    cy = 900
    ctx.save(); ctx.translate(540, cy); ctx.scale(ck, ck); ctx.translate(-540, -cy)
    soft_shadow(ctx, 110, cy - 300, 860, 600, 44, a=0.22)
    rrect(ctx, 110, cy - 300, 860, 600, 44); fill(ctx, "#ffffff"); ctx.fill()
    blit(ctx, text_sprite("CÍRCULO DAS CORES", 40, "#2a2238", 900, stroke=0, shadow=False), 540, cy - 250)
    ctx.restore()
    hp, hy = pop(t, T_ROXO3, 0.3), pop(t, T_AM, 0.3)
    wk = ck * out_k(t, T_ENC - 0.1, 0.3)
    color_wheel(ctx, t, 540, cy + 10, 200, wk, min(1, hp), min(1, hy))
    vk = pop(t, T_ENC - 0.05, 0.3)
    slide = ease_in_out(prog(t, T_ENC + 0.1, 0.55))
    lens = ease_in_out(prog(t, T_NEU, 0.6))
    venn(ctx, t, 540, cy + 20, 165, vk, slide, lens)
    # rótulos
    if t < T_ENC - 0.05:
        pill(ctx, t, T_ROXO3 + 0.05, 820, cy + 230, "ROXO", bg=PURPLE, fg="#ffffff", size=40)
        pill(ctx, t, T_AM + 0.05, 260, cy + 230, "AMARELO", bg="#ffe135", fg=INK, size=40)
    else:
        d = (260 - 170 * slide) * vk
        pill(ctx, t, T_ENC, 540 + d + 60, cy + 230, "ROXO", bg=PURPLE, fg="#ffffff", size=40)
        pill(ctx, t, T_ENC, 540 - d - 60, cy + 230, "AMARELO", bg="#ffe135", fg=INK, size=40)
        if t >= T_BR: pill(ctx, t, T_BR, 540, cy + 20, "BRANCO", bg="#ffffff", fg=INK, size=34)
    # dente embaixo: amarelado -> película roxa -> branco e feliz
    if t >= T_TOM - 0.1:
        dk = pop(t, T_TOM - 0.1, 0.3) * 0.5
        dirt = 0.85 * (1 - ease_in_out(prog(t, T_NEU + 0.2, T_BR - T_NEU)))
        happy = t >= T_BR - 0.05
        tooth(ctx, t, 540, 1520, dk, mood="happy" if happy else "sad", dirt=dirt, shine=happy)
        purple_rain(ctx, t, T_NEU, T_BR, 540, 1330, 1560)
        if happy: sparkles(ctx, t, T_BR, 540, 1480, spread=(170, 120), n=6, seed=9)


# ---------------------------------------------------------------- cena 3: produto, demonstração e prova
def bubbles(ctx, t, t0, cx, cy, k, seed=4):
    if k <= 0: return
    rnd = random.Random(seed)
    col = mix(hex2rgb("#8b5cf6"), hex2rgb("#4fc3ff"), ease_in_out(prog(t, T_MUDA, 0.9)))
    for i in range(20):
        x = cx + rnd.uniform(-190, 190); y = cy + rnd.uniform(-150, 150); r = rnd.uniform(16, 38)
        g = pop(t, t0 + i * 0.03, 0.3) * k
        y += 6 * math.sin(t * 4 + i)
        if g <= 0: continue
        ctx.arc(x, y, r * g, 0, 6.28); ctx.set_source_rgba(*col, 0.9); ctx.fill_preserve()
        ctx.set_line_width(4); ctx.set_source_rgba(1, 1, 1, .9); ctx.stroke()
        ctx.arc(x - r * .35 * g, y - r * .35 * g, r * .22 * g, 0, 6.28); ctx.set_source_rgba(1, 1, 1, .8); ctx.fill()


def produto(ctx, t):
    # posição do produto em cada fase
    e1 = ease_in_out(prog(t, T_ZERO - 0.3, 0.4))           # centro -> esquerda (pílulas)
    e2 = ease_in_out(prog(t, T_VOCE2 - 0.25, 0.4))         # -> canto (demonstração)
    e3 = ease_in_out(prog(t, T_TEST - 0.2, 0.4))           # -> em cima (checklist)
    cx = 540 + (300 - 540) * e1 + (860 - 300) * e2 + (540 - 860) * e3
    cy = 1020 + (1030 - 1020) * e1 + (1470 - 1030) * e2 + (820 - 1470) * e3
    h = 900 + (700 - 900) * e1 + (380 - 700) * e2 + (660 - 380) * e3
    if t < T_VOCE2: sparkles(ctx, t, T_TOY + 0.05, 540 - 240 * e1, 1020, spread=(300, 420), n=9, seed=3)
    # pílulas (fase 1)
    pk = out_k(t, T_VOCE2 - 0.3, 0.25)
    for i, (txt, t0) in enumerate((("0 AGENTE CLAREADOR", T_ZERO), ("SEM SULFATO", T_SEM),
                                   ("FLÚOR", T_FLU), ("NANO-HIDROXIAPATITA", T_NANO))):
        y = 770 + i * 140
        scaled(ctx, 770, y, pk, lambda: pill(ctx, t, t0, 770, y, txt, size=34, icon="check"))
    # demonstração ilustrada (fase 2)
    dk = pop(t, T_VOCE2 - 0.1, 0.3) * out_k(t, T_TEST - 0.25, 0.25)
    if dk > 0:
        scaled(ctx, 520, 1000, dk, lambda: tooth(ctx, t, 520, 1000, 0.95, mood="happy", dirt=0.0, shine=True))
        bubbles(ctx, t, T_ESPUMA - 0.3, 520, 950, dk)
        bx = 520 + 100 * math.sin(t * 15)
        toothbrush(ctx, bx, 990, rot=-0.12, s=dk)
        if t >= T_MUDA:
            scaled(ctx, 440, 1420, dk, lambda: pill(ctx, t, T_MUDA, 440, 1420, "MUDA DE ROXO PRA AZUL", bg="#ffffff", fg=INK, size=36))
    # produto (sempre visível a partir da virada)
    product(ctx, t, T_TOY + 0.05, cx, cy, img=PRODUTO, h=h)
    # prova (fase 3)
    if t >= T_TEST - 0.1:
        checklist(ctx, t, [("TESTADO CLINICAMENTE", T_TEST), ("+256 MIL VENDIDOS", T_MAIS),
                           ("1 TUBO DURA ~90 DIAS", T_TUBO)], x=150, y=1250, w=780)


# ---------------------------------------------------------------- cena 4: CTA com TV
def tv(ctx, t, t0, cx, cy, k):
    if k <= 0: return
    sw, sh = DEMO.w, DEMO.h
    bw, bh = sw + 170, sh + 90
    ctx.save(); ctx.translate(cx, cy + 6 * math.sin((t - t0) * 2.4)); ctx.rotate(math.radians(-3)); ctx.scale(k, k)
    # antenas
    for sgn in (-1, 1):
        ctx.move_to(0, -bh / 2); ctx.line_to(sgn * 130, -bh / 2 - 170 - 8 * math.sin(t * 3 + sgn)); stroke_ink(ctx, 9)
        ctx.arc(sgn * 130, -bh / 2 - 175, 14, 0, 6.28); fill(ctx, "#ffd23f"); ctx.fill_preserve(); stroke_ink(ctx, 6)
    ground_shadow(ctx, 0, bh / 2 + 40, bw * 0.45, a=0.25)
    for sgn in (-1, 1):                                  # pezinhos
        rrect(ctx, sgn * (bw / 2 - 90) - 22, bh / 2 - 10, 44, 46, 10); fill(ctx, "#6b4a2e"); ctx.fill_preserve(); stroke_ink(ctx, 6)
    soft_shadow(ctx, -bw / 2, -bh / 2, bw, bh, 46, a=0.3)
    rrect(ctx, -bw / 2, -bh / 2, bw, bh, 46); fill(ctx, "#ff9a3c"); ctx.fill_preserve(); stroke_ink(ctx, 9)
    rrect(ctx, -bw / 2 + 18, -bh / 2 + 14, bw - 36, 26, 13); ctx.set_source_rgba(1, 1, 1, .3); ctx.fill()
    sx = -bw / 2 + 30
    # painel lateral
    px = sx + sw + 30
    for j, yy in enumerate((-90, 10)):
        ctx.arc(px + 55, yy, 30, 0, 6.28); fill(ctx, "#2a2238"); ctx.fill_preserve(); stroke_ink(ctx, 5)
        a = t * (1.5 if j else -1.1)
        ctx.move_to(px + 55, yy); ctx.line_to(px + 55 + 22 * math.cos(a), yy + 22 * math.sin(a)); ctx.set_line_width(5)
        ctx.set_source_rgb(1, 1, 1); ctx.stroke()
    for j in range(4):
        rrect(ctx, px + 20, 80 + j * 24, 70, 10, 5); fill(ctx, "#a9541d"); ctx.fill()
    # tela
    rrect(ctx, sx - 8, -sh / 2 - 8, sw + 16, sh + 16, 36); fill(ctx, "#2a2238"); ctx.fill()
    ctx.save(); rrect(ctx, sx, -sh / 2, sw, sh, 30); ctx.clip()
    on = prog(t, t0 + 0.1, 0.3)
    surf = DEMO.frame(t - t0 - 0.1) if on > 0 else None
    fill(ctx, "#111018"); ctx.paint()
    if surf is not None:
        lh = max(4, sh * ease_out(on))                   # efeito de TV ligando: faixa que abre
        ctx.save(); ctx.rectangle(sx, -lh / 2, sw, lh); ctx.clip()
        ctx.set_source_surface(surf, sx, -sh / 2); ctx.paint()
        ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - on)); ctx.paint(); ctx.restore()
    for yy in range(int(-sh / 2), int(sh / 2), 6):        # scanlines
        ctx.rectangle(sx, yy, sw, 2)
    ctx.set_source_rgba(0, 0, 0, .10); ctx.fill()
    g = cairo.LinearGradient(sx, -sh / 2, sx + sw * .6, sh / 2)
    g.add_color_stop_rgba(0, 1, 1, 1, .22); g.add_color_stop_rgba(.4, 1, 1, 1, 0)
    ctx.set_source(g); ctx.paint()
    ctx.restore()
    rrect(ctx, sx, -sh / 2, sw, sh, 30); stroke_ink(ctx, 7)
    ctx.restore()
    pill(ctx, t, t0 + 0.45, cx - 150, cy - bh / 2 - 20, "TESTE REAL", bg="#ffd23f", fg=INK, size=34)


def final(ctx, t):
    tv(ctx, t, T_TOCA - 0.05, 420, 930, pop(t, T_TOCA - 0.05, 0.32))
    product(ctx, t, T_TOCA + 0.1, 900, 1230, img=PRODUTO, h=520)
    sparkles(ctx, t, T_TOCA + 0.1, 900, 1230, spread=(170, 260), n=6, seed=8)
    cta(ctx, t, T_CARR - 0.1, 540, 1580)


SCENES = [
    {"t": 0, "theme": "red", "draw": hook},
    {"t": T_FLASH, "theme": "blue", "draw": mecanismo, "d": 0},     # corte seco escondido no pico do branco
    {"t": T_TOY - 0.12, "theme": "purple", "draw": produto, "origin": (540, 1000)},
    {"t": T_TOCA - 0.15, "theme": "purple", "draw": final, "origin": (420, 930)},
]


def flash_alpha(t):
    up, hold, down = 0.22, 0.06, 0.40
    if T_FLASH - up <= t < T_FLASH: return ((t - (T_FLASH - up)) / up) ** 2
    if T_FLASH <= t < T_FLASH + hold: return 1.0
    if T_FLASH + hold <= t < T_FLASH + hold + down: return 1 - ease_out((t - T_FLASH - hold) / down)
    return 0.0


def frame(ctx, t):
    timeline(ctx, t, SCENES)
    cap.draw(ctx, t)
    a = flash_alpha(t)
    if a > 0: ctx.set_source_rgba(1, 1, 1, a); ctx.paint()


# ---------------------------------------------------------------- som: narração + SFX da biblioteca
SFX_ROOT = os.path.abspath(os.path.join(VDIR, *[".."] * 5, "binarios", "sfx"))
SR = 48000
RISER, QUICK = "03_risers/reverse whoosh.wav", "01_impacts/Quick_Impact_01.wav"
POP, CLICK, DING = "08_cartoon_comedia/CARTOON POP.mp3", "05_interface/Mouse Click.mp3", "05_interface/Ding Sound Effect.mp3"
SWISH, BASS = "02_whooshes/Fast Swish.wav", "02_whooshes/Bass Whoosh Sound Effect By Techno.mp3"
GLEAM, SPLAT, BUZZ = "11_magia_energia/Gleams_01.mp3", "08_cartoon_comedia/SPLAT.mp3", "08_cartoon_comedia/BUZZER OR WRONG ANSWER.mp3"
STATIC, CASH = "10_glitch_digital/TV STATIC.mp3", "05_interface/Ka-Ching $$$.mp3"


def hit(rel, t, gain, **o):
    """SFX cujo ataque (ou `at`, segundo dentro do arquivo) cai em t."""
    return (rel, t, gain, o)


def sfx_events():
    pops = lambda *ts, g=-15: [hit(POP, x, g, pitch=(0.92, 1.0, 1.08)[i % 3]) for i, x in enumerate(ts)]
    ev = [hit(QUICK, 0.05, -9), hit(SWISH, 0.3, -21), hit(SWISH, 1.1, -22), hit(SWISH, 1.9, -22),
          *pops(T_AMAR), hit(BUZZ, T_ESC + 0.03, -20, len=0.55, fade=0.15), hit(SWISH, T_ESC + 0.35, -15),
          hit(CLICK, T_FALTA2 - 0.2, -13, len=0.3), *pops(T_FALTA2 - 0.35, g=-16),
          *[hit(CLICK, x, -16, len=0.2) for x in reel_ticks()],
          hit(SPLAT, T_ROXO + 0.05, -7),
          hit(RISER, T_FLASH, -9, at=1.98, len=2.01, fade=0.03),     # pico no branco, corte seco
          hit(QUICK, T_FLASH, -6),
          # mecanismo
          hit(SWISH, T_SH, -15), hit(GLEAM, T_LOIRO - 0.1, -16, len=1.4, fade=0.5),
          hit(SWISH, T_POIS, -17), *pops(T_CIRC - 0.15, T_ROXO3, T_AM, T_TOM - 0.1),
          hit(SWISH, T_ENC + 0.1, -15), hit(GLEAM, T_NEU, -19, len=1.2, fade=0.5), hit(DING, T_BR, -13),
          # produto
          hit(BASS, T_TOY - 0.12, -9), hit(QUICK, T_TOY + 0.05, -8), hit(GLEAM, T_TOY + 0.1, -15, len=1.6, fade=0.6),
          *pops(T_ZERO, T_SEM, T_FLU, T_NANO), hit(SWISH, T_VOCE2 - 0.2, -14),
          *pops(T_ESPUMA - 0.3, T_ESPUMA - 0.1, g=-18), hit(GLEAM, T_MUDA, -19, len=1.0, fade=0.4),
          hit(SWISH, T_TEST - 0.2, -15), *[hit(DING, x + 0.15, -15) for x in (T_TEST, T_MAIS, T_TUBO)],
          # CTA
          hit(BASS, T_TOCA - 0.15, -11), hit(STATIC, T_TOCA + 0.05, -21, len=0.35, fade=0.1),
          *pops(T_TOCA - 0.05, T_TOCA + 0.1, g=-14), hit(CASH, T_CARR, -15, len=1.2, fade=0.4)]
    return ev


def load_audio(path):
    c = av.open(path)
    rs = av.AudioResampler(format="fltp", layout="stereo", rate=SR)
    ch = [o.to_ndarray() for fr in c.decode(audio=0) for o in rs.resample(fr)] + [o.to_ndarray() for o in rs.resample(None)]
    c.close()
    return np.concatenate(ch, axis=1).astype(np.float32)


def build_audio(report=False):
    n = int(DUR * SR)
    mixb = np.zeros((2, n), np.float32)
    voice = load_audio(AUDIO); voice *= 0.9 / np.abs(voice).max()
    mixb[:, :min(n, voice.shape[1])] += voice[:, :n]
    cache = {}
    for rel, t, gain, o in sfx_events():
        if rel not in cache:
            x = load_audio(os.path.join(SFX_ROOT, rel)); x /= np.abs(x).max() + 1e-9
            att = int(np.argmax(np.abs(x).max(0) > 0.3)) / SR
            cache[rel] = (x, att)
        x, att = cache[rel]
        if o.get("pitch", 1.0) != 1.0:
            p = o["pitch"]; idx = np.arange(0, x.shape[1] - 1, p)
            x = np.stack([np.interp(idx, np.arange(x.shape[1]), c) for c in x]).astype(np.float32)
            att = att / p
        at = o.get("at", att)
        seg = x
        if "len" in o: seg = seg[:, :int(o["len"] * SR)].copy()
        else: seg = seg.copy()
        f = int(o.get("fade", 0.05) * SR)
        if f and seg.shape[1] > f: seg[:, -f:] *= np.linspace(1, 0, f, dtype=np.float32)
        i0 = int((t - at) * SR)
        if i0 < 0: seg = seg[:, -i0:]; i0 = 0
        i1 = min(n, i0 + seg.shape[1])
        mixb[:, i0:i1] += seg[:, :i1 - i0] * 10 ** (gain / 20)
        if report: print(f"{t:6.2f}s  {gain:4d} dB  {rel}")
    peak = np.abs(mixb).max()
    if peak > 0.95: mixb *= 0.95 / peak
    return mixb


def write_wav(path, x):
    c = av.open(path, "w"); s = c.add_stream("pcm_s16le", rate=SR); s.layout = "stereo"
    fr = av.AudioFrame.from_ndarray(np.ascontiguousarray((x * 32767).astype(np.int16).T.reshape(1, -1)), format="s16", layout="stereo")
    fr.sample_rate = SR
    for p in s.encode(fr): c.mux(p)
    for p in s.encode(None): c.mux(p)
    c.close()


def low_priority():
    try:
        import ctypes
        k = ctypes.windll.kernel32; k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)   # BELOW_NORMAL
    except Exception:
        pass


import av  # noqa: E402  (só o som usa PyAV)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if mode == "stills":
        times = [float(x) for x in sys.argv[2:]] or None
        print(storyboard(frame, DUR, os.path.join(VDIR, "storyboard.jpg"), times=times))
    elif mode == "audio":
        write_wav(MIX, build_audio(report=True)); print(MIX)
    elif mode == "render":
        low_priority()
        write_wav(MIX, build_audio())
        os.makedirs(os.path.join(VDIR, "out"), exist_ok=True)
        out = os.path.join(VDIR, "out", f"{SLUG}.mp4")
        print(render_parallel(__file__, DUR, out, audio=MIX, workers=max(1, os.cpu_count() // 2)))
