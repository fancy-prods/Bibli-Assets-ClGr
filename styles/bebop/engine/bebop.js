/* bebop.js: motor do estilo "bebop" (capa de disco de jazz dos anos 50/60 em movimento).
 * Canvas 2D. Simula impressão em chapas: cada cor é uma chapa em tons de cinza (alfa), composta sobre o
 * papel em multiply, com registro levemente fora e tinta irregular. Sobreposição de chapas = sobreimpressão.
 * Depende de shared/web/kit.js. Expõe window.Bebop.
 */
(function (g) {
  const K = g.Kit, B = {};
  B.PRENSAGENS = {
    cobalto: { paper: '#f0e8d6', K: '#15171c', A: '#1f4fd8', B: '#ff5a1f' },
    mostarda: { paper: '#efe5cd', K: '#1b1814', A: '#dfa000', B: '#0f7f7c' },
    carmim: { paper: '#f3ecdf', K: '#17151c', A: '#e23a4e', B: '#2a2f96' },
    menta: { paper: '#eef0e2', K: '#14181a', A: '#18a07a', B: '#f2478b' },
  };
  /* ---------- tempo: compasso com swing ---------- */
  /* beats(t, bpm): posição em tempos. swingAt(n): instante (s) da colcheia n com swing 2:1 */
  B.Tempo = function (bpm = 120, swing = 0.66) {
    const spb = 60 / bpm;
    return { bpm, spb, beat: (t) => t / spb, at: (b) => b * spb,
      /* colcheia n (0,1,2..): as ímpares atrasam (swing) */
      eighth: (n) => (Math.floor(n / 2) + (n % 2 ? swing : 0)) * spb,
      /* pulso 1 -> 0 a cada tempo (para batidas visuais) */
      pulse: (t, decay = 6) => Math.exp(-((t / spb) % 1) * decay),
      /* entrada seca: 0 antes, overshoot e assenta em dur segundos */
      snap: (t, b, dur = 0.26) => { const k = (t - b * spb) / dur; return k <= 0 ? 0 : k >= 1 ? 1 : K.ease.outBack(k); },
      hit: (t, b, dur = 0.26) => { const k = (t - b * spb) / dur; return k <= 0 ? 0 : k >= 1 ? 1 : K.ease.outExpo(k); },
    };
  };

  /* ---------- prensa: chapas + composição ---------- */
  B.Press = function (canvas, { W = K.W, H = K.H, prensagem = 'cobalto', seed = 7 } = {}) {
    canvas.width = W; canvas.height = H; const out = canvas.getContext('2d');
    const plates = {}, names = ['A', 'B', 'K']; for (const n of names) { const c = K.canvas(W, H); plates[n] = { c, x: c.getContext('2d') }; }
    const tint = K.canvas(W, H), tx = tint.getContext('2d');
    // texturas: grão do papel (3 variações) e manchado de tinta (por chapa)
    const mkNoise = (w, h, fn) => { const c = K.canvas(w, h), x = c.getContext('2d'), id = x.createImageData(w, h), d = id.data; for (let i = 0, p = 0; i < w * h; i++, p += 4) { const [r, gg, b, a] = fn(i % w, (i / w) | 0); d[p] = r; d[p + 1] = gg; d[p + 2] = b; d[p + 3] = a; } x.putImageData(id, 0, 0); return c; };
    const r = K.rng(seed);
    const grain = [0, 1, 2].map(() => mkNoise(480, 270, () => { const v = r(); return [60, 40, 20, v > 0.5 ? (v - 0.5) * 90 : 0]; }));
    const speck = [0, 1, 2].map(() => mkNoise(960, 540, () => { const v = r(); return [255, 255, 255, v > 0.985 ? 255 : v > 0.93 ? 70 : 0]; }));   // falhas: pontos sem tinta
    const mottle = [1, 2, 3].map((k) => mkNoise(240, 135, (x, y) => [255, 255, 255, Math.max(0, K.fbm(x / 26 + k * 9, y / 26, 3) - 0.5) * 2 * 150]));
    let pal = Object.assign({}, B.PRENSAGENS[prensagem] || prensagem);
    const api = {
      W, H, plates, get pal() { return pal; }, set(p) { pal = Object.assign({}, B.PRENSAGENS[p] || p); },
      /* começa o quadro: limpa as chapas. Desenhe em api.A / api.B / api.K com fillStyle preto (alfa = carga de tinta) */
      begin() { for (const n of names) { const x = plates[n].x; x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none'; x.clearRect(0, 0, W, H); x.fillStyle = '#000'; x.strokeStyle = '#000'; } },
      A: plates.A.x, B: plates.B.x, K: plates.K.x,
      /* desenha a mesma forma em várias chapas; modo 'knock' abre janela (papel) */
      on(list, fn, knock = false) { for (const n of list) { const x = plates[n].x; x.save(); if (knock) x.globalCompositeOperation = 'destination-out'; fn(x); x.restore(); } },
      /* fecha o quadro: papel + chapas em multiply, fora de registro, com manchado e grão. t dá a fervura (12 poses/s) */
      end(t, { misreg = 2.4, boil = true } = {}) {
        const k = boil ? Math.floor(t * 12) : 0, rr = K.rng(k * 31 + 5);
        out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; out.fillStyle = pal.paper; out.fillRect(0, 0, W, H);
        names.forEach((n, i) => {
          tx.setTransform(1, 0, 0, 1, 0, 0); tx.globalCompositeOperation = 'source-over'; tx.globalAlpha = 1; tx.clearRect(0, 0, W, H); tx.drawImage(plates[n].c, 0, 0);
          tx.globalCompositeOperation = 'destination-out'; tx.imageSmoothingEnabled = true; tx.globalAlpha = n === 'K' ? 0.3 : 0.42; tx.drawImage(mottle[i], 0, 0, W, H);
          tx.globalAlpha = n === 'K' ? 0.5 : 0.62; tx.drawImage(speck[(k + i) % 3], 0, 0, W, H);
          tx.globalCompositeOperation = 'source-in'; tx.globalAlpha = 1; tx.fillStyle = pal[n]; tx.fillRect(0, 0, W, H);
          const ox = n === 'K' ? 0 : (i === 0 ? -misreg : misreg) + (rr() - 0.5) * 0.8, oy = n === 'K' ? 0 : (i === 0 ? misreg * 0.6 : -misreg * 0.5) + (rr() - 0.5) * 0.8;
          out.globalCompositeOperation = 'multiply'; out.drawImage(tint, ox, oy);
        });
        out.globalCompositeOperation = 'multiply'; out.globalAlpha = 0.5; out.imageSmoothingEnabled = false; out.drawImage(grain[k % 3], 0, 0, W, H); out.imageSmoothingEnabled = true;
        out.globalAlpha = 1; out.globalCompositeOperation = 'source-over';
      },
    };
    return api;
  };

  /* ---------- formas ---------- */
  /* recorte de tesoura: polígono com vértices levemente tremidos (seed fixa); wob (rad) balança em torno de (cx,cy) */
  B.cut = function (x, pts, { seed = 1, jit = 3.5, close = true } = {}) {
    const r = K.rng(seed); x.beginPath(); pts.forEach(([px, py], i) => { const jx = px + (r() - 0.5) * jit * 2, jy = py + (r() - 0.5) * jit * 2; i ? x.lineTo(jx, jy) : x.moveTo(jx, jy); }); if (close) x.closePath(); x.fill();
  };
  /* retícula (meio-tom): pontos em grade a 45°, raio por função (px, py) -> 0..1, recortada pela forma atual */
  B.halftone = function (x, bbox, clipFn, valueFn, { pitch = 13, angle = Math.PI / 4 } = {}) {
    x.save(); if (clipFn) { clipFn(x); x.clip(); }
    const [bx, by, bw, bh] = bbox, cx = bx + bw / 2, cy = by + bh / 2, R = Math.hypot(bw, bh) / 2 + pitch, c = Math.cos(angle), s = Math.sin(angle);
    x.beginPath();
    for (let v = -R; v <= R; v += pitch) for (let u = -R; u <= R; u += pitch) { const px = cx + u * c - v * s, py = cy + u * s + v * c; if (px < bx - pitch || px > bx + bw + pitch || py < by - pitch || py > by + bh + pitch) continue; const val = valueFn(px, py); if (val <= 0.02) continue; const rad = Math.sqrt(Math.min(1, val)) * pitch * 0.72; x.moveTo(px + rad, py); x.arc(px, py, rad, 0, 6.2832); }
    x.fill(); x.restore();
  };
  /* texto: bloco ajustado à largura. Devolve altura usada. opts: font (família), weight, w (largura alvo) ou size, align, track */
  B.fit = function (x, text, w, font, weight = 400, track = 0) { x.font = `${weight} 100px "${font}"`; x.letterSpacing = track + 'px'; const m = x.measureText(text).width; return 100 * w / m; };
  B.type = function (x, text, px, py, { font = 'League Gothic', size = 200, weight = 400, align = 'left', track = 0, base = 'alphabetic', rot = 0 } = {}) {
    x.save(); x.translate(px, py); if (rot) x.rotate(rot); x.font = `${weight} ${size}px "${font}"`; x.letterSpacing = track + 'px'; x.textAlign = align; x.textBaseline = base; x.fillText(text, 0, 0); const w = x.measureText(text).width; x.restore(); return w;
  };
  /* janela de revelação: desenha fn recortado por um retângulo que abre de um lado (k 0..1) */
  B.reveal = function (x, [rx, ry, rw, rh], k, from, fn) {
    if (k <= 0) return; x.save(); x.beginPath();
    if (from === 'left') x.rect(rx, ry, rw * k, rh); else if (from === 'right') x.rect(rx + rw * (1 - k), ry, rw * k, rh); else if (from === 'top') x.rect(rx, ry, rw, rh * k); else x.rect(rx, ry + rh * (1 - k), rw, rh * k);
    x.clip(); fn(x); x.restore();
  };

  /* ---------- figura recortada: leitor sentado de perfil (olha para +x). Caixa local 620×680, origem no canto superior esquerdo ---------- */
  B.leitor = function (P, ox, oy, s, { t = 0, tempo = null, hat = 'B', book = 'B', body = 'K', shade = true, seed = 3 } = {}) {
    const beat = tempo ? Math.floor(tempo.beat(t)) : 0, r = K.rng(seed + beat * 0), nod = tempo ? tempo.pulse(t, 5) * 0.035 : 0, tap = tempo ? tempo.pulse(t, 7) : 0;
    const tr = (x) => { x.translate(ox, oy); x.scale(s, s); };
    P.on([body], (x) => { tr(x);
      B.cut(x, [[214, 396], [372, 392], [524, 424], [512, 492], [360, 484], [210, 474]], { seed: 11 });                 // coxa
      B.cut(x, [[468, 436], [522, 436], [546, 640], [488, 642]], { seed: 12 });                                           // canela
      x.save(); x.translate(488, 640); x.rotate(-tap * 0.16); B.cut(x, [[0, -18], [112, 2], [114, 22], [0, 22]], { seed: 13 }); x.restore();   // pé (bate no tempo)
      B.cut(x, [[222, 208], [362, 200], [396, 330], [370, 446], [212, 446], [192, 318]], { seed: 14 });                  // tronco
      B.cut(x, [[286, 176], [328, 172], [338, 216], [278, 218]], { seed: 15 });                                           // pescoço
      x.save(); x.translate(306, 180); x.rotate(nod); x.translate(-306, -180);
      B.cut(x, [[244, 62], [330, 44], [376, 96], [398, 118], [366, 130], [354, 172], [282, 190], [234, 134]], { seed: 16 }); x.restore();   // cabeça com nariz
      B.cut(x, [[338, 228], [384, 240], [408, 338], [362, 352]], { seed: 17 });                                           // braço
      B.cut(x, [[358, 330], [402, 318], [506, 296], [506, 334], [372, 366]], { seed: 18 });                               // antebraço
      B.cut(x, [[150, 300], [196, 300], [204, 660], [160, 660]], { seed: 19 }); B.cut(x, [[150, 470], [400, 478], [398, 508], [150, 500]], { seed: 20 }); B.cut(x, [[366, 500], [398, 500], [410, 660], [376, 660]], { seed: 21 });   // cadeira
    });
    // olho: janela no preto
    P.on([body], (x) => { tr(x); x.translate(306, 180); x.rotate(nod); x.translate(-306, -180); B.cut(x, [[322, 98], [352, 92], [348, 108], [326, 110]], { seed: 22, jit: 1.5 }); }, true);
    if (hat) { const hf = (x) => { tr(x); x.translate(306, 180); x.rotate(nod); x.translate(-306, -180); B.cut(x, [[222, 76], [262, 22], [352, 18], [388, 62], [300, 58]], { seed: 23 }); }; P.on(['A', 'B', 'K'].filter((n) => n !== hat), hf, true); P.on([hat], hf); }
    if (book) { const bk = (x) => { tr(x); B.cut(x, [[492, 248], [596, 214], [612, 304], [508, 338]], { seed: 24 }); B.cut(x, [[492, 248], [408, 226], [404, 306], [508, 338]], { seed: 25 }); };
      P.on(['A', 'B', 'K'].filter((n) => n !== book), bk, true); P.on([book], bk);
      P.on(['K'], (x) => { tr(x); x.lineWidth = 5; x.beginPath(); x.moveTo(492, 250); x.lineTo(508, 338); x.stroke(); x.lineWidth = 3.5; for (let i = 0; i < 4; i++) { x.beginPath(); x.moveTo(516, 262 + i * 17); x.lineTo(588, 240 + i * 17); x.stroke(); x.beginPath(); x.moveTo(424, 250 + i * 16); x.lineTo(480, 266 + i * 16); x.stroke(); } }); }
    // sombra em retícula: janelas redondas no preto do tronco e da coxa (aparece a cor de baixo), mais abertas do lado da luz
    if (shade) P.on([body], (x) => { tr(x);
      B.halftone(x, [190, 190, 220, 270], (c) => { c.beginPath(); c.moveTo(232, 216); c.lineTo(354, 210); c.lineTo(384, 330); c.lineTo(360, 436); c.lineTo(224, 436); c.lineTo(204, 318); c.closePath(); }, (px, py) => K.remap(px + (py - 320) * 0.25, 262, 392, 0, 0.62), { pitch: 12 });
      B.halftone(x, [360, 400, 170, 100], (c) => { c.beginPath(); c.moveTo(372, 402); c.lineTo(514, 432); c.lineTo(504, 482); c.lineTo(366, 474); c.closePath(); }, (px, py) => K.remap(py, 480, 400, 0, 0.55), { pitch: 12 }); }, true);
  };
  g.Bebop = B;
})(window);
