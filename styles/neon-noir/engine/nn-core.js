/* nn-core.js: núcleo do estilo neon-noir (pipeline de luz 2.5D em Canvas 2D + pós em WebGL).
 * Depende de shared/web/kit.js. Expõe window.NN.
 *
 * Pipeline por quadro (NN.Shot.render):
 *   1. céu + camadas distantes (paralaxe)                      -> base
 *   2. fachada: albedo × luz (multiply)  + emissivos (tubos, janelas)
 *   3. chão: albedo × luz + reflexo molhado (fachada e figuras espelhadas, borradas na vertical)
 *   4. volumetria (cone do poste, vapor)
 *   5. figuras: silhueta + luz de recorte (rim) + sombra de contato
 *   6. chuva iluminada pelos emissivos + respingos
 *   7. primeiro plano desfocado
 *   8. bloom (emissivos borrados em 3 raios)
 *   9. HUD/legenda, depois pós em WebGL: aberração cromática, scanlines, grão, vinheta, glitch
 */
(function (g) {
  const K = g.Kit, { W, H } = K;
  const NN = {};
  NN.PAL = {
    night: '#06041a', indigo: '#120a2a', violet: '#2a1248', haze: '#5a1f6e',
    magenta: '#ff2e88', cyan: '#19e6ff', amber: '#ffab40', red: '#ff3d3d', acid: '#b6ff3c', white: '#fff4f8',
    ambient: '#2b2152', ink: '#0b0818',
  };

  /* ---------- sinais de neon ---------- */
  NN.flicker = function (t, seed, amount = 1) {
    const shimmer = 0.94 + 0.06 * Math.sin(t * 377 + seed * 9.1);
    const n = K.noise1(t * 1.7 + seed * 13.37);
    if (amount > 0 && n > 1 - 0.2 * amount) return (K.hash(Math.floor(t * 22) + seed * 7.7) > 0.45 ? 1 : 0.12) * shimmer;
    return shimmer;
  };
  /* tubo: desenha o traçado atual do ctx como tubo aceso (cor saturada + miolo quase branco) */
  NN.tubeStroke = function (ctx, drawPath, color, w = 7) {
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = color; ctx.lineWidth = w; drawPath(ctx); ctx.stroke();
    ctx.strokeStyle = K.mix(color, '#ffffff', 0.78); ctx.lineWidth = Math.max(1.5, w * 0.42); drawPath(ctx); ctx.stroke();
    ctx.restore();
  };
  NN.tubeUnlit = function (ctx, drawPath, w = 7) {
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = '#141018'; ctx.lineWidth = w + 3; drawPath(ctx); ctx.stroke();
    ctx.strokeStyle = '#6b6276'; ctx.lineWidth = w; drawPath(ctx); ctx.stroke();
    ctx.strokeStyle = '#9a93a6'; ctx.lineWidth = w * 0.3; drawPath(ctx); ctx.stroke();
    ctx.restore();
  };
  /* texto em neon. mode: 'outline' (letra de forma contornada por tubo) | 'fill' (fonte monolinha/Tilt Neon) */
  NN.textTube = function (ctx, text, x, y, { font, color, mode = 'outline', w = 6, lit = true, align = 'center', spacing = 0 }) {
    ctx.save(); ctx.font = font; ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    if (spacing) ctx.letterSpacing = spacing + 'px';
    if (mode === 'outline') {
      if (lit) {
        ctx.strokeStyle = color; ctx.lineWidth = w; ctx.strokeText(text, x, y);
        ctx.strokeStyle = K.mix(color, '#ffffff', 0.78); ctx.lineWidth = Math.max(1.5, w * 0.42); ctx.strokeText(text, x, y);
      } else {
        ctx.strokeStyle = '#141018'; ctx.lineWidth = w + 3; ctx.strokeText(text, x, y);
        ctx.strokeStyle = '#6b6276'; ctx.lineWidth = w; ctx.strokeText(text, x, y);
      }
    } else {
      if (lit) {
        ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineWidth = w * 0.5; ctx.strokeText(text, x, y); ctx.fillText(text, x, y);
        ctx.fillStyle = K.mix(color, '#ffffff', 0.8); ctx.fillText(text, x, y);
      } else { ctx.fillStyle = '#6b6276'; ctx.strokeStyle = '#141018'; ctx.lineWidth = 3; ctx.strokeText(text, x, y); ctx.fillText(text, x, y); }
    }
    ctx.restore();
  };

  /* ---------- luz de recorte genérica ---------- */
  /* Desenha uma peça numa tela de rascunho, aplica rims e devolve na tela da figura.
   * rims: [{color, dir:[x,y] (para onde está a luz, espaço de tela), w (px), a (0..1), soft (px de blur)}] */
  function Rimmer(size) {
    const S = K.canvas(size, size), R = K.canvas(size, size), s = S.getContext('2d'), r = R.getContext('2d');
    function apply(C, c, rims) { // aplica rims na tela C (in place), limitado ao alfa existente
      for (const rim of rims || []) {
        if (!rim || rim.a <= 0) continue;
        r.setTransform(1, 0, 0, 1, 0, 0); r.globalCompositeOperation = 'source-over'; r.filter = 'none'; r.globalAlpha = 1; r.clearRect(0, 0, size, size);
        r.drawImage(C, 0, 0); r.globalCompositeOperation = 'source-in'; r.fillStyle = rim.color; r.fillRect(0, 0, size, size);
        r.globalCompositeOperation = 'destination-out'; if (rim.soft) r.filter = `blur(${rim.soft}px)`;
        const l = Math.hypot(rim.dir[0], rim.dir[1]) || 1;
        r.drawImage(C, -rim.dir[0] / l * rim.w, -rim.dir[1] / l * rim.w); r.filter = 'none';
        c.setTransform(1, 0, 0, 1, 0, 0); c.globalCompositeOperation = rim.add ? 'lighter' : 'source-atop'; c.globalAlpha = rim.a; c.drawImage(R, 0, 0);
        c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
      }
    }
    const part = function (dst, setXf, draw, rims) {
      s.setTransform(1, 0, 0, 1, 0, 0); s.globalCompositeOperation = 'source-over'; s.clearRect(0, 0, size, size);
      setXf(s); draw(s); s.setTransform(1, 0, 0, 1, 0, 0); apply(S, s, rims); dst.drawImage(S, 0, 0);
    };
    part.wrap = (C, c, rims) => apply(C, c, rims);
    return part;
  }
  NN.Rimmer = Rimmer;

  /* ---------- pós-processamento WebGL ---------- */
  function Post(canvas) {
    const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, alpha: false });
    const vs = `#version 300 es
      in vec2 p; out vec2 uv; void main(){ uv = p*0.5+0.5; uv.y = 1.0-uv.y; gl_Position = vec4(p,0.,1.); }`;
    const fs = `#version 300 es
      precision highp float; in vec2 uv; out vec4 o; uniform sampler2D tex; uniform vec2 res;
      uniform float time, ca, scan, grain, vig, glitch, bars;
      float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
      void main(){
        vec2 u = uv; float fr = floor(time*30.0);
        if (glitch > 0.0) {
          float band = floor(u.y*18.0 + h(vec2(fr, 1.0))*18.0);
          float on = step(1.0 - 0.55*glitch, h(vec2(band, fr)));
          u.x += on * (h(vec2(band*3.1, fr*1.7)) - 0.5) * 0.12 * glitch;
          u.x += (h(vec2(floor(u.y*res.y*0.5), fr)) - 0.5) * 0.004 * glitch;
          u.y += step(0.92, h(vec2(fr, 9.0))) * 0.02 * glitch;
        }
        vec2 d = u - 0.5; float r2 = dot(d, d);
        vec2 off = d * ca * (0.35 + 3.2*r2) + vec2(ca*0.22 + glitch*0.006, 0.0);
        vec3 c = vec3(texture(tex, u + off).r, texture(tex, u).g, texture(tex, u - off).b);
        // sangramento horizontal de croma (VHS)
        vec3 b = (texture(tex, u + vec2(3.0/res.x,0.)).rgb + texture(tex, u - vec2(3.0/res.x,0.)).rgb) * 0.5;
        c = mix(c, vec3(c.g*0.0 + dot(c, vec3(0.299,0.587,0.114))) + (b - dot(b, vec3(0.299,0.587,0.114))), 0.35);
        // curva + véu violeta nas sombras
        c = c + vec3(0.016, 0.008, 0.040) * (1.0 - c);
        c = mix(c, c*c*(3.0-2.0*c), 0.35);
        float l = dot(c, vec3(0.299,0.587,0.114)); c = mix(vec3(l), c, 1.12);
        c *= 1.0 - scan * (0.5 + 0.5*sin(uv.y*res.y*3.14159265*0.6667));
        c += (h(uv*res + fr*17.0) - 0.5) * grain;
        c *= 1.0 - vig * smoothstep(0.38, 1.02, length(d*vec2(1.0, 1.18))*1.25);
        if (bars > 0.0) { float e = bars; c *= step(e, uv.y) * step(uv.y, 1.0 - e); }
        o = vec4(clamp(c, 0., 1.), 1.0);
      }`;
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    const U = {}; for (const n of ['res', 'time', 'ca', 'scan', 'grain', 'vig', 'glitch', 'bars']) U[n] = gl.getUniformLocation(pr, n);
    return function (src, t, fx) {
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
      gl.uniform2f(U.res, canvas.width, canvas.height); gl.uniform1f(U.time, t);
      gl.uniform1f(U.ca, fx.ca); gl.uniform1f(U.scan, fx.scan); gl.uniform1f(U.grain, fx.grain); gl.uniform1f(U.vig, fx.vig); gl.uniform1f(U.glitch, fx.glitch); gl.uniform1f(U.bars, fx.bars);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); gl.finish();
    };
  }

  /* ---------- plano (shot) ---------- */
  NN.FX = { ca: 0.0035, scan: 0.07, grain: 0.055, vig: 0.62, glitch: 0, bars: 0 };
  NN.Shot = function (glCanvas, scene) {
    glCanvas.width = W; glCanvas.height = H;
    const post = Post(glCanvas);
    const mk = () => { const c = K.canvas(W, H); return [c, c.getContext('2d')]; };
    const [outC, out] = mk(), [midC, mid] = mk(), [lightC, light] = mk(), [emisC, emis] = mk(), [reflC, refl] = mk(), [tmpC, tmp] = mk(), [rainC, rain] = mk(), [occC, occ] = mk();
    const b4 = K.canvas(W / 4, H / 4), b4x = b4.getContext('2d'), b8 = K.canvas(W / 8, H / 8), b8x = b8.getContext('2d');
    const figSize = 1240, figC = K.canvas(figSize, figSize), fig = figC.getContext('2d'), rimmer = Rimmer(figSize);
    const reset = (c) => { c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.filter = 'none'; };
    const clear = (c) => { reset(c); c.clearRect(0, 0, W, H); };

    this.render = function (t) {
      const cam = scene.camera(t), z = cam.zoom || 1, py = scene.pivotY || H * 0.62;
      const xf = (c, p = 1) => c.setTransform(z, 0, 0, z, (1 - z) * W / 2 - cam.x * p * z, (1 - z) * py - (cam.y || 0) * p * z);
      const sx = (wx, p = 1) => wx * z + (1 - z) * W / 2 - cam.x * p * z, sy = (wy, p = 1) => wy * z + (1 - z) * py - (cam.y || 0) * p * z;
      const lights = scene.lights(t);

      // 1. céu e fundo
      clear(out); scene.sky(out, t, cam);
      for (const L of scene.far || []) { xf(out, L.parallax); out.globalAlpha = L.alpha == null ? 1 : L.alpha; out.drawImage(L.canvas, L.x || 0, L.y || 0); if (L.dynamic) L.dynamic(out, t); }
      reset(out);

      // luz acumulada (espaço de tela)
      clear(light); light.fillStyle = scene.ambient || NN.PAL.ambient; light.fillRect(0, 0, W, H);
      light.globalCompositeOperation = 'lighter';
      for (const L of lights) {
        const x = sx(L.x), y = sy(L.y), r = L.r * z, gr = light.createRadialGradient(x, y, 0, x, y, r);
        gr.addColorStop(0, K.rgba(L.color, L.i)); gr.addColorStop(0.35, K.rgba(L.color, L.i * 0.45)); gr.addColorStop(1, K.rgba(L.color, 0));
        light.save(); if (L.sy) { light.translate(x, y); light.scale(1, L.sy); light.translate(-x, -y); }
        light.fillStyle = gr; light.fillRect(x - r, y - r, r * 2, r * 2); light.restore();
      }
      reset(light);

      // 2. fachada + chão: albedo × luz
      clear(mid); xf(mid); mid.drawImage(scene.albedo.canvas, scene.albedo.x, 0); if (scene.albedoDynamic) scene.albedoDynamic(mid, t);
      reset(mid); mid.globalCompositeOperation = 'multiply'; mid.drawImage(lightC, 0, 0);
      mid.globalCompositeOperation = 'destination-in'; xf(mid); mid.drawImage(scene.albedo.canvas, scene.albedo.x, 0); reset(mid);

      // emissivos (tubos acesos, janelas, lâmpadas)
      clear(emis); emis.fillStyle = '#000'; emis.fillRect(0, 0, W, H); xf(emis);
      if (scene.emis) emis.drawImage(scene.emis.canvas, scene.emis.x, 0);
      for (const s of scene.signs) { const a = s.level ? s.level(t) : 1; if (a <= 0.01) continue; emis.globalAlpha = a; emis.drawImage(s.canvas, s.x, s.y); }
      emis.globalAlpha = 1; if (scene.emisDynamic) scene.emisDynamic(emis, t); reset(emis);

      // figuras do quadro
      const figs = scene.figures(t);

      // 3. reflexo molhado
      const yb = sy(scene.groundY);
      clear(refl); refl.save(); refl.beginPath(); refl.rect(0, yb, W, H - yb); refl.clip();
      refl.setTransform(1, 0, 0, -1.25, 0, yb * 2.25); refl.drawImage(midC, 0, 0); refl.globalCompositeOperation = 'lighter'; refl.drawImage(emisC, 0, 0); refl.restore();
      reset(refl);
      // figuras refletidas (espelhadas nos próprios pés)
      const drawFig = (f) => {
        reset(fig); fig.clearRect(0, 0, figSize, figSize);
        const s = f.scale * z, setXf = (c) => c.setTransform(s * (f.flip ? -1 : 1), 0, 0, s, figSize / 2, figSize - 80);
        f.draw({ part: (draw, rims) => rimmer(fig, setXf, draw, rims === undefined ? f.rims : rims), t });
        if (f.wrap) { reset(fig); rimmer.wrap(figC, fig, f.wrap); }
      };
      const figDraws = [];
      for (const f of figs) { drawFig(f); const c = K.canvas(figSize, figSize); c.getContext('2d').drawImage(figC, 0, 0); figDraws.push(c); }
      figs.forEach((f, i) => {
        const fx = sx(f.x, f.parallax || 1), fy = sy(f.y, f.parallax || 1);
        if (f.noReflect) return;
        refl.save(); refl.beginPath(); refl.rect(0, yb, W, H - yb); refl.clip();
        refl.setTransform(1, 0, 0, -1.1, fx - figSize / 2, fy + (figSize - 80) * 1.1); refl.globalAlpha = 0.9; refl.drawImage(figDraws[i], 0, 0); refl.restore();
      });
      reset(refl);
      // borrão vertical + ondulação
      clear(tmp); const N = 9;
      tmp.globalCompositeOperation = 'lighter';
      for (let i = 0; i < N; i++) { tmp.globalAlpha = (scene.reflect || 1) / (i * 0.55 + 1.6) / 2.1; tmp.drawImage(reflC, Math.sin(i * 1.7 + t * 2.0) * 1.8, i * 8 * z); }
      reset(tmp); tmp.globalCompositeOperation = 'destination-in'; xf(tmp); tmp.drawImage(scene.wet.canvas, scene.wet.x, 0); reset(tmp);

      // composição da cena
      out.drawImage(midC, 0, 0);
      out.globalCompositeOperation = 'lighter'; out.drawImage(tmpC, 0, 0);
      out.filter = 'blur(3px)'; out.globalAlpha = 0.9; out.drawImage(emisC, 0, 0); out.filter = 'none'; out.globalAlpha = 1; out.drawImage(emisC, 0, 0);
      reset(out);

      // bloom curto atrás das figuras (elas recortam o brilho)
      b4x.globalCompositeOperation = 'copy'; b4x.filter = 'blur(5px)'; b4x.drawImage(emisC, 0, 0, W / 4, H / 4);
      out.globalCompositeOperation = 'lighter'; out.globalAlpha = scene.bloom ? scene.bloom[0] : 0.55; out.drawImage(b4, 0, 0, W, H); reset(out);

      // 4. volumetria atrás das figuras
      xf(out); if (scene.volumetrics) scene.volumetrics(out, t, 'back'); reset(out);

      // 5. figuras
      clear(occ); occ.drawImage(emisC, 0, 0);
      figs.forEach((f, i) => {
        const fx = sx(f.x, f.parallax || 1), fy = sy(f.y, f.parallax || 1), s = f.scale * z;
        if (!f.noShadow) { out.save(); out.translate(fx, fy + 2); out.scale(1, 0.16); const gr = out.createRadialGradient(0, 0, 0, 0, 0, 120 * s / 0.8); gr.addColorStop(0, 'rgba(0,0,6,0.75)'); gr.addColorStop(1, 'rgba(0,0,6,0)'); out.fillStyle = gr; out.fillRect(-200, -200, 400, 400); out.restore(); }
        out.save(); if (f.blur) out.filter = `blur(${f.blur}px)`; out.drawImage(figDraws[i], fx - figSize / 2, fy - (figSize - 80)); out.restore();
        occ.save(); occ.filter = 'brightness(0)'; occ.drawImage(figDraws[i], fx - figSize / 2, fy - (figSize - 80)); occ.restore();
        if (f.emis) { for (const c of [out, occ]) { c.save(); c.globalCompositeOperation = 'lighter'; c.setTransform(s * (f.flip ? -1 : 1), 0, 0, s, fx, fy); f.emis(c, t); c.restore(); } }
      });
      reset(out); reset(occ);
      xf(out); if (scene.volumetrics) scene.volumetrics(out, t, 'front'); reset(out);

      // bloom a partir dos emissivos ocluídos
      b8x.globalCompositeOperation = 'copy'; b8x.filter = 'blur(9px)'; b8x.drawImage(occC, 0, 0, W / 8, H / 8);

      // 6. chuva iluminada
      if (scene.rain) {
        clear(rain); scene.rain(rain, t, { sx, sy, z, yb });
        rain.globalCompositeOperation = 'source-atop'; rain.fillStyle = scene.rainColor || '#39356b'; rain.fillRect(0, 0, W, H);
        rain.globalCompositeOperation = 'lighter'; rain.globalAlpha = 1; // tinge pela luz local, só onde há gota
        clear(tmp); tmp.drawImage(rainC, 0, 0); tmp.globalCompositeOperation = 'source-in'; tmp.imageSmoothingEnabled = true; tmp.globalAlpha = 1; tmp.drawImage(b8, 0, 0, W, H); reset(tmp);
        out.globalCompositeOperation = 'lighter'; out.drawImage(rainC, 0, 0); out.globalAlpha = 1; out.drawImage(tmpC, 0, 0); out.drawImage(tmpC, 0, 0); reset(out);
      }

      // 7. primeiro plano
      for (const L of scene.fg || []) { xf(out, L.parallax); if (L.blur) out.filter = `blur(${L.blur}px)`; out.drawImage(L.canvas, L.x || 0, L.y || 0); reset(out); }

      // 8. bloom
      out.globalCompositeOperation = 'lighter'; out.imageSmoothingEnabled = true;
      out.globalAlpha = scene.bloom ? scene.bloom[1] : 0.5; out.drawImage(b8, 0, 0, W, H); reset(out);

      // 9. sobreposições e pós
      if (scene.overlay) scene.overlay(out, t);
      post(outC, t, Object.assign({}, NN.FX, scene.fx ? scene.fx(t) : {}));
    };
  };
  g.NN = NN;
})(window);
