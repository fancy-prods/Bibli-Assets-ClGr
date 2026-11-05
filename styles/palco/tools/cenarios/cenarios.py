"""Cenários paramétricos do estilo palco (aprovados em 2026-11-05), no padrão da seção 8 do STYLE.md:
mundo com 1920 de altura, desenhado de x -2000 a 3100 (cobre o 16:9 de x -1167 a 2247 com
folga para câmera), zona segura do 9:16 em x 0 a 1080. Piso em y 1257 (como a loja).

Cada cenário é uma função build(epoca=False, hora="dia") que devolve um dict:
  back    camadas atrás dos personagens (recebem a escuridão)
  front   peças na frente dos personagens (mesa, balcão, carteiras): cor já escurecida
  sources fontes de luz, desenhadas por cima de tudo
  pools   poças de luz [(cx, cy, rx, ry, cor, opacidade)]
  dark    (cor, opacidade) da escuridão global
  anchors âncoras para posicionar personagens (dict nome -> dict)
  sample  personagens de exemplo [(params, x, pés, escala, modo)] modo: em_pe | sentado | costas
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import objetos as O  # noqa: E402
from objetos import R, f, shade  # noqa: E402

from cenarios_base import *  # noqa: E402,F401,F403
from cenarios_base import (X0, X1, FLOOR, FEET, SC, SAFE, VIEW_169, VIEW_916, DARK_DIA, DARK_TARDE,  # noqa: E402
                           seated_feet, wall, floor, wainscot, wallpaper_stripes, ceiling, pool)


# ---------------------------------------------------------------- 1. escritório de executivo
def escritorio(epoca=False, hora="dia"):
    back, front, src = [], [], []
    if epoca:
        back += [wallpaper_stripes("#e9d8b4", "#e2cda4"), wainscot("#9a6a44", 900), ceiling("#7a5236"), floor("madeira", "#a8703f")]
        back.append(O.janela(1250, 280, 1.0, w=520, h=600, vista="cidade", fr="#5a3a26", hora=hora))
        back.append(O.estante(-560, FLOOR, 1.15, cor="#6a3f26", seed=3))
        back.append(O.relogio_parede(-1080, 620, 60, 10.2, cor="#5a3a26", epoca=True))
        back.append(O.quadro(220, 330, 220, 270, "retrato", "#b08a3a"))
        back.append(O.quadro(560, 380, 160, 200, "diploma", "#b08a3a"))
        back.append(O.cabideiro(2050, FLOOR, 1.2))
        back.append(O.porta(2550, FLOOR, 1.25, cor="#6a3f26"))
        back.append(O.planta(-1500, FLOOR + 6, 1.3, pot="#a35a3a"))
        back.append(O.cadeira_executivo(540, FEET, SC, cor="#5a2f24", epoca=True, base=False))
        desk = O.mesa_escritorio(540, FEET, SC, cor="#6a3f26", epoca=True, w=640)
        top = FEET - 250 * SC
        front += [desk, O.luminaria_mesa(290, top, 1.2, epoca=True), O.telefone_disco(820, top, 1.1),
                  O.papeis(560, top, 1.2), O.maquina_escrever(560, top, 0.0001)]
        pools = [pool(330, top - 120, 420, 260, "#ffe0a0", 0.6), pool(1510, 1300, 420, 120, "#bfe0ff", 0.35)]
        dark = DARK_TARDE
    else:
        back += [wall("#dfe6ea"), R(X0, 1060, X1 - X0, FLOOR - 1060, "#cdd6dc"), ceiling("#f1f4f6", 150), floor("carpete")]
        back.append(O.janela(1180, 220, 1.0, w=900, h=760, vista="cidade", fr="#3a4650", hora=hora))
        back.append(O.estante(-560, FLOOR, 1.15, cor="#5a5f66", seed=7))
        back.append(O.arquivo(-1080, FLOOR, 1.1))
        back.append(O.quadro(240, 360, 200, 250, "diploma", "#2b2f36"))
        back.append(O.quadro(520, 330, 300, 220, "paisagem", "#2b2f36"))
        back.append(O.planta(980, FLOOR + 6, 1.3, pot="#3a4650"))
        back.append(O.porta(2550, FLOOR, 1.25, cor="#b9c2c9"))
        back.append(O.cadeira_executivo(540, FEET, SC, cor="#2b2f36", base=False))
        desk = O.mesa_escritorio(540, FEET, SC, cor="#8a6a4e", w=640)
        top = FEET - 250 * SC
        front += [desk, O.monitor(760, top, 1.1), O.notebook(330, top, 1.0), O.xicara(170, top, 1.0), O.papeis(560, top, 1.1)]
        for lx in (-600, 540, 1700):
            src.append(R(lx - 160, 150, 320, 18, "#fbfdff", 6))
        pools = [pool(540, 900, 700, 420, "#fffbe8", 0.35), pool(1630, 1330, 600, 140, "#cfe6ff", 0.45)]
        dark = DARK_DIA
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools, dark=dark,
                anchors={"executivo_sentado": dict(x=540, feet=seated_feet(), scale=SC, recorte_y=top + 30),
                         "visitante_em_pe": dict(x=-150, feet=FEET, scale=SC),
                         "visitante_2_em_pe": dict(x=1400, feet=FEET, scale=SC)},
                sample=[({"outfit": {"shirt": "#e8e2d6", "pants": "#2f3a4a"}, "hair": {"style": "default", "color": "#8a8a8a"},
                          "pose": "explicando"}, 540, seated_feet(), SC, "sentado", top + 30),
                        ({"npc": 2, "pose": "neutro"}, -150, FEET, SC, "em_pe", None),
                        ({"npc": 5, "pose": "pensativo"}, 1400, FEET, SC, "em_pe", None)])


# ---------------------------------------------------------------- 2. sala de jantar
def sala_jantar(epoca=False, hora="dia"):
    back, front, src = [], [], []
    if epoca:
        back += [wallpaper_stripes("#d9c7a4", "#cfb98f"), wainscot("#7a4a2e", 880), ceiling("#5a3a26"), floor("madeira", "#9a6440")]
        back.append(O.janela(1300, 300, 1.0, w=460, h=560, vista="arvores", fr="#5a3a26", hora=hora))
        back.append(O.quadro(180, 330, 260, 210, "paisagem", "#b08a3a"))
        back.append(O.quadro(620, 300, 180, 240, "retrato", "#b08a3a"))
        back.append(O.relogio_parede(-500, 560, 60, 19.5, cor="#5a3a26", epoca=True))
    else:
        back += [wall("#f2e3c6"), wainscot("#c58a5f", 930), ceiling("#e9dcc0", 150), floor("madeira")]
        back.append(O.janela(1260, 260, 1.0, w=640, h=620, vista="arvores", fr="#4a6b57", hora=hora))
        back.append(O.quadro(220, 330, 300, 220, "paisagem", "#8f5636"))
        back.append(O.quadro(620, 360, 160, 190, "mapa", "#8f5636"))
    # aparador com louça (os dois)
    ap = "#6a3f26" if epoca else "#8f5636"
    back.append(f'<g>{R(-1300, FLOOR - 420, 700, 420, ap)}{R(-1280, FLOOR - 400, 660, 160, shade(ap, -0.2))}'
                + "".join(f'<circle cx="{-1230 + k * 110}" cy="{FLOOR - 320}" r="40" fill="#f4efe6"/>' for k in range(6))
                + R(-1320, FLOOR - 436, 740, 20, shade(ap, 0.12), 4) + "</g>")
    back.append(O.porta(2650, FLOOR, 1.25, cor=ap, aberta=0.4))     # fora do 16:9: entrada por pan
    for cx in (240, 540, 840):
        back.append(O.cadeira(cx, FEET, SC, cor=ap))
    front.append(O.mesa_jantar(540, FEET, SC, w=980, cloth="#fbf6ea" if epoca else "#f4efe6", epoca=epoca, pratos=3))
    top = FEET - 250 * SC
    if epoca:
        src.append(O.lustre(540, 520, teto=0))
        pools = [pool(540, 1000, 760, 460, "#ffd98f", 0.6), pool(1530, 1320, 380, 110, "#ffdcb0", 0.35)]
        dark = DARK_TARDE
    else:
        src.append(O.luminaria_pendente(540, 560))
        pools = [pool(540, 1050, 620, 400, "#ffd9a0", 0.55), pool(1580, 1330, 520, 120, "#cfe6ff", 0.45)]
        dark = DARK_DIA
    seat = seated_feet()
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools, dark=dark,
                anchors={"sentados": dict(xs=[240, 540, 840], feet=seat, scale=SC, recorte_y=top + 30),
                         "em_pe_porta": dict(x=2650, feet=FEET, scale=SC, nota="porta fora do 16:9; entra pela direita")},
                sample=[({"npc": 1}, 240, seat, SC, "sentado", top + 30),
                        ({"outfit": {"shirt": "#c24a3a"}, "hair": {"color": "#3b2418"}, "pose": "explicando"}, 540, seat, SC, "sentado", top + 30),
                        ({"npc": 4}, 840, seat, SC, "sentado", top + 30)])


# ---------------------------------------------------------------- 3. fábrica / usina
def fabrica(epoca=True, hora="dia"):
    back, front, src = [], [], []
    brick, mortar = "#b8735a", "#a2634c"
    back += [wall("#c3c9ce"), R(X0, 700, X1 - X0, FLOOR - 700, brick)]
    for k, y in enumerate(range(720, FLOOR, 46)):
        back.append(R(X0, y, X1 - X0, 5, mortar))
        back += [R(x + (k % 2) * 60, y, 6, 46, mortar) for x in range(X0, X1, 120)]
    back.append(floor("concreto"))
    for wx in range(-1700, 3000, 620):      # janelas altas
        back.append(O.janela(wx, 160, 1.0, w=380, h=420, vista="fabrica", fr="#5a6570", hora=hora))
    for bx in range(-1900, 3100, 620):      # pilares e viga
        back.append(R(bx - 30, -200, 60, FLOOR + 200, "#5a6570") + R(bx - 44, 640, 88, 40, "#4a545e"))
    back.append(R(X0, 640, X1 - X0, 34, "#4a545e"))
    # passarela com guarda-corpo
    back += [R(X0, 660, X1 - X0, 24, "#4a545e")] + [R(x, 600, 8, 60, "#4a545e") for x in range(X0, X1, 90)] + [R(X0, 596, X1 - X0, 10, "#4a545e")]
    # forno (fonte de luz quente) à esquerda e máquina à direita
    back.append(R(20, 760, 540, FLOOR - 760, "#4a3a34") + R(60, 820, 460, 60, "#3a2e2a"))
    back.append(R(1650, 880, 520, FLOOR - 880, "#7d8790", 10) + R(1700, 930, 160, 120, "#5a6570", 8)
                + "".join(f'<circle cx="{1950 + k * 70}" cy="1000" r="26" fill="#d9b14a"/>' for k in range(3))
                + R(1680, 1120, 460, 26, "#4a545e"))
    back.append(O.relogio_parede(1180, 820, 54, 14.0, cor="#3a3f45"))
    # caçamba (primeiro plano à direita, na frente dos personagens)
    front.append(f'<path d="M1550 1680 L2100 1680 L2040 1960 L1610 1960 Z" fill="{shade("#6a7480", -0.08)}"/>' + R(1530, 1660, 590, 30, "#5a6570", 6))
    src.append(R(100, 900, 380, FLOOR - 920, "#ff9a3c", 12) + R(140, 960, 300, FLOOR - 1000, "#ffd36a", 10))
    pools = [pool(290, 1150, 900, 520, "#ff9a3c", 0.55), pool(540, 600, 1400, 600, "#dfeeff", 0.25)]
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools, dark=("#2a2240", 0.2),
                anchors={"em_pe": dict(xs=[680, 920], feet=FEET, scale=SC, nota="forno em x 20..560 (fonte de luz por cima: não pôr gente na frente)"),
                         "piso_giz": dict(x=540, y=1760)},
                sample=[({"npc": 3, "outfit": {"shirt": "#5a7aa0"}}, 680, FEET, SC, "em_pe", None),
                        ({"npc": 6, "outfit": {"shirt": "#5a7aa0"}, "expression": "feliz"}, 920, FEET, SC, "em_pe", None)])


# ---------------------------------------------------------------- 4. parque
def parque(epoca=False, hora="dia"):
    back, front, src = [], [], []
    sky = {"dia": ("#9fd6f2", "#d6f0fa"), "entardecer": ("#f2a98a", "#fbd6a8"), "noite": ("#2c3a5a", "#46597d")}[hora]
    back += [R(X0, -200, X1 - X0, 1200, sky[0]), R(X0, 500, X1 - X0, 700, sky[1])]
    sun_x, sun_y = {"dia": (1900, 300), "entardecer": (1220, 880), "noite": (1900, 260)}[hora]   # entardecer: entre as árvores, perto do horizonte
    back.append(f'<circle cx="{sun_x}" cy="{sun_y}" r="90" fill="{"#fff4cf" if hora == "dia" else ("#ffe2a8" if hora == "entardecer" else "#f2f2e6")}"/>')
    back.append(R(X0, 960, X1 - X0, 2100 - 960, "#9fd18a"))
    back.append(R(X0, 960, X1 - X0, 30, "#8cc27a"))
    for tx, r, c in ((-1700, 210, "#6fae7c"), (-1100, 260, "#7fb98e"), (-400, 200, "#6aa878"), (960, 220, "#6aa878"), (1500, 240, "#7fb98e"),
                     (2100, 280, "#6fae7c"), (2800, 220, "#7fb98e")):
        back += [O.shadow(tx, 1000 + r * 0.1, r * 0.9, 22, 0.18), R(tx - 22, 980 - r * 0.6, 44, r * 0.7 + 20, "#7d5a43"), f'<circle cx="{tx}" cy="{f(980 - r * 1.1)}" r="{r}" fill="{c}"/>',
                 f'<circle cx="{tx - r * 0.6}" cy="{f(980 - r * 0.7)}" r="{f(r * 0.7)}" fill="{shade(c, 0.08)}"/>']
    # caminho em perspectiva
    back.append(f'<path d="M300 990 L780 990 L1700 2100 L-620 2100 Z" fill="#e8d9b8"/>')
    for x, y, s in ((-900, 1300, 1.0), (1950, 1350, 1.1), (-300, 1110, 0.7)):    # arbustos
        back.append(f'<ellipse cx="{x}" cy="{y}" rx="{170 * s}" ry="{90 * s}" fill="#6aa878"/><ellipse cx="{x + 60 * s}" cy="{y - 30 * s}" rx="{110 * s}" ry="{70 * s}" fill="#78b585"/>')
    # banco (atrás dos personagens) e poste
    bench = "#8f5636"
    back.append(O.shadow(1500, 1500, 300, 22) + R(1230, 1220, 540, 26, bench, 8) + R(1230, 1270, 540, 26, bench, 8)
                + R(1220, 1340, 560, 30, shade(bench, 0.1), 8) + R(1250, 1370, 24, 130, "#2b2f36") + R(1726, 1370, 24, 130, "#2b2f36"))
    back.append(R(70, 380, 22, 1100, "#2b2f36") + R(30, 1470, 100, 26, "#2b2f36", 8))
    src.append(f'<path d="M20 380 L148 380 L120 320 L48 320 Z" fill="#2b2f36"/><ellipse cx="81" cy="382" rx="50" ry="12" fill="#fff2c0"/>')
    pools = ([pool(540, 800, 1500, 900, "#fff2c8", 0.3)] if hora == "dia" else
             [pool(81, 420, 260, 200, "#ffd98f", 0.6), pool(81, 1490, 380, 90, "#ffd98f", 0.55), pool(1220, 900, 900, 400, "#ffb36a", 0.3)])
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools,
                dark=DARK_DIA if hora == "dia" else DARK_TARDE,
                anchors={"caminho": dict(xs=[380, 700], feet=FEET, scale=SC), "banco_sentado": dict(xs=[1380, 1620], assento_y=1340)},
                sample=[({"npc": 0, "pose": "acenando"}, 380, FEET, SC, "em_pe", None),
                        ({"outfit": {"shirt": "#3f7fc4"}, "hair": {"color": "#d9a441"}}, 720, FEET, SC, "em_pe", None)])


# ---------------------------------------------------------------- 5. balcão de atendimento / guichê
def balcao(epoca=False, hora="dia"):
    back, front, src = [], [], []
    if epoca:
        back += [wall("#e8dcc4"), wainscot("#7a4a2e", 980), ceiling("#c9b896"), floor("ceramica", "#d8cbb2")]
        back.append(O.relogio_parede(540, 380, 80, 11.0, cor="#5a3a26"))
        back.append(f'<g>{R(-200, 220, 520, 90, "#2f3b36", 6)}{R(-170, 250, 460, 16, "#d9b14a", 6)}</g>')
    else:
        back += [wall("#e3ecef"), R(X0, 1000, X1 - X0, FLOOR - 1000, "#cfdde2"), ceiling("#f4f7f8", 150), floor("ceramica")]
        back.append(O.relogio_parede(540, 380, 70, 11.0, cor="#2b2f36"))
        back.append(f'<g>{R(-200, 220, 520, 90, "#3f7fc4", 10)}{R(-170, 252, 300, 18, "#ffffff", 6)}</g>')
        for lx in (-600, 540, 1700):
            src.append(R(lx - 160, 140, 320, 16, "#fbfdff", 6))
    back.append(O.porta(-1400, FLOOR, 1.25, cor="#8f5636" if epoca else "#b9c2c9"))
    back.append(O.planta(2300, FLOOR + 6, 1.3))
    back.append(O.quadro(1700, 380, 260, 180, "mapa", "#8f5636"))
    # balcão: atendente atrás (pés a 1450), cliente na frente (pés a FEET)
    top = 1180
    wood = "#8f5636" if epoca else "#c4cbd2"
    front_counter = (R(-700, top, 2600, 1440 - top, wood) + R(-720, top - 20, 2640, 30, shade(wood, 0.15), 6)
                     + "".join(R(x, top + 40, 380, 1440 - top - 70, shade(wood, -0.08), 8) for x in range(-660, 1880, 420)))
    glass = []
    for gx in (-700, 260, 1220):
        if epoca:   # grade de latão
            glass.append(R(gx, top - 420, 680, 400, "#d9b14a", 0, ' opacity="0.15"') + R(gx, top - 430, 680, 14, "#d9b14a")
                         + "".join(R(x, top - 420, 6, 400, "#d9b14a") for x in range(gx + 30, gx + 680, 40)) + R(gx + 230, top - 120, 220, 100, "#f4efe6", 30, ' opacity="0.0"'))
        else:       # acrílico
            glass.append(R(gx + 20, top - 420, 640, 400, "#dff2fb", 8, ' opacity="0.35"') + R(gx + 20, top - 420, 640, 10, "#ffffff", 4, ' opacity="0.8"'))
    front.append(front_counter)
    # vidro/grade fica entre atendente e cliente: vai junto do front
    front.append("".join(glass))
    pools = [pool(540, 1000, 1300, 520, "#fff3d6", 0.35)]
    att_feet = 1450 + (622 - 375 - 160) * 1.1     # (referência) atendente sentado atrás do balcão
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools,
                dark=DARK_TARDE if epoca else DARK_DIA,
                anchors={"atendente": dict(xs=[-360, 600, 1560], feet=1450, scale=1.1, recorte_y=top + 20),
                         "cliente_em_pe": dict(xs=[540], feet=1900, scale=1.45, nota="desenhar DEPOIS do front")},
                sample=[({"npc": 7, "outfit": {"shirt": "#e8e2d6"}}, 600, 1450, 1.1, "atras", top + 20),
                        ({"outfit": {"shirt": "#4f8a6b"}, "hair": {"color": "#3b2418"}}, 380, 1950, 1.45, "costas", None)])


# ---------------------------------------------------------------- 6. sala de aula
def sala_aula(epoca=False, hora="dia", infantil=False):
    back, front, src = [], [], []
    if epoca:
        back += [wall("#e2d3b4"), wainscot("#7a4a2e", 960), ceiling("#8f6a48"), floor("madeira", "#a8703f")]
    else:
        back += [wall("#f4ecd8" if not infantil else "#fbeed0"), wainscot("#9fc4d8" if infantil else "#c9b896", 980),
                 ceiling("#f1ede4", 150), floor("madeira")]
    back.append(O.quadro_negro(80, 300, 920, 440, verde=not epoca))
    back.append(O.janela(1380, 280, 1.0, w=440, h=560, vista="arvores", fr="#5a3a26" if epoca else "#4a6b57", hora=hora))
    back.append(O.janela(1960, 280, 1.0, w=440, h=560, vista="arvores", fr="#5a3a26" if epoca else "#4a6b57", hora=hora))
    back.append(O.relogio_parede(-260, 380, 62, 9.0, cor="#5a3a26", epoca=epoca))
    back.append(O.quadro(-900, 320, 380, 280, "mapa", "#8f5636"))
    if infantil:   # alfabeto e desenhos
        letters = "ABCDEFGHIJKLM"
        back.append("".join(R(-1700 + k * 160, 170, 140, 110, ("#f2c14e", "#e2574c", "#3f7fc4", "#4a9a5c")[k % 4], 10)
                            + f'<text x="{-1630 + k * 160}" y="252" font-family="Arial" font-weight="900" font-size="80" fill="#fff" text-anchor="middle">{c}</text>'
                            for k, c in enumerate(letters)))
        back.append("".join(R(1350 + k * 220, 900, 180, 140, "#fff", 6) + f'<circle cx="{1440 + k * 220}" cy="970" r="40" fill="{c}"/>'
                            for k, c in enumerate(("#f2c14e", "#e2574c", "#3f7fc4"))))
    back.append(O.globo(1150, 1120, 1.0) + R(1060, 1120, 180, FLOOR - 1120, "#7a4a2e"))
    # mesa do professor (atrás do professor, à esquerda) e carteiras de alunos de costas no primeiro plano
    back.append(O.mesa_escritorio(-500, 1500, 1.15, cor="#7a4a2e", epoca=epoca, w=560))
    back.append(O.pilha_livros(-620, 1500 - 250 * 1.15, 1.1) + O.giz(-380, 1500 - 250 * 1.15))
    for x in (-700, 0, 700, 1400):
        front.append(O.carteira(x, 2060, 1.7, epoca=epoca))
    if epoca:
        for lx in (200, 1250):
            src.append(O.luminaria_pendente(lx, 420, cor="#d9d2bf"))
        pools = [pool(540, 900, 1300, 600, "#fff0c8", 0.35), pool(1900, 1300, 700, 160, "#ffe9c0", 0.35)]
        dark = DARK_TARDE
    else:
        for lx in (-600, 540, 1700):
            src.append(R(lx - 160, 140, 320, 16, "#fbfdff", 6))
        pools = [pool(540, 900, 1300, 600, "#fffbe8", 0.3), pool(1900, 1330, 800, 150, "#cfe6ff", 0.4)]
        dark = DARK_DIA
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools, dark=dark,
                anchors={"professor_em_pe": dict(x=540, feet=FEET, scale=SC),
                         "alunos_costas": dict(xs=[-700, 0, 700, 1400], feet=2380, scale=1.7, nota="atrás das carteiras do front")},
                sample=[({"outfit": {"shirt": "#e8e2d6", "pants": "#3a3f45"}, "hair": {"color": "#3b2418"}, "pose": "explicando"},
                         540, FEET, SC, "em_pe", None),
                        ({"npc": 1}, 0, 2380, 1.7, "costas", None), ({"npc": 4}, 700, 2380, 1.7, "costas", None)])


CENARIOS = {
    "escritorio": (escritorio, [dict(), dict(epoca=True)]),
    "sala_jantar": (sala_jantar, [dict(), dict(epoca=True, hora="entardecer")]),
    "fabrica": (fabrica, [dict()]),
    "parque": (parque, [dict(), dict(hora="entardecer")]),
    "balcao": (balcao, [dict(), dict(epoca=True)]),
    "sala_aula": (sala_aula, [dict(), dict(epoca=True), dict(infantil=True)]),
}


from cenarios_genericos import GENERICOS  # noqa: E402
CENARIOS.update(GENERICOS)
