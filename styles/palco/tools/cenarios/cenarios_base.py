"""Utilidades comuns dos cenários do estilo palco (ver cenarios.py)."""
from __future__ import annotations

import objetos as O  # noqa: F401
from objetos import R, f, shade  # noqa: F401

X0, X1 = -2000, 3100
FLOOR = 1257
FEET, SC = 1600, 1.25          # personagem em pé (como na loja)
SAFE = (0, 1080)
VIEW_169 = (-1167, 0, 3414, 1920)
VIEW_916 = (0, 0, 1080, 1920)
DARK_DIA = ("#2a2240", 0.1)
DARK_TARDE = ("#2a2240", 0.18)


SEAT_HIP = 235     # quadril de quem senta à mesa, acima do chão (em px do personagem): tampo fica na barriga


def seated_feet(s=SC, hip=SEAT_HIP):
    """Personagem sentado atrás de móvel: devolve o 'pé virtual' para posicionar como em pé
    (quadril a `hip` do chão). Use com recorte abaixo do tampo. Com 160 o tampo batia nos ombros
    e o personagem parecia criança (revisão de 2026-11-05)."""
    return FEET + (622 - 375 - hip) * s


def wall(c, y0=-200, y1=FLOOR):
    return R(X0, y0, X1 - X0, y1 - y0, c)


def floor(kind="madeira", c=None):
    c = c or {"madeira": "#c98d5c", "carpete": "#8e9aa6", "concreto": "#a9a59c", "ceramica": "#e3ddd2", "grama": "#9fd18a"}[kind]
    out = [R(X0, FLOOR, X1 - X0, 2100 - FLOOR, c)]
    if kind == "madeira":
        out += [R(X0, y, X1 - X0, 3 + 2 * i, shade(c, -0.12), 0, ' opacity="0.8"') for i, y in enumerate((1320, 1410, 1530, 1690, 1890))]
    elif kind == "ceramica":
        out += [R(X0, y, X1 - X0, 4, shade(c, -0.1)) for y in (1330, 1440, 1600, 1830)]
        out += [f'<path d="M{x} {FLOOR} L{f(540 + (x - 540) * 2.2)} 2100" stroke="{shade(c, -0.1)}" stroke-width="4"/>'
                for x in range(-1900, 3100, 260)]
    elif kind == "concreto":
        out += [R(X0, y, X1 - X0, 5, shade(c, -0.1)) for y in (1380, 1700)]
        out += [f'<path d="M{x} {FLOOR} L{f(540 + (x - 540) * 2.0)} 2100" stroke="{shade(c, -0.1)}" stroke-width="5"/>'
                for x in range(-1800, 3100, 700)]
    elif kind == "carpete":
        out.append(R(X0, FLOOR, X1 - X0, 10, shade(c, -0.15)))
    out.append(R(X0, FLOOR - 4, X1 - X0, 18, shade(c, -0.22)))     # rodapé / linha do piso
    return "".join(out)


def wainscot(c, top=930, trim=None):
    trim = trim or shade(c, -0.2)
    return (R(X0, top, X1 - X0, FLOOR - top, c) + R(X0, top - 12, X1 - X0, 16, trim)
            + "".join(R(x, top + 30, 8, FLOOR - top - 60, shade(c, -0.08)) for x in range(X0 + 60, X1, 120)))


def wallpaper_stripes(c, c2, y0=-200, y1=930, w=60):
    return R(X0, y0, X1 - X0, y1 - y0, c) + "".join(R(x, y0, w / 2, y1 - y0, c2) for x in range(X0, X1, w))


def ceiling(c, h=170):
    return R(X0, -200, X1 - X0, h + 200, c) + R(X0, h - 14, X1 - X0, 14, shade(c, -0.18))


def pool(cx, cy, rx, ry, col, op):
    return (cx, cy, rx, ry, col, op)


