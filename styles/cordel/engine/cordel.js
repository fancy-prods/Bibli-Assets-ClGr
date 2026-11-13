/* cordel.js: motor do estilo "cordel" (xilogravura). SVG + filtros; animação em passos de 1/12 s.
 * Depende de shared/web/kit.js. Expõe window.Cordel.
 *
 * Ideia: tudo é "matriz de madeira" preta impressa sobre papel colorido. Formas pretas, detalhes entalhados
 * em branco (cor do papel), borda roída pelo filtro #xilo, falhas de tinta, e até 2 cores chapadas por baixo
 * (impressas fora de registro). O filtro troca de semente a cada 1/6 s: a borda "ferve" como impressão manual.
 */
(function (g) {
  const K = g.Kit, NS = 'http://www.w3.org/2000/svg', X = {};
  X.INK = '#1a1410';
  X.PAPER = { palha: '#efd68a', rosa: '#f2a79c', verde: '#a9d4a0', azul: '#9bc7de', cru: '#e9dcc0', laranja: '#f3b36a' };
  X.SPOT = { urucum: '#cf3a2b', anil: '#27599a', gema: '#f0b02c', mata: '#2f8a4e' };
  const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  X.el = el;

  /* cria o <svg> do palco com papel, filtros e camadas: spot (cores chapadas, multiply) e ink (preto) */
  X.stage = function (root, { paper = 'palha', W = K.W, H = K.H } = {}) {
    const svg = el('svg', { xmlns: NS, viewBox: `0 0 ${W} ${H}`, width: W, height: H }, root); svg.style.display = 'block';
    const defs = el('defs', {}, svg);
    defs.innerHTML = `
      <filter id="xilo" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="2" seed="3" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.55 0.75" numOctaves="2" seed="8" result="g"/>
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -16 11.3" result="falha"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="2" seed="5" result="g2"/>
        <feColorMatrix in="g2" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -8 7.0" result="rolo"/>
        <feComposite in="d" in2="falha" operator="in" result="a"/>
        <feComposite in="a" in2="rolo" operator="in"/>
      </filter>
      <filter id="xilo-fino" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="3" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.55 0.75" numOctaves="2" seed="8" result="g"/>
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -16 11.6" result="falha"/>
        <feComposite in="d" in2="falha" operator="in"/>
      </filter>
      <filter id="xilo-spot" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="11" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="16" xChannelSelector="R" yChannelSelector="G" result="d"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.4" numOctaves="2" seed="2" result="g"/>
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -6 4.4" result="m"/>
        <feComposite in="d" in2="m" operator="in"/>
      </filter>
      <filter id="papel" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.9 0.35" numOctaves="3" seed="4" result="f"/>
        <feColorMatrix in="f" type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.18  0 0 0 0 0.1  0 0 0 0.55 -0.12" result="fib"/>
        <feTurbulence type="fractalNoise" baseFrequency="0.004" numOctaves="2" seed="9" result="m"/>
        <feColorMatrix in="m" type="matrix" values="0 0 0 0 1  0 0 0 0 0.96  0 0 0 0 0.85  0 0 0 0.9 -0.3" result="mancha"/>
        <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="mancha"/><feMergeNode in="fib"/></feMerge>
      </filter>
      <radialGradient id="vinheta" cx="50%" cy="50%" r="75%"><stop offset="0.62" stop-color="#3a2a14" stop-opacity="0"/><stop offset="1" stop-color="#3a2a14" stop-opacity="0.42"/></radialGradient>`;
    const paperColor = X.PAPER[paper] || paper;
    el('rect', { width: W, height: H, fill: paperColor, filter: 'url(#papel)' }, svg);
    const sheet = el('g', {}, svg);                       // tudo que é impresso (treme junto: registro)
    const spot = el('g', { filter: 'url(#xilo-spot)', style: 'mix-blend-mode:multiply' }, sheet);
    const ink = el('g', { filter: 'url(#xilo)' }, sheet);
    const type = el('g', { filter: 'url(#xilo-fino)' }, sheet);   // texto: borda menos roída, sem falha de rolo
    el('rect', { width: W, height: H, fill: 'url(#vinheta)', style: 'mix-blend-mode:multiply' }, svg);
    const turb = defs.querySelectorAll('#xilo feTurbulence');
    return { svg, defs, sheet, spot, ink, type, paperColor,
      /* chamar a cada quadro: ferve as bordas e treme o registro (passo de 1/6 s) */
      boil(t) { const k = Math.floor(t * 6); turb[0].setAttribute('seed', 3 + (k % 5)); turb[1].setAttribute('seed', 8 + (k % 4)); 
        const r = K.rng(k + 77); sheet.setAttribute('transform', `translate(${(r() - 0.5) * 1.6},${(r() - 0.5) * 1.6})`); spot.setAttribute('transform', `translate(${5 + (r() - 0.5) * 2},${4 + (r() - 0.5) * 2})`); } };
  };
  /* tempo em passos (animação "em dois": 12 poses por segundo) */
  X.step = (t, fps = 12) => Math.floor(t * fps + 1e-6) / fps;
  /* carimbo: aparece em 3 poses (fantasma maior e claro -> assenta). Devolve {opacity, transform} */
  X.stamp = function (node, t, t0, cx, cy) {
    const k = Math.round((X.step(t) - t0) * 12);
    if (k < 0) { node.setAttribute('opacity', 0); return false; }
    const sc = k === 0 ? 1.05 : k === 1 ? 0.985 : 1, op = k === 0 ? 0.45 : 1, rot = k === 0 ? -1.2 : k === 1 ? 0.5 : 0;
    node.setAttribute('opacity', op); node.setAttribute('transform', `translate(${cx},${cy}) rotate(${rot}) scale(${sc}) translate(${-cx},${-cy})`); return true;
  };

  /* ---------- peças de desenho (devolvem <g>) ---------- */
  const P = X.INK;
  /* faixa decorativa de triângulos (dente de serra) */
  X.serrilha = function (parent, x, y, w, h, n, up = true) { let d = ''; const s = w / n; for (let i = 0; i < n; i++) d += `M${x + i * s},${up ? y + h : y} L${x + i * s + s / 2},${up ? y : y + h} L${x + (i + 1) * s},${up ? y + h : y} Z `; return el('path', { d, fill: P }, parent); };
  /* moldura: filete grosso + serrilha em cima e embaixo + pontos nos cantos */
  X.moldura = function (parent, { W = K.W, H = K.H, m = 44, band = 40 } = {}) {
    const gr = el('g', {}, parent);
    el('rect', { x: m, y: m, width: W - 2 * m, height: H - 2 * m, fill: 'none', stroke: P, 'stroke-width': 16 }, gr);
    X.serrilha(gr, m + 8, m + 8, W - 2 * m - 16, band, 44, false); X.serrilha(gr, m + 8, H - m - 8 - band, W - 2 * m - 16, band, 44, true);
    return gr;
  };
  /* sol com rosto. rays gira em passos. Devolve {g, rays, spot} */
  X.sol = function (ink, spot, cx, cy, r, { color = X.SPOT.gema, n = 16 } = {}) {
    const gr = el('g', { transform: `translate(${cx},${cy})` }, ink), rays = el('g', {}, gr); let d = '';
    for (let i = 0; i < n; i++) { const a = i / n * K.TAU, l = r * (i % 2 ? 1.55 : 1.95), w = 0.17; d += `M${Math.cos(a - w) * r * 1.12},${Math.sin(a - w) * r * 1.12} L${Math.cos(a) * l},${Math.sin(a) * l} L${Math.cos(a + w) * r * 1.12},${Math.sin(a + w) * r * 1.12} Z `; }
    el('path', { d, fill: P }, rays);
    el('circle', { r, fill: 'none', stroke: P, 'stroke-width': r * 0.13 }, gr);
    // rosto entalhado
    const f = el('g', {}, gr), s = r / 100;
    el('path', { d: `M${-52 * s},${-22 * s} Q${-32 * s},${-44 * s} ${-12 * s},${-22 * s} Q${-32 * s},${-8 * s} ${-52 * s},${-22 * s} Z M${12 * s},${-22 * s} Q${32 * s},${-44 * s} ${52 * s},${-22 * s} Q${32 * s},${-8 * s} ${12 * s},${-22 * s} Z`, fill: 'none', stroke: P, 'stroke-width': 7 * s }, f);
    const eyes = el('g', {}, f); el('circle', { cx: -32 * s, cy: -23 * s, r: 8 * s, fill: P }, eyes); el('circle', { cx: 32 * s, cy: -23 * s, r: 8 * s, fill: P }, eyes);
    el('path', { d: `M${-58 * s},${-48 * s} Q${-34 * s},${-64 * s} ${-8 * s},${-46 * s} M${8 * s},${-46 * s} Q${34 * s},${-64 * s} ${58 * s},${-48 * s}`, fill: 'none', stroke: P, 'stroke-width': 9 * s, 'stroke-linecap': 'round' }, f);
    el('path', { d: `M${-2 * s},${-16 * s} L${-10 * s},${22 * s} L${8 * s},${22 * s}`, fill: 'none', stroke: P, 'stroke-width': 7 * s, 'stroke-linejoin': 'round' }, f);
    el('path', { d: `M${-40 * s},${40 * s} Q0,${74 * s} ${40 * s},${40 * s} Q0,${56 * s} ${-40 * s},${40 * s} Z`, fill: P }, f);
    el('circle', { cx: -62 * s, cy: 18 * s, r: 9 * s, fill: P }, f); el('circle', { cx: 62 * s, cy: 18 * s, r: 9 * s, fill: P }, f);
    const sp = spot ? el('circle', { cx, cy, r: r * 1.02, fill: color }, spot) : null;
    return { g: gr, rays, eyes, spot: sp };
  };
  /* copa de árvore: massa preta com folhas entalhadas (lentes brancas) */
  X.copa = function (parent, cx, cy, rx, ry, paper, { seed = 3, leaf = 30 } = {}) {
    const gr = el('g', {}, parent), r = K.rng(seed); let d = '';
    for (let i = 0; i < 18; i++) { const a = i / 18 * K.TAU, k = 1 + (r() - 0.5) * 0.22, x = cx + Math.cos(a) * rx * k, y = cy + Math.sin(a) * ry * k; d += (i ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1) + ' '; }
    el('path', { d: d + 'Z', fill: P, stroke: P, 'stroke-width': 30, 'stroke-linejoin': 'round' }, gr);
    let l = ''; const step = leaf * 1.5;
    for (let y = cy - ry; y < cy + ry; y += step * 0.72) for (let x = cx - rx + ((y / step | 0) % 2) * step / 2; x < cx + rx; x += step) {
      const px = x + (r() - 0.5) * 12, py = y + (r() - 0.5) * 12, nx = (px - cx) / rx, ny = (py - cy) / ry; if (nx * nx + ny * ny > 0.86) continue;
      const a = Math.atan2(ny, nx) + (r() - 0.5) * 0.9, c = Math.cos(a), s = Math.sin(a), L = leaf * (0.75 + r() * 0.5), w = L * 0.32;
      l += `M${(px - c * L / 2).toFixed(1)},${(py - s * L / 2).toFixed(1)} Q${(px - s * w).toFixed(1)},${(py + c * w).toFixed(1)} ${(px + c * L / 2).toFixed(1)},${(py + s * L / 2).toFixed(1)} Q${(px + s * w).toFixed(1)},${(py - c * w).toFixed(1)} ${(px - c * L / 2).toFixed(1)},${(py - s * L / 2).toFixed(1)} Z `;
    }
    el('path', { d: l, fill: paper }, gr); return gr;
  };
  X.tronco = function (parent, x, yTop, yBase, w, paper) {
    const gr = el('g', {}, parent);
    el('path', { d: `M${x - w * 0.5},${yTop} C${x - w * 0.42},${(yTop + yBase) / 2} ${x - w * 0.6},${yBase - 60} ${x - w * 1.25},${yBase} L${x + w * 1.3},${yBase} C${x + w * 0.62},${yBase - 60} ${x + w * 0.4},${(yTop + yBase) / 2} ${x + w * 0.5},${yTop} L${x + w * 1.6},${yTop - w * 1.8} L${x + w * 1.1},${yTop - w * 2.1} L${x + w * 0.1},${yTop - w * 0.6} L${x - w * 1.3},${yTop - w * 2.2} L${x - w * 1.8},${yTop - w * 1.8} Z`, fill: P }, gr);
    let d = ''; const r = K.rng(5); for (let i = 0; i < 9; i++) { const px = x + (r() - 0.5) * w * 0.6, y0 = K.lerp(yTop, yBase - 50, r()), len = 40 + r() * 70; d += `M${px},${y0} q${(r() - 0.5) * 10},${len / 2} 0,${len} `; }
    el('path', { d, fill: 'none', stroke: paper, 'stroke-width': 5, 'stroke-linecap': 'round' }, gr); return gr;
  };
  /* mandacaru: caule e braços com frisos; flor (cor chapada opcional) */
  X.mandacaru = function (ink, spot, x, yBase, h, paper, { color = X.SPOT.urucum } = {}) {
    const gr = el('g', {}, ink), w = h * 0.105, st = { fill: 'none', stroke: P, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    const arms = [`M${x},${yBase} L${x},${yBase - h}`, `M${x},${yBase - h * 0.34} L${x - h * 0.24},${yBase - h * 0.34} L${x - h * 0.24},${yBase - h * 0.76}`, `M${x},${yBase - h * 0.5} L${x + h * 0.22},${yBase - h * 0.5} L${x + h * 0.22},${yBase - h * 0.88}`];
    arms.forEach((d) => el('path', Object.assign({ d }, st), gr));
    arms.forEach((d) => { el('path', { d, fill: 'none', stroke: paper, 'stroke-width': w * 0.1, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': `${w * 0.5} ${w * 0.32}` }, gr); });
    const tips = [[x, yBase - h], [x - h * 0.24, yBase - h * 0.76], [x + h * 0.22, yBase - h * 0.88]];
    tips.forEach(([tx, ty], i) => { let d = ''; for (let k = 0; k < 7; k++) { const a = -Math.PI / 2 + (k - 3) * 0.42; d += `M${tx + Math.cos(a) * w * 0.3},${ty - w * 0.45 + Math.sin(a) * w * 0.3} L${tx + Math.cos(a) * w * 1.25},${ty - w * 0.45 + Math.sin(a) * w * 1.25} `; } el('path', { d, fill: 'none', stroke: P, 'stroke-width': w * 0.16, 'stroke-linecap': 'round' }, gr); if (spot && i !== 1) el('circle', { cx: tx, cy: ty - w * 0.9, r: w * 0.85, fill: color }, spot); });
    return gr;
  };
  /* casinha de taipa com telhado riscado */
  X.casa = function (ink, spot, x, yBase, w, paper, { color = X.SPOT.anil } = {}) {
    const gr = el('g', {}, ink), h = w * 0.55;
    el('rect', { x, y: yBase - h, width: w, height: h, fill: spot ? 'none' : paper, stroke: P, 'stroke-width': 9 }, gr);
    el('path', { d: `M${x - w * 0.1},${yBase - h} L${x + w * 0.5},${yBase - h - w * 0.4} L${x + w * 1.1},${yBase - h} Z`, fill: P }, gr);
    let d = ''; for (let i = 1; i < 9; i++) { const k = i / 9; d += `M${x - w * 0.1 + k * w * 1.2},${yBase - h - 4} L${x + w * 0.5 + (k - 0.5) * w * 0.12},${yBase - h - w * 0.4 + 12} `; }
    el('path', { d, stroke: paper, 'stroke-width': 4, fill: 'none' }, gr);
    el('rect', { x: x + w * 0.14, y: yBase - h * 0.72, width: w * 0.24, height: h * 0.72, fill: P }, gr);
    el('rect', { x: x + w * 0.58, y: yBase - h * 0.7, width: w * 0.26, height: h * 0.36, fill: P }, gr);
    el('path', { d: `M${x + w * 0.71},${yBase - h * 0.7} v${h * 0.36} M${x + w * 0.58},${yBase - h * 0.52} h${w * 0.26}`, stroke: paper, 'stroke-width': 4 }, gr);
    if (spot) el('rect', { x, y: yBase - h, width: w, height: h, fill: color, opacity: 0.85 }, spot);
    return gr;
  };
  /* pássaro em 2 poses (asa para cima / para baixo) */
  X.passaro = function (parent, s = 1) {
    const gr = el('g', {}, parent);
    el('path', { d: `M${-46 * s},0 Q${-10 * s},${-24 * s} ${34 * s},${-8 * s} L${56 * s},${-2 * s} L${34 * s},${4 * s} Q${-6 * s},${22 * s} ${-46 * s},0 Z M${-46 * s},0 L${-78 * s},${-14 * s} L${-70 * s},${2 * s} L${-80 * s},${14 * s} Z`, fill: P }, gr);
    const up = el('path', { d: `M${-14 * s},${-8 * s} L${-30 * s},${-58 * s} L${14 * s},${-12 * s} Z`, fill: P }, gr), dn = el('path', { d: `M${-14 * s},${6 * s} L${-26 * s},${48 * s} L${14 * s},${8 * s} Z`, fill: P }, gr);
    el('circle', { cx: 28 * s, cy: -4 * s, r: 3.2 * s, fill: '#fff' }, gr).setAttribute('class', 'paper-fill');
    return { g: gr, pose(i) { up.setAttribute('opacity', i % 2 ? 0 : 1); dn.setAttribute('opacity', i % 2 ? 1 : 0); } };
  };
  /* chão: morro preto com riscos entalhados e tufos */
  X.chao = function (parent, y, paper, { W = K.W, H = K.H, seed = 2 } = {}) {
    const gr = el('g', {}, parent), r = K.rng(seed);
    el('path', { d: `M0,${y + 30} C${W * 0.2},${y - 30} ${W * 0.38},${y + 34} ${W * 0.55},${y + 6} C${W * 0.75},${y - 28} ${W * 0.9},${y + 16} ${W},${y - 6} L${W},${H} L0,${H} Z`, fill: P }, gr);
    let d = ''; for (let i = 0; i < 110; i++) { const px = 70 + r() * (W - 140), py = y + 56 + r() * (H - y - 206), l = 24 + r() * 50; d += `M${px.toFixed(0)},${py.toFixed(0)} q${(l / 2).toFixed(0)},${(-6 - r() * 8).toFixed(0)} ${l.toFixed(0)},0 `; }
    el('path', { d, fill: 'none', stroke: paper, 'stroke-width': 5, 'stroke-linecap': 'round' }, gr);
    return gr;
  };
  X.tufo = function (parent, x, y, s = 1) { let d = ''; for (let i = -2; i <= 2; i++) d += `M${x + i * 7 * s},${y} Q${x + i * 13 * s},${y - 30 * s} ${x + i * 22 * s},${y - (44 - Math.abs(i) * 8) * s} L${x + i * 7 * s + 9 * s},${y} Z `; return el('path', { d, fill: P }, parent); };
  /* nuvem de espiral */
  X.nuvem = function (parent, x, y, s = 1) {
    const gr = el('g', { transform: `translate(${x},${y}) scale(${s})` }, parent);
    el('path', { d: 'M-120,30 C-150,30 -160,-10 -122,-18 C-124,-58 -64,-70 -44,-38 C-24,-78 46,-74 56,-30 C100,-44 136,-4 110,30 Z', fill: 'none', stroke: P, 'stroke-width': 11, 'stroke-linejoin': 'round' }, gr);
    el('path', { d: 'M-70,6 C-70,-24 -24,-24 -24,2 C-24,20 -52,20 -52,4 M20,8 C20,-26 72,-26 72,4 C72,22 40,22 40,6', fill: 'none', stroke: P, 'stroke-width': 8, 'stroke-linecap': 'round' }, gr);
    return gr;
  };
  /* estrelinhas/asteriscos para preencher o vazio */
  X.asteriscos = function (parent, pts, s = 13) { let d = ''; for (const [x, y] of pts) for (let k = 0; k < 4; k++) { const a = k * Math.PI / 4; d += `M${(x - Math.cos(a) * s).toFixed(1)},${(y - Math.sin(a) * s).toFixed(1)} L${(x + Math.cos(a) * s).toFixed(1)},${(y + Math.sin(a) * s).toFixed(1)} `; } return el('path', { d, stroke: P, 'stroke-width': 5, 'stroke-linecap': 'round', fill: 'none' }, parent); };

  /* leitor sentado, de perfil (olha para +x). Caixa local ~ 400×500, origem nos pés do banco (0,0), y negativo para cima */
  X.leitor = function (ink, spot, x, y, s, paper, { shirt = X.SPOT.urucum } = {}) {
    const gr = el('g', { transform: `translate(${x},${y}) scale(${s})` }, ink), sp = spot ? el('g', { transform: `translate(${x},${y}) scale(${s})` }, spot) : null;
    const st = (w, extra = {}) => Object.assign({ fill: 'none', stroke: P, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, extra);
    // banco
    el('path', { d: 'M-96,-150 L60,-150 L60,-128 L-96,-128 Z M-84,-128 L-98,0 L-78,0 L-62,-128 Z M34,-128 L52,0 L72,0 L54,-128 Z', fill: P }, gr);
    el('path', { d: 'M-80,-139 L44,-139', stroke: paper, 'stroke-width': 4, 'stroke-dasharray': '26 12' }, gr);
    // perna de trás, perna da frente (calça preta com vinco entalhado), pés
    el('path', Object.assign({ d: 'M-30,-168 L112,-176 L122,-34' }, st(50)), gr);
    el('path', { d: 'M96,-34 L188,-34 Q196,-8 176,-4 L96,-4 Z', fill: P }, gr);
    el('path', { d: 'M-10,-170 L104,-178 M118,-150 L124,-50', stroke: paper, 'stroke-width': 4.5, fill: 'none', 'stroke-linecap': 'round' }, gr);
    el('path', { d: 'M112,-18 L170,-18', stroke: paper, 'stroke-width': 4, 'stroke-dasharray': '10 9' }, gr);
    // tronco: camisa listrada
    const cid = 'cam' + Math.random().toString(36).slice(2), torso = 'M-66,-172 C-78,-250 -70,-322 -34,-350 L36,-350 C70,-330 78,-250 62,-172 Z';
    el('clipPath', { id: cid }, gr).appendChild(el('path', { d: torso }));
    el('path', { d: torso, fill: P }, gr);
    let d = ''; for (let i = -58; i < 70; i += 21) d += `M${i},-342 L${i - 6},-176 `; el('path', { d, stroke: paper, 'stroke-width': 6.5, 'clip-path': `url(#${cid})` }, gr);
    if (sp) el('path', { d: torso, fill: shirt }, sp);
    // pescoço e cabeça (cor do papel, contorno preto)
    el('path', { d: 'M-16,-352 L-14,-384 L26,-384 L28,-350 Z', fill: paper, stroke: P, 'stroke-width': 8 }, gr);
    const head = el('g', {}, gr);
    el('path', { d: 'M-50,-420 C-56,-470 -20,-500 24,-492 C52,-486 62,-466 62,-448 L84,-420 L64,-414 L68,-398 L54,-392 C56,-378 46,-366 28,-366 L-6,-366 C-34,-372 -48,-392 -50,-420 Z', fill: paper, stroke: P, 'stroke-width': 9, 'stroke-linejoin': 'round' }, head);
    const eye = el('g', {}, head);
    el('path', { d: 'M14,-440 Q32,-458 52,-440 Q32,-428 14,-440 Z', fill: paper, stroke: P, 'stroke-width': 6 }, eye); el('circle', { cx: 36, cy: -441, r: 6.5, fill: P }, eye);
    const lid = el('path', { d: 'M12,-440 Q32,-452 54,-440', fill: 'none', stroke: P, 'stroke-width': 8, 'stroke-linecap': 'round', opacity: 0 }, head);
    el('path', { d: 'M8,-462 Q30,-476 54,-462', fill: 'none', stroke: P, 'stroke-width': 9, 'stroke-linecap': 'round' }, head);
    el('path', { d: 'M40,-392 Q52,-388 60,-394', fill: 'none', stroke: P, 'stroke-width': 6, 'stroke-linecap': 'round' }, head);
    el('path', { d: 'M-22,-436 q-14,12 0,26', fill: 'none', stroke: P, 'stroke-width': 6, 'stroke-linecap': 'round' }, head);
    // chapéu de couro: copa + aba virada, com estrela e pontos entalhados
    el('path', { d: 'M-58,-470 C-50,-540 34,-548 56,-486 L98,-470 C84,-452 -66,-446 -92,-468 C-84,-474 -70,-474 -58,-470 Z', fill: P }, head);
    el('path', { d: 'M-2,-526 l5,12 13,1 -10,8 3,13 -11,-7 -11,7 3,-13 -10,-8 13,-1 Z', fill: paper }, head);
    el('path', { d: 'M-66,-464 L84,-470', stroke: paper, 'stroke-width': 5, 'stroke-dasharray': '2 14', 'stroke-linecap': 'round' }, head);
    // braço + livro
    const arm = el('g', {}, gr);
    el('path', Object.assign({ d: 'M30,-318 L72,-246 L142,-262' }, st(40)), arm);
    el('path', { d: 'M40,-312 L74,-256', stroke: paper, 'stroke-width': 4.5, 'stroke-linecap': 'round' }, arm);
    el('circle', { cx: 150, cy: -264, r: 19, fill: paper, stroke: P, 'stroke-width': 8 }, arm);
    const book = el('g', {}, gr);
    el('path', { d: 'M132,-250 L214,-286 L228,-352 L150,-318 Z', fill: paper, stroke: P, 'stroke-width': 8, 'stroke-linejoin': 'round' }, book);
    el('path', { d: 'M132,-250 L74,-300 L96,-362 L150,-318 Z', fill: paper, stroke: P, 'stroke-width': 8, 'stroke-linejoin': 'round' }, book);
    el('path', { d: 'M158,-300 L212,-324 M162,-284 L208,-304 M166,-268 L204,-285 M100,-340 L138,-310 M94,-322 L132,-292 M92,-304 L126,-276', stroke: P, 'stroke-width': 4.5, 'stroke-linecap': 'round' }, book);
    const page = el('path', { d: 'M132,-250 L150,-318 L170,-378 L146,-300 Z', fill: paper, stroke: P, 'stroke-width': 7, 'stroke-linejoin': 'round', opacity: 0 }, book);
    return { g: gr, head, eye, lid, page, arm,
      blink(on) { lid.setAttribute('opacity', on ? 1 : 0); eye.setAttribute('opacity', on ? 0 : 1); },
      nod(deg) { head.setAttribute('transform', `rotate(${deg} 6 -372)`); },
      turn(on) { page.setAttribute('opacity', on ? 1 : 0); } };
  };
  /* faixa de título: tarja preta com letras entalhadas */
  X.faixa = function (parent, text, cx, y, { size = 86, pad = 44, paper, font = 'Alfa Slab One', spacing = 3 } = {}) {
    const gr = el('g', {}, parent), tx = el('text', { x: cx, y: y + size * 0.36, 'text-anchor': 'middle', 'font-family': font, 'font-size': size, fill: paper, 'letter-spacing': spacing }, null); tx.textContent = text;
    gr.appendChild(tx); const w = tx.getComputedTextLength() + pad * 2, h = size * 1.42; gr.removeChild(tx);
    el('path', { d: `M${cx - w / 2 - 34},${y - h / 2} L${cx + w / 2 + 34},${y - h / 2} L${cx + w / 2 + 4},${y} L${cx + w / 2 + 34},${y + h / 2} L${cx - w / 2 - 34},${y + h / 2} L${cx - w / 2 - 4},${y} Z`, fill: P }, gr);
    gr.appendChild(tx); return { g: gr, text: tx, w, h };
  };
  /* legenda em palavras carimbadas uma a uma. words: [{w, t}] ; devolve update(t) */
  X.legenda = function (parent, words, cx, y, { size = 58, font = 'IM Fell English', italic = true, fill = P } = {}) {
    const tx = el('text', { x: cx, y, 'text-anchor': 'middle', 'font-family': font, 'font-size': size, 'font-style': italic ? 'italic' : 'normal', fill }, parent);
    const spans = words.map((w, i) => { const s = el('tspan', {}, tx); s.textContent = (i ? ' ' : '') + w.w; return s; });
    return { text: tx, update(t) { const ts = X.step(t); spans.forEach((s, i) => s.setAttribute('fill-opacity', ts >= words[i].t ? (ts - words[i].t < 1 / 12 - 1e-6 ? 0.45 : 1) : 0)); } };
  };
  g.Cordel = X;
})(window);
