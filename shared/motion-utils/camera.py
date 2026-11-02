"""Câmera virtual 2D para cenas em SVG (agnóstica de estilo). Só biblioteca padrão.

A cena é desenhada em coordenadas de mundo dentro de um <g transform="...">;
a câmera diz qual ponto do mundo fica no centro da tela e com que zoom.

    from camera import Cam, cam_transform, shake_at, flash_envelope, ease_out_expo, ease_in_quad

    cam = Cam([
        (0.0, 340, 900, 5.0, None),            # (t, cx, cy, zoom, easing do trecho que CHEGA aqui)
        (1.0, 540, 1180, 0.98, ease_out_expo), # afastamento rápido
        (8.1, 540, 1000, 1.75, ease_in_quad),  # push lento até o corte
    ])
    cx, cy, z = cam.at(t)
    g = f'<g transform="{cam_transform(cx, cy, z, shake_at(t, amp=12), w=1080, h=1920)}">...</g>'
    flash = flash_envelope(t, t_cut=8.1)        # opacidade de um <rect> branco por cima de tudo

Usado primeiro em carlbob1 (hook: zoom 5 -> 0,98 em 1 s, tremida no pouso,
riser com tremida crescente e flash branco no corte).
"""
from __future__ import annotations

import math


# ---------------------------------------------------------------- easings
def clamp01(x: float) -> float: return max(0.0, min(1.0, x))
def lerp(a: float, b: float, t: float) -> float: return a + (b - a) * t
def linear(t: float) -> float: return clamp01(t)
def ease_out_cubic(t: float) -> float: t = clamp01(t); return 1 - (1 - t) ** 3
def ease_in_out(t: float) -> float: t = clamp01(t); return t * t * (3 - 2 * t)
def ease_out_expo(t: float) -> float: t = clamp01(t); return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)
def ease_in_quad(t: float) -> float: t = clamp01(t); return t * t


def ease_out_back(t: float, s: float = 2.2) -> float:
    t = clamp01(t) - 1
    return 1 + t * t * ((s + 1) * t + s)


def pop(t: float, t0: float, dur: float = 0.28) -> float:
    """Escala de entrada com overshoot (0 antes de t0). Bom para texto e ícones."""
    if t < t0:
        return 0.0
    return ease_out_back((t - t0) / dur)


def noise(t: float, seed: float, freq: float) -> float:
    """Ruído suave determinístico em -1..1 (soma de senos)."""
    return (math.sin(t * freq * 6.283 + seed * 1.7) * 0.6
            + math.sin(t * freq * 2.31 * 6.283 + seed * 4.1) * 0.4)


# ---------------------------------------------------------------- câmera
class Cam:
    """Keyframes (t, cx, cy, z, ease). Ponto do mundo (cx, cy) no centro da tela.
    O ease de cada keyframe vale para o trecho que termina nele (None = linear)."""

    def __init__(self, keys):
        self.keys = keys

    def at(self, t: float):
        k = self.keys
        if t <= k[0][0]:
            return k[0][1:4]
        for a, b in zip(k, k[1:]):
            if t <= b[0]:
                u = (b[4] or linear)((t - a[0]) / (b[0] - a[0]))
                # zoom interpolado em escala log (sensação de velocidade constante)
                z = math.exp(lerp(math.log(a[3]), math.log(b[3]), u))
                return lerp(a[1], b[1], u), lerp(a[2], b[2], u), z
        return k[-1][1:4]


def cam_transform(cx: float, cy: float, z: float, shake=(0.0, 0.0, 0.0), w: int = 1080, h: int = 1920) -> str:
    sx, sy, rot = shake
    return (f"translate({w / 2 + sx:.2f},{h / 2 + sy:.2f}) rotate({rot:.3f}) "
            f"scale({z:.4f}) translate({-cx:.2f},{-cy:.2f})")


def shake_at(t: float, amp: float, seed: int = 0):
    """(dx, dy, rotação em graus) da tremida; amp em px de tela."""
    if amp <= 0:
        return (0.0, 0.0, 0.0)
    return (amp * noise(t, seed, 9.0), amp * noise(t, seed + 3, 8.3), amp * 0.06 * noise(t, seed + 7, 5.1))


def shake_decay(t: float, t0: float, amp: float, dur: float = 0.5) -> float:
    """Amplitude de tremida de impacto: amp em t0, decai até 0 em dur."""
    if not t0 <= t < t0 + dur:
        return 0.0
    return amp * (1 - ease_out_cubic((t - t0) / dur))


def flash_envelope(t: float, t_cut: float, attack: float = 0.24, hold: float = 0.06, release: float = 0.34) -> float:
    """Opacidade do flash branco de corte: sobe antes do corte, segura, e some depois."""
    if t_cut - attack <= t < t_cut:
        return ease_in_quad((t - (t_cut - attack)) / attack)
    if t_cut <= t < t_cut + hold:
        return 1.0
    if t_cut + hold <= t < t_cut + hold + release:
        return 1 - ease_out_cubic((t - t_cut - hold) / release)
    return 0.0
