/* sumi.js: motor do estilo "sumi" (nanquim e aguada sobre papel de arroz). Canvas 2D.
 * Cada marca é pré-renderizada uma vez (pincelada com cerdas, aguada, montanha) e depois revelada no tempo:
 * a pincelada se revela ao longo do próprio traçado; a aguada "abre" em alfa. Tudo determinístico (semente).
 * Depende de shared/web/kit.js. Expõe window.Sumi.
 */
(function (g) {
  const K = g.Kit, S = {};
  S.PAPEL = '#f0eadb'; S.TINTA = '#191715'; S.SELO = '#c0281f';
  const ink = (a) => K.rgba(S.TINTA, a);
  /* spline Catmull-Rom amostrada: pts [[x,y],...] -> n amostras {x,y,nx,ny,u} */
  function sample(pts, n) {
    const P = [pts[0], ...pts, pts[pts.length - 1]], out = [], segs = pts.length - 1;
    for (let i = 0; i < n; i++) { const u = i / (n - 1), f = u * segs, s = Math.min(segs - 1, Math.floor(f)), t = f - s, [p0, p1, p2, p3] = [P[s], P[s + 1], P[s + 2], P[s + 3]];
      const cr = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
      out.push({ x: cr(p0[0], p1[0], p2[0], p3[0]), y: cr(p0[1], p1[1], p2[1], p3[1]), u }); }
    for (let i = 0; i < n; i++) { const a = out[Math.max(0, i - 1)], b = out[Math.min(n - 1, i + 1)], dx = b.x - a.x, dy = b.y - a.y, l = Math.hypot(dx, dy) || 1; out[i].nx = -dy / l; out[i].ny = dx / l; }
    return out;
  }
  /* perfil de pressão: entra fino, incha, sai em ponta. tin/tout = fração de entrada/saída */
  const pressure = (u, tin, tout) => Math.min(1, K.smooth(u / tin) * 0.85 + 0.15) * (u > 1 - tout ? Math.pow((1 - u) / tout, 0.7) : 1);

  /* pincelada: {pts, w, tone, dry (0 = encharcada, 1 = pincel seco), tin, tout, seed, bristles}
   * devolve {canvas, ox, oy, draw(ctx, k)} ; k = 0..1 revela ao longo do traço */
  S.stroke = function ({ pts, w = 40, tone = 0.9, dry = 0.35, tin = 0.12, tout = 0.3, seed = 1, bristles = 0, n = 0, wfn = null }) {
    let len = 0; for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    n = n || Math.max(24, Math.round(len / 5)); const sm = sample(pts, n), r = K.rng(seed), nb = bristles || Math.max(8, Math.round(w / 2.4));
    sm.forEach((p) => { p.w = w * (wfn ? wfn(p.u) : pressure(p.u, tin, tout)); });
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (const p of sm) { x0 = Math.min(x0, p.x - w); y0 = Math.min(y0, p.y - w); x1 = Math.max(x1, p.x + w); y1 = Math.max(y1, p.y + w); }
    x0 = Math.floor(x0); y0 = Math.floor(y0); const cw = Math.ceil(x1 - x0), ch = Math.ceil(y1 - y0), c = K.canvas(cw, ch), x = c.getContext('2d'); x.translate(-x0, -y0);
    const poly = (c2, a, b, grow = 0) => { c2.beginPath(); for (let i = a; i <= b; i++) { const p = sm[i], h = p.w / 2 + grow; i === a ? c2.moveTo(p.x + p.nx * h, p.y + p.ny * h) : c2.lineTo(p.x + p.nx * h, p.y + p.ny * h); } for (let i = b; i >= a; i--) { const p = sm[i], h = p.w / 2 + grow; c2.lineTo(p.x - p.nx * h, p.y - p.ny * h); } c2.closePath(); };
    // miolo molhado (some conforme o pincel seca)
    const core = tone * (1 - dry * 0.75) * 0.62; if (core > 0.02) { const steps = 6; for (let s = 0; s < steps; s++) { const a = Math.floor(n * s / steps), b = Math.min(n - 1, Math.floor(n * (s + 1) / steps) + 1); x.fillStyle = ink(core * (1 - dry * 0.8 * (s / steps))); poly(x, a, b, -0.5); x.fill(); } }
    // cerdas: cada uma é uma sequência de trechos contínuos (o pincel falha onde o ruído cai abaixo do limiar)
    x.lineCap = 'butt'; x.lineJoin = 'round';
    for (let j = 0; j < nb; j++) { const o = (j + 0.5) / nb - 0.5 + (r() - 0.5) / nb, load = 0.4 + 0.6 * r(), edge = Math.pow(Math.abs(o) * 2, 3) * 0.4, ph = r() * 100; let run = [];
      const flush = () => { if (run.length > 1) { let wsum = 0; for (const p of run) wsum += p.w; x.strokeStyle = ink(tone * load * 0.78); x.lineWidth = Math.max(0.8, wsum / run.length / nb * 1.55); x.beginPath(); run.forEach((p, i) => { const px = p.x + p.nx * p.w * o, py = p.y + p.ny * p.w * o; i ? x.lineTo(px, py) : x.moveTo(px, py); }); x.stroke(); } run = run.length ? [run[run.length - 1]] : []; };
      for (let i = 0; i < n; i++) { const p = sm[i], thr = dry * (0.12 + 0.88 * Math.pow(p.u, 1.3)) + edge - 0.1, gn = K.noise2(j * 1.7 + ph, p.u * len / 60);
        if (gn < thr) { flush(); run = []; continue; } run.push(p); if (run.length >= 7) flush(); }
      flush(); }
    return { canvas: c, ox: x0, oy: y0, len, sm,
      draw(ctx, k = 1, alpha = 1) { if (k <= 0) return; ctx.save(); ctx.globalAlpha *= alpha; if (k < 1) { const b = Math.max(1, Math.min(n - 1, Math.round(k * (n - 1)))); poly(ctx, 0, b, w * 0.6); ctx.clip(); } ctx.drawImage(c, x0, y0); ctx.restore(); } };
  };
  /* aguada: mancha diluída com borda mais escura (linha de maré) e granulação. rx, ry em px */
  S.wash = function ({ rx = 200, ry = 120, tone = 0.4, seed = 2, edge = 0.5, rough = 0.35 }) {
    const pad = 20, w = Math.ceil(rx * 2 + pad * 2), h = Math.ceil(ry * 2 + pad * 2), sc = 0.5, c = K.canvas(Math.ceil(w * sc), Math.ceil(h * sc)), x = c.getContext('2d'), id = x.createImageData(c.width, c.height), d = id.data, [ir, ig, ib] = K.hex(S.TINTA);
    for (let py = 0; py < c.height; py++) for (let px = 0; px < c.width; px++) { const X = (px / sc - w / 2) / rx, Y = (py / sc - h / 2) / ry, a = Math.atan2(Y, X), rr = Math.hypot(X, Y) / (1 + rough * (K.fbm(Math.cos(a) * 1.6 + seed, Math.sin(a) * 1.6 + seed * 2, 3) - 0.5) * 2);
      let v = rr < 1 ? 1 : 0; if (rr > 0.94 && rr < 1) v = (1 - rr) / 0.06; const body = 0.5 + 0.5 * K.fbm(px / 26 + seed * 3, py / 26, 4), tide = Math.exp(-Math.pow((rr - 0.9) / 0.07, 2)) * edge, gr = 0.85 + 0.3 * K.hash2(px + seed, py);
      const al = K.clamp(v * tone * (body * 0.75 + tide) * gr), i = (py * c.width + px) * 4; d[i] = ir; d[i + 1] = ig; d[i + 2] = ib; d[i + 3] = al * 255; }
    x.putImageData(id, 0, 0);
    return { canvas: c, w, h, draw(ctx, cx, cy, k = 1, alpha = 1) { if (k <= 0) return; const e = K.ease.outCubic(K.clamp(k)), s = 0.72 + 0.28 * e; ctx.save(); ctx.globalAlpha *= alpha * Math.min(1, k * 1.6); ctx.imageSmoothingEnabled = true; ctx.drawImage(c, cx - w * s / 2, cy - h * s / 2, w * s, h * s); ctx.restore(); } };
  };
  /* cordilheira em aguada: crista por ruído, tinta forte na crista esmaecendo para baixo (névoa) */
  S.mountain = function ({ W = K.W, y = 400, amp = 180, tone = 0.5, fade = 260, seed = 3, freq = 1, peaks = [] }) {
    const top = Math.floor(y - amp * 1.45 - 20), h = Math.ceil(amp * 1.45 + fade + 40), sc = 0.5, c = K.canvas(Math.ceil(W * sc), Math.ceil(h * sc)), x = c.getContext('2d'), id = x.createImageData(c.width, c.height), d = id.data, [ir, ig, ib] = K.hex(S.TINTA), ridge = new Float32Array(c.width);
    for (let px = 0; px < c.width; px++) { const X = px / sc; let v = K.fbm(X / 420 * freq + seed, seed * 1.3, 4); v = Math.pow(v, 1.5) * 1.9; for (const [pxk, ph, pw] of peaks) v += ph * Math.exp(-Math.pow((X - pxk) / pw, 2)); ridge[px] = y - amp * Math.min(1.4, Math.max(0, v)); }
    for (let px = 0; px < c.width; px++) for (let py = 0; py < c.height; py++) { const Y = py / sc + top, dd = Y - ridge[px]; if (dd < 0) continue; const f = Math.exp(-dd / fade * 3.2), tex = 0.4 + 0.6 * K.fbm(px / 30 + seed, py / 70 + seed, 4) * (0.7 + 0.6 * K.fbm(px / 7 + seed, py / 90, 2)), rim = Math.exp(-dd / 4) * 0.55 * (0.4 + 1.2 * K.noise1(px / 9 + seed)), gr = 0.86 + 0.28 * K.hash2(px, py + seed);
      const al = K.clamp(tone * (f * tex + rim) * gr) * Math.min(1, dd / 2), i = (py * c.width + px) * 4; d[i] = ir; d[i + 1] = ig; d[i + 2] = ib; d[i + 3] = al * 255; }
    x.putImageData(id, 0, 0);
    return { canvas: c, top, h, ridge: (X) => ridge[Math.max(0, Math.min(c.width - 1, Math.round(X * sc)))],
      /* k revela da esquerda para a direita com borda macia */
      draw(ctx, k = 1, alpha = 1) { if (k <= 0) return; ctx.save(); ctx.globalAlpha *= alpha; if (k < 1) { const tmp = S._tmp || (S._tmp = K.canvas(K.W, K.H)), tx = tmp.getContext('2d'); tx.setTransform(1, 0, 0, 1, 0, 0); tx.globalCompositeOperation = 'source-over'; tx.clearRect(0, 0, tmp.width, tmp.height); tx.drawImage(c, 0, top, W, h); const xe = k * (W + 500) - 250, gr = tx.createLinearGradient(xe - 250, 0, xe + 250, 0); gr.addColorStop(0, '#000'); gr.addColorStop(1, 'rgba(0,0,0,0)'); tx.globalCompositeOperation = 'destination-in'; tx.fillStyle = gr; tx.fillRect(0, 0, tmp.width, tmp.height); ctx.drawImage(tmp, 0, 0); } else ctx.drawImage(c, 0, top, W, h); ctx.restore(); } };
  };
  /* papel de arroz: fibras longas, manchas, vinheta */
  S.paper = function (W = K.W, H = K.H, seed = 5) { const c = K.canvas(W, H), x = c.getContext('2d'), r = K.rng(seed); x.fillStyle = S.PAPEL; x.fillRect(0, 0, W, H);
    const n = K.canvas(W / 4, H / 4), nx = n.getContext('2d'), id = nx.createImageData(n.width, n.height), d = id.data; for (let py = 0; py < n.height; py++) for (let px = 0; px < n.width; px++) { const v = K.fbm(px / 70, py / 70, 4), i = (py * n.width + px) * 4; d[i] = 130; d[i + 1] = 105; d[i + 2] = 60; d[i + 3] = Math.max(0, v - 0.42) * 60; } nx.putImageData(id, 0, 0); x.drawImage(n, 0, 0, W, H);
    for (let i = 0; i < 1500; i++) { x.strokeStyle = r() > 0.5 ? 'rgba(255,255,255,0.16)' : 'rgba(110,90,50,0.1)'; x.lineWidth = 0.8 + r(); const px = r() * W, py = r() * H, a = r() * 6.28, l = 12 + r() * 60; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + Math.cos(a) * l * 0.5 + (r() - 0.5) * 14, py + Math.sin(a) * l * 0.5 + (r() - 0.5) * 14, px + Math.cos(a) * l, py + Math.sin(a) * l); x.stroke(); }
    const v = x.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, W * 0.75); v.addColorStop(0, 'rgba(80,60,30,0)'); v.addColorStop(1, 'rgba(80,60,30,0.2)'); x.fillStyle = v; x.fillRect(0, 0, W, H); return c; };
  /* névoa: borrões da cor do papel passando devagar */
  S.mist = function (ctx, t, list) { for (const m of list) { const x = m.x + Math.sin(t * 0.2 + m.ph) * 30 + t * (m.v || 6), gr = ctx.createRadialGradient(x, m.y, 0, x, m.y, m.r); gr.addColorStop(0, K.rgba(S.PAPEL, m.a)); gr.addColorStop(1, K.rgba(S.PAPEL, 0)); ctx.save(); ctx.translate(x, m.y); ctx.scale(1, m.sy || 0.3); ctx.translate(-x, -m.y); ctx.fillStyle = gr; ctx.fillRect(x - m.r, m.y - m.r, m.r * 2, m.r * 2); ctx.restore(); } };
  /* tufo de agulhas de pinheiro: leque de riscos saindo de (x,y) na direção ang */
  S.needles = function ({ x, y, ang = -Math.PI / 2, spread = 1.5, n = 13, len = 60, seed = 1, tone = 0.9 }) { const r = K.rng(seed), list = []; for (let i = 0; i < n; i++) { const a = ang + (i / (n - 1) - 0.5) * spread + (r() - 0.5) * 0.12, l = len * (0.7 + r() * 0.5); list.push(S.stroke({ pts: [[x, y], [x + Math.cos(a) * l * 0.5, y + Math.sin(a) * l * 0.5], [x + Math.cos(a) * l, y + Math.sin(a) * l]], w: 4.2 + r() * 2, tone, dry: 0.15, tin: 0.05, tout: 0.75, seed: seed * 31 + i, n: 10, bristles: 3 })); } return { draw(ctx, k = 1) { list.forEach((s, i) => s.draw(ctx, K.clamp(k * 1.6 - i / n * 0.6))); } }; };
  /* pássaro: dois riscos em "v" que batem asa */
  S.bird = function (ctx, x, y, s, flap, alpha = 1) { ctx.save(); ctx.translate(x, y); ctx.strokeStyle = ink(0.85 * alpha); ctx.lineWidth = 2.6 * s; ctx.lineCap = 'round'; const a = 0.25 + 0.5 * flap; ctx.beginPath(); ctx.moveTo(-16 * s, -16 * s * a); ctx.quadraticCurveTo(-7 * s, -6 * s * a - 4 * s, 0, 0); ctx.quadraticCurveTo(7 * s, -6 * s * a - 4 * s, 16 * s, -14 * s * a); ctx.stroke(); ctx.restore(); };
  /* selo vermelho (hanko) com iniciais; k = batida 0..1 */
  S.seal = function (ctx, x, y, size, text, k = 1, font = '700 {s}px "Shippori Mincho"') { if (k <= 0) return; const e = K.ease.outExpo(K.clamp(k)), sc = 1 + (1 - e) * 0.7; ctx.save(); ctx.translate(x, y); ctx.rotate(-0.04); ctx.scale(sc, sc); ctx.globalAlpha = Math.min(1, k * 3) * 0.92; ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = S.SELO; ctx.beginPath(); ctx.roundRect(-size / 2, -size / 2, size, size, size * 0.12); ctx.fill();
    ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = S.PAPEL; ctx.font = font.replace('{s}', Math.round(size * 0.52)); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 0, size * 0.03); ctx.strokeStyle = S.PAPEL; ctx.lineWidth = size * 0.035; ctx.strokeRect(-size * 0.4, -size * 0.4, size * 0.8, size * 0.8);
    const r = K.rng(9); ctx.fillStyle = S.PAPEL; for (let i = 0; i < 46; i++) ctx.fillRect((r() - 0.5) * size, (r() - 0.5) * size, 1 + r() * 4, 1 + r() * 2); ctx.restore(); };
  /* texto que "assenta" como tinta: entra borrado e claro, firma. */
  S.text = function (ctx, text, x, y, k, { font = '500 96px "Shippori Mincho"', track = 0, align = 'left', tone = 0.92 } = {}) { if (k <= 0) return; const e = K.ease.outCubic(K.clamp(k)); ctx.save(); ctx.font = font; ctx.letterSpacing = track + 'px'; ctx.textAlign = align; ctx.fillStyle = ink(tone * e); if (e < 1) ctx.filter = `blur(${(1 - e) * 7}px)`; ctx.fillText(text, x, y); ctx.restore(); };
  g.Sumi = S;
})(window);
