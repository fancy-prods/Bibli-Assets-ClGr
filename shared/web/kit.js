/* kit.js: utilitários comuns das demos web (estilos novos, nov/2026).
 * Sem dependências. Contrato com o renderizador (shared/web/render.cjs):
 *   window.DEMO = {duration, fps}; window.renderFrame(t) -> (Promise|void); window.READY -> Promise
 * Tudo que é aleatório usa semente fixa: o mesmo t gera sempre o mesmo quadro.
 */
(function (g) {
  const q = new URLSearchParams(location.search);
  const format = q.get('format') === '9x16' ? '9x16' : '16x9';
  const W = format === '9x16' ? 1080 : 1920, H = format === '9x16' ? 1920 : 1080;

  function rng(seed) {
    let a = (seed >>> 0) || 1;
    const f = function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    f.range = (lo, hi) => lo + (hi - lo) * f();
    f.int = (lo, hi) => Math.floor(f.range(lo, hi + 1));
    f.pick = (arr) => arr[Math.floor(f() * arr.length)];
    f.chance = (p) => f() < p;
    f.gauss = () => { let u = 0; for (let i = 0; i < 4; i++) u += f(); return (u - 2) / 0.58; };
    return f;
  }
  function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
  function hash2(x, y) { const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s); }
  const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
  const remap = (v, a, b, c = 0, d = 1) => c + (d - c) * clamp((v - a) / (b - a));
  function noise1(x) { const i = Math.floor(x), f = x - i; return lerp(hash(i), hash(i + 1), f * f * (3 - 2 * f)); }
  function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
    return lerp(lerp(hash2(ix, iy), hash2(ix + 1, iy), ux), lerp(hash2(ix, iy + 1), hash2(ix + 1, iy + 1), ux), uy);
  }
  function fbm(x, y, oct = 4) { let a = 0.5, s = 0, n = 0; for (let i = 0; i < oct; i++) { s += a * noise2(x, y); n += a; x *= 2.03; y *= 2.03; a *= 0.5; } return s / n; }
  const ease = {
    linear: (t) => t,
    inQuad: (t) => t * t, outQuad: (t) => 1 - (1 - t) * (1 - t),
    inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    outCubic: (t) => 1 - Math.pow(1 - t, 3),
    outExpo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    outBack: (t) => { const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
    outElastic: (t) => (t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1),
  };
  /* tween(t, t0, t1, a, b, easing): valor em t, preso fora do intervalo */
  function tween(t, t0, t1, a = 0, b = 1, e = ease.inOut) { return lerp(a, b, e(clamp((t - t0) / (t1 - t0)))); }
  function hex(c) { c = c.replace('#', ''); if (c.length === 3) c = c.split('').map((x) => x + x).join(''); return [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16)); }
  function rgba(c, a = 1) { const [r, gg, b] = hex(c); return `rgba(${r},${gg},${b},${a})`; }
  function mix(c1, c2, t) { const a = hex(c1), b = hex(c2); return '#' + a.map((v, i) => Math.round(lerp(v, b[i], t)).toString(16).padStart(2, '0')).join(''); }

  /* fontes: [{family, url, weight, style}] */
  function fonts(list) {
    return Promise.all(list.map((f) => {
      const ff = new FontFace(f.family, `url(${f.url})`, { weight: String(f.weight || 400), style: f.style || 'normal' });
      return ff.load().then((x) => document.fonts.add(x));
    }));
  }
  function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

  /* stage(el): encaixa o elemento W×H na janela (o renderizador usa a janela exata, escala 1) */
  function stage(el) {
    el.style.width = W + 'px'; el.style.height = H + 'px'; el.style.position = 'absolute'; el.style.left = '0'; el.style.top = '0';
    el.style.transformOrigin = '0 0'; document.body.style.margin = '0'; document.body.style.background = '#000'; document.body.style.overflow = 'hidden';
    const fit = () => { const s = Math.min(innerWidth / W, innerHeight / H); el.style.transform = `translate(${(innerWidth - W * s) / 2}px,${(innerHeight - H * s) / 2}px) scale(${s})`; };
    fit(); addEventListener('resize', fit);
  }
  /* run({duration, fps, render, ready}): registra o contrato e, fora do renderizador, toca em loop */
  function run({ duration, fps = 30, render, ready }) {
    g.DEMO = { duration, fps, format, W, H };
    g.renderFrame = (t) => render(t);
    g.READY = Promise.resolve(ready).then(() => {
      if (q.get('driven')) return;
      if (q.has('t')) { render(parseFloat(q.get('t'))); return; }
      const t0 = performance.now();
      const loop = () => { render(((performance.now() - t0) / 1000) % duration); requestAnimationFrame(loop); };
      loop();
    });
  }
  g.Kit = { q, format, W, H, rng, hash, hash2, clamp, lerp, smooth, remap, noise1, noise2, fbm, ease, tween, hex, rgba, mix, fonts, canvas, stage, run, TAU: Math.PI * 2 };
})(window);
