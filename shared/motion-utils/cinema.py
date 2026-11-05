"""Efeitos cinematográficos calmos para cenas em SVG (agnóstico de estilo). Só biblioteca padrão.
Aprovado em 2026-11-05; testado na prévia da abertura do amigos1 (variante B).

    from cinema import blur_filter, rack_focus, parallax_dx, sepia_filter, typewriter, fade_through

Desfoque de profundidade: aplique o filtro num <g> que ENVOLVE o grupo da câmera (o espaço do
filtro fica em pixels de tela). Um filtro por camada (fundo / primeiro plano).

    bg_sd, fg_sd = rack_focus(t, t0=2.5, t1=3.7, far_sd=9, near_sd=8)   # foco passa do perto para o longe
    defs += blur_filter("bgb", bg_sd, W, H) + blur_filter("fgb", fg_sd, W, H)
    bg = f'<g filter="url(#bgb)"><g transform="{cam}">{mundo}</g></g>' if bg_sd > 0.05 else ...

Sépia: filtro de cor com intensidade k (0 = cor normal, 1 = sépia cheia), para transições no tempo.
Cartela: texto que entra letra a letra com cursor piscando (som: 07_foley_cotidiano/Typewriter Sound Effect.mp3).
"""
from __future__ import annotations

import math


def _f(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- profundidade
def blur_filter(fid: str, sd: float, w: int, h: int, margin: int = 40) -> str:
    """Filtro de desfoque em espaço de tela (userSpaceOnUse), com margem para não cortar a borda."""
    return (f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="{-margin}" y="{-margin}" '
            f'width="{w + 2 * margin}" height="{h + 2 * margin}"><feGaussianBlur stdDeviation="{_f(sd)}"/></filter>')


def rack_focus(t: float, t0: float, t1: float, far_sd: float = 9.0, near_sd: float = 8.0, to_far: bool = True):
    """Troca de foco entre t0 e t1. Devolve (sd_do_fundo, sd_do_primeiro_plano).
    to_far=True: começa focado no primeiro plano e termina no fundo."""
    k = smooth((t - t0) / (t1 - t0))
    if not to_far:
        k = 1 - k
    return far_sd * (1 - k), near_sd * k


def parallax_dx(cx: float, cx0: float, z: float, factor: float) -> float:
    """Deslocamento em px de tela de uma camada com paralaxe `factor` (1 = anda com o fundo;
    >1 = mais perto da câmera, anda mais) quando a câmera vai de cx0 para cx com zoom z."""
    return -(cx - cx0) * z * factor


# ---------------------------------------------------------------- cor
# sépia quente: luminância (Rec. 601) tingida de marrom; os escuros ficam marrons (a matriz
# clássica esverdeava os escuros e estourava os claros)
LUMA = (0.299, 0.587, 0.114)
SEPIA_TINT = (1.07, 0.88, 0.66)
SEPIA = tuple(t * l for t in SEPIA_TINT for l in LUMA)


def sepia_filter(fid: str, k: float, fade: float = 0.0) -> str:
    """feColorMatrix entre identidade (k=0) e sépia (k=1). fade (0..1) lava um pouco o contraste,
    como foto antiga (de leve: 0,3 já basta). Use num <g> por cima de tudo (ou no grupo do mundo)."""
    ident = (1, 0, 0, 0, 1, 0, 0, 0, 1)
    m = [a + (b - a) * k for a, b in zip(ident, SEPIA)]
    c = 1 - 0.12 * fade * k
    off = 0.05 * fade * k
    rows = [m[0:3], m[3:6], m[6:9]]
    vals = " ".join(" ".join(_f(v * c) for v in r) + f" 0 {_f(off)}" for r in rows) + " 0 0 0 1 0"
    return f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{vals}"/></filter>'


def fade_through(t: float, t_mid: float, dur: float = 0.8) -> float:
    """Opacidade de um véu (preto, branco ou sépia) que sobe até t_mid e desce depois. Transição calma."""
    u = abs(t - t_mid) / (dur / 2)
    return 1 - smooth(u) if u < 1 else 0.0


# ---------------------------------------------------------------- cartela
def typewriter(text: str, t: float, t0: float, x: float, y: float, size: float = 64, cps: float = 14,
               fill: str = "#f4efe6", font: str = "Courier New", weight: int = 700, anchor: str = "start",
               cursor: bool = True, hold_cursor: float = 1.2) -> str:
    """Texto entrando letra a letra a partir de t0 (cps = caracteres por segundo). O cursor pisca
    enquanto digita e por `hold_cursor` segundos depois. Devolve <text>. Os instantes de cada tecla
    (para o som) saem de typewriter_keys()."""
    n = int(max(0.0, t - t0) * cps)
    shown = text[:n]
    esc = shown.replace("&", "&amp;").replace("<", "&lt;")
    done_at = t0 + len(text) / cps
    cur = ""
    if cursor and t >= t0 and t < done_at + hold_cursor and (int(t * 2.4) % 2 == 0 or t < done_at):
        cur = "▌"
    return (f'<text x="{_f(x)}" y="{_f(y)}" font-family="{font}" font-weight="{weight}" font-size="{_f(size)}" '
            f'fill="{fill}" text-anchor="{anchor}" xml:space="preserve">{esc}{cur}</text>')


def typewriter_keys(text: str, t0: float, cps: float = 14) -> list[float]:
    """Instantes das teclas (ignora espaços) para alinhar o som da máquina de escrever."""
    return [t0 + i / cps for i, ch in enumerate(text) if not ch.isspace()]


def letterbox(w: int, h: int, k: float, ratio: float = 2.39, color: str = "#000") -> str:
    """Faixas de cinema (k 0..1 anima a entrada) para momentos de abertura."""
    bar = max(0.0, (h - w / ratio) / 2) * smooth(k)
    if bar <= 0:
        return ""
    return (f'<rect x="0" y="0" width="{w}" height="{_f(bar)}" fill="{color}"/>'
            f'<rect x="0" y="{_f(h - bar)}" width="{w}" height="{_f(bar)}" fill="{color}"/>')
