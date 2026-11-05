#!/usr/bin/env python3
"""Animação ociosa (idle) + roteiro do estilo "palco". Gera um SVG por frame.

Só biblioteca padrão. Usa o montador (compose_character.py) para cada frame.

Uso:
    python tools/animate.py timeline.json -o renders/frames/
    python tools/animate.py timeline.json -o renders/frames/ --state estado.json

O idle nunca sobrescreve o roteiro: cada parte do personagem é um canal.
  breath  aditivo      grupo superior sobe 2.5·b, ombros abrem 1.5·b graus,
                       b = (1 − cos(2πt/4))/2; nunca desligado
  blink   aditivo      sin(π·k) em 0,17 s, a cada 2,5–5 s, e em 50% das mudanças
                       de olhar; suprimido por (1 − w) do canal lids
  gaze    substituível centro (0, 0.1) ↔ desvio (±0,35–0,7, ±0,25);
                       desvio 0,8–2 s, centro 3–7 s; cur += (tgt − cur)·min(1, dt·18)
  lids    substituível lid_upper 0,12
  pose    substituível preset "neutro"

Mistura: w anda linearmente em 0,3 s; ws = w²(3 − 2w); final = lerp(idle, roteiro, ws).
A rampa de entrada termina em `t` e a de saída começa em `until`, de modo que
dentro de [t, until] o roteiro vale 100%.
Pálpebra final = max(lerp(0.12, roteiro, ws), blink·(1 − ws)).

Toda aleatoriedade vem de uma semente derivada do id do personagem: a mesma
timeline gera sempre os mesmos frames.

Formato da timeline:
{
  "fps": 30, "duration": 6, "canvas": [680, 680],          # canvas opcional
  "characters": [{"id": "joao", "params": {...}, "position": [340, 0], "scale": 1}],
  "script": [
    {"char": "joao", "t": 1.0, "until": 3.5, "pose": "explicando"},
    {"char": "joao", "t": 2.0, "until": 4.0, "gaze": {"point": [100, 150]}},
    {"char": "joao", "t": 2.0, "until": 4.0, "gaze": {"target": "personagem:maria"}},
    {"char": "joao", "t": 2.0, "until": 4.0, "gaze": {"look_x": 0.5, "look_y": 0}},
    {"char": "joao", "t": 4.5, "until": 5.5, "lids": {"lid_upper": 1}}
  ]
}
`params` segue o formato do montador. `position` é onde fica o ponto (340, 0) das
coordenadas base; `scale` escala em torno dele. Coordenadas de `point` são do canvas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose_character as cc  # noqa: E402

# ---------------------------------------------------------------- constantes
BREATH_PERIOD = 4.0
BREATH_RISE = 2.5          # unidades base
BREATH_SHOULDER = 1.5      # graus
BLINK_DUR = 0.17
BLINK_INTERVAL = (2.5, 5.0)
GAZE_CENTER = (0.0, 0.1)
GAZE_DEV_X = (0.35, 0.7)
GAZE_DEV_Y = 0.25
GAZE_DEV_DUR = (0.8, 2.0)
GAZE_CENTER_DUR = (3.0, 7.0)
GAZE_SPEED = 18.0
GAZE_BLINK_CHANCE = 0.5
LID_IDLE = 0.12
RAMP = 0.3
POSE_KEYS = ("right_shoulder", "right_elbow", "left_shoulder", "left_elbow")
CHANNELS = ("pose", "gaze", "lids")


def seed_for(char_id: str, stream: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{char_id}:{stream}".encode()).digest()[:8], "big")


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def smooth(w: float) -> float:
    return w * w * (3 - 2 * w)


# ---------------------------------------------------------------- idle: agenda
def gaze_schedule(char_id: str, duration: float):
    """Lista de (início, alvo_x, alvo_y) e instantes das mudanças de olhar."""
    rng = random.Random(seed_for(char_id, "gaze"))
    t, segs, at_center = 0.0, [], True
    while t <= duration:
        if at_center:
            segs.append((t, *GAZE_CENTER))
            t += rng.uniform(*GAZE_CENTER_DUR)
        else:
            x = rng.uniform(*GAZE_DEV_X) * rng.choice((-1, 1))
            y = rng.uniform(-GAZE_DEV_Y, GAZE_DEV_Y)
            segs.append((t, x, y))
            t += rng.uniform(*GAZE_DEV_DUR)
        at_center = not at_center
    return segs


def blink_schedule(char_id: str, duration: float, gaze_segs) -> list[float]:
    rng = random.Random(seed_for(char_id, "blink"))
    starts, t = [], rng.uniform(*BLINK_INTERVAL)
    while t <= duration:
        starts.append(t)
        t += rng.uniform(*BLINK_INTERVAL)
    rng_g = random.Random(seed_for(char_id, "gaze-blink"))
    for (ts, _, _) in gaze_segs[1:]:           # mudanças de olhar (não o início)
        if rng_g.random() < GAZE_BLINK_CHANCE:
            starts.append(ts)
    return sorted(starts)


def blink_value(t: float, starts: list[float]) -> float:
    v = 0.0
    for s in starts:
        k = (t - s) / BLINK_DUR
        if 0 <= k <= 1:
            v = max(v, math.sin(math.pi * k))
    return v


# ---------------------------------------------------------------- roteiro
def channel_weight(t: float, entries: list[dict]):
    """Peso linear (0..1) e entrada dominante do canal no instante t."""
    best_w, best_e = 0.0, None
    for e in entries:
        a, b = float(e["t"]), float(e["until"])
        if a <= t <= b:
            w = 1.0
        elif t < a:
            w = 1 - (a - t) / RAMP
        else:
            w = 1 - (t - b) / RAMP
        w = max(0.0, min(1.0, w))
        if w > best_w:
            best_w, best_e = w, e
    return best_w, best_e


# ---------------------------------------------------------------- frames
class Character:
    def __init__(self, spec: dict, duration: float, poses: dict):
        self.id = spec["id"]
        self.params = spec.get("params", {})
        self.pos = spec.get("position", [340, 0])
        self.scale = float(spec.get("scale", 1))
        self.gaze_segs = gaze_schedule(self.id, duration)
        self.blinks = blink_schedule(self.id, duration, self.gaze_segs)
        self.gaze_cur = list(GAZE_CENTER)
        self.poses = poses
        self.script = {c: [] for c in CHANNELS}

    def head_center(self) -> tuple[float, float]:
        return (self.pos[0] + (cc.HEAD_CX - 340) * self.scale,
                self.pos[1] + cc.HEAD_CY * self.scale)

    def idle_gaze_target(self, t: float):
        tgt = self.gaze_segs[0]
        for seg in self.gaze_segs:
            if seg[0] <= t:
                tgt = seg
            else:
                break
        return tgt[1], tgt[2]

    def pose_angles(self, value) -> dict:
        if isinstance(value, str):
            if value not in self.poses or value.startswith("_"):
                raise SystemExit(f"pose desconhecida no roteiro: {value!r}")
            return self.poses[value]
        merged = dict(self.poses["neutro"])
        merged.update(value)
        return merged


def resolve_gaze(spec: dict, ch: Character, chars: dict) -> tuple[float, float]:
    if "look_x" in spec or "look_y" in spec:
        return (cc.clamp(spec.get("look_x", 0), -1, 1), cc.clamp(spec.get("look_y", 0), -1, 1))
    if "point" in spec:
        px, py = spec["point"]
    elif "target" in spec:
        name = spec["target"].split(":", 1)[-1]
        if name not in chars:
            raise SystemExit(f"alvo de olhar desconhecido: {spec['target']!r}")
        px, py = chars[name].head_center()
    else:
        raise SystemExit(f"gaze sem look_x/look_y, point ou target: {spec!r}")
    hx, hy = ch.head_center()
    dx, dy = px - hx, py - hy
    n = math.hypot(dx, dy)
    if n == 0:
        return 0.0, 0.0
    return cc.clamp(dx / n, -1, 1), cc.clamp(dy / n, -1, 1)


def frame_state(ch: Character, chars: dict, t: float, dt: float) -> dict:
    # breath (aditivo)
    b = (1 - math.cos(2 * math.pi * t / BREATH_PERIOD)) / 2

    # gaze idle (aproximação rápida, com estado)
    gx, gy = ch.idle_gaze_target(t)
    k = min(1.0, dt * GAZE_SPEED)
    ch.gaze_cur[0] += (gx - ch.gaze_cur[0]) * k
    ch.gaze_cur[1] += (gy - ch.gaze_cur[1]) * k
    w_g, e_g = channel_weight(t, ch.script["gaze"])
    ws_g = smooth(w_g)
    if e_g is not None:
        sx, sy = resolve_gaze(e_g["gaze"], ch, chars)
    else:
        sx, sy = ch.gaze_cur
    look_x = lerp(ch.gaze_cur[0], sx, ws_g)
    look_y = lerp(ch.gaze_cur[1], sy, ws_g)

    # lids + blink
    w_l, e_l = channel_weight(t, ch.script["lids"])
    ws_l = smooth(w_l)
    lids_s = e_l["lids"] if e_l is not None else {}
    blink = blink_value(t, ch.blinks)
    lid_upper = max(lerp(LID_IDLE, float(lids_s.get("lid_upper", LID_IDLE)), ws_l), blink * (1 - ws_l))
    lid_lower = lerp(0.0, float(lids_s.get("lid_lower", 0.0)), ws_l)

    # pose
    idle_pose = ch.poses["neutro"]
    w_p, e_p = channel_weight(t, ch.script["pose"])
    ws_p = smooth(w_p)
    script_pose = ch.pose_angles(e_p["pose"]) if e_p is not None else idle_pose
    pose = {key: lerp(idle_pose[key], script_pose[key], ws_p) for key in POSE_KEYS}
    pose["left_shoulder"] += BREATH_SHOULDER * b     # ombros abrem (esq. para fora = +)
    pose["right_shoulder"] -= BREATH_SHOULDER * b    # (dir. para fora = −)
    # camada do braço que cruza: a do preset quando o roteiro domina, senão automática
    pose["crosses_body"] = script_pose.get("crosses_body") if ws_p >= 1 else None
    held = None
    if e_p is not None and ws_p >= 0.5:
        held = e_p.get("held_object", script_pose.get("default_held_object"))

    return {
        "t": round(t, 6), "breath": b, "upper_dy": BREATH_RISE * b,
        "look_x": look_x, "look_y": look_y,
        "lid_upper": min(1.0, lid_upper), "lid_lower": lid_lower, "blink": blink,
        "pose": pose, "held_object": held,
        "weights": {"pose": ws_p, "gaze": ws_g, "lids": ws_l},
    }


def render_character(ch: Character, st: dict) -> str:
    raw = dict(ch.params)
    raw["pose"] = st["pose"]
    raw["eyes"] = {"look_x": st["look_x"], "look_y": st["look_y"],
                   "lid_upper": st["lid_upper"], "lid_lower": st["lid_lower"]}
    raw["held_object"] = st["held_object"]
    p = cc.resolve_params(raw)
    inner = cc.compose_group(p, uid=f"{ch.id}-", upper_dy=st["upper_dy"])
    s = ch.scale
    tr = f"translate({cc.f(ch.pos[0])},{cc.f(ch.pos[1])}) scale({cc.f(s)}) translate(-340,0)"
    if ch.pos == [340, 0] and s == 1:
        tr = ""
    attr = f' transform="{tr}"' if tr else ""
    return f'<g id="char-{ch.id}"{attr}>{inner}</g>'


def run(timeline: dict, out_dir: str, state_path: str | None = None) -> int:
    fps = int(timeline.get("fps", 30))
    duration = float(timeline["duration"])
    width, height = timeline.get("canvas", [cc.CANVAS_W, cc.CANVAS_H])
    poses = cc.load_json(os.path.join(cc.PRESETS_DIR, "poses.json"))

    chars: dict[str, Character] = {}
    for spec in timeline["characters"]:
        if spec["id"] in chars:
            raise SystemExit(f"id de personagem repetido: {spec['id']!r}")
        chars[spec["id"]] = Character(spec, duration, poses)
    for e in timeline.get("script", []):
        if e["char"] not in chars:
            raise SystemExit(f"roteiro cita personagem desconhecido: {e['char']!r}")
        for c in CHANNELS:
            if c in e:
                chars[e["char"]].script[c].append(e)

    os.makedirs(out_dir, exist_ok=True)
    n = int(round(duration * fps))
    dt = 1.0 / fps
    states = []
    for i in range(n):
        t = i / fps
        layers, fstate = [], {"frame": i, "t": round(t, 6), "characters": {}}
        for ch in chars.values():
            st = frame_state(ch, chars, t, dt)
            fstate["characters"][ch.id] = st
            layers.append(render_character(ch, st))
        svg = cc.svg_document("".join(layers), width, height)
        with open(os.path.join(out_dir, f"frame_{i:04d}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        states.append(fstate)
    if state_path:
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump(states, fh, ensure_ascii=False, indent=1)
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("timeline", help="JSON da timeline")
    ap.add_argument("-o", "--output", required=True, help="pasta dos frames SVG")
    ap.add_argument("--state", help="grava o estado de cada frame (JSON) para inspeção")
    a = ap.parse_args(argv)
    n = run(cc.load_json(a.timeline), a.output, a.state)
    print(f"{n} frames em {a.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
