/* cedula.js: motor do estilo "cédula" (gravura em talho-doce de papel-moeda).
 * Ideia central: pinta-se qualquer coisa em TONS DE CINZA (Canvas 2D, com degradês) e um shader transforma
 * o tom em linhas gravadas: linhas paralelas que engrossam no escuro, desviam com o volume e ganham hachura
 * cruzada nas sombras. Em volta, guilhochês (rosáceas e faixas de linhas entrelaçadas), tipografia capitular,
 * numeração e selo. Depende de shared/web/kit.js. Expõe window.Cedula.
 */
(function (g) {
  const K = g.Kit, C = {};
  C.TINTAS = { verde: '#1d5741', sepia: '#5b3a21', azul: '#1c3d6b', bordo: '#7a1f2c', grafite: '#22252b' };
  C.PAPEL = '#efe8d3';

  /* ---------- gravador (WebGL): tom -> linhas ---------- */
  function Engraver(W, H) {
    const cv = K.canvas(W, H), gl = cv.getContext('webgl2', { premultipliedAlpha: true, alpha: true, preserveDrawingBuffer: true, antialias: false });
    const vs = `#version 300 es
      in vec2 p; out vec2 uv; void main(){ uv = p*0.5+0.5; uv.y = 1.0-uv.y; gl_Position = vec4(p,0.,1.); }`;
    const fs = `#version 300 es
      precision highp float; in vec2 uv; out vec4 o; uniform sampler2D tone, blurT; uniform vec2 res, cam; uniform vec3 ink;
      uniform float period, angle, depth, zoom, cross, gain, wave;
      float lum(vec3 c){ return dot(c, vec3(0.299,0.587,0.114)); }
      void main(){
        vec2 px = uv*res, w = (px - res*0.5)/zoom + cam;
        float T = clamp((1.0 - lum(texture(tone, uv).rgb)) * gain, 0.0, 1.0), Hh = lum(texture(blurT, uv).rgb);
        vec2 n = vec2(-sin(angle), cos(angle)), tg = vec2(cos(angle), sin(angle));
        float phi = dot(w, n) + depth*Hh + wave*sin(dot(w, tg)*0.04 + dot(w, n)*0.011);
        float s = abs(fract(phi/period) - 0.5)*2.0, aa = 1.6/(period*zoom);
        float wd = clamp(T*1.12, 0.0, 0.95);
        float l1 = (1.0 - smoothstep(wd - aa, wd + aa, s)) * smoothstep(0.03, 0.09, T);
        vec2 n2 = vec2(-sin(angle + 1.08), cos(angle + 1.08));
        float s2 = abs(fract((dot(w, n2) + depth*0.55*Hh)/period) - 0.5)*2.0, w2 = clamp((T - 0.48)*1.5, 0.0, 0.72);
        float l2 = (1.0 - smoothstep(w2 - aa, w2 + aa, s2)) * smoothstep(0.48, 0.56, T) * cross;
        float cov = max(l1, l2);
        o = vec4(ink*cov, cov);
      }`;
    const sh = (t, src) => { const s = gl.createShader(t); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const mkTex = (unit) => { const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t); for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, v); return t; };
    mkTex(0); mkTex(1); const U = {}; for (const n of ['tone', 'blurT', 'res', 'cam', 'ink', 'period', 'angle', 'depth', 'zoom', 'cross', 'gain', 'wave']) U[n] = gl.getUniformLocation(pr, n);
    gl.uniform1i(U.tone, 0); gl.uniform1i(U.blurT, 1);
    const blurC = K.canvas(W, H), bx = blurC.getContext('2d');
    /* engrave(toneCanvas, opts) -> canvas com as linhas (fundo transparente) */
    return function (tone, { ink = C.TINTAS.verde, period = 6.5, angle = 0, depth = 22, cam = [W / 2, H / 2], zoom = 1, cross = 1, gain = 1, wave = 2.2, blur = 9 } = {}) {
      bx.filter = `blur(${blur * zoom}px)`; bx.globalCompositeOperation = 'copy'; bx.drawImage(tone, 0, 0); bx.filter = 'none';
      gl.viewport(0, 0, W, H); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.activeTexture(gl.TEXTURE0); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, tone);
      gl.activeTexture(gl.TEXTURE1); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, blurC);
      const [r, gg, b] = K.hex(ink); gl.uniform3f(U.ink, r / 255, gg / 255, b / 255); gl.uniform2f(U.res, W, H); gl.uniform2f(U.cam, cam[0], cam[1]);
      gl.uniform1f(U.period, period); gl.uniform1f(U.angle, angle); gl.uniform1f(U.depth, depth); gl.uniform1f(U.zoom, zoom); gl.uniform1f(U.cross, cross); gl.uniform1f(U.gain, gain); gl.uniform1f(U.wave, wave);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.finish(); return cv;
    };
  }

  /* ---------- palco ---------- */
  C.Stage = function (view, { W = K.W, H = K.H, seed = 4 } = {}) {
    view.width = W; view.height = H; const out = view.getContext('2d'), engrave = Engraver(W, H);
    const toneC = K.canvas(W, H), tone = toneC.getContext('2d');
    // papel de segurança: tom creme, manchas, fibrinhas coloridas (estático, em resolução de tela)
    const paperC = K.canvas(W, H), px = paperC.getContext('2d'), r = K.rng(seed);
    px.fillStyle = C.PAPEL; px.fillRect(0, 0, W, H);
    { const n = K.canvas(W / 4, H / 4), nx = n.getContext('2d'), id = nx.createImageData(W / 4, H / 4), d = id.data; for (let y = 0; y < H / 4; y++) for (let x = 0; x < W / 4; x++) { const v = K.fbm(x / 60, y / 60, 4), i = (y * (W / 4) + x) * 4; d[i] = 120; d[i + 1] = 90; d[i + 2] = 40; d[i + 3] = Math.max(0, v - 0.45) * 70; } nx.putImageData(id, 0, 0); px.drawImage(n, 0, 0, W, H); }
    for (let i = 0; i < 520; i++) { px.strokeStyle = K.rgba(r.pick(['#b23a3a', '#2f5fa8', '#3c7a4a', '#8a7a55']), r.range(0.25, 0.6)); px.lineWidth = 1; const x = r() * W, y = r() * H, a = r() * 6.28, l = r.range(5, 14); px.beginPath(); px.moveTo(x, y); px.quadraticCurveTo(x + Math.cos(a) * l * 0.5 + r.range(-3, 3), y + Math.sin(a) * l * 0.5 + r.range(-3, 3), x + Math.cos(a) * l, y + Math.sin(a) * l); px.stroke(); }
    const api = { W, H, out, tone, toneC, engrave, paperC,
      /* câmera: {x, y, zoom} em px de mundo (a cédula é o mundo W×H) */
      cam: { x: W / 2, y: H / 2, zoom: 1 },
      xf(c) { const z = api.cam.zoom; c.setTransform(z, 0, 0, z, W / 2 - api.cam.x * z, H / 2 - api.cam.y * z); },
      begin() { out.setTransform(1, 0, 0, 1, 0, 0); out.globalAlpha = 1; out.globalCompositeOperation = 'source-over'; out.filter = 'none'; out.drawImage(paperC, 0, 0); api.xf(out); },
      /* abre uma tela de tom limpa (branca) já com a câmera aplicada */
      toneBegin() { tone.setTransform(1, 0, 0, 1, 0, 0); tone.globalAlpha = 1; tone.globalCompositeOperation = 'source-over'; tone.filter = 'none'; tone.fillStyle = '#fff'; tone.fillRect(0, 0, W, H); api.xf(tone); return tone; },
      /* grava a tela de tom atual e imprime no quadro (multiply) */
      print(opts = {}) { const cv = engrave(toneC, Object.assign({ cam: [api.cam.x, api.cam.y], zoom: api.cam.zoom }, opts)); out.save(); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'multiply'; out.globalAlpha = opts.alpha == null ? 1 : opts.alpha; out.drawImage(cv, 0, 0); out.restore(); },
      /* acabamento: vinheta e brilho que varre (faixa holográfica opcional) */
      finish(t, { sweep = -1 } = {}) { out.setTransform(1, 0, 0, 1, 0, 0); const v = out.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, W * 0.75); v.addColorStop(0, 'rgba(60,40,10,0)'); v.addColorStop(1, 'rgba(60,40,10,0.28)'); out.fillStyle = v; out.fillRect(0, 0, W, H);
        if (sweep >= 0 && sweep <= 1) { const x = K.lerp(-400, W + 400, sweep), gr = out.createLinearGradient(x - 260, 0, x + 260, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,252,235,0.34)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); out.save(); out.transform(1, 0, -0.35, 1, 200, 0); out.globalCompositeOperation = 'soft-light'; out.fillStyle = gr; out.fillRect(-600, 0, W + 1200, H); out.restore(); } },
    };
    return api;
  };

  /* ---------- guilhochê ---------- */
  const G = {};
  /* rosácea: n curvas r(θ) = R + a·sin(kθ + fase_i) + b·sin(mθ), defasadas -> anéis entrelaçados */
  G.rosette = function (ctx, cx, cy, R, { a = 18, k = 12, n = 8, b = 0, m = 3, phase = 0, color = C.TINTAS.verde, w = 1.15, alpha = 0.85, steps = 360 } = {}) {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.globalAlpha = alpha;
    for (let i = 0; i < n; i++) { const ph = phase + i / n * K.TAU; ctx.beginPath(); for (let s = 0; s <= steps; s++) { const th = s / steps * K.TAU, rr = R + a * Math.sin(k * th + ph) + b * Math.sin(m * th - ph * 0.5), x = cx + Math.cos(th) * rr, y = cy + Math.sin(th) * rr; s ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.closePath(); ctx.stroke(); }
    ctx.restore();
  };
  /* oval de guilhochê (para medalhão) */
  G.oval = function (ctx, cx, cy, rx, ry, opts = {}) { ctx.save(); ctx.translate(cx, cy); ctx.scale(1, ry / rx); G.rosette(ctx, 0, 0, rx, opts); ctx.restore(); };
  /* faixa: senoides defasadas ao longo de um segmento horizontal ou vertical */
  G.band = function (ctx, x0, y0, len, { vertical = false, a = 14, f = 0.055, n = 6, phase = 0, color = C.TINTAS.verde, w = 1.1, alpha = 0.8, a2 = 0, f2 = 0.017 } = {}) {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.globalAlpha = alpha;
    for (let i = 0; i < n; i++) { const ph = phase + i / n * K.TAU; ctx.beginPath(); for (let s = 0; s <= len; s += 3) { const d = a * Math.sin(s * f + ph) + a2 * Math.sin(s * f2 - ph); vertical ? (s ? ctx.lineTo(x0 + d, y0 + s) : ctx.moveTo(x0 + d, y0 + s)) : (s ? ctx.lineTo(x0 + s, y0 + d) : ctx.moveTo(x0 + s, y0 + d)); } ctx.stroke(); }
    ctx.restore();
  };
  /* moldura completa da cédula: filetes + 4 faixas de guilhochê + rosáceas de canto */
  G.frame = function (ctx, W, H, { m = 34, t = 0, color = C.TINTAS.verde, band = 30 } = {}) {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.strokeRect(m, m, W - 2 * m, H - 2 * m); ctx.lineWidth = 1.2; ctx.strokeRect(m + 8, m + 8, W - 2 * m - 16, H - 2 * m - 16); ctx.strokeRect(m + 2 * band + 22, m + 2 * band + 22, W - 2 * (m + 2 * band + 22), H - 2 * (m + 2 * band + 22)); ctx.restore();
    const c = m + 11 + band, o = { a: band - 6, n: 7, color, phase: t * 0.5, f: 0.05, a2: 4 };
    G.band(ctx, c + band + 30, c, W - 2 * (c + band + 30), o); G.band(ctx, c + band + 30, H - c, W - 2 * (c + band + 30), Object.assign({}, o, { phase: -t * 0.5 }));
    G.band(ctx, c, c + band + 30, H - 2 * (c + band + 30), Object.assign({}, o, { vertical: true })); G.band(ctx, W - c, c + band + 30, H - 2 * (c + band + 30), Object.assign({}, o, { vertical: true, phase: -t * 0.5 }));
    for (const [x, y] of [[c, c], [W - c, c], [c, H - c], [W - c, H - c]]) { G.rosette(ctx, x, y, band * 0.62, { a: band * 0.32, k: 8, n: 6, color, phase: t * 0.8 }); }
  };
  C.G = G;

  /* ---------- pintores de tom (desenham em cinza: branco = sem tinta, preto = tinta cheia) ---------- */
  const T = {}, gray = (v) => { const c = Math.round(255 * (1 - K.clamp(v))); return `rgb(${c},${c},${c})`; };
  T.gray = gray;
  /* fundo oval do medalhão: mais escuro nas bordas */
  T.ovalBg = function (x, cx, cy, rx, ry, { inner = 0.2, outer = 0.72, ox = 0.2 } = {}) { x.save(); x.beginPath(); x.ellipse(cx, cy, rx, ry, 0, 0, 7); x.clip(); x.translate(cx, cy); x.scale(1, ry / rx); const g2 = x.createRadialGradient(rx * ox, -rx * 0.1, rx * 0.1, 0, 0, rx * 1.05); g2.addColorStop(0, gray(inner)); g2.addColorStop(1, gray(outer)); x.fillStyle = g2; x.fillRect(-rx, -rx, 2 * rx, 2 * rx); x.restore(); };
  /* busto de perfil (olha para +x). Caixa local 600×760; (ox, oy) = canto superior esquerdo; s = escala */
  T.busto = function (x, ox, oy, s, { hair = 0.9, skin = 0.34, coat = 0.92, oculos = true } = {}) {
    x.save(); x.translate(ox, oy); x.scale(s, s); x.lineCap = 'round'; x.lineJoin = 'round';
    const lg = (x0, y0, x1, y1, a, b) => { const g2 = x.createLinearGradient(x0, y0, x1, y1); g2.addColorStop(0, gray(a)); g2.addColorStop(1, gray(b)); return g2; };
    const glow = (cx, cy, r, v, a = 1) => { const c = Math.round(255 * (1 - v)), g2 = x.createRadialGradient(cx, cy, 0, cx, cy, r); g2.addColorStop(0, `rgba(${c},${c},${c},${a})`); g2.addColorStop(1, `rgba(${c},${c},${c},0)`); x.fillStyle = g2; x.fillRect(cx - r, cy - r, 2 * r, 2 * r); };
    // ombros e paletó
    x.fillStyle = lg(100, 560, 540, 780, coat * 0.78, coat); x.beginPath(); x.moveTo(10, 790); x.quadraticCurveTo(40, 610, 214, 560); x.lineTo(352, 556); x.quadraticCurveTo(540, 600, 600, 790); x.closePath(); x.fill();
    x.fillStyle = gray(0.05); x.beginPath(); x.moveTo(286, 540); x.lineTo(362, 548); x.lineTo(404, 650); x.lineTo(340, 720); x.closePath(); x.fill();          // camisa
    x.fillStyle = gray(0.66); x.beginPath(); x.moveTo(346, 610); x.lineTo(376, 616); x.lineTo(392, 790); x.lineTo(320, 790); x.closePath(); x.fill();          // gravata
    x.fillStyle = lg(200, 560, 340, 720, 0.55, 0.8); x.beginPath(); x.moveTo(214, 560); x.lineTo(286, 540); x.lineTo(340, 720); x.lineTo(292, 790); x.lineTo(170, 790); x.closePath(); x.fill();   // lapela
    x.strokeStyle = gray(1); x.lineWidth = 5; x.beginPath(); x.moveTo(286, 540); x.lineTo(340, 720); x.lineTo(292, 790); x.stroke();
    // pescoço
    x.fillStyle = lg(240, 430, 350, 560, skin + 0.36, skin + 0.16); x.beginPath(); x.moveTo(232, 400); x.lineTo(340, 452); x.lineTo(352, 556); x.lineTo(240, 566); x.closePath(); x.fill();
    // cabeça de perfil: testa, nariz, lábios, queixo, mandíbula, nuca
    const face = () => { x.beginPath(); x.moveTo(296, 120); x.quadraticCurveTo(376, 122, 396, 196); x.quadraticCurveTo(402, 226, 396, 248); x.quadraticCurveTo(398, 262, 410, 280); x.quadraticCurveTo(432, 306, 448, 326); x.quadraticCurveTo(450, 340, 420, 342);
      x.quadraticCurveTo(418, 354, 426, 364); x.quadraticCurveTo(426, 374, 414, 378); x.quadraticCurveTo(428, 388, 418, 400); x.quadraticCurveTo(408, 408, 414, 424); x.quadraticCurveTo(418, 456, 384, 466); x.quadraticCurveTo(350, 474, 322, 462);
      x.quadraticCurveTo(270, 448, 240, 420); x.quadraticCurveTo(170, 400, 160, 290); x.quadraticCurveTo(160, 124, 296, 120); x.closePath(); };
    face(); x.fillStyle = lg(210, 180, 440, 360, skin + 0.2, skin - 0.12); x.fill();
    x.save(); face(); x.clip();
    glow(360, 310, 90, 0.06, 0.9);                    // maçã do rosto
    glow(376, 180, 70, 0.1, 0.7);                     // testa
    glow(330, 470, 110, 0.72, 0.9);                   // sombra sob o queixo
    glow(300, 400, 80, 0.6, 0.6);                     // mandíbula
    glow(388, 262, 42, 0.7, 0.8);                     // órbita
    glow(410, 348, 26, 0.55, 0.6);                    // sob o nariz
    x.restore();
    face(); x.strokeStyle = gray(0.95); x.lineWidth = 4.5; x.stroke();
    // cabelo: massa escura do alto da testa até a nuca, com costeleta
    x.fillStyle = lg(170, 110, 330, 420, hair, hair * 0.8); x.beginPath(); x.moveTo(392, 184); x.quadraticCurveTo(372, 92, 280, 92); x.quadraticCurveTo(140, 96, 140, 270); x.quadraticCurveTo(142, 370, 236, 428);
    x.quadraticCurveTo(236, 372, 258, 348); x.lineTo(262, 300); x.quadraticCurveTo(292, 290, 300, 246); x.quadraticCurveTo(330, 196, 392, 184); x.closePath(); x.fill();
    x.strokeStyle = gray(hair * 0.55); x.lineWidth = 5; for (let i = 0; i < 6; i++) { x.beginPath(); x.moveTo(372 - i * 30, 112 + i * 4); x.quadraticCurveTo(250 - i * 20, 130 + i * 16, 196 - i * 6, 290 + i * 20); x.stroke(); }
    // orelha
    x.fillStyle = gray(skin + 0.02); x.beginPath(); x.ellipse(278, 318, 22, 36, 0.12, 0, 7); x.fill(); x.strokeStyle = gray(0.9); x.lineWidth = 4; x.stroke(); x.lineWidth = 5; x.beginPath(); x.arc(280, 314, 12, -0.6, 2.4); x.stroke();
    // olho, sobrancelha, narina, boca
    x.fillStyle = gray(1); x.beginPath(); x.ellipse(384, 262, 10, 6.5, 0, 0, 7); x.fill(); x.strokeStyle = gray(1); x.lineWidth = 4; x.beginPath(); x.moveTo(366, 258); x.quadraticCurveTo(384, 248, 402, 258); x.stroke();
    x.lineWidth = 8; x.beginPath(); x.moveTo(356, 234); x.quadraticCurveTo(384, 220, 404, 232); x.stroke();
    x.lineWidth = 5; x.beginPath(); x.moveTo(424, 378); x.quadraticCurveTo(398, 384, 380, 374); x.stroke(); x.beginPath(); x.moveTo(436, 336); x.quadraticCurveTo(424, 344, 414, 334); x.stroke();
    if (oculos) { x.strokeStyle = gray(1); x.lineWidth = 5.5; x.beginPath(); x.ellipse(384, 262, 28, 25, 0, 0, 7); x.stroke(); x.beginPath(); x.moveTo(356, 258); x.lineTo(284, 296); x.stroke(); }
    x.restore();
  };
  /* livro aberto com raios (vinheta) */
  T.livro = function (x, cx, cy, s, { rays = 1, t = 0 } = {}) {
    x.save(); x.translate(cx, cy); x.scale(s, s);
    if (rays > 0) for (let i = 0; i < 15; i++) { const a = -Math.PI + (i + 0.5) / 15 * Math.PI, w = 0.07, L = 250 * rays; const g2 = x.createLinearGradient(0, 0, Math.cos(a) * L, Math.sin(a) * L); g2.addColorStop(0.3, gray(i % 2 ? 0.5 : 0.28)); g2.addColorStop(1, gray(0)); x.fillStyle = g2; x.beginPath(); x.moveTo(Math.cos(a - w) * 70, Math.sin(a - w) * 70 - 30); x.lineTo(Math.cos(a - w * 0.3) * L, Math.sin(a - w * 0.3) * L - 30); x.lineTo(Math.cos(a + w * 0.3) * L, Math.sin(a + w * 0.3) * L - 30); x.lineTo(Math.cos(a + w) * 70, Math.sin(a + w) * 70 - 30); x.closePath(); x.fill(); }
    const pg = (sx) => { x.save(); x.scale(sx, 1); let g2 = x.createLinearGradient(0, 0, 150, 0); g2.addColorStop(0, gray(0.55)); g2.addColorStop(0.25, gray(0.12)); g2.addColorStop(1, gray(0.3)); x.fillStyle = g2; x.beginPath(); x.moveTo(0, -30); x.quadraticCurveTo(70, -64, 150, -40); x.lineTo(150, 50); x.quadraticCurveTo(70, 26, 0, 60); x.closePath(); x.fill();
      x.fillStyle = gray(0.9); x.beginPath(); x.moveTo(0, 60); x.quadraticCurveTo(70, 26, 150, 50); x.lineTo(156, 64); x.quadraticCurveTo(74, 44, 0, 76); x.closePath(); x.fill(); x.restore(); };
    pg(1); pg(-1); x.restore();
  };
  /* pilha de moedas */
  T.moedas = function (x, cx, base, n, { rx = 64, ry = 18, h = 15 } = {}) {
    for (let i = 0; i < n; i++) { const y = base - i * h, ox = Math.sin(i * 2.4) * 4; let g2 = x.createLinearGradient(cx - rx, 0, cx + rx, 0); g2.addColorStop(0, gray(0.75)); g2.addColorStop(0.35, gray(0.25)); g2.addColorStop(0.6, gray(0.4)); g2.addColorStop(1, gray(0.88)); x.fillStyle = g2; x.beginPath(); x.ellipse(cx + ox, y, rx, ry, 0, 0, Math.PI); x.lineTo(cx + ox - rx, y - h); x.ellipse(cx + ox, y - h, rx, ry, 0, Math.PI, 0, true); x.closePath(); x.fill();
      g2 = x.createLinearGradient(cx - rx, y - h - ry, cx + rx, y - h + ry); g2.addColorStop(0, gray(0.1)); g2.addColorStop(1, gray(0.4)); x.fillStyle = g2; x.beginPath(); x.ellipse(cx + ox, y - h, rx, ry, 0, 0, 7); x.fill(); if (i === n - 1) { x.strokeStyle = gray(0.6); x.lineWidth = 3; x.beginPath(); x.ellipse(cx + ox, y - h, rx * 0.74, ry * 0.74, 0, 0, 7); x.stroke(); } }
  };
  /* texto sombreado: tom mais escuro em cima (vira linhas dentro da letra) */
  T.texto = function (x, text, px, py, { font = '900 150px Cinzel', top = 0.95, bottom = 0.45, align = 'left', track = 0 } = {}) {
    x.save(); x.font = font; x.textAlign = align; x.letterSpacing = track + 'px'; x.textBaseline = 'alphabetic'; const m = x.measureText(text), h = m.actualBoundingBoxAscent; const g2 = x.createLinearGradient(0, py - h, 0, py); g2.addColorStop(0, gray(top)); g2.addColorStop(1, gray(bottom)); x.fillStyle = g2; x.fillText(text, px, py); x.restore(); return m.width;
  };
  C.T = T;

  /* ---------- vetores impressos direto (sem gravação) ---------- */
  C.contorno = function (ctx, text, px, py, { font = '900 150px Cinzel', color = C.TINTAS.verde, w = 2.2, align = 'left', track = 0 } = {}) { ctx.save(); ctx.font = font; ctx.textAlign = align; ctx.letterSpacing = track + 'px'; ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.strokeText(text, px, py); ctx.restore(); };
  C.serie = function (ctx, text, px, py, { color = '#b3261e', size = 44, align = 'left' } = {}) { ctx.save(); ctx.font = `700 ${size}px "Zilla Slab"`; ctx.letterSpacing = '5px'; ctx.textAlign = align; ctx.fillStyle = color; ctx.globalAlpha = 0.9; ctx.globalCompositeOperation = 'multiply'; ctx.fillText(text, px, py); ctx.restore(); };
  /* microtexto: linha repetida minúscula */
  C.micro = function (ctx, text, x0, y, len, { color = C.TINTAS.verde, size = 11 } = {}) { ctx.save(); ctx.font = `500 ${size}px Cinzel`; ctx.letterSpacing = '1.5px'; ctx.fillStyle = color; ctx.globalAlpha = 0.8; let s = ''; while (ctx.measureText(s + text).width < len) s += text; ctx.fillText(s, x0, y); ctx.restore(); };
  /* selo/carimbo circular com estrela e texto em arco; k = 0..1 (batida) */
  C.selo = function (ctx, cx, cy, R, { text = 'UNFOLD · LIVRO LIDO · ', color = '#b3261e', k = 1, rot = -0.2 } = {}) {
    if (k <= 0) return; const s = k < 1 ? 1 + (1 - K.ease.outExpo(k)) * 0.9 : 1; ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(s, s); ctx.globalAlpha = Math.min(1, k * 3) * 0.86; ctx.globalCompositeOperation = 'multiply'; ctx.strokeStyle = color; ctx.fillStyle = color;
    ctx.lineWidth = 7; ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.stroke(); ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(0, 0, R - 12, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.arc(0, 0, R * 0.56, 0, 7); ctx.stroke();
    ctx.font = `700 ${R * 0.2}px Cinzel`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const chars = (text + text).split(''), step = K.TAU / chars.length; chars.forEach((ch, i) => { ctx.save(); ctx.rotate(i * step); ctx.translate(0, -R * 0.76); ctx.fillText(ch, 0, 0); ctx.restore(); });
    ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = i / 10 * K.TAU - Math.PI / 2, rr = i % 2 ? R * 0.18 : R * 0.42; i ? ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); } ctx.closePath(); ctx.fill(); ctx.restore();
  };
  /* assinatura: laçadas cursivas (trocoide de raio variável) que se escrevem (k = 0..1) */
  C.assinatura = function (ctx, x0, y0, w, { k = 1, color = '#1b2440', seed = 3 } = {}) { if (k <= 0) return; const N = 260, n = Math.max(2, Math.floor(N * k));
    ctx.save(); ctx.translate(x0, y0); ctx.transform(1, 0, -0.32, 1, 0, 0); ctx.strokeStyle = color; ctx.lineWidth = 2.6; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.globalAlpha = 0.88; ctx.beginPath();
    for (let i = 0; i < n; i++) { const u = i / N, th = u * 46, r = (9 + 13 * K.noise1(u * 9 + seed)) * (u < 0.1 ? 2.6 : 1) * (1 - u * 0.35), px = u * w + Math.cos(th) * r * 0.8, py = -Math.sin(th) * r - (u < 0.1 ? 14 : 0) + Math.sin(u * 7) * 5; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.stroke(); if (k >= 1) { ctx.beginPath(); ctx.moveTo(-6, 24); ctx.quadraticCurveTo(w * 0.5, 34, w + 30, 6); ctx.stroke(); } ctx.restore(); };
  g.Cedula = C;
})(window);
