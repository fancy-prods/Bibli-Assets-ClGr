"""Exporta os cenários paramétricos do estilo palco para SVG (sem personagens).

    python styles/palco/tools/cenarios/exportar.py                 # todas as variantes registradas
    python styles/palco/tools/cenarios/exportar.py parque          # só um cenário
    python styles/palco/tools/cenarios/exportar.py parque hora=noite -o saida.svg   # variante avulsa

Cada SVG segue a seção 8 do STYLE.md: viewBox = 16:9 inteiro (x -1167..2247), mundo desenhado de
x -2000 a 3100, zona segura do 9:16 em x 0..1080. Camadas: #back (recebe a escuridão), [personagens],
#front (móvel da frente, cor já escurecida), #pocas (screen), #sources (fontes de luz por cima de tudo).
Âncoras para posicionar personagens ficam no comentário do arquivo.
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cenarios as CN  # noqa: E402

SCENES_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "scenes"))


def pools_svg(pools):
    defs, out = [], []
    for i, (cx, cy, rx, ry, col, op) in enumerate(pools):
        defs.append(f'<radialGradient id="pl{i}"><stop offset="0" stop-color="{col}" stop-opacity="{op}"/>'
                    f'<stop offset="0.5" stop-color="{col}" stop-opacity="{op * 0.35:.3f}"/>'
                    f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#pl{i})" style="mix-blend-mode:screen"/>')
    return "".join(defs), "".join(out)


def tag_of(kw: dict) -> str:
    return "_".join(f"{k}-{v}" if v is not True else k for k, v in kw.items()) or "padrao"


def scene_svg(name: str, kw: dict) -> str:
    fn, _ = CN.CENARIOS[name]
    sc = fn(**kw)
    anchors = "; ".join(f"{k}: {v}" for k, v in sc["anchors"].items())
    note = (f'<!-- Cenário "{name}" ({tag_of(kw)}) do estilo palco, gerado por styles/palco/tools/cenarios/exportar.py.\n'
            f'     Mundo com 1920 de altura, desenhado de x {CN.X0} a {CN.X1}; 16:9 = viewBox; zona segura 9:16 = x 0..1080.\n'
            f'     Piso em y {CN.FLOOR}. Personagem em pé: pés y {CN.FEET}, escala {CN.SC}. Âncoras: {anchors}.\n'
            f'     Sentado atrás de móvel: recorte o personagem abaixo de recorte_y e desenhe-o entre #escuridao e #front.\n'
            f'     Camadas: #back (recebe escuridão), personagens, #front (cor já escurecida), poças (screen), #sources. -->\n')
    pdefs, pls = pools_svg(sc["pools"])
    dc, do = sc["dark"]
    x, y, vw, vh = CN.VIEW_169
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {vw} {vh}" width="{vw}" height="{vh}">\n{note}'
         f'<defs>{pdefs}</defs><g id="back">{sc["back"]}</g>'
         f'<rect id="escuridao" x="-2200" y="-400" width="5600" height="2800" fill="{dc}" opacity="{do}" style="mix-blend-mode:multiply"/>'
         f'<g id="front">{sc["front"]}</g><g id="pocas">{pls}</g><g id="sources">{sc["sources"]}</g></svg>\n')
    ET.fromstring(s)        # tem que fazer parse
    return s


def parse_kw(args):
    kw = {}
    for a in args:
        k, v = a.split("=", 1)
        kw[k] = {"true": True, "false": False}.get(v.lower(), v)
    return kw


def main(argv):
    if "-o" in argv:
        i = argv.index("-o")
        name, kw, out = argv[0], parse_kw(argv[1:i]), argv[i + 1]
        open(out, "w", encoding="utf-8").write(scene_svg(name, kw))
        print(out)
        return
    os.makedirs(SCENES_DIR, exist_ok=True)
    for name in (argv or list(CN.CENARIOS)):
        for kw in CN.CENARIOS[name][1]:
            path = os.path.join(SCENES_DIR, f"{name}_{tag_of(kw)}.svg")
            open(path, "w", encoding="utf-8").write(scene_svg(name, kw))
            print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
