"""Cenários genéricos do estilo palco (aprovados em 2026-11-05): sala de estar, quarto, rua, palco neutro, banquete.
Mesmo padrão de cenarios.py (que importa este módulo e registra os cenários em CENARIOS)."""
from __future__ import annotations

import objetos as O
from objetos import R, shade
from cenarios_base import (X0, X1, FLOOR, FEET, SC, DARK_DIA, DARK_TARDE, wall, floor, wainscot,
                           wallpaper_stripes, ceiling, pool, seated_feet)


# ---------------------------------------------------------------- sala de estar
def sala_estar(epoca=False, hora="dia"):
    back, front, src = [], [], []
    if epoca:
        back += [wallpaper_stripes("#d8c49a", "#cdb68a"), wainscot("#7a4a2e", 900), ceiling("#6a4a30"), floor("madeira", "#9a6440")]
        sofa_c = "#7a3a3a"
    else:
        back += [wall("#e9e2d2"), ceiling("#f4efe4", 150), floor("madeira")]
        sofa_c = "#4f7fa8"
    back.append(O.janela(1350, 260, 1.0, w=560, h=620, vista="arvores", fr="#5a3a26" if epoca else "#a8693f", hora=hora))
    back.append(O.estante(-700, FLOOR, 1.1, cor="#6a3f26" if epoca else "#a8693f", seed=11))
    back.append(O.quadro(260, 360, 420, 260, "paisagem", "#b08a3a" if epoca else "#2b2f36"))
    back.append(O.planta(-1250, FLOOR + 6, 1.4))
    back.append(O.porta(2550, FLOOR, 1.25, cor="#8f5636"))
    if not epoca:   # rack e TV
        back.append(R(1200, FLOOR - 220, 520, 220, "#7a4a2e", 8) + R(1260, FLOOR - 560, 420, 250, "#1f2328", 10)
                    + R(1440, FLOOR - 310, 60, 90, "#1f2328"))
    else:           # gramofone sobre um móvel: caixa de madeira, disco, braço e corneta
        T = FLOOR - 300
        back.append(R(1260, T, 420, 300, "#6a3f26", 8) + R(1290, T + 40, 360, 220, "#5a3424", 6)
                    + R(1370, T - 110, 220, 110, "#8a5236", 6) + R(1370, T - 30, 220, 8, "#6a3f26")
                    + f'<ellipse cx="1480" cy="{T - 112}" rx="96" ry="13" fill="#1f1f1f"/>'
                    + f'<ellipse cx="1480" cy="{T - 114}" rx="22" ry="4" fill="#c24a3a"/>'
                    + f'<path d="M1560 {T - 118} L1560 {T - 150} Q1562 {T - 190} 1600 {T - 210}" stroke="#b08a3a" stroke-width="12" fill="none" stroke-linecap="round"/>'
                    + f'<path d="M1592 {T - 200} Q1640 {T - 260} 1690 {T - 400} L1800 {T - 300} Q1700 {T - 250} 1608 {T - 216} Z" fill="#d9b14a"/>'
                    + f'<ellipse cx="1745" cy="{T - 350}" rx="78" ry="30" transform="rotate(-42 1745 {T - 350})" fill="#a8822e"/>'
                    + f'<ellipse cx="1745" cy="{T - 350}" rx="56" ry="18" transform="rotate(-42 1745 {T - 350})" fill="#5a3a1a"/>')
    back.append(R(-280, FLOOR - 200, 240, 200, "#7a4a2e", 6))
    sofa_floor = FEET - 40
    back.append(O.sofa(540, sofa_floor, 1.45, cor=sofa_c, w=640))
    # mesa de centro na frente (esconde as pernas de quem está no sofá)
    front.append(O.shadow(540, 1900, 380, 24) + R(180, 1730, 720, 34, "#7a4a2e", 10) + R(220, 1764, 26, 140, "#5a3a26")
                 + R(834, 1764, 26, 140, "#5a3a26") + O.xicara(420, 1730, 1.3) + O.livro_aberto(640, 1730, 1.2))
    src.append(O.luminaria_mesa(-160, FLOOR - 200, 1.6, epoca=epoca))
    pools = [pool(-160, FLOOR - 300, 600, 420, "#ffd98f", 0.5), pool(1630, 1340, 600, 130, "#cfe6ff", 0.35)]
    # quadril no assento do sofá (assento a 170*1.45 do chão do sofá)
    seat_hip = sofa_floor - 150 * 1.45
    feet = seat_hip + (622 - 375) * SC
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools,
                dark=DARK_TARDE if epoca else DARK_DIA,
                anchors={"sofa_sentados": dict(xs=[400, 680], feet=feet, scale=SC, recorte_y=seat_hip + 20),
                         "em_pe": dict(x=1100, feet=FEET, scale=SC)},
                sample=[({"outfit": {"shirt": "#c24a3a"}, "hair": {"style": "comprido", "color": "#3b2418"}, "pose": "explicando"},
                         400, feet, SC, "sentado", seat_hip + 20),
                        ({"npc": 2, "pose": "segurando_caneca"}, 680, feet, SC, "sentado", seat_hip + 20)])


# ---------------------------------------------------------------- quarto
def quarto(epoca=False, hora="noite", infantil=False):
    back, front, src = [], [], []
    wallc = "#c9d9ee" if infantil else ("#d8c7a8" if epoca else "#dcd3e6")
    back += [wall(wallc), ceiling(shade(wallc, -0.1), 150), floor("madeira", "#b07a4e")]
    if infantil:
        def star(x, y, r):
            import math
            pts = " ".join(f"{x + (r if k % 2 == 0 else r * 0.45) * math.sin(k * math.pi / 5):.1f},"
                           f"{y - (r if k % 2 == 0 else r * 0.45) * math.cos(k * math.pi / 5):.1f}" for k in range(10))
            return f'<polygon points="{pts}" fill="#f2c14e"/>'
        back.append("".join(star(x, y, r) for x, y, r in ((-900, 300, 34), (-420, 230, 26), (60, 330, 30), (520, 240, 38),
                                                           (880, 360, 26), (1300, 230, 32), (2000, 300, 30))))
    back.append(O.janela(1450, 280, 1.0, w=440, h=520, vista="cidade", fr="#e8e2d6", hora=hora))
    back.append(O.quadro(-300, 380, 200, 240, "paisagem", "#8f5636"))
    cama = "#8f5636"
    bx = -120       # cama à esquerda: no 9:16 aparece meia cama e quem está ao lado fica inteiro
    back.append(R(bx, FLOOR - 470, 720, 330, cama, 30) + R(bx + 30, FLOOR - 440, 660, 270, shade(cama, 0.1), 22))
    back.append(R(bx + 70, FLOOR - 260, 250, 110, "#f4efe6", 30) + R(bx + 400, FLOOR - 260, 250, 110, "#f4efe6", 30))
    front.append(R(bx - 30, FLOOR - 130, 780, 330, "#6f9fd8" if infantil else "#b85c5c", 24) + R(bx - 30, FLOOR - 140, 780, 60, "#f4efe6", 20)
                 + R(bx - 30, FLOOR + 160, 780, 60, cama, 10))
    back.append(R(-560, FLOOR - 260, 300, 260, "#7a4a2e", 8) + R(-540, FLOOR - 180, 260, 12, "#5a3a26"))
    src.append(O.luminaria_mesa(-410, FLOOR - 260, 1.4, epoca=epoca))
    if infantil:
        front.append(O.shadow(1300, FLOOR + 400, 140, 20) + f'<circle cx="1300" cy="{FLOOR + 330}" r="70" fill="#e2574c"/>'
                     + f'<path d="M1240 {FLOOR + 300} Q1300 {FLOOR + 330} 1360 {FLOOR + 300}" stroke="#fff" stroke-width="10" fill="none"/>')
    pools = [pool(-410, FLOOR - 320, 650, 460, "#ffcf7a", 0.6)] + ([pool(1670, 1300, 400, 120, "#9db8e8", 0.3)] if hora == "noite" else [])
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools,
                dark=("#1e1a38", 0.32) if hora == "noite" else DARK_DIA,
                anchors={"deitado_cabeca": dict(x=240, y=FLOOR - 200, nota="cabeça no travesseiro; corpo coberto pela colcha (front)"),
                         "em_pe_ao_lado": dict(x=800, feet=FEET, scale=SC)},
                sample=[({"outfit": {"shirt": "#f4efe6", "pants": "#3a3f45"}, "hair": {"style": "curto", "color": "#3b2418"},
                          "pose": "pensativo", "expression": "triste"}, 800, FEET, SC, "em_pe", None)])


# ---------------------------------------------------------------- rua / calçada
def rua(epoca=False, hora="dia"):
    back, front, src = [], [], []
    sky = {"dia": "#9fd6f2", "entardecer": "#f2a98a", "noite": "#2c3a5a"}[hora]
    back.append(R(X0, -200, X1 - X0, 1300, sky))
    cols = (["#b8735a", "#c9a37a", "#9a7a5a", "#b88a6a", "#a86a4a", "#c4a882"] if epoca
            else ["#f2b880", "#e88f6a", "#f6d69a", "#8fb6d9", "#c9a3d6", "#9cc7a4"])
    x, k = X0, 0
    while x < X1:
        w = 520 + (k * 137) % 200
        top = 120 + (k * 211) % 260
        c = cols[k % len(cols)]
        back.append(R(x, top, w, FLOOR - top, c) + R(x, top, w, 26, shade(c, -0.15)))
        for wy in range(top + 80, FLOOR - 300, 170):
            for wx in range(int(x + 50), int(x + w - 120), 150):
                back.append(R(wx, wy, 90, 120, "#ffffff" if hora == "dia" else "#ffd98f", 4,
                              f' opacity="{0.5 if hora == "dia" else 0.8}"'))
        back.append(R(x + 40, FLOOR - 280, w - 80, 280, shade(c, -0.25), 4) + R(x + 60, FLOOR - 260, w * 0.5, 200, "#cfe6f2", 4, ' opacity="0.8"')
                    + R(x + w - 160, FLOOR - 260, 90, 260, "#5a3a26", 4))
        if epoca:   # toldos
            back.append(f'<path d="M{x + 40} {FLOOR - 300} L{x + w - 40} {FLOOR - 300} L{x + w - 10} {FLOOR - 230} L{x + 10} {FLOOR - 230} Z" '
                        f'fill="{["#c24a3a", "#3f7f5c", "#3f5f8a"][k % 3]}"/>')
        x += w + 20
        k += 1
    back.append(R(X0, FLOOR, X1 - X0, 360, "#c9c2b4") + R(X0, FLOOR, X1 - X0, 10, "#b0a898")
                + "".join(R(xx, FLOOR, 6, 360, "#b0a898") for xx in range(X0, X1, 300)))
    back.append(R(X0, FLOOR + 360, X1 - X0, 30, "#8a8478") + R(X0, FLOOR + 390, X1 - X0, 2100, "#5a5f66"))
    back.append("".join(R(xx, FLOOR + 600, 200, 18, "#f4efe6", 4) for xx in range(X0, X1, 420)))
    back.append(R(-150, 300, 26, FEET - 300, "#2b2f36") + R(-190, FEET - 20, 106, 22, "#2b2f36", 8))
    if epoca:
        src.append(R(-170, 220, 66, 90, "#2b2f36", 6) + R(-160, 232, 46, 66, "#ffe6a0", 4))
    else:
        src.append('<path d="M-170 300 L-60 300 L-80 250 L-150 250 Z" fill="#2b2f36"/><ellipse cx="-115" cy="302" rx="46" ry="10" fill="#fff2c0"/>')
    pools = [pool(540, 900, 1600, 800, "#fff2c8", 0.25)] if hora == "dia" else [pool(-115, 1300, 600, 600, "#ffd98f", 0.6)]
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools,
                dark=DARK_DIA if hora == "dia" else ("#1e1a38", 0.35),
                anchors={"calcada": dict(xs=[300, 780], feet=FEET, scale=SC), "rua": dict(y=FLOOR + 500)},
                sample=[({"npc": 1}, 300, FEET, SC, "em_pe", None),
                        ({"outfit": {"shirt": "#e2574c"}, "hair": {"style": "coque", "color": "#3b2418"}, "pose": "acenando"},
                         780, FEET, SC, "em_pe", None)])


# ---------------------------------------------------------------- palco neutro (explicações abstratas)
def palco_neutro(epoca=False, hora="dia", refletores="dois"):
    lados = refletores == "dois"
    back = [R(X0, -200, X1 - X0, FLOOR + 200, "#2f2a3a"), R(X0, FLOOR, X1 - X0, 900, "#3e3648"), R(X0, FLOOR - 4, X1 - X0, 12, "#24202e")]
    pools = []
    if lados:   # dois refletores: quente à esquerda, frio à direita (pares simpatia x resistência)
        for cx, col in ((260, "#ffd98f"), (820, "#9dbcf0")):
            back.append(f'<path d="M{cx - 70} -200 L{cx + 70} -200 L{cx + 330} {FEET} L{cx - 330} {FEET} Z" fill="{col}" opacity="0.10"/>')
            pools += [pool(cx, FEET - 10, 380, 70, col, 0.75), pool(cx, FEET - 380, 420, 520, col, 0.28)]
    else:
        back.append('<path d="M470 -200 L610 -200 L940 1600 L140 1600 Z" fill="#fff3c4" opacity="0.10"/>')
        pools += [pool(540, FEET - 10, 420, 80, "#fff3c4", 0.8), pool(540, FEET - 380, 460, 540, "#fff3c4", 0.3)]
    sample = ([({"npc": 0, "expression": "feliz"}, 170, FEET, SC, "em_pe", None),
               ({"npc": 3}, 350, FEET, SC, "em_pe", None),
               ({"npc": 5, "pose": "bracos_cruzados", "expression": "desconfiado"}, 730, FEET, SC, "em_pe", None),
               ({"npc": 6, "expression": "bravo"}, 910, FEET, SC, "em_pe", None)] if lados
              else [({"outfit": {"shirt": "#3f7fc4"}, "hair": {"style": "curto", "color": "#3b2418"}, "pose": "explicando"}, 540, FEET, SC, "em_pe", None)])
    return dict(back="".join(back), front="", sources="", pools=pools, dark=("#1a1626", 0.25),
                anchors={"esquerda": dict(xs=[170, 350], feet=FEET, scale=SC), "direita": dict(xs=[730, 910], feet=FEET, scale=SC),
                         "centro": dict(x=540, feet=FEET, scale=SC)},
                sample=sample)


# ---------------------------------------------------------------- salão de banquete
def banquete(epoca=True, hora="noite"):
    back, front, src = [], [], []
    back += [wall("#7a2f36"), R(X0, 880, X1 - X0, FLOOR - 880, "#5a2228"), R(X0, 868, X1 - X0, 16, "#d9b14a"),
             ceiling("#3a1a1e"), floor("madeira", "#6a3f26")]
    for i, x in enumerate(range(-1755, 3100, 700)):   # colunas e quadros (vãos centrados em -5, 695, 1395...)
        back.append(R(x, 170, 90, FLOOR - 170, "#e8dcc4") + R(x - 14, 170, 118, 30, "#d9c7a4") + R(x - 14, FLOOR - 40, 118, 40, "#d9c7a4"))
        back.append(O.quadro(x + 245, 240, 200, 250, "retrato" if i % 2 else "paisagem", "#d9b14a"))
    for cx in (240, 540, 840):
        back.append(O.cadeira(cx, FEET, SC, cor="#5a2f24"))
    front.append(O.mesa_jantar(540, FEET, SC, w=1400, cloth="#fbf6ea", epoca=True, pratos=3, centro=150))
    for lx in (-5, 695, 1395):
        src.append(O.lustre(lx, 640, teto=0))
    pools = [pool(lx, 960, 700, 500, "#ffd98f", 0.5) for lx in (-5, 695, 1395)]
    seat = seated_feet()
    top = FEET - 250 * SC
    return dict(back="".join(back), front="".join(front), sources="".join(src), pools=pools, dark=("#2a1a2a", 0.22),
                anchors={"sentados": dict(xs=[240, 540, 840], feet=seat, scale=SC, recorte_y=top + 30)},
                sample=[({"jacket": {"color": "#1f1f1f"}, "shirt": "#f4efe6", "tie": "borboleta",
                          "hair": {"style": "repartido", "color": "#3b2418"}, "mustache": "fino"}, 240, seat, SC, "sentado", top + 30),
                        ({"jacket": {"color": "#2b2b38"}, "shirt": "#f4efe6", "tie": "borboleta", "hair": {"style": "entradas", "color": "#9a9a9a"},
                          "glasses": "grau"}, 540, seat, SC, "sentado", top + 30),
                        ({"npc": 4, "shirt": "#7a3a5a"}, 840, seat, SC, "sentado", top + 30)])


GENERICOS = {
    "sala_estar": (sala_estar, [dict(), dict(epoca=True, hora="entardecer")]),
    "quarto": (quarto, [dict(), dict(infantil=True, hora="dia")]),
    "rua": (rua, [dict(), dict(epoca=True), dict(hora="noite")]),
    "palco_neutro": (palco_neutro, [dict(), dict(refletores="um")]),
    "banquete": (banquete, [dict()]),
}
