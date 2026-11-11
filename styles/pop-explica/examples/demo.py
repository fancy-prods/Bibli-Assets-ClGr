"""Demo do estilo Pop Explica (sem áudio, tempos de palavra simulados).
python3 demo.py video  -> demo.mp4
python3 demo.py stills 1 5 9 ... -> frames para conferência
"""
import sys
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from popx import *

SCRIPT = ("Todo mundo já reparou nisso. Menos você. "
          "Não é falta de cuidado. É o hábito de todo santo dia. "
          "O pulo do gato está no mecanismo. Sem sulfato e registrado na Anvisa. "
          "Toca no carrinho e garante o seu.")
COLORS = {"Anvisa.": "green", "sulfato": "green", "hábito": "orange", "carrinho": "orange", "mecanismo.": "pink"}


def fake_times(text, t=0.3):
    out = []
    for w in text.split():
        d = 0.11 + 0.055 * len(w)
        item = {"w": w, "s": round(t, 3), "e": round(t + d, 3)}
        if w in COLORS: item["c"] = COLORS[w]
        out.append(item); t += d + (0.28 if w[-1] in ".!?" else 0.03)
    return out


WORDS = fake_times(SCRIPT)
cap = Captions(WORDS)
T = lambda word, n=1: [w["s"] for w in WORDS if w["w"].strip(".,").lower() == word.lower()][n - 1]
END = WORDS[-1]["e"] + 1.2

t_orange, t_purple, t_cta = T("Não"), T("pulo") - 0.2, T("Toca")


def s1(ctx, t):  # problema: todo mundo reparou
    tooth(ctx, t, 540, 1080, 1.25 * pop(t, 0.25), "sad", 0.85)
    for i, (x, y) in enumerate([(200, 620), (880, 640), (170, 1500), (900, 1480), (540, 560)]):
        eyes_pair(ctx, t, T("reparou") + i * 0.12, x, y, 0.9)


def s2(ctx, t):  # causa: hábito diário
    tooth(ctx, t, 540, 1080, 1.25, "sad", 0.85 + 0.1 * prog(t, T("santo"), 0.6))
    pill(ctx, t, T("cuidado"), 540, 470, "ESCOVA 2x AO DIA", icon="check")
    progress_bar(ctx, t, T("hábito"), 540, 1560, "ESMALTE", 0.9, 0.35)


def s3(ctx, t):  # virada: produto + mecanismo + confiança
    product(ctx, t, t_purple + 0.15, 540, 1000, h=820)
    sparkles(ctx, t, t_purple + 0.3, 540, 1000)
    checklist(ctx, t, [("Sem sulfato", T("sulfato")), ("Registrado na Anvisa", T("Anvisa"))], y=1460)


def s4(ctx, t):  # resultado + CTA
    tooth(ctx, t, 540, 1020, 1.1 * pop(t, t_cta, 0.35), "happy", 0.0, shine=True)
    sparkles(ctx, t, t_cta + 0.1, 540, 1000, (260, 300), 7, seed=8)
    cta(ctx, t, T("carrinho"), 540, 1560)


SCENES = [
    {"t": 0, "theme": "red", "draw": s1},
    {"t": t_orange, "theme": "orange", "draw": s2, "origin": (540, 1250)},
    {"t": t_purple, "theme": "purple", "draw": s3, "origin": (540, 1000)},
    {"t": t_cta, "theme": "purple", "draw": s4, "origin": (540, 1000)},
]


def frame(ctx, t):
    timeline(ctx, t, SCENES)
    cap.draw(ctx, t)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "video"
    if mode == "video":
        render(frame, END, "demo.mp4"); print("ok", END)
    else:
        for x in sys.argv[2:]: still(frame, float(x), f"st_{x}.png", 0.33)
