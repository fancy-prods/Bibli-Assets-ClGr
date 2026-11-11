"""Modelo de vídeo Pop Explica. Copie esta pasta para videos/<slug>/ e edite só as CENAS.

    python video.py stills            -> storyboard.jpg (12 frames)  — sempre olhar antes de renderizar
    python video.py stills 1.2 5 9.4  -> storyboard nos segundos pedidos
    python video.py render            -> out/<slug>.mp4 (paralelo, com narração normalizada)
"""
import sys, os, json
VDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(VDIR, "..", "..", "engine"))
from popx import *

SLUG = os.path.basename(VDIR)
AUDIO = os.path.join(VDIR, "narracao.mp3")
WORDS = json.load(open(os.path.join(VDIR, "words.json"), encoding="utf-8"))
DUR = audio_duration(AUDIO) + 0.6

# Cores de destaque por palavra (grafia do roteiro, sem pontuação). Sem entrada = amarelo.
HIGHLIGHT = {
    # "refrigerante": "red", "chá": "green",
}
for w in WORDS:
    c = HIGHLIGHT.get(w["w"].strip(".,!?;:").lower())
    if c: w["c"] = c
cap = Captions(WORDS)


def T(word, n=1):
    """Segundo em que a n-ésima ocorrência de `word` começa a ser falada. Ancore TUDO nisso."""
    hits = [w["s"] for w in WORDS if w["w"].strip(".,!?;:").lower() == word.lower()]
    if len(hits) < n: raise KeyError(f"palavra '{word}' (ocorrência {n}) não está no words.json")
    return hits[n - 1]


def A(name):
    return os.path.join(VDIR, "assets", name)


# ---- assets (carregue uma vez, em nível de módulo)
# PRODUTO = pil_to_surface(Image.open(A("produto.png")))
# DEMO = Clip(A("demo.mp4"), w=760, h=1000, start=0.0)

# ---- cenas: uma função por bloco do roteiro, todas f(ctx, t)
def hook(ctx, t):
    pass


def virada(ctx, t):
    # product(ctx, t, T("pulo") + 0.15, 540, 1000, img=PRODUTO, h=820)
    pass


def final(ctx, t):
    # product(...); cta(ctx, t, T("carrinho"), 540, 1560)
    pass


SCENES = [
    {"t": 0, "theme": "red", "draw": hook},
    # {"t": T("pulo") - 0.2, "theme": "purple", "draw": virada, "origin": (540, 1000)},
    # {"t": T("toca"), "theme": "purple", "draw": final},
]


def frame(ctx, t):
    timeline(ctx, t, SCENES)
    cap.draw(ctx, t)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if mode == "stills":
        times = [float(x) for x in sys.argv[2:]] or None
        print(storyboard(frame, DUR, os.path.join(VDIR, "storyboard.jpg"), times=times))
    elif mode == "render":
        os.makedirs(os.path.join(VDIR, "out"), exist_ok=True)
        out = os.path.join(VDIR, "out", f"{SLUG}.mp4")
        print(render_parallel(__file__, DUR, out, audio=AUDIO))
