/* nn-city.js: peças de cenário urbano do neon-noir (desenhadas em albedo "claro"; a luz vem do pipeline).
 * Convenção: funções (ctx, ...) desenham em coordenadas de mundo. Albedo = cor sem luz (médio-claro).
 */
(function (g) {
  const K = g.Kit, NN = g.NN, C = {};

  C.brickWall = function (ctx, x, y, w, h, { base = '#8a5f68', mortar = '#4b3340', seed = 1, bw = 62, bh = 24 } = {}) {
    const r = K.rng(seed); ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
    ctx.fillStyle = mortar; ctx.fillRect(x, y, w, h);
    for (let j = 0, yy = y; yy < y + h; j++, yy += bh) for (let xx = x - (j % 2 ? bw / 2 : 0); xx < x + w; xx += bw) {
      const v = r(); ctx.fillStyle = K.mix(base, v > 0.5 ? '#b98a86' : '#4d3344', Math.abs(v - 0.5) * 0.7);
      ctx.fillRect(xx + 1.5, yy + 1.5, bw - 3, bh - 3);
    }
    // sujeira: manchas verticais e fuligem no topo/base
    for (let i = 0; i < w / 90; i++) { const sx = x + r() * w, sw = 20 + r() * 60, sh = h * (0.2 + r() * 0.6), gr = ctx.createLinearGradient(0, y, 0, y + sh); gr.addColorStop(0, 'rgba(20,10,25,0.38)'); gr.addColorStop(1, 'rgba(20,10,25,0)'); ctx.fillStyle = gr; ctx.fillRect(sx, y, sw, sh); }
    const gb = ctx.createLinearGradient(0, y + h - 90, 0, y + h); gb.addColorStop(0, 'rgba(15,8,22,0)'); gb.addColorStop(1, 'rgba(15,8,22,0.5)'); ctx.fillStyle = gb; ctx.fillRect(x, y + h - 90, w, 90);
    ctx.restore();
  };
  C.plasterWall = function (ctx, x, y, w, h, { base = '#6c7691', seed = 2, panel = 0 } = {}) {
    const r = K.rng(seed); ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); ctx.fillStyle = base; ctx.fillRect(x, y, w, h);
    for (let i = 0; i < w * h / 2600; i++) { ctx.fillStyle = r() > 0.5 ? 'rgba(255,255,255,0.035)' : 'rgba(0,0,10,0.06)'; ctx.fillRect(x + r() * w, y + r() * h, 2 + r() * 26, 1 + r() * 3); }
    if (panel) { ctx.strokeStyle = 'rgba(10,8,25,0.4)'; ctx.lineWidth = 2; for (let xx = x + panel; xx < x + w; xx += panel) { ctx.beginPath(); ctx.moveTo(xx, y); ctx.lineTo(xx, y + h); ctx.stroke(); } for (let yy = y + panel * 0.6; yy < y + h; yy += panel * 0.6) { ctx.beginPath(); ctx.moveTo(x, yy); ctx.lineTo(x + w, yy); ctx.stroke(); } }
    for (let i = 0; i < w / 70; i++) { const sx = x + r() * w, sw = 10 + r() * 50, sh = h * (0.15 + r() * 0.7), gr = ctx.createLinearGradient(0, y, 0, y + sh); gr.addColorStop(0, 'rgba(10,8,25,0.35)'); gr.addColorStop(1, 'rgba(10,8,25,0)'); ctx.fillStyle = gr; ctx.fillRect(sx, y, sw, sh); }
    ctx.restore();
  };
  /* sombra projetada suave (AO pintado) abaixo de uma aresta */
  C.dropShade = function (ctx, x, y, w, h, a = 0.55) { const gr = ctx.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, `rgba(8,4,16,${a})`); gr.addColorStop(1, 'rgba(8,4,16,0)'); ctx.fillStyle = gr; ctx.fillRect(x, y, w, h); };
  C.ledge = function (ctx, x, y, w, h = 16, color = '#9c8a94') { ctx.fillStyle = color; ctx.fillRect(x, y, w, h); ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillRect(x, y, w, 3); C.dropShade(ctx, x, y + h, w, 34, 0.6); };
  /* janela: moldura no albedo; se acesa, conteúdo vai no emissivo */
  C.window = function (alb, em, x, y, w, h, { lit = null, blinds = false, frame = '#3a3040', seed = 1, figure = false } = {}) {
    const r = K.rng(seed);
    alb.fillStyle = frame; alb.fillRect(x - 8, y - 8, w + 16, h + 16); alb.fillStyle = '#b7a9b4'; alb.fillRect(x - 12, y + h + 6, w + 24, 10);
    C.dropShade(alb, x - 12, y + h + 16, w + 24, 26, 0.5);
    alb.fillStyle = '#141024'; alb.fillRect(x, y, w, h);
    if (!lit) { const gr = alb.createLinearGradient(x, y, x + w, y + h); gr.addColorStop(0, 'rgba(120,110,200,0.28)'); gr.addColorStop(0.5, 'rgba(120,110,200,0.05)'); gr.addColorStop(1, 'rgba(120,110,200,0.16)'); alb.fillStyle = gr; alb.fillRect(x, y, w, h); }
    else {
      const gr = em.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, K.mix(lit, '#ffffff', 0.25)); gr.addColorStop(1, K.mix(lit, '#000000', 0.45)); em.fillStyle = gr; em.fillRect(x, y, w, h);
      if (figure) { em.fillStyle = '#000'; em.beginPath(); em.ellipse(x + w * 0.62, y + h * 0.5, w * 0.1, h * 0.11, 0, 0, 7); em.fill(); em.beginPath(); em.moveTo(x + w * 0.42, y + h); em.quadraticCurveTo(x + w * 0.62, y + h * 0.46, x + w * 0.84, y + h); em.fill(); }
      if (blinds) { em.fillStyle = 'rgba(0,0,0,0.82)'; for (let yy = y; yy < y + h; yy += 13) em.fillRect(x, yy, w, 7.5); }
      else { em.fillStyle = 'rgba(0,0,0,0.5)'; em.fillRect(x, y, w * (0.12 + r() * 0.2), h); em.fillRect(x + w * (0.8 - r() * 0.1), y, w, h); }
    }
    for (const c of lit ? [alb, em] : [alb]) { c.fillStyle = c === em ? '#000' : frame; c.fillRect(x + w / 2 - 3, y, 6, h); c.fillRect(x, y + h * 0.45, w, 5); }
  };
  C.fireEscape = function (ctx, x, y, w, floors, fh, color = '#3d3345') {
    ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineCap = 'butt';
    for (let i = 0; i < floors; i++) {
      const py = y + i * fh; ctx.fillRect(x - 10, py, w + 20, 9); C.dropShade(ctx, x - 10, py + 9, w + 20, 40, 0.5);
      ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x - 10, py - 70); ctx.lineTo(x + w + 10, py - 70); ctx.stroke();
      ctx.lineWidth = 3; for (let xx = x - 8; xx <= x + w + 8; xx += 17) { ctx.beginPath(); ctx.moveTo(xx, py - 70); ctx.lineTo(xx, py); ctx.stroke(); }
      if (i < floors - 1) { ctx.lineWidth = 5; const dir = i % 2 ? -1 : 1, x0 = dir > 0 ? x + 20 : x + w - 20, x1 = dir > 0 ? x + w - 30 : x + 30; ctx.beginPath(); ctx.moveTo(x0, py + 9); ctx.lineTo(x1, py + fh); ctx.moveTo(x0, py - 50); ctx.lineTo(x1, py + fh - 60); ctx.stroke(); ctx.lineWidth = 2.5; for (let k = 1; k < 9; k++) { const xx = K.lerp(x0, x1, k / 9), yy = K.lerp(py + 9, py + fh, k / 9); ctx.beginPath(); ctx.moveTo(xx - 12, yy); ctx.lineTo(xx + 12, yy); ctx.stroke(); } }
    }
    ctx.restore();
  };
  C.pipe = function (ctx, x, y0, y1, w = 12, color = '#5a4e60') { ctx.fillStyle = color; ctx.fillRect(x, y0, w, y1 - y0); ctx.fillStyle = 'rgba(255,255,255,0.14)'; ctx.fillRect(x + 2, y0, 3, y1 - y0); ctx.fillStyle = '#2c2434'; for (let y = y0 + 60; y < y1; y += 150) ctx.fillRect(x - 3, y, w + 6, 8); ctx.fillStyle = 'rgba(8,4,16,0.35)'; ctx.fillRect(x + w, y0, 9, y1 - y0); };
  C.acUnit = function (ctx, x, y, w = 92, h = 58) { ctx.fillStyle = '#7d7888'; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#34303f'; for (let yy = y + 8; yy < y + h - 6; yy += 7) ctx.fillRect(x + 8, yy, w - 16, 3); ctx.fillStyle = '#4a4353'; ctx.fillRect(x - 4, y + h, w + 8, 7); C.dropShade(ctx, x - 4, y + h + 7, w + 8, 46, 0.6); };
  C.awning = function (ctx, x, y, w, h, c1 = '#8c3550', c2 = '#c9b9c0', stripes = 7) {
    const d = 26; ctx.save();
    for (let i = 0; i < stripes; i++) { ctx.fillStyle = i % 2 ? c2 : c1; const x0 = x + (w / stripes) * i, x1 = x0 + w / stripes; ctx.beginPath(); ctx.moveTo(x0 + (i === 0 ? 0 : 0), y); ctx.lineTo(x1, y); ctx.lineTo(x1 + (x1 - x - w / 2) / w * d, y + h); ctx.lineTo(x0 + (x0 - x - w / 2) / w * d, y + h); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.arc((x0 + x1) / 2 + ((x0 + x1) / 2 - x - w / 2) / w * d, y + h, (w / stripes) * 0.52, 0, Math.PI); ctx.fill(); }
    const gr = ctx.createLinearGradient(0, y, 0, y + h + 20); gr.addColorStop(0, 'rgba(255,255,255,0.12)'); gr.addColorStop(1, 'rgba(8,4,16,0.4)'); ctx.fillStyle = gr; ctx.fillRect(x - 20, y, w + 40, h + 22);
    ctx.restore(); C.dropShade(ctx, x - 14, y + h + 16, w + 28, 120, 0.62);
  };
  C.door = function (alb, em, x, y, w, h, { color = '#4c2b3c', glass = null, frame = '#2b2130' } = {}) {
    alb.fillStyle = frame; alb.fillRect(x - 12, y - 12, w + 24, h + 12); alb.fillStyle = color; alb.fillRect(x, y, w, h);
    alb.fillStyle = 'rgba(0,0,0,0.25)'; alb.fillRect(x + 12, y + h * 0.55, w - 24, h * 0.38); alb.strokeStyle = 'rgba(255,255,255,0.1)'; alb.lineWidth = 2; alb.strokeRect(x + 12, y + h * 0.55, w - 24, h * 0.38);
    const gx = x + 14, gy = y + 16, gw = w - 28, gh = h * 0.44;
    alb.fillStyle = '#141024'; alb.fillRect(gx, gy, gw, gh);
    if (glass) { const gr = em.createLinearGradient(0, gy, 0, gy + gh); gr.addColorStop(0, K.mix(glass, '#fff', 0.2)); gr.addColorStop(1, K.mix(glass, '#000', 0.55)); em.fillStyle = gr; em.fillRect(gx, gy, gw, gh); em.fillStyle = '#000'; em.fillRect(gx + gw / 2 - 2, gy, 4, gh); }
    alb.fillStyle = '#d9c9a8'; alb.fillRect(x + w - 26, y + h * 0.5, 9, 30);
    alb.fillStyle = '#a79aa6'; alb.fillRect(x - 22, y + h - 14, w + 44, 14);
  };
  /* caixa de letreiro vertical (blade) presa na parede */
  C.signBox = function (ctx, x, y, w, h, color = '#241c2e') {
    ctx.fillStyle = '#3d3345'; ctx.fillRect(x - 46, y + 40, 46, 8); ctx.fillRect(x - 46, y + h - 48, 46, 8);
    ctx.fillStyle = color; ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.roundRect(x + 4, y + 4, w - 8, h - 8, 8); ctx.stroke();
    ctx.fillStyle = 'rgba(8,4,16,0.4)'; ctx.fillRect(x + w, y + 14, 16, h - 6);
  };
  C.lampPost = function (ctx, x, yBase, hgt, armDir = 1, color = '#2a2434') {
    ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineCap = 'round';
    ctx.fillRect(x - 9, yBase - 70, 18, 70); ctx.fillRect(x - 5, yBase - hgt, 10, hgt);
    ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(x, yBase - hgt + 4); ctx.quadraticCurveTo(x + armDir * 10, yBase - hgt - 40, x + armDir * 96, yBase - hgt - 34); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + armDir * 70, yBase - hgt - 40); ctx.lineTo(x + armDir * 132, yBase - hgt - 40); ctx.lineTo(x + armDir * 124, yBase - hgt - 24); ctx.lineTo(x + armDir * 78, yBase - hgt - 24); ctx.closePath(); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fillRect(x - 5, yBase - hgt, 3, hgt); ctx.restore();
    return { lx: x + armDir * 101, ly: yBase - hgt - 22 };
  };
  C.cables = function (ctx, list, color = '#07050f', w = 3) { ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = w; for (const [x0, y0, x1, y1, sag] of list) { ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo((x0 + x1) / 2, (y0 + y1) / 2 + sag * 2, x1, y1); ctx.stroke(); } ctx.restore(); };
  C.dumpster = function (ctx, x, y, w = 190, h = 120) { ctx.fillStyle = '#3f5a55'; ctx.fillRect(x, y - h, w, h - 10); ctx.fillStyle = '#2c403d'; ctx.fillRect(x - 6, y - h - 12, w + 12, 16); ctx.fillStyle = 'rgba(0,0,0,0.3)'; for (let i = 1; i < 4; i++) ctx.fillRect(x + i * w / 4, y - h + 8, 5, h - 26); ctx.fillStyle = '#17141d'; ctx.fillRect(x + 14, y - 12, 22, 12); ctx.fillRect(x + w - 36, y - 12, 22, 12); };
  /* horizonte de prédios distante (silhuetas + janelinhas) */
  C.skyline = function (ctx, x0, x1, yBase, { seed = 5, minH = 120, maxH = 420, color = '#1b1238', win = ['#ffb04a', '#19e6ff', '#ff2e88'], winP = 0.16, minW = 60, maxW = 170, emis = null, cell = [5, 7] } = {}) {
    const r = K.rng(seed);
    for (let x = x0; x < x1;) {
      const w = r.range(minW, maxW), h = r.range(minH, maxH), top = yBase - h; ctx.fillStyle = color; ctx.fillRect(x, top, w + 1, h + 400);
      if (r.chance(0.3)) ctx.fillRect(x + w * 0.3, top - r.range(14, 50), w * 0.4, 60);
      if (r.chance(0.25)) ctx.fillRect(x + w * r.range(0.2, 0.8), top - r.range(40, 110), 3, 120);
      const cw = cell[0] + r.int(0, 2), ch = cell[1] + r.int(0, 3), gx = cw + r.pick([5, 7, 9]), gy = ch + r.pick([7, 10, 13]), cw_ = win.length;
      for (let yy = top + 14; yy < yBase + 200; yy += gy) for (let xx = x + 8; xx < x + w - cw - 4; xx += gx) if (r.chance(winP)) { (emis || ctx).fillStyle = K.rgba(win[Math.floor(r() * r() * cw_)], r.range(0.35, 0.95)); (emis || ctx).fillRect(xx, yy, cw, ch); }
      x += w + (r.chance(0.2) ? r.range(6, 40) : 0);
    }
  };
  /* chão: calçada + meio-fio + asfalto; devolve também a máscara de "molhado" */
  C.ground = function (alb, wet, x0, x1, yWall, ySide, H, seed = 3) {
    const r = K.rng(seed), w = x1 - x0;
    alb.fillStyle = '#8f8a9c'; alb.fillRect(x0, yWall, w, ySide - yWall);
    alb.strokeStyle = 'rgba(20,14,34,0.5)'; alb.lineWidth = 2; for (let x = x0; x < x1; x += 118) { alb.beginPath(); alb.moveTo(x, yWall); alb.lineTo(x - 14, ySide); alb.stroke(); }
    C.dropShade(alb, x0, yWall, w, 26, 0.6);
    alb.fillStyle = '#b3aec0'; alb.fillRect(x0, ySide, w, 7); alb.fillStyle = '#4d485c'; alb.fillRect(x0, ySide + 7, w, 13);
    const gr = alb.createLinearGradient(0, ySide + 20, 0, H); gr.addColorStop(0, '#5c5870'); gr.addColorStop(1, '#6e6a84'); alb.fillStyle = gr; alb.fillRect(x0, ySide + 20, w, H - ySide - 20);
    for (let i = 0; i < w * 1.6; i++) { const px = x0 + r() * w, py = ySide + 22 + r() * (H - ySide - 22); alb.fillStyle = r() > 0.5 ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,10,0.16)'; alb.fillRect(px, py, 2 + r() * 5, 1.5); }
    // máscara de molhado: calçada pouco reflexiva, asfalto mais, poças muito
    wet.fillStyle = 'rgba(255,255,255,0.3)'; wet.fillRect(x0, yWall, w, ySide - yWall + 20);
    const gw = wet.createLinearGradient(0, ySide + 20, 0, H); gw.addColorStop(0, 'rgba(255,255,255,0.62)'); gw.addColorStop(1, 'rgba(255,255,255,0.4)'); wet.fillStyle = gw; wet.fillRect(x0, ySide + 20, w, H - ySide - 20);
    // poças: manchas irregulares e de borda macia (várias elipses achatadas por poça)
    wet.save(); wet.filter = 'blur(7px)'; wet.fillStyle = 'rgba(255,255,255,0.9)';
    for (let i = 0; i < w / 260; i++) { const px = x0 + r() * w, py = ySide + 50 + r() * (H - ySide - 70), rx = 120 + r() * 260; wet.beginPath();
      for (let k = 0; k < 6; k++) { const ox = (r() - 0.5) * rx * 1.5, oy = (r() - 0.5) * 20; wet.ellipse(px + ox, py + oy, rx * (0.25 + r() * 0.5), 5 + r() * 11, 0, 0, 7); wet.closePath(); } wet.fill(); }
    wet.restore();
    // textura horizontal fina no reflexo (rugosidade do asfalto)
    wet.globalCompositeOperation = 'destination-out'; for (let i = 0; i < (H - ySide) * 3; i++) { wet.fillStyle = `rgba(0,0,0,${0.1 + r() * 0.35})`; wet.fillRect(x0 + r() * w, ySide + 20 + r() * (H - ySide - 20), 30 + r() * 240, 1.2); } wet.globalCompositeOperation = 'source-over';
  };
  C.manhole = function (ctx, x, y, rx = 62) { ctx.fillStyle = '#34303f'; ctx.beginPath(); ctx.ellipse(x, y, rx, rx * 0.2, 0, 0, 7); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.ellipse(x, y, rx * 0.8, rx * 0.15, 0, 0, 7); ctx.stroke(); };

  /* chuva: três profundidades; devolve função (ctx, t, {yb}) */
  C.rain = function ({ n = 520, wind = 0.16, seed = 11, W = K.W, H = K.H } = {}) {
    const r = K.rng(seed), drops = []; for (let i = 0; i < n; i++) { const d = r(); drops.push({ x: r() * (W + 500) - 250, y: r() * H, d, sp: 900 + d * 1700 + r() * 200, len: 18 + d * 70, a: 0.16 + d * 0.5, w: 0.8 + d * 1.5 }); }
    const sp = []; for (let i = 0; i < 150; i++) sp.push({ x: r() * W, yk: r(), ph: r() * 10, per: 0.5 + r() * 0.9 });
    return function (ctx, t, { yb }) {
      ctx.lineCap = 'round'; ctx.strokeStyle = '#fff';
      for (const d of drops) { const y = (d.y + d.sp * t) % (H + 200) - 100, x = d.x - wind * (d.sp * t % (H + 200)) + 140; ctx.globalAlpha = d.a; ctx.lineWidth = d.w; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + wind * d.len, y - d.len); ctx.stroke(); }
      for (const s of sp) { const k = ((t + s.ph) % s.per) / 0.28; if (k > 1) continue; const y = yb + 8 + s.yk * (H - yb - 8), sc = 0.5 + s.yk; ctx.globalAlpha = (1 - k) * 0.8; ctx.lineWidth = 1.3; ctx.beginPath(); ctx.ellipse(s.x, y, (4 + 16 * k) * sc, (1.2 + 4 * k) * sc, 0, 0, 7); ctx.stroke();
        if (k < 0.5) { ctx.beginPath(); ctx.moveTo(s.x, y); ctx.lineTo(s.x - 3, y - 9 * (1 - k) * sc * 2); ctx.moveTo(s.x, y); ctx.lineTo(s.x + 4, y - 7 * (1 - k) * sc * 2); ctx.stroke(); } }
      ctx.globalAlpha = 1;
    };
  };
  /* vapor: bolhas suaves subindo de (x,y) */
  C.steam = function (ctx, t, x, y, { color = '#8a7ab8', n = 16, rise = 300, spread = 150, seed = 4, a = 0.1, size = 1 } = {}) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) { const ph = K.hash(i * 3.3 + seed), k = (t * (0.1 + 0.07 * K.hash(i + seed * 2)) + ph) % 1, px = x + (K.hash(i * 7.1 + seed) - 0.5) * spread * (0.3 + k) + Math.sin(t * 0.6 + i) * 18 * k, py = y - k * rise, r = (40 + 130 * k) * size, al = a * Math.sin(Math.PI * Math.min(1, k * 1.2)) * (1 - k * 0.5);
      const gr = ctx.createRadialGradient(px, py, 0, px, py, r); gr.addColorStop(0, K.rgba(color, al)); gr.addColorStop(1, K.rgba(color, 0)); ctx.fillStyle = gr; ctx.fillRect(px - r, py - r, r * 2, r * 2); }
    ctx.restore();
  };
  /* cone de luz volumétrico */
  C.cone = function (ctx, x, y, { color = '#ffab40', len = 640, spread = 250, a = 0.2 } = {}) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; const gr = ctx.createLinearGradient(0, y, 0, y + len); gr.addColorStop(0, K.rgba(color, a)); gr.addColorStop(0.6, K.rgba(color, a * 0.35)); gr.addColorStop(1, K.rgba(color, 0));
    ctx.fillStyle = gr; ctx.filter = 'blur(14px)'; ctx.beginPath(); ctx.moveTo(x - 22, y); ctx.lineTo(x + 22, y); ctx.lineTo(x + spread, y + len); ctx.lineTo(x - spread, y + len); ctx.closePath(); ctx.fill(); ctx.restore();
  };
  NN.City = C;
})(window);
