#!/usr/bin/env python3
"""Montador paramétrico do personagem base do estilo "palco" (v1).

Só biblioteca padrão. Lê um JSON de parâmetros e escreve um SVG standalone
com fundo transparente.

Uso:
    python tools/compose_character.py params.json -o renders/nome.svg
    python tools/compose_character.py --export-pieces characters/base

Formato do JSON (todas as chaves são opcionais):
{
  "skin": "#f1d6c2",
  "outfit": {"shirt": "#4f8a6b", "pants": "#2f3a4a", "shoes": "#222222"},
  "hair": {"style": "default", "color": "#4a3226"},
  "brow_color": "#3a2a20",
  "iris": "castanho" | "azul" | "verde" | "mel" | "cinza" | "#rrggbb",
  "pose": "neutro" | {"right_shoulder": -4, "right_elbow": 0,
                      "left_shoulder": 4, "left_elbow": 0,
                      "crosses_body": ["right"]},
  "expression": "neutro",              # preset de presets/expressions.json
  "eyes": {"look_x": 0, "look_y": 0, "lid_upper": 0, "lid_lower": 0},
  "brows": {"raise": 0, "tilt": 0},
  "held_object": {"type": "caneca" | "celular" | "livro",
                  "hand": "right" | "left", "color": "#ffffff"} | null,
  "npc": 0,                            # figurante: preset de presets/npc.json (índice)
  "glasses": {"style": "escuros", "glint": 0.0..1.0 | null} | null
}

"npc": i preenche pele, roupa, cabelo (careca), sobrancelha e íris com o
tom de cinza i do preset; chaves explícitas sobrescrevem. "glasses.glint" é a
posição do reflexo que atravessa as lentes (0 = entrando, 1 = saindo); anime
de 0 a 1 em ~0,45 s.

Precedência: valores explícitos em "eyes"/"brows" sobrescrevem o preset de
"expression". Se "held_object" não for informado e a pose tiver
"default_held_object", ele é usado; "held_object": null remove.

A geometria abaixo é a fonte da verdade da seção 4 do STYLE.md (H = 116,
cabeça r = 58, centro do personagem em x = 340).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_DIR = os.path.dirname(HERE)
PRESETS_DIR = os.path.join(STYLE_DIR, "presets")
HAIR_DIR = os.path.join(STYLE_DIR, "characters", "base", "cabelos")

SVG_NS = "http://www.w3.org/2000/svg"
CANVAS_W, CANVAS_H = 680, 680

# ---------------------------------------------------------------- defaults
DEFAULT_COLORS = {
    "skin": "#f1d6c2",
    "hair": "#4a3226",
    "brow": "#3a2a20",
    "shirt": "#4f8a6b",
    "pants": "#2f3a4a",
    "shoes": "#222222",
}
OUTLINE_COLOR = "#111111"
IRIS_PALETTE = {
    "castanho": "#7a5230",
    "azul": "#3f7fc4",
    "verde": "#4a9a5c",
    "mel": "#c08a2e",
    "cinza": "#8f9aa3",
}

# ---------------------------------------------------------------- geometria
HEAD_CX, HEAD_CY, HEAD_R = 340, 140, 58          # H = 116
SHOULDER = {"left": (279, 210), "right": (401, 210)}
UPPER_ARM_LEN = 85                                # ombro -> cotovelo (centros)
FOREARM_LEN = 80                                  # cotovelo -> centro da mão
ARM_W = 22
HAND_R = 11
EYE_R = 13.9
EYE_CY = 148
EYE_CX = {"left": 320.3, "right": 359.7}
EYE_STROKE = 3
IRIS_R = 6.25
IRIS_STROKE = 2
PUPIL_R = 2.6
LID_STROKE = 2.5
LID_HIDE = 0.03
LOOK_X_MAX = 0.47                                 # fração do raio do olho
LOOK_Y_MAX = 0.45
BROW = {"left": (308, 119), "right": (348, 119)}  # x, y do rect 24x5
BROW_W, BROW_H = 24, 5
BROW_RAISE_PX = 8                                 # raise = 1 -> sobe 8 px
TORSO_X = (285, 395)

OUTLINE_FILTER = (
    '<filter id="outline" x="-15%" y="-10%" width="130%" height="120%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="3.5" result="d"/>'
    f'<feFlood flood-color="{OUTLINE_COLOR}"/>'
    '<feComposite in2="d" operator="in" result="o"/>'
    '<feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge>'
    '</filter>'
)


def f(v: float) -> str:
    """Formata número de forma compacta."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- params
def darken(hexc: str, k: float) -> str:
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def npc_defaults(i: int) -> dict:
    """Parâmetros do figurante cinza i (presets/npc.json, cíclico)."""
    n = load_json(os.path.join(PRESETS_DIR, "npc.json"))
    g = n["grays"][i % len(n["grays"])]
    return {"skin": g,
            "outfit": {"shirt": g, "pants": darken(g, n["pants_darken"]), "shoes": darken(g, n["shoes_darken"])},
            "hair": {"style": n["hair_style"], "color": g},
            "brow_color": g,
            "iris": n["iris"][i % len(n["iris"])]}


def resolve_params(raw: dict) -> dict:
    poses = load_json(os.path.join(PRESETS_DIR, "poses.json"))
    expressions = load_json(os.path.join(PRESETS_DIR, "expressions.json"))
    if raw.get("npc") is not None:
        base = npc_defaults(int(raw["npc"]))
        base.update({k: v for k, v in raw.items() if k != "npc"})
        raw = base

    outfit = dict(raw.get("outfit", {}))
    for k in ("shirt", "pants", "shoes"):   # atalho: cores de roupa no nível de cima
        if k in raw:
            outfit.setdefault(k, raw[k])
    hair = raw.get("hair", {})
    if isinstance(hair, str):
        hair = {"style": hair}
    p = {
        "skin": raw.get("skin", DEFAULT_COLORS["skin"]),
        "shirt": outfit.get("shirt", DEFAULT_COLORS["shirt"]),
        "pants": outfit.get("pants", DEFAULT_COLORS["pants"]),
        "shoes": outfit.get("shoes", DEFAULT_COLORS["shoes"]),
        "hair_style": hair.get("style", "default"),
        "hair_color": hair.get("color", DEFAULT_COLORS["hair"]),
        "brow_color": raw.get("brow_color", DEFAULT_COLORS["brow"]),
    }

    iris = raw.get("iris", "castanho")
    if iris in IRIS_PALETTE:
        iris = IRIS_PALETTE[iris]
    elif not (isinstance(iris, str) and iris.startswith("#")):
        raise SystemExit(f"íris inválida: {iris!r} (use {list(IRIS_PALETTE)} ou #hex)")
    p["iris"] = iris

    # pose
    pose = raw.get("pose", "neutro")
    if isinstance(pose, str):
        if pose not in poses or pose.startswith("_"):
            raise SystemExit(f"pose desconhecida: {pose!r}")
        pose_d = dict(poses[pose])
    else:
        pose_d = dict(poses["neutro"])
        pose_d.update(pose)
        if "crosses_body" not in pose:
            pose_d["crosses_body"] = None
    p["pose"] = pose_d

    # expressão
    exp_name = raw.get("expression", "neutro")
    if exp_name not in expressions or exp_name.startswith("_") or exp_name == "blink":
        raise SystemExit(f"expressão desconhecida: {exp_name!r}")
    eyes = dict(expressions[exp_name]["eyes"])
    eyes.update(raw.get("eyes", {}))
    brows = dict(expressions[exp_name]["brows"])
    brows.update(raw.get("brows", {}))
    p["eyes"] = {
        "look_x": clamp(eyes.get("look_x", 0), -1, 1),
        "look_y": clamp(eyes.get("look_y", 0), -1, 1),
        "lid_upper": clamp(eyes.get("lid_upper", 0), 0, 1),
        "lid_lower": clamp(eyes.get("lid_lower", 0), 0, 1),
    }
    p["brows"] = {
        "raise": clamp(brows.get("raise", 0), -1, 1),
        "tilt": float(brows.get("tilt", 0)),
    }

    # objeto segurado
    if "held_object" in raw:
        held = raw["held_object"]
    else:
        held = pose_d.get("default_held_object")
    if held is not None:
        held = dict(held)
        held.setdefault("hand", "right")
        if held.get("type") not in HELD_OBJECTS:
            raise SystemExit(f"objeto desconhecido: {held.get('type')!r} (use {list(HELD_OBJECTS)})")
    p["held"] = held

    glasses = raw.get("glasses")
    if isinstance(glasses, str):
        glasses = {"style": glasses}
    if glasses is not None:
        glasses = dict(glasses)
        glasses.setdefault("style", "escuros")
        if glasses["style"] not in GLASSES:
            raise SystemExit(f"óculos desconhecido: {glasses['style']!r} (use {list(GLASSES)})")
    p["glasses"] = glasses
    return p


# ---------------------------------------------------------------- braços
def rot(vx: float, vy: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return (vx * math.cos(a) - vy * math.sin(a), vx * math.sin(a) + vy * math.cos(a))


def arm_points(side: str, shoulder: float, elbow: float):
    sx, sy = SHOULDER[side]
    ex, ey = rot(0, UPPER_ARM_LEN, shoulder)
    hx, hy = rot(0, FOREARM_LEN, shoulder + elbow)
    return (sx, sy), (sx + ex, sy + ey), (sx + ex + hx, sy + ey + hy)


def arm_crosses(side: str, pose: dict) -> bool:
    explicit = pose.get("crosses_body")
    if explicit is not None:
        return side in explicit
    _, (ex, _), (hx, _) = arm_points(side, pose[f"{side}_shoulder"], pose[f"{side}_elbow"])
    inner = lambda x: TORSO_X[0] + ARM_W / 2 < x < TORSO_X[1] - ARM_W / 2  # noqa: E731
    return inner(hx) or inner(ex)


def svg_arm(side: str, shoulder: float, elbow: float, shirt: str, skin: str,
            draw_hand: bool = True) -> str:
    sx, sy = SHOULDER[side]
    hand = f'<circle cx="0" cy="{FOREARM_LEN}" r="{HAND_R}" fill="{skin}"/>' if draw_hand else ""
    return (
        f'<g class="arm-{side}" transform="translate({sx},{sy}) rotate({f(shoulder)})">'
        f'<rect x="-11" y="-11" width="{ARM_W}" height="107" rx="11" fill="{shirt}"/>'
        f'<g transform="translate(0,{UPPER_ARM_LEN}) rotate({f(elbow)})">'
        f'<rect x="-11" y="-11" width="{ARM_W}" height="91" rx="11" fill="{shirt}"/>'
        f'{hand}</g></g>'
    )


# ---------------------------------------------------------------- objetos
def obj_caneca(hx: float, hy: float, side: str, color: str | None) -> str:
    """Caneca: corpo centrado na mão, alça do lado de fora. Fica atrás da mão."""
    c = color or "#f4efe6"
    w, h = 30, 34
    out = 1 if side == "right" else -1
    x, y = hx - w / 2 - 6 * out, hy - h / 2 - 2   # mão pega a lateral, perto da alça
    handle_x = x + w if out > 0 else x
    return (
        '<g class="held caneca">'
        f'<path d="M{f(handle_x)} {f(y + 8)} q{f(13 * out)} 0 {f(13 * out)} 9 '
        f'q0 9 {f(-13 * out)} 9" fill="none" stroke="{c}" stroke-width="5"/>'
        f'<rect x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="4" fill="{c}"/>'
        f'<rect x="{f(x + 3)}" y="{f(y + 3)}" width="{w - 6}" height="4" rx="2" fill="#000" opacity="0.12"/>'
        '</g>'
    )


def obj_celular(hx: float, hy: float, side: str, color: str | None) -> str:
    c = color or "#2b2f36"
    w, h = 20, 36
    x, y = hx - w / 2, hy - h + 8
    return (
        '<g class="held celular">'
        f'<rect x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="4" fill="{c}"/>'
        f'<rect x="{f(x + 3)}" y="{f(y + 4)}" width="{w - 6}" height="{h - 12}" rx="2" fill="#8fc6ff"/>'
        '</g>'
    )


def obj_livro(hx: float, hy: float, side: str, color: str | None) -> str:
    c = color or "#c24a3a"
    w, h = 34, 44
    x, y = hx - w / 2, hy - h / 2
    return (
        '<g class="held livro">'
        f'<rect x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="3" fill="{c}"/>'
        f'<rect x="{f(x + w - 6)}" y="{f(y + 2)}" width="4" height="{h - 4}" fill="#fff" opacity="0.7"/>'
        '</g>'
    )


HELD_OBJECTS = {"caneca": obj_caneca, "celular": obj_celular, "livro": obj_livro}


# ---------------------------------------------------------------- olhos
def svg_eye(side: str, iris: str, skin: str, e: dict, uid: str = "") -> str:
    cx, cy, r = EYE_CX[side], EYE_CY, EYE_R
    ix = cx + e["look_x"] * LOOK_X_MAX * r
    iy = cy + e["look_y"] * LOOK_Y_MAX * r
    up_edge = cy - r + e["lid_upper"] * 2 * r
    lo_edge = max(cy + r - e["lid_lower"] * 2 * r, up_edge)   # nunca acima da superior
    cid = f"{uid}eye-{side}"
    x0, x1 = cx - r - 2, cx + r + 2
    parts = [
        f'<g class="eye eye-{side}">',
        f'<clipPath id="{cid}"><circle cx="{f(cx)}" cy="{cy}" r="{r}"/></clipPath>',
        f'<g clip-path="url(#{cid})">',
        f'<circle cx="{f(cx)}" cy="{cy}" r="{r}" fill="#ffffff"/>',
        f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{IRIS_R}" fill="{iris}" stroke="#111" stroke-width="{IRIS_STROKE}"/>',
        f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{PUPIL_R}" fill="#111"/>',
        # pálpebra superior
        f'<rect class="lid-upper" x="{f(x0)}" y="{f(cy - r - 2)}" width="{f(x1 - x0)}" '
        f'height="{f(max(up_edge - (cy - r - 2), 0))}" fill="{skin}"/>',
        # pálpebra inferior
        f'<rect class="lid-lower" x="{f(x0)}" y="{f(lo_edge)}" width="{f(x1 - x0)}" '
        f'height="{f(max(cy + r + 2 - lo_edge, 0))}" fill="{skin}"/>',
    ]
    if e["lid_upper"] >= LID_HIDE:
        parts.append(f'<line x1="{f(x0)}" y1="{f(up_edge)}" x2="{f(x1)}" y2="{f(up_edge)}" '
                     f'stroke="#111" stroke-width="{LID_STROKE}"/>')
    if e["lid_lower"] >= LID_HIDE:
        parts.append(f'<line x1="{f(x0)}" y1="{f(lo_edge)}" x2="{f(x1)}" y2="{f(lo_edge)}" '
                     f'stroke="#111" stroke-width="{LID_STROKE}"/>')
    parts.append("</g>")
    parts.append(f'<circle cx="{f(cx)}" cy="{cy}" r="{r}" fill="none" stroke="#111" stroke-width="{EYE_STROKE}"/>')
    parts.append("</g>")
    return "".join(parts)


def svg_brows(color: str, b: dict) -> str:
    dy = -b["raise"] * BROW_RAISE_PX
    out = ['<g class="brows">']
    for side, sign in (("left", 1), ("right", -1)):
        x, y = BROW[side]
        y += dy
        ccx, ccy = x + BROW_W / 2, y + BROW_H / 2
        t = sign * b["tilt"]   # tilt > 0: pontas internas para baixo
        tr = f' transform="rotate({f(t)} {f(ccx)} {f(ccy)})"' if t else ""
        out.append(f'<rect x="{x}" y="{f(y)}" width="{BROW_W}" height="{BROW_H}" rx="2.5" fill="{color}"{tr}/>')
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- acessórios
LENS = {"left": 301.5, "right": 341.5}            # x das lentes; y 134, 37 x 31
LENS_Y, LENS_W, LENS_H, LENS_RX = 134, 37, 31, 11


def svg_glasses_escuros(g: dict, uid: str = "") -> str:
    """Óculos escuros na linha dos olhos; lentes cobrem o olho inteiro."""
    lenses = "".join(f'<rect x="{x}" y="{LENS_Y}" width="{LENS_W}" height="{LENS_H}" rx="{LENS_RX}" fill="#141414"/>'
                     for x in LENS.values())
    out = ['<g class="glasses">',
           '<path d="M302 140 L284 134" stroke="#141414" stroke-width="5" stroke-linecap="round"/>',
           '<path d="M378 140 L396 134" stroke="#141414" stroke-width="5" stroke-linecap="round"/>',
           '<rect x="336" y="137" width="8" height="5" rx="2" fill="#141414"/>',
           lenses,
           '<path d="M306 137 l10 0 l-8 14 l-6 0 Z" fill="#ffffff" opacity="0.18"/>',
           '<path d="M346 137 l10 0 l-8 14 l-6 0 Z" fill="#ffffff" opacity="0.18"/>']
    u = g.get("glint")
    if u is not None and 0 <= u <= 1:
        gx = 280 + 120 * u * u * (3 - 2 * u)
        out.append(f'<clipPath id="{uid}lens">'
                   + lenses.replace(' fill="#141414"', "") + '</clipPath>'
                   f'<path d="M{f(gx)} 128 l14 0 l-22 40 l-14 0 Z" fill="#ffffff" opacity="0.75" '
                   f'clip-path="url(#{uid}lens)"/>')
    out.append("</g>")
    return "".join(out)


GLASSES = {"escuros": svg_glasses_escuros}


# ---------------------------------------------------------------- cabelo
def load_hair(style: str) -> tuple[str, str]:
    path = os.path.join(HAIR_DIR, f"{style}.svg")
    if not os.path.isfile(path):
        raise SystemExit(f"cabelo não encontrado: {path}")
    ET.register_namespace("", SVG_NS)
    root = ET.parse(path).getroot()
    parts = {}
    for g in root.iter(f"{{{SVG_NS}}}g"):
        gid = g.get("id")
        if gid in ("back", "front"):
            inner = "".join(ET.tostring(ch, encoding="unicode") for ch in g)
            parts[gid] = inner.replace(f' xmlns="{SVG_NS}"', "").replace("ns0:", "")
    return parts.get("back", ""), parts.get("front", "")


# ---------------------------------------------------------------- montagem
def body_parts(p: dict) -> dict:
    return {
        "legs": (
            f'<g class="legs"><rect x="304" y="375" width="32" height="235" rx="5" fill="{p["pants"]}"/>'
            f'<rect x="344" y="375" width="32" height="235" rx="5" fill="{p["pants"]}"/></g>'
        ),
        "shoes": (
            f'<g class="shoes"><ellipse cx="318" cy="614" rx="22" ry="8" fill="{p["shoes"]}"/>'
            f'<ellipse cx="362" cy="614" rx="22" ry="8" fill="{p["shoes"]}"/></g>'
        ),
        "torso": (
            f'<path class="torso" d="M285 385 L285 225 Q285 192 340 192 Q395 192 395 225 L395 385 Z" '
            f'fill="{p["shirt"]}"/>'
        ),
        "head": f'<circle class="head" cx="{HEAD_CX}" cy="{HEAD_CY}" r="{HEAD_R}" fill="{p["skin"]}"/>',
    }


def compose_group(p: dict, uid: str = "", upper_dy: float = 0.0) -> str:
    """Retorna só as camadas do personagem (sem <svg>/<defs>), para montar cenas
    com vários personagens. uid prefixa os ids internos (clipPath dos olhos).
    upper_dy sobe o grupo superior (respiração); pernas e sapatos ficam parados."""
    pose = p["pose"]
    held = p["held"]
    bp = body_parts(p)
    hair_back, hair_front = load_hair(p["hair_style"])
    hc = p["hair_color"]

    back_arms, front_groups = [], []
    for side in ("left", "right"):
        sh, el = pose[f"{side}_shoulder"], pose[f"{side}_elbow"]
        holds = held is not None and held["hand"] == side
        crosses = arm_crosses(side, pose)
        if not holds and not crosses:
            back_arms.append(svg_arm(side, sh, el, p["shirt"], p["skin"]))
            continue
        # braço + objeto + mão em grupo próprio; mão por cima do objeto
        _, _, (hx, hy) = arm_points(side, sh, el)
        g = [svg_arm(side, sh, el, p["shirt"], p["skin"], draw_hand=False)]
        if holds:
            g.append(HELD_OBJECTS[held["type"]](hx, hy, side, held.get("color")))
        g.append(f'<circle class="hand" cx="{f(hx)}" cy="{f(hy)}" r="{HAND_R}" fill="{p["skin"]}"/>')
        group = f'<g class="limb-{side}" filter="url(#outline)">{"".join(g)}</g>'
        if crosses:
            front_groups.append(group)
        else:
            back_arms.append(group)  # segura objeto sem cruzar: continua atrás do tronco

    # back_arms podem conter grupos com filtro próprio; os demais braços ficam no grupo principal
    main_back = [a for a in back_arms if 'filter=' not in a]
    own_back = [a for a in back_arms if 'filter=' in a]

    def upper(content: str) -> str:
        if not content:
            return ""
        if not upper_dy:
            return content
        return f'<g class="upper" transform="translate(0,{f(-upper_dy)})">{content}</g>'

    body = (
        '<g class="character" filter="url(#outline)">'
        + upper(f'<g class="hair-back" color="{hc}" fill="currentColor">{hair_back}</g>'
                + "".join(main_back))
        + f'{bp["legs"]}{bp["shoes"]}'
        + upper(f'{bp["torso"]}{bp["head"]}'
                f'{svg_eye("left", p["iris"], p["skin"], p["eyes"], uid)}'
                f'{svg_eye("right", p["iris"], p["skin"], p["eyes"], uid)}'
                f'{svg_brows(p["brow_color"], p["brows"])}'
                f'<g class="hair-front" color="{hc}" fill="currentColor">{hair_front}</g>'
                + (GLASSES[p["glasses"]["style"]](p["glasses"], uid) if p["glasses"] else ""))
        + '</g>'
    )
    # braço que segura sem cruzar: desenhado antes do corpo, contorno próprio
    return upper("".join(own_back)) + body + upper("".join(front_groups))


def svg_document(content: str, width: int = CANVAS_W, height: int = CANVAS_H) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
        f'<defs>{OUTLINE_FILTER}</defs>{content}</svg>\n'
    )


def compose(p: dict) -> str:
    return svg_document(compose_group(p))


# ---------------------------------------------------------------- peças
def export_pieces(out_dir: str) -> list[str]:
    """Exporta as peças do personagem base (cores default) como SVGs de referência."""
    os.makedirs(out_dir, exist_ok=True)
    p = resolve_params({})
    bp = body_parts(p)
    neutral_eyes = {"look_x": 0, "look_y": 0, "lid_upper": 0, "lid_lower": 0}
    head = (
        "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 680 680\" width=\"680\" height=\"680\">"
        "{}</svg>\n"
    )
    pieces = {
        "contorno.svg": f"<defs>{OUTLINE_FILTER}</defs>"
                        '<!-- Filtro de contorno de silhueta: aplicar a GRUPOS (filter="url(#outline)"), nunca peça por peça. -->',
        "cabeca.svg": bp["head"],
        "tronco.svg": bp["torso"],
        "pernas.svg": bp["legs"] + bp["shoes"],
        "braco.svg": "<!-- Braço em duas peças. Pivô do ombro (279,210) esq. / (401,210) dir.; "
                     "cotovelo em translate(0,85) no espaço do braço. Ângulos: SHOULDER, ELBOW. -->"
                     + svg_arm("left", 4, 0, p["shirt"], p["skin"])
                     + svg_arm("right", -4, 0, p["shirt"], p["skin"]),
        "olho.svg": "<!-- Olho paramétrico (look_x, look_y, lid_upper, lid_lower, iris). Estado aberto/neutro. -->"
                    + svg_eye("left", p["iris"], p["skin"], neutral_eyes)
                    + svg_eye("right", p["iris"], p["skin"], neutral_eyes),
        "sobrancelhas.svg": svg_brows(p["brow_color"], {"raise": 0, "tilt": 0}),
    }
    written = []
    for name, body in pieces.items():
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head.format(body))
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("params", nargs="?", help="JSON de parâmetros")
    ap.add_argument("-o", "--output", help="arquivo SVG de saída (padrão: stdout)")
    ap.add_argument("--export-pieces", metavar="DIR", help="exporta as peças base em DIR")
    a = ap.parse_args(argv)

    if a.export_pieces:
        for w in export_pieces(a.export_pieces):
            print(w)
        return 0
    if not a.params:
        ap.error("informe o JSON de parâmetros")
    svg = compose(resolve_params(load_json(a.params)))
    if a.output:
        os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
        with open(a.output, "w", encoding="utf-8") as fh:
            fh.write(svg)
    else:
        sys.stdout.write(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
