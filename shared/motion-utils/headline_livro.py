"""Headline de abertura dos vídeos de livros (agnóstica de estilo), com templates de texto.

A capa 3D surge no topo, mostra a frente por um instante, gira rápido para a esquerda
(quase duas voltas) e para inclinada no canto esquerdo; ao lado entram o rótulo
("explicando livros") e o título. Tudo sobe e some em t_out (padrão: 2,85 s; fim em 3,1 s).
Camada de UI em coordenadas de tela 1080x1920.

    from headline_livro import TEMPLATES
    hl = TEMPLATES["etiquetas"](r"...\\loop\\frames", ["Como fazer amigos", "e influenciar", "pessoas"])
    svg += hl.svg(t)

Templates: "padrao" (Arial Black branco com contorno), "marca-texto" (Ink Free + Bahnschrift,
marca-texto amarelo atrás de cada linha), "etiquetas" (pílula preta + tiras de papel com fita),
"impacto" (Impact em caixa alta, linhas batendo na tela, a do meio em vermelho).
Os templates de texto escuro precisam de fundo claro (ou de uma base) para ler bem.

Os frames da capa vêm do loop RGBA de shared/models/book (book.py --render): o frame k
(1..N) mostra o livro girado (k-1) * 360/N graus; ângulo crescente = frente indo para a
direita, então girar para a esquerda é percorrer os ângulos em ordem decrescente.
Larguras de texto (fundo do marca-texto, tiras) são medidas rasterizando com resvg_py.
Dependências: resvg_py, av, numpy; fontes do Windows (Arial, Ink Free, Bahnschrift, Segoe UI, Impact).
"""
from __future__ import annotations

import base64
import glob
import os

from camera import clamp01, lerp, ease_out_cubic, ease_in_quad, ease_in_out, ease_out_back, pop

TX = 395            # início do bloco de texto (à direita da capa)


def _f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def font_text(x, y, size, content, family, fill, weight="700", extra=""):
    return (f'<text x="{_f(x)}" y="{_f(y)}" font-family="{family}" font-weight="{weight}" font-size="{_f(size)}" '
            f'fill="{fill}" {extra}>{content}</text>')


def _outlined(x, y, size, content, fill, sw):
    return font_text(x, y, size, content, "Arial", fill, "900",
                     f'stroke="#111111" stroke-width="{_f(sw)}" stroke-linejoin="round" paint-order="stroke"')


_widths = {}


def text_width(content, family, weight, size, extra=""):
    """Largura real do texto em px (rasteriza com resvg e mede a última coluna com tinta)."""
    key = (content, family, weight, size, extra)
    if key not in _widths:
        import av
        import numpy as np
        import resvg_py
        w, h = int(size * len(content) * 1.2) + 40, int(size * 1.6)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
               + font_text(0, size * 1.1, size, content, family, "#000", weight, extra) + '</svg>')
        png = bytes(resvg_py.svg_to_bytes(svg_string=svg))
        alpha = av.CodecContext.create("png", "r").decode(av.Packet(png))[0].to_ndarray(format="rgba")[:, :, 3]
        cols = np.nonzero(alpha.max(axis=0) > 20)[0]
        _widths[key] = float(cols[-1] + 1) if len(cols) else 0.0
    return _widths[key]


class Headline:
    """Template "padrao". Subclasses mudam só text_svg (o livro e o tempo são os mesmos)."""
    name = "padrao"

    def __init__(self, frames_dir, title_lines, *, label="explicando livros", t0=0.0, t_out=2.85,
                 end_angle=28.0, turns=2, spin=1.15, book_px=470, accent="#ffd34d"):
        self.files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
        if not self.files:
            raise SystemExit(f"sem frames em {frames_dir}")
        self.cache = {}
        self.title = title_lines
        self.label = label
        self.t0, self.t_out = t0, t_out
        self.end_angle, self.turns, self.spin = end_angle, turns, spin
        self.book_px = book_px
        self.accent = accent

    def _frame(self, angle):
        n = len(self.files)
        k = int(round(angle % 360 / 360 * n)) % n
        if k not in self.cache:
            with open(self.files[k], "rb") as fh:
                self.cache[k] = base64.b64encode(fh.read()).decode()
        return self.cache[k]

    def svg(self, t):
        u = t - self.t0
        if u < 0:
            return ""
        out_k = ease_in_quad((t - self.t_out) / 0.25) if t >= self.t_out else 0.0
        if out_k >= 1:
            return ""
        dy = -420 * out_k
        return (f'<g transform="translate(0,{_f(dy)})" opacity="{_f(1 - out_k)}">'
                f'<g opacity="{_f(clamp01(u / 0.08))}">{self.book_svg(u)}</g>{self.text_svg(u)}</g>')

    def book_svg(self, u):
        """Livro: surge no centro do topo, gira para a esquerda enquanto vai para o canto."""
        s_in = pop(u, 0.0, 0.25)
        e = ease_out_cubic((u - 0.12) / self.spin)   # mostra a capa de frente por um instante
        angle = self.end_angle + 360 * self.turns * (1 - e)
        x = lerp(540, 215, ease_out_cubic(u / (self.spin * 0.8)))
        y = lerp(380, 280, ease_out_cubic(u / (self.spin * 0.8)))
        scale = lerp(1.25, 1.0, e) * s_in
        tilt = lerp(0, -6, e)
        px = self.book_px * scale
        return (f'<g transform="translate({_f(x)},{_f(y)}) rotate({_f(tilt)})">'
                f'<image href="data:image/png;base64,{self._frame(angle)}" x="{_f(-px / 2)}" y="{_f(-px / 2)}" '
                f'width="{_f(px)}" height="{_f(px)}"/></g>')

    def text_svg(self, u):
        """Textos: entram quando o giro está acabando."""
        k1 = ease_out_back((u - self.spin * 0.7) / 0.3) if u >= self.spin * 0.7 else 0.0
        k2 = ease_out_back((u - self.spin * 0.8) / 0.3) if u >= self.spin * 0.8 else 0.0
        texts = ""
        if k1 > 0:
            texts += (f'<g transform="translate({TX},170) scale({_f(k1)})">'
                      + _outlined(0, 0, 42, self.label.upper(), self.accent, 10) + '</g>')
        if k2 > 0:
            lines = "".join(_outlined(0, 66 * i, 58, line, "#ffffff", 12) for i, line in enumerate(self.title))
            texts += f'<g transform="translate({TX},238) scale({_f(k2)})">{lines}</g>'
        return texts


class MarcaTexto(Headline):
    name = "marca-texto"

    def text_svg(self, u):
        ts = self.spin * 0.7
        out = []
        if u >= ts:
            k = ease_out_back((u - ts) / 0.3)
            out.append(f'<g transform="translate({TX},165) rotate(-3) scale({_f(k)})">'
                       + font_text(0, 0, 44, f"{self.label}...", "Ink Free", "#3a3a3a", "700") + '</g>')
        for i, line in enumerate(self.title):
            t0 = ts + 0.12 + 0.13 * i
            if u < t0:
                continue
            y = 255 + 72 * i
            w = (text_width(line, "Bahnschrift", "700", 62) + 6) * ease_in_out((u - t0) / 0.3)
            op = clamp01((u - t0) / 0.12)
            out.append(f'<path d="M{TX - 10} {y - 44} l{_f(w + 14)} -4 l2 52 l{_f(-w - 14)} 6 Z" fill="#ffe14d" opacity="0.9"/>'
                       f'<g opacity="{_f(op)}">'
                       + font_text(TX, y, 62, line, "Bahnschrift", "#1d1d1d", "700") + '</g>')
        return "".join(out)


class Etiquetas(Headline):
    name = "etiquetas"

    def text_svg(self, u):
        ts = self.spin * 0.7
        out = []
        if u >= ts:
            k = ease_out_back((u - ts) / 0.3)
            label = self.label.upper()
            ls = 'letter-spacing="3"'
            pw = text_width(label, "Bahnschrift", "700", 28, ls) + 48
            out.append(f'<g transform="translate({TX},150) scale({_f(k)})">'
                       f'<rect x="0" y="-8" width="{_f(pw)}" height="52" rx="26" fill="#111111"/>'
                       + font_text(pw / 2, 28, 28, label, "Bahnschrift", "#ffffff", "700",
                                   f'text-anchor="middle" {ls}') + '</g>')
        for i, line in enumerate(self.title):
            t0 = ts + 0.1 + 0.11 * i
            if u < t0:
                continue
            k = ease_out_back((u - t0) / 0.35, 1.6)
            w = text_width(line, "Segoe UI", "900", 52) + 40
            x = TX + 500 * (1 - k)
            y = 232 + 82 * i
            rot = (-2, 1.5, -1)[i % 3]
            out.append(f'<g transform="translate({_f(x)},{y}) rotate({rot})">'
                       f'<rect x="8" y="8" width="{_f(w)}" height="70" fill="#000" opacity="0.18"/>'
                       f'<rect x="0" y="0" width="{_f(w)}" height="70" fill="#fffdf4" stroke="#111" stroke-width="5"/>'
                       '<rect x="-34" y="-6" width="74" height="26" fill="#f6e7a8" opacity="0.85" transform="rotate(-35)"/>'
                       + font_text(18, 54, 52, line, "Segoe UI", "#111111", "900") + '</g>')
        return "".join(out)


class Impacto(Headline):
    name = "impacto"
    SIZES = (78, 78, 104)       # a última linha maior
    YS = (258, 340, 440)

    def text_svg(self, u):
        ts = self.spin * 0.7
        out = []
        if u >= ts:
            k = ease_out_back((u - ts) / 0.25)
            label = self.label.upper()
            ls = 'letter-spacing="1"'
            bw = text_width(label, "Impact", "400", 38, ls) + 30
            out.append(f'<g transform="translate({TX},160) rotate(-2) scale({_f(k)})">'
                       f'<rect x="-6" y="-38" width="{_f(bw)}" height="50" fill="#e2574c"/>'
                       + font_text(bw / 2 - 6, 2, 38, label, "Impact", "#ffffff", "400",
                                   f'text-anchor="middle" {ls}') + '</g>')
        for i, line in enumerate(self.title):
            t0 = ts + 0.1 + 0.12 * i
            if u < t0:
                continue
            uu = clamp01((u - t0) / 0.18)
            s = lerp(2.4, 1.0, ease_out_cubic(uu))
            fill = "#e2574c" if i == 1 else "#111111"
            j = min(i, len(self.SIZES) - 1)
            out.append(f'<g opacity="{_f(clamp01(uu * 2))}" transform="translate({TX},{self.YS[j]}) scale({_f(s)})">'
                       + font_text(0, 0, self.SIZES[j], line.upper(), "Impact", fill, "400") + '</g>')
        return "".join(out)


TEMPLATES = {"padrao": Headline, "marca-texto": MarcaTexto, "etiquetas": Etiquetas, "impacto": Impacto}
