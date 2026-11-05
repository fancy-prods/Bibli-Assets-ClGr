"""Objetos do estilo palco (aprovados em 2026-11-05). Cenário: chapado, sem contorno, sombra de contato.

Convenção: cada função recebe (x, y) = ponto de apoio (centro da base, no chão ou no tampo)
e s = escala (1 = escala do personagem 1,0; personagem em pé tem 622 de altura).
Retornam um trecho de SVG. Cores com parâmetro onde faz sentido. `epoca=True` troca o
desenho por uma versão de 1900-1940 quando existe.
"""
from __future__ import annotations

import math


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def shade(c, k):
    """k < 0 escurece, k > 0 clareia (0..1)."""
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    t = 255 if k > 0 else 0
    k = abs(k)
    return "#" + "".join(f"{round(v + (t - v) * k):02x}" for v in (r, g, b))


def shadow(x, y, rx, ry=None, op=0.24):
    ry = ry if ry is not None else rx * 0.16
    return f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}" fill="#000" opacity="{op}"/>'


def R(x, y, w, h, c, rx=0, extra=""):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{c}"{extra}/>'


def g(content, x=0, y=0, s=1.0):
    return f'<g transform="translate({f(x)},{f(y)}) scale({f(s)})">{content}</g>'


# ---------------------------------------------------------------- móveis
def mesa_escritorio(x, y, s=1.0, cor="#7a4a2e", epoca=False, w=520):
    """Mesa de executivo vista de frente (painel fechado até o chão: esconde as pernas de quem
    está sentado atrás). Tampo a 250 unidades do chão. y = chão."""
    h = 250
    d = shade(cor, -0.2)
    out = [shadow(0, 4, w / 2 + 40, 16),
           R(-w / 2, -h + 18, w, h - 18, cor),
           R(-w / 2 - 14, -h, w + 28, 26, shade(cor, 0.12), 6)]
    if epoca:   # gavetas com puxadores de latão e pés torneados
        for gx in (-w / 2 + 20, w / 2 - 170):
            for k in range(3):
                out += [R(gx, -h + 40 + k * 64, 150, 54, d, 4), R(gx + 60, -h + 62 + k * 64, 30, 8, "#d9b14a", 4)]
        out.append(R(-w / 2 + 190, -h + 40, w - 380, 180, d, 4))
    else:       # painel liso com faixa
        out += [R(-w / 2 + 24, -h + 44, w - 48, 8, d, 4), R(-w / 2 + 24, -h + 70, w - 48, h - 88, shade(cor, -0.08), 6)]
    return g("".join(out), x, y, s)


def cadeira_executivo(x, y, s=1.0, cor="#3a2a24", epoca=False, base=True):
    """Cadeira de encosto alto (desenhar ANTES do personagem). y = chão.
    base=True desenha assento e pé (giratório com rodinhas; época: pés de madeira); atrás de uma mesa
    eles ficam escondidos pelo móvel, então tanto faz."""
    top = -560 if not epoca else -520
    w = 230
    out = []
    if base:
        dk = shade(cor, -0.25)
        if epoca:
            out += [R(-100, -200, 18, 200, dk, 5), R(82, -200, 18, 200, dk, 5)]
        else:
            out += [shadow(0, 4, 120, 14), R(-9, -200, 18, 170, "#2b2b2b", 4),
                    f'<path d="M-115 -18 L115 -18 L105 -34 L-105 -34 Z" fill="#2b2b2b"/>']
            out += [f'<circle cx="{cx}" cy="-8" r="10" fill="#1a1a1a"/>' for cx in (-108, 0, 108)]
        out += [R(-w / 2 - 6, -250, w + 12, 56, shade(cor, 0.06), 22), R(-w / 2, -205, w, 16, dk, 6)]
    out += [R(-w / 2, top, w, 330, cor, 40), R(-w / 2 + 22, top + 24, w - 44, 280, shade(cor, 0.1), 30)]
    if epoca:
        out += [f'<circle cx="{f(cx)}" cy="{f(top + 60 + r * 70)}" r="6" fill="{shade(cor, -0.3)}"/>'
                for cx in (-60, 0, 60) for r in range(4)]
    return g("".join(out), x, y, s)


def cadeira(x, y, s=1.0, cor="#8f5636", lado="frente"):
    """Cadeira de madeira simples. lado: frente (encosto atrás do personagem) ou perfil."""
    if lado == "perfil":
        out = [shadow(0, 4, 90), R(-70, -170, 140, 18, cor, 6), R(-66, -160, 14, 160, cor, 4), R(52, -160, 14, 160, cor, 4),
               R(52, -420, 16, 270, cor, 6), R(48, -420, 24, 40, shade(cor, 0.1), 8)]
    else:
        # de frente: encosto (atrás do personagem) acima do assento; assento largo com tampo em perspectiva
        out = [shadow(0, 4, 95), R(-66, -190, 14, 190, shade(cor, -0.2), 4), R(52, -190, 14, 190, shade(cor, -0.2), 4),   # pernas de trás
               R(-75, -420, 16, 240, cor, 6), R(59, -420, 16, 240, cor, 6),                                    # montantes do encosto
               R(-82, -430, 164, 34, shade(cor, 0.08), 12), R(-75, -340, 150, 16, cor, 6),
               f'<path d="M-72 -212 L72 -212 L90 -180 L-90 -180 Z" fill="{shade(cor, 0.12)}"/>',              # tampo do assento
               R(-90, -182, 180, 26, shade(cor, -0.08), 6),                                                    # frente do assento
               R(-84, -160, 16, 160, cor, 4), R(68, -160, 16, 160, cor, 4)]                                    # pernas da frente
    return g("".join(out), x, y, s)


def sofa(x, y, s=1.0, cor="#c0574a", w=620):
    d, l = shade(cor, -0.18), shade(cor, 0.1)
    out = [shadow(0, 6, w / 2 + 30, 18),
           R(-w / 2, -330, w, 210, d, 40),                       # encosto
           R(-w / 2 - 40, -230, 90, 210, cor, 36), R(w / 2 - 50, -230, 90, 210, cor, 36),   # braços
           R(-w / 2 + 40, -170, w - 80, 110, l, 24),             # assento
           R(-w / 2 + 20, -80, w - 40, 60, d, 10),
           R(-w / 2 + 10, -22, 24, 22, "#3a2a20", 4), R(w / 2 - 34, -22, 24, 22, "#3a2a20", 4)]
    out += [R(-w / 2 + 50 + k * (w - 100) / 3 + 6, -320, (w - 100) / 3 - 12, 150, cor, 28) for k in range(3)]
    return g("".join(out), x, y, s)


def mesa_toalha(x, y, s=1.0, rx=250, cloth="#f7f1e6", altura=240):
    """Mesa redonda com toalha até o chão (esconde o corpo de quem senta atrás). y = chão."""
    c, cd = cloth, shade(cloth, -0.12)
    top = -altura
    path = (f'M{-rx} {top} L{-rx - 18} 0 '
            + "".join(f'Q{f(-rx - 18 + (k + 0.5) * (2 * rx + 36) / 6)} 10 {f(-rx - 18 + (k + 1) * (2 * rx + 36) / 6)} 0 ' for k in range(6))
            + f'L{rx} {top} Z')
    out = [shadow(0, 6, rx + 30, 16), f'<path d="{path}" fill="{cd}"/>', f'<ellipse cx="0" cy="{top}" rx="{rx}" ry="30" fill="{c}"/>',
           R(-rx * 0.45 - 4, top + 30, 8, altura - 44, "#000", 4, ' opacity="0.06"'),
           R(rx * 0.45 - 4, top + 30, 8, altura - 44, "#000", 4, ' opacity="0.06"')]
    return g("".join(out), x, y, s)


def mesa_jantar(x, y, s=1.0, w=900, cloth="#f4efe6", epoca=False, pratos=4, centro=120):
    """Mesa de jantar retangular vista de frente, toalha até perto do chão, com pratos e copos.
    centro = distância do centro dos enfeites (castiçais, jarra, vaso), para caírem entre os lugares."""
    top = -250
    out = [shadow(0, 6, w / 2 + 40, 18),
           f'<path d="M{-w / 2} {top} L{w / 2} {top} L{w / 2 + 16} -30 L{-w / 2 - 16} -30 Z" fill="{shade(cloth, -0.1)}"/>',
           R(-w / 2 - 16, -34, w + 32, 10, shade(cloth, -0.18), 4),
           f'<ellipse cx="0" cy="{top}" rx="{w / 2}" ry="26" fill="{cloth}"/>',
           R(-w / 2 + 30, -30, 22, 30, "#5a3a26"), R(w / 2 - 52, -30, 22, 30, "#5a3a26")]
    if epoca:
        out.append(R(-w / 2, top + 30, w, 20, "#c9a35a", 0, ' opacity="0.5"'))
    for k in range(pratos):
        px = -w / 2 + (k + 0.5) * w / pratos
        out += [f'<ellipse cx="{f(px)}" cy="{top - 2}" rx="56" ry="11" fill="#ffffff"/>',
                f'<ellipse cx="{f(px)}" cy="{top - 4}" rx="34" ry="6" fill="#e9e1d4"/>',
                R(px + 66, top - 46, 18, 44, "#cfe6f2", 4, ' opacity="0.85"')]
    if epoca:   # castiçal no centro
        for cx in (-centro, centro):   # castiçais entre os lugares (não tampam rostos)
            out += [R(cx - 10, top - 120, 20, 118, "#d9b14a", 4), R(cx - 30, top - 10, 60, 10, "#d9b14a", 4),
                    R(cx - 6, top - 160, 12, 40, "#fbf3dc", 3), f'<ellipse cx="{cx}" cy="{top - 172}" rx="7" ry="13" fill="#ffcf5a"/>']
    else:       # jarra e vaso entre os lugares
        out += [R(-centro - 20, top - 70, 40, 70, "#9fd0e6", 10, ' opacity="0.85"'),
                f'<circle cx="{centro}" cy="{top - 60}" r="26" fill="#e2574c"/><circle cx="{centro + 24}" cy="{top - 76}" r="20" fill="#f2c14e"/>',
                R(centro - 10, top - 40, 40, 40, "#5a8fb8", 8)]
    return g("".join(out), x, y, s)


def estante(x, y, s=1.0, w=420, h=780, cor="#7a4a2e", seed=1):
    """Estante de livros (y = chão)."""
    out = [R(-w / 2, -h, w, h, cor), R(-w / 2 + 16, -h + 16, w - 32, h - 32, shade(cor, -0.25))]
    cores = ["#c24a3a", "#3f7fc4", "#f2c14e", "#4a9a5c", "#8a5aa8", "#e8e2d6", "#2f3b36", "#d9825b"]
    shelves = 5
    sh = (h - 32) / shelves
    rnd = seed
    for k in range(shelves):
        by = -h + 16 + (k + 1) * sh
        out.append(R(-w / 2 + 16, by - 12, w - 32, 12, cor))
        bx = -w / 2 + 24
        while bx < w / 2 - 50:
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            bw = 18 + rnd % 22
            bh = sh - 40 - (rnd >> 8) % 34
            out.append(R(bx, by - 12 - bh, bw, bh, cores[(rnd >> 4) % len(cores)], 2))
            bx += bw + 3
            if (rnd >> 12) % 11 == 0:
                bx += 30
    return g("".join(out), x, y, s)


def arquivo(x, y, s=1.0, cor="#8f9aa3"):
    out = [shadow(0, 4, 110), R(-95, -520, 190, 520, cor, 6)]
    for k in range(4):
        out += [R(-80, -505 + k * 126, 160, 110, shade(cor, 0.1), 4), R(-30, -460 + k * 126, 60, 12, shade(cor, -0.35), 6)]
    return g("".join(out), x, y, s)


def cabideiro(x, y, s=1.0, cor="#5a3a26", chapeu=True):
    out = [shadow(0, 4, 70), R(-8, -620, 16, 620, cor, 6), R(-60, -14, 120, 14, cor, 6),
           f'<path d="M0 -600 l-60 40 M0 -600 l60 40 M0 -560 l-50 50 M0 -560 l50 50" stroke="{cor}" stroke-width="10" stroke-linecap="round"/>']
    if chapeu:
        out += [f'<ellipse cx="-62" cy="-556" rx="56" ry="10" fill="#2b2b2b"/>', R(-96, -610, 68, 56, "#2b2b2b", 14)]
        out += [R(30, -540, 70, 220, "#4a5a6b", 20)]   # casaco pendurado
    return g("".join(out), x, y, s)


def porta(x, y, s=1.0, cor="#8f5636", aberta=0.0):
    """Porta na parede (y = chão). aberta 0..1 mostra o vão escuro."""
    w, h = 260, 560
    out = [R(-w / 2 - 20, -h - 20, w + 40, h + 20, shade(cor, -0.25)), R(-w / 2, -h, w, h, "#3a2f2a")]
    leaf = w * (1 - 0.8 * aberta)
    out += [R(-w / 2, -h, leaf, h, cor), R(-w / 2 + 24, -h + 30, leaf - 48, 220, shade(cor, 0.08), 6),
            R(-w / 2 + 24, -h + 290, leaf - 48, 230, shade(cor, 0.08), 6),
            f'<circle cx="{f(-w / 2 + leaf - 30)}" cy="{-h / 2 + 10}" r="12" fill="#d9b14a"/>']
    return g("".join(out), x, y, s)


# ---------------------------------------------------------------- paredes e janelas
def janela(x, y, s=1.0, w=430, h=560, vista="cidade", fr="#4a6b57", hora="dia"):
    """Janela (x, y = canto superior esquerdo). vista: cidade | arvores | ceu | fabrica."""
    sky = {"dia": ("#bfe6f6", "#d9f1f9"), "entardecer": ("#f6b98a", "#fbd9b0"), "noite": ("#2c3a5a", "#3e4f73")}[hora]
    out = [R(0, 0, w, h, sky[0]), R(0, h * 0.55, w, h * 0.45, sky[1])]
    if vista == "cidade":
        for k, (bx, bw, bh, c) in enumerate(((0.02, 0.22, 0.6, "#a9c3d9"), (0.2, 0.18, 0.78, "#8fb0cc"),
                                              (0.42, 0.2, 0.55, "#b7cde0"), (0.6, 0.22, 0.85, "#9ab8d2"), (0.8, 0.2, 0.62, "#adc6dc"))):
            out.append(R(bx * w, h * (1 - bh), bw * w, h * bh, c))
            for j in range(int(bh * 9)):
                for i in range(2):
                    out.append(R(bx * w + 10 + i * bw * w * 0.45, h * (1 - bh) + 16 + j * 38, bw * w * 0.3, 16, "#fff",
                                 0, ' opacity="0.45"'))
    elif vista == "arvores":
        out += [R(w * 0.18, h * 0.55, 16, h * 0.45, "#7d5a43"), f'<circle cx="{f(w * 0.2)}" cy="{f(h * 0.5)}" r="{f(w * 0.22)}" fill="#8cc59a"/>',
                f'<circle cx="{f(w * 0.72)}" cy="{f(h * 0.62)}" r="{f(w * 0.2)}" fill="#7fb98e"/>', R(w * 0.7, h * 0.75, 14, h * 0.25, "#7d5a43")]
    elif vista == "fabrica":
        out += [R(w * 0.1, h * 0.5, w * 0.3, h * 0.5, "#9aa4ad"), R(w * 0.2, h * 0.2, 30, h * 0.3, "#7d8790"),
                R(w * 0.55, h * 0.6, w * 0.4, h * 0.4, "#aab3bb"), R(w * 0.75, h * 0.3, 26, h * 0.3, "#7d8790"),
                f'<circle cx="{f(w * 0.22)}" cy="{f(h * 0.14)}" r="34" fill="#dfe3e6" opacity="0.8"/>']
    t = 16
    out += [R(-t, -t, w + 2 * t, t + 2, fr), R(-t, h - 2, w + 2 * t, t + 6, fr), R(-t, -t, t + 2, h + 2 * t, fr),
            R(w - 2, -t, t + 2, h + 2 * t, fr), R(w / 2 - 6, 0, 12, h, fr), R(0, h * 0.42, w, 10, fr),
            R(-30, h + 16, w + 60, 16, shade(fr, 0.55), 4)]
    return g("".join(out), x, y, s)


def quadro(x, y, w=180, h=220, tipo="paisagem", moldura="#8f5636", s=1.0):
    """Quadro na parede (x, y = canto superior esquerdo). tipo: paisagem | retrato | diploma | mapa."""
    out = [R(0, 0, w, h, moldura, 4), R(12, 12, w - 24, h - 24, "#f4efe6")]
    iw, ih = w - 24, h - 24
    if tipo == "paisagem":
        out += [R(12, 12, iw, ih * 0.6, "#9fd6f2"), R(12, 12 + ih * 0.6, iw, ih * 0.4, "#8cc59a"),
                f'<path d="M12 {f(12 + ih * 0.62)} L{f(12 + iw * 0.4)} {f(12 + ih * 0.25)} L{f(12 + iw * 0.7)} {f(12 + ih * 0.62)} Z" fill="#7d8fa8"/>',
                f'<circle cx="{f(12 + iw * 0.8)}" cy="{f(12 + ih * 0.22)}" r="{f(iw * 0.08)}" fill="#fff2b0"/>']
    elif tipo == "retrato":
        out += [R(12, 12, iw, ih, "#5a4a42"), f'<circle cx="{f(w / 2)}" cy="{f(12 + ih * 0.4)}" r="{f(iw * 0.2)}" fill="#e0b18f"/>',
                f'<path d="M{f(w / 2 - iw * 0.32)} {f(12 + ih)} Q{f(w / 2)} {f(12 + ih * 0.5)} {f(w / 2 + iw * 0.32)} {f(12 + ih)} Z" fill="#2b2b2b"/>']
    elif tipo == "diploma":
        out += [R(30, 34, iw - 36, 10, "#2f3b36", 3)] + [R(36, 60 + k * 22, iw - 48, 6, "#9a8f80", 3) for k in range(int((ih - 90) / 22))]
        out.append(f'<circle cx="{f(w - 46)}" cy="{f(h - 44)}" r="18" fill="#c24a3a"/>')
    elif tipo == "mapa":
        out += [R(12, 12, iw, ih, "#cfe6f2"),
                f'<path d="M{f(12 + iw * 0.1)} {f(12 + ih * 0.3)} q{f(iw * 0.2)} -{f(ih * 0.2)} {f(iw * 0.35)} 0 t{f(iw * 0.1)} {f(ih * 0.4)} '
                f'q-{f(iw * 0.3)} {f(ih * 0.1)} -{f(iw * 0.45)} -{f(ih * 0.4)} Z" fill="#a8cf8f"/>',
                f'<path d="M{f(12 + iw * 0.6)} {f(12 + ih * 0.2)} q{f(iw * 0.25)} 0 {f(iw * 0.3)} {f(ih * 0.3)} t-{f(iw * 0.1)} {f(ih * 0.4)} '
                f'q-{f(iw * 0.2)} -{f(ih * 0.2)} -{f(iw * 0.2)} -{f(ih * 0.7)} Z" fill="#d9c27a"/>']
    return g("".join(out), x, y, s)


def relogio_parede(x, y, r=70, t=None, cor="#3a2a20", epoca=False):
    """Relógio de parede (x, y = centro). t = horas do dia (ex.: 9.5 = 9h30) para os ponteiros."""
    t = 10.15 if t is None else t
    hh = (t % 12) / 12 * 360
    mm = (t % 1) * 360
    out = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + 10)}" fill="{cor}"/>',
           f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#fbf6ea"/>']
    for k in range(12):
        a = math.radians(k * 30)
        L = 14 if k % 3 == 0 else 7
        out.append(f'<line x1="{f(x + math.sin(a) * (r - 6))}" y1="{f(y - math.cos(a) * (r - 6))}" '
                   f'x2="{f(x + math.sin(a) * (r - 6 - L))}" y2="{f(y - math.cos(a) * (r - 6 - L))}" stroke="#3a2a20" stroke-width="{4 if L > 10 else 3}"/>')
    for ang, L, w in ((hh, r * 0.5, 8), (mm, r * 0.78, 5)):
        a = math.radians(ang)
        out.append(f'<line x1="{f(x)}" y1="{f(y)}" x2="{f(x + math.sin(a) * L)}" y2="{f(y - math.cos(a) * L)}" '
                   f'stroke="#2b2b2b" stroke-width="{w}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="7" fill="#c24a3a"/>')
    if epoca:   # caixa de pêndulo
        out.insert(0, R(x - r - 24, y - r - 24, 2 * r + 48, 3.2 * r, cor, 12))
        out.append(R(x - 4, y + r + 12, 8, r * 1.3, "#d9b14a", 3))
        out.append(f'<circle cx="{f(x)}" cy="{f(y + r * 2.4)}" r="18" fill="#d9b14a"/>')
    return "".join(out)


def luminaria_pendente(x, y, cor="#e3a23f", teto=0):
    """Fonte de luz: fio do teto, cúpula e lâmpada (desenhar por cima de tudo). y = borda da cúpula."""
    return (R(x - 2, teto, 4, y - 40 - teto, "#3a2a20")
            + f'<path d="M{f(x - 70)} {f(y)} Q{f(x - 64)} {f(y - 62)} {f(x)} {f(y - 64)} Q{f(x + 64)} {f(y - 62)} {f(x + 70)} {f(y)} Z" fill="{cor}"/>'
            + f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="70" ry="10" fill="{shade(cor, -0.2)}"/>'
            + f'<ellipse cx="{f(x)}" cy="{f(y + 6)}" rx="26" ry="12" fill="#fff6d8"/>')


def lustre(x, y, teto=0, cor="#d9b14a"):
    """Lustre de época com velas/lâmpadas (fonte de luz)."""
    out = [R(x - 3, teto, 6, y - teto - 40, cor), f'<ellipse cx="{f(x)}" cy="{f(y - 30)}" rx="26" ry="20" fill="{cor}"/>',
           f'<path d="M{f(x - 150)} {f(y)} Q{f(x)} {f(y + 60)} {f(x + 150)} {f(y)}" stroke="{cor}" stroke-width="10" fill="none"/>']
    for k in range(5):
        bx = x - 150 + k * 75
        by = y + (30 if 0 < k < 4 else 0) + (14 if k == 2 else 0)
        out += [R(bx - 6, by - 34, 12, 30, "#fbf3dc", 3), f'<ellipse cx="{f(bx)}" cy="{f(by - 44)}" rx="8" ry="13" fill="#ffd36a"/>']
    return "".join(out)


def luminaria_mesa(x, y, s=1.0, epoca=False):
    """Luminária de mesa (y = tampo). Época: luminária de banqueiro verde."""
    if epoca:
        out = [R(-50, -10, 100, 10, "#d9b14a", 4), R(-6, -100, 12, 92, "#d9b14a"),
               f'<path d="M-90 -100 Q-88 -140 0 -142 Q88 -140 90 -100 Z" fill="#2f7a4f"/>',
               f'<ellipse cx="0" cy="-100" rx="88" ry="8" fill="#fff2c0"/>']
    else:
        out = [R(-44, -10, 88, 10, "#2b2f36", 4), f'<path d="M0 -10 L-30 -130 L40 -170" stroke="#2b2f36" stroke-width="10" fill="none" stroke-linecap="round"/>',
               f'<path d="M20 -186 L90 -150 L60 -126 Z" fill="#2b2f36"/>', f'<ellipse cx="75" cy="-138" rx="16" ry="6" fill="#fff2c0"/>']
    return g("".join(out), x, y, s)


# ---------------------------------------------------------------- objetos de mesa (y = tampo)
def xicara(x, y, s=1.0, cor="#f4efe6", cafe="#5a3320"):
    out = [f'<ellipse cx="0" cy="2" rx="40" ry="8" fill="{shade(cor, -0.08)}"/>',
           f'<path d="M26 -30 q18 -2 18 13 q0 14 -20 13" fill="none" stroke="{cor}" stroke-width="7"/>',
           f'<path d="M-28 -42 L28 -42 Q27 -6 13 0 L-13 0 Q-27 -6 -28 -42 Z" fill="{cor}"/>',
           f'<ellipse cx="0" cy="-42" rx="28" ry="6" fill="{shade(cor, -0.06)}"/>',
           f'<ellipse cx="0" cy="-41" rx="23" ry="4" fill="{cafe}"/>']
    return g("".join(out), x, y, s)


def vapor(x, y, t, s=1.0, n=3, altura=120, op=0.45):
    """Vapor animado (t em segundos) subindo de (x, y). Sem máscara: opacidade cai por segmento."""
    out = []
    for i in range(n):
        dx, ph = (i - (n - 1) / 2) * 12, i * 1.9
        prev = None
        for j in range(13):
            u = j / 12
            yy = y - u * altura * s
            xx = x + dx * s + (4 + 10 * u) * s * math.sin(u * 5.2 - t * 2.1 + ph)
            if prev:
                a = op * math.sin(math.pi * min(1, u * 1.3)) ** 0.8
                out.append(f'<line x1="{f(prev[0])}" y1="{f(prev[1])}" x2="{f(xx)}" y2="{f(yy)}" stroke="#fff" '
                           f'stroke-width="{f(5 * s)}" stroke-linecap="round" opacity="{f(a)}"/>')
            prev = (xx, yy)
    return "".join(out)


def notebook(x, y, s=1.0, cor="#c4cbd2", lado="tras"):
    """Notebook aberto. lado: tras (tela virada para quem está atrás da mesa) ou frente."""
    if lado == "tras":
        out = [R(-80, -110, 160, 104, cor, 8), f'<circle cx="0" cy="-60" r="10" fill="{shade(cor, 0.4)}"/>', R(-92, -8, 184, 8, shade(cor, -0.2), 3)]
    else:
        out = [R(-80, -110, 160, 104, "#2b2f36", 8), R(-70, -100, 140, 84, "#8fc6ff", 4), R(-92, -8, 184, 8, cor, 3)]
    return g("".join(out), x, y, s)


def monitor(x, y, s=1.0):
    out = [R(-30, -12, 60, 12, "#2b2f36", 4), R(-8, -60, 16, 50, "#2b2f36"), R(-120, -200, 240, 145, "#2b2f36", 10),
           R(-110, -190, 220, 125, "#8fc6ff", 4), R(-100, -180, 120, 10, "#ffffff", 4, ' opacity="0.6"')]
    return g("".join(out), x, y, s)


def telefone_disco(x, y, s=1.0, cor="#1f1f1f"):
    out = [f'<path d="M-70 0 L-56 -50 Q0 -64 56 -50 L70 0 Z" fill="{cor}"/>',
           f'<circle cx="0" cy="-30" r="24" fill="#e8e2d6"/>',
           *[f'<circle cx="{f(math.cos(math.radians(a)) * 15)}" cy="{f(-30 + math.sin(math.radians(a)) * 15)}" r="3.5" fill="{cor}"/>'
             for a in range(-60, 241, 30)],
           f'<path d="M-74 -62 Q-74 -86 -50 -86 L50 -86 Q74 -86 74 -62 L58 -56 Q50 -74 30 -72 L-30 -72 Q-50 -74 -58 -56 Z" fill="{cor}"/>']
    return g("".join(out), x, y, s)


def maquina_escrever(x, y, s=1.0, cor="#2b2f36"):
    out = [f'<path d="M-110 0 L-90 -70 L90 -70 L110 0 Z" fill="{cor}"/>', R(-100, -96, 200, 26, shade(cor, 0.15), 12),
           R(-60, -160, 120, 70, "#fbf6ea"), *[R(-46, -150 + k * 12, 92, 4, "#9a8f80", 2) for k in range(4)],
           *[f'<circle cx="{-72 + i * 16 + (j % 2) * 8}" cy="{-50 + j * 16}" r="6" fill="#e8e2d6"/>' for j in range(3) for i in range(9)]]
    return g("".join(out), x, y, s)


def livro_aberto(x, y, s=1.0, capa="#c24a3a"):
    out = [f'<path d="M-90 0 L-86 -14 Q-46 -26 0 -14 Q46 -26 86 -14 L90 0 Q46 -10 0 0 Q-46 -10 -90 0 Z" fill="{capa}"/>',
           f'<path d="M-82 -12 Q-44 -26 0 -12 L0 -6 Q-44 -18 -82 -6 Z" fill="#fbf6ea"/>',
           f'<path d="M82 -12 Q44 -26 0 -12 L0 -6 Q44 -18 82 -6 Z" fill="#f2ead8"/>']
    return g("".join(out), x, y, s)


def pilha_livros(x, y, s=1.0, n=3):
    cores = ["#3f7fc4", "#c24a3a", "#4a9a5c", "#f2c14e", "#8a5aa8"]
    out, yy = [], 0
    for k in range(n):
        w = 150 - (k % 2) * 20
        out += [R(-w / 2 + (k % 2) * 8, yy - 22, w, 22, cores[k % 5], 3), R(-w / 2 + 6 + (k % 2) * 8, yy - 18, w - 12, 4, "#fff", 2, ' opacity="0.5"')]
        yy -= 22
    return g("".join(out), x, y, s)


def papeis(x, y, s=1.0, n=3):
    out = []
    for k in range(n):
        out.append(f'<g transform="rotate({(k - 1) * 6} 0 -4)">{R(-60, -8 - k * 3, 120, 8, "#fbf6ea", 2)}</g>')
    return g("".join(out), x, y, s)


def carta(x, y, s=1.0, rot=0, linhas=6):
    """Folha de carta vista de frente (para close/inserto). x, y = centro."""
    out = [R(-90, -120, 180, 240, "#fbf6ea", 4), *[R(-70, -90 + k * 30, 140 - (k == linhas - 1) * 60, 7, "#5a6b7a", 3) for k in range(linhas)]]
    return f'<g transform="translate({f(x)},{f(y)}) rotate({f(rot)}) scale({f(s)})">{"".join(out)}</g>'


def planta(x, y, s=1.0, pot="#d9825b"):
    leaves = "".join(
        f'<ellipse cx="{dx}" cy="{-120 + dy}" rx="30" ry="78" fill="{c}" transform="rotate({a} {dx} {-120 + dy})"/>'
        for dx, dy, a, c in ((-40, -10, -30, "#5e9e6e"), (40, -10, 30, "#5e9e6e"), (0, -40, 0, "#78b585"),
                             (-70, 30, -55, "#6aa878"), (70, 30, 55, "#6aa878")))
    return g(shadow(0, 0, 80, 14, 0.22) + leaves + f'<path d="M-62 -110 L62 -110 L46 0 L-46 0 Z" fill="{pot}"/>', x, y, s)


def globo(x, y, s=1.0):
    out = [R(-40, -10, 80, 10, "#5a3a26", 4), R(-6, -60, 12, 52, "#5a3a26"),
           f'<path d="M-60 -120 A62 62 0 0 0 30 -60" stroke="#d9b14a" stroke-width="7" fill="none"/>',
           f'<circle cx="0" cy="-120" r="52" fill="#7fb7dc"/>',
           f'<path d="M-30 -150 q20 -10 30 6 t10 30 q-20 10 -36 -8 Z" fill="#a8cf8f"/><path d="M14 -110 q20 0 18 24 q-16 4 -20 -10 Z" fill="#a8cf8f"/>']
    return g("".join(out), x, y, s)


# ---------------------------------------------------------------- escola
def quadro_negro(x, y, w=900, h=420, escrito=True, verde=False):
    """Quadro-negro (x, y = canto superior esquerdo)."""
    face = "#2f4a3c" if verde else "#2f3b36"
    out = [R(x - 20, y - 20, w + 40, h + 40, "#8f5636", 6), R(x, y, w, h, face), R(x - 10, y + h + 16, w + 20, 18, "#7a4a2e", 4)]
    if escrito:
        n = max(2, min(5, int((h - 60) / 60)))
        out += [R(x + w * 0.06, y + h * 0.12 + k * (h * 0.76 / n), w * (0.42, 0.58, 0.34, 0.52, 0.3)[k], max(5, h * 0.02), "#ffffff", 4,
                  ' opacity="0.55"') for k in range(n)]
        out.append(R(x + w - 120, y + h + 8, 40, 8, "#fbf6ea", 3))
    return "".join(out)


def carteira(x, y, s=1.0, cor="#a8693f", epoca=False):
    """Carteira escolar vista de frente: painel até o chão (esconde as pernas do aluno). y = chão."""
    top = -230
    out = [shadow(0, 4, 170, 14), R(-150, top, 300, 22, shade(cor, 0.1), 6)]
    if epoca:   # carteira de ferro fundido com tampo de madeira
        out += [R(-140, top + 20, 280, 120, cor, 4),
                f'<path d="M-130 {top + 140} q20 40 0 {-top - 140} M130 {top + 140} q-20 40 0 {-top - 140}" stroke="#2b2b2b" stroke-width="12" fill="none"/>',
                f'<path d="M-130 -60 L130 -60" stroke="#2b2b2b" stroke-width="8"/>']
    else:
        out += [R(-140, top + 20, 280, -top - 24, cor, 4), R(-120, top + 50, 240, 10, shade(cor, -0.2), 4)]
    return g("".join(out), x, y, s)


# ---------------------------------------------------------------- objetos pequenos (para inserto ou mão)
def charuto(x, y, s=1.0, aceso=True):
    out = [R(-60, -8, 120, 16, "#7a4a2e", 8), R(-20, -8, 16, 16, "#c24a3a"), R(-24, -8, 3, 16, "#d9b14a")]
    if aceso:
        out += [R(54, -7, 10, 14, "#9a9a9a", 4), f'<circle cx="64" cy="0" r="5" fill="#ff8a3c"/>']
    return g("".join(out), x, y, s)


def giz(x, y, s=1.0):
    return g(R(-24, -6, 48, 12, "#fbf6ea", 5), x, y, s)


CATALOGO = {
    "mesa_escritorio": "móvel; painel até o chão; epoca", "cadeira_executivo": "encosto alto; epoca",
    "cadeira": "frente | perfil", "sofa": "", "mesa_toalha": "redonda com toalha", "mesa_jantar": "epoca",
    "estante": "livros aleatórios por seed", "arquivo": "", "cabideiro": "com chapéu e casaco", "porta": "aberta 0..1",
    "janela": "vista cidade|arvores|fabrica; hora dia|entardecer|noite", "quadro": "paisagem|retrato|diploma|mapa",
    "relogio_parede": "t = hora (anima ponteiros); epoca = pêndulo", "luminaria_pendente": "fonte de luz",
    "lustre": "fonte de luz, época", "luminaria_mesa": "epoca = banqueiro", "xicara": "", "vapor": "animado por t",
    "notebook": "", "monitor": "", "telefone_disco": "época", "maquina_escrever": "época", "livro_aberto": "",
    "pilha_livros": "", "papeis": "", "carta": "inserto", "planta": "", "globo": "", "quadro_negro": "",
    "carteira": "esconde pernas; epoca", "charuto": "aceso", "giz": "",
}
