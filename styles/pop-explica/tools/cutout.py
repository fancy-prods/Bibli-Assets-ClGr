"""Recorta fundo LISO (branco, cinza claro, cor única) de foto de produto -> PNG transparente cortado justo.

    python tools/cutout.py assets/produto.jpg assets/produto.png [tolerancia=38]

Funciona por preenchimento a partir das bordas, então só remove o fundo conectado à borda da imagem
(o branco DENTRO da embalagem é preservado). Não serve para banner com gradiente/texto atrás do produto:
nesse caso pedir ao Grok outra imagem (ver ASSETS.md) ou avisar o Arthur.
Se o PNG já tiver transparência, só corta as margens.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from collections import deque


def cutout(src, dst, tol=38):
    im = Image.open(src).convert("RGBA")
    a = np.array(im)
    if a[..., 3].min() < 250:
        out = im
    else:
        rgb = a[..., :3].astype(np.int16); h, w = rgb.shape[:2]
        border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
        bg = np.median(border, axis=0)
        close = np.abs(rgb - bg).max(axis=2) <= tol
        mask = np.zeros((h, w), bool); q = deque()
        for x in range(w):
            for y in (0, h - 1):
                if close[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
        for y in range(h):
            for x in (0, w - 1):
                if close[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not mask[ny, nx]:
                    mask[ny, nx] = True; q.append((ny, nx))
        alpha = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
        alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
        out = im.copy(); out.putalpha(alpha)
        removed = mask.mean()
        print(f"fundo removido: {removed:.0%} da imagem (bg ~ {tuple(int(v) for v in bg)})")
        if removed < 0.10: print("AVISO: removeu pouco — o fundo provavelmente não é liso.")
    bb = out.getbbox()
    out = out.crop(bb) if bb else out
    out.save(dst); print(f"{dst}: {out.size[0]}x{out.size[1]}")


if __name__ == "__main__":
    cutout(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 38)
