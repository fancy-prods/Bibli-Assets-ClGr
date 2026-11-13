/* maquete.js: motor do estilo "maquete" (diorama isométrico em miniatura, Three.js).
 * Módulo ES. Importa three pelo import map da página. Depende de shared/web/kit.js (global Kit).
 *
 * createStage(view2d) -> { scene, root, camera, render(t, overlayFn), ... }
 * O WebGL é desenhado fora da tela e composto num canvas 2D: desfoque tilt-shift, vinheta, grão e textos.
 */
import * as THREE from 'three';
import { RoundedBoxGeometry } from '../../../shared/vendor/three/RoundedBoxGeometry.js';
const K = window.Kit;

export const PAL = {
  fundo: '#f4d9c6', fundo2: '#e9b9a4', base: '#b98a63', piso: '#e3bf95', piso2: '#d8b084', parede: '#f6ecdf', parede2: '#eadccb',
  coral: '#f0725a', mostarda: '#f2b441', turquesa: '#35a79c', marinho: '#2d3f73', ameixa: '#8a4f7d', folha: '#5aa469', creme: '#fbf3e4', grafite: '#3b3a42', madeira: '#a9744f', madeira2: '#8a5a3c', pele: ['#f2c9a5', '#d99a6c', '#8d5a3b', '#f7dcc4'],
};
const matCache = new Map();
export function mat(color, { rough = 0.92, emissive = null, ei = 1, flat = false } = {}) {
  const key = color + rough + emissive + ei + flat; if (matCache.has(key)) return matCache.get(key);
  const m = new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0, flatShading: flat }); if (emissive) { m.emissive = new THREE.Color(emissive); m.emissiveIntensity = ei; }
  matCache.set(key, m); return m;
}
const sh = (m, cast = true, recv = true) => { m.castShadow = cast; m.receiveShadow = recv; return m; };
/* caixa de cantos arredondados, apoiada no chão (origem na base, centro em x/z) */
export function box(w, h, d, color, { r = 0.05, x = 0, y = 0, z = 0, ry = 0, opts } = {}) {
  const g = new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2 - 1e-3, h / 2 - 1e-3, d / 2 - 1e-3)); g.translate(0, h / 2, 0);
  const m = sh(new THREE.Mesh(g, mat(color, opts))); m.position.set(x, y, z); m.rotation.y = ry; return m;
}
export function cyl(rt, rb, h, color, { x = 0, y = 0, z = 0, seg = 28, opts } = {}) { const g = new THREE.CylinderGeometry(rt, rb, h, seg); g.translate(0, h / 2, 0); const m = sh(new THREE.Mesh(g, mat(color, opts))); m.position.set(x, y, z); return m; }
export function ball(r, color, { x = 0, y = 0, z = 0, opts, sy = 1 } = {}) { const m = sh(new THREE.Mesh(new THREE.SphereGeometry(r, 28, 20), mat(color, opts))); m.position.set(x, y, z); m.scale.y = sy; return m; }
export function group(...kids) { const g = new THREE.Group(); kids.forEach((k) => g.add(k)); return g; }

/* ---------- boneco-pino: corpo cônico, cabeça esférica, cabelo em calota; sem boca, dois pontinhos de olho ---------- */
export function pino({ body = PAL.coral, skin = PAL.pele[0], hair = PAL.grafite, hat = null, sit = false, book = null, s = 1 } = {}) {
  const g = new THREE.Group(), h = sit ? 0.42 : 0.62;
  const torso = cyl(0.13, sit ? 0.2 : 0.25, h, body, { seg: 24 }); g.add(torso);
  const sho = ball(0.13, body, { y: h, sy: 0.6 }); g.add(sho);
  const head = new THREE.Group(); head.position.y = h + 0.2; g.add(head);
  head.add(ball(0.19, skin));
  const hg = new THREE.SphereGeometry(0.2, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.52); const hm = sh(new THREE.Mesh(hg, mat(hair))); hm.rotation.x = -0.28; hm.position.y = 0.012; head.add(hm);
  for (const sx of [-0.07, 0.07]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.022, 10, 8), mat('#2a2530', { rough: 0.4 })); e.position.set(sx, -0.01, 0.178); head.add(e); }
  if (hat) { head.add(cyl(0.16, 0.2, 0.1, hat, { y: 0.13 })); head.add(cyl(0.27, 0.27, 0.025, hat, { y: 0.12 })); }
  const arms = [];
  for (const sx of [-1, 1]) { const a = new THREE.Group(); a.position.set(sx * 0.15, h - 0.04, 0); const am = sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.045, 0.2, 4, 10), mat(body))); am.position.y = -0.13; a.add(am); const hand = ball(0.05, skin, { y: -0.27 }); a.add(hand); a.rotation.z = sx * 0.22; g.add(a); arms.push(a); }
  if (sit) for (const sx of [-0.08, 0.08]) { const l = sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.26, 4, 10), mat(PAL.marinho))); l.rotation.x = Math.PI / 2; l.position.set(sx, 0.07, 0.24); g.add(l); const f = ball(0.07, PAL.grafite, { x: sx, y: 0.02, z: 0.42, sy: 0.7 }); g.add(f); }
  let bk = null;
  if (book) { bk = new THREE.Group(); const c1 = box(0.2, 0.025, 0.26, book, { r: 0.008 }), c2 = box(0.2, 0.025, 0.26, book, { r: 0.008 }), p1 = box(0.18, 0.02, 0.24, PAL.creme, { r: 0.005, y: 0.02 }), p2 = box(0.18, 0.02, 0.24, PAL.creme, { r: 0.005, y: 0.02 });
    const L = group(c1, p1), R = group(c2, p2); L.position.x = -0.1; R.position.x = 0.1; L.rotation.z = -0.3; R.rotation.z = 0.3; bk.add(L, R); bk.position.set(0, h - 0.2, 0.3); bk.rotation.x = 0.9; g.add(bk); arms.forEach((a, i) => { a.rotation.x = -1.0; a.rotation.z = (i ? 1 : -1) * -0.25; }); }
  g.scale.setScalar(s); g.userData = { head, arms, book: bk, torso }; return g;
}
/* ---------- móveis ---------- */
export function estante(w, h, d, { rows = 4, color = PAL.madeira, seed = 3, cores = [PAL.coral, PAL.mostarda, PAL.turquesa, PAL.marinho, PAL.ameixa, PAL.creme, PAL.folha] } = {}) {
  const g = new THREE.Group(), t = 0.07, r = K.rng(seed); g.userData.books = [];
  g.add(box(w, h, 0.04, PAL.madeira2, { r: 0.01, z: -d / 2 + 0.02 })); g.add(box(t, h, d, color, { r: 0.015, x: -w / 2 + t / 2 })); g.add(box(t, h, d, color, { r: 0.015, x: w / 2 - t / 2 }));
  const rh = (h - t) / rows;
  for (let i = 0; i <= rows; i++) g.add(box(w, t, d, color, { r: 0.015, y: i * rh }));
  for (let i = 0; i < rows; i++) { let x = -w / 2 + t + 0.03; const y = i * rh + t;
    while (x < w / 2 - t - 0.1) { const bw = r.range(0.055, 0.12), bh = r.range(rh * 0.5, rh * 0.82), bd = r.range(d * 0.6, d * 0.85);
      if (r.chance(0.1)) { x += r.range(0.08, 0.2); continue; }
      if (r.chance(0.1) && x + 0.3 < w / 2 - t) { for (let k = 0; k < r.int(2, 4); k++) { const b = box(0.3, 0.06, bd, r.pick(cores), { r: 0.012, x: x + 0.15, y: y + k * 0.062, z: 0.02 }); g.add(b); g.userData.books.push(b); } x += 0.34; continue; }
      const b = box(bw, bh, bd, r.pick(cores), { r: 0.012, x: x + bw / 2, y, z: 0.02 }); if (r.chance(0.08)) b.rotation.z = -0.22; g.add(b); g.userData.books.push(b); x += bw + 0.008; } }
  return g;
}
export function poltrona(color = PAL.turquesa) {
  const g = new THREE.Group(); g.add(box(0.95, 0.3, 0.85, color, { r: 0.1, y: 0.1 })); g.add(box(0.95, 0.75, 0.24, color, { r: 0.1, y: 0.1, z: -0.36 }));
  g.add(box(0.2, 0.5, 0.8, color, { r: 0.09, y: 0.1, x: -0.44 })); g.add(box(0.2, 0.5, 0.8, color, { r: 0.09, y: 0.1, x: 0.44 })); g.add(box(0.6, 0.12, 0.56, PAL.creme, { r: 0.05, y: 0.37, z: 0.04 }));
  for (const [x, z] of [[-0.38, -0.32], [0.38, -0.32], [-0.38, 0.32], [0.38, 0.32]]) g.add(cyl(0.035, 0.03, 0.1, PAL.madeira2, { x, z })); return g;
}
export function luminaria(color = PAL.mostarda) {
  const g = new THREE.Group(); g.add(cyl(0.2, 0.22, 0.04, PAL.grafite)); g.add(cyl(0.02, 0.02, 1.7, PAL.grafite, { seg: 10 }));
  const shade = cyl(0.16, 0.3, 0.34, color, { y: 1.62, opts: { emissive: '#ffcf70', ei: 0.0 } }); shade.material = shade.material.clone(); g.add(shade);
  const bulb = ball(0.08, '#fff2c8', { y: 1.62, opts: { emissive: '#ffe3a0', ei: 0 } }); bulb.material = bulb.material.clone(); bulb.castShadow = false; g.add(bulb);
  const light = new THREE.PointLight('#ffc466', 0, 5.5, 1.6); light.position.y = 1.55; g.add(light);
  g.userData = { on(k) { light.intensity = 9 * k; shade.material.emissiveIntensity = 0.75 * k; bulb.material.emissiveIntensity = 2.2 * k; } }; return g;
}
export function mesa(r = 0.5, h = 0.45, color = PAL.madeira) { const g = new THREE.Group(); g.add(cyl(r, r, 0.06, color, { y: h - 0.06, seg: 36 })); for (let i = 0; i < 3; i++) { const a = i / 3 * Math.PI * 2; g.add(cyl(0.03, 0.025, h - 0.06, PAL.madeira2, { x: Math.cos(a) * r * 0.6, z: Math.sin(a) * r * 0.6, seg: 10 })); } return g; }
export function pilha(n = 4, seed = 2, cores = [PAL.coral, PAL.mostarda, PAL.turquesa, PAL.marinho, PAL.ameixa]) { const g = new THREE.Group(), r = K.rng(seed); for (let i = 0; i < n; i++) { const b = box(r.range(0.3, 0.38), 0.07, r.range(0.22, 0.27), cores[(i + seed) % cores.length], { r: 0.014, y: i * 0.072, ry: r.range(-0.25, 0.25) }); g.add(b); } return g; }
export function caneca(color = PAL.creme) { const g = new THREE.Group(); g.add(cyl(0.07, 0.06, 0.13, color, { seg: 20 })); const h = sh(new THREE.Mesh(new THREE.TorusGeometry(0.04, 0.012, 8, 16), mat(color))); h.position.set(0.075, 0.07, 0); g.add(h); const c = cyl(0.058, 0.058, 0.005, '#6b4226', { y: 0.122 }); c.castShadow = false; g.add(c); return g; }
export function planta(s = 1) { const g = new THREE.Group(); g.add(cyl(0.2, 0.15, 0.3, PAL.coral)); g.add(cyl(0.21, 0.21, 0.05, PAL.coral, { y: 0.28 })); g.add(cyl(0.17, 0.17, 0.02, '#5b4030', { y: 0.31 }));
  const r = K.rng(8); g.userData.leaves = []; for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2 + r() * 0.4, l = new THREE.Group(), lg = new THREE.SphereGeometry(0.13, 14, 10); lg.scale(0.45, 1.5, 0.14); lg.translate(0, 0.2, 0); const lm = sh(new THREE.Mesh(lg, mat(i % 3 ? PAL.folha : '#7cc08a'))); l.add(lm); l.position.y = 0.3; l.rotation.y = a; l.rotation.x = 0.35 + r() * 0.75; l.scale.setScalar(0.9 + r() * 0.9); g.add(l); g.userData.leaves.push(l); }
  g.scale.setScalar(s); return g; }
export function tapete(r, color = PAL.creme, color2 = PAL.coral) { const g = new THREE.Group(); const a = cyl(r, r, 0.03, color, { seg: 48 }); a.castShadow = false; g.add(a); const b = new THREE.Mesh(new THREE.RingGeometry(r * 0.72, r * 0.82, 48), mat(color2)); b.rotation.x = -Math.PI / 2; b.position.y = 0.032; b.receiveShadow = true; g.add(b); const c = new THREE.Mesh(new THREE.RingGeometry(r * 0.3, r * 0.36, 48), mat(color2)); c.rotation.x = -Math.PI / 2; c.position.y = 0.032; c.receiveShadow = true; g.add(c); return g; }
export function quadro(w, h, color, art = PAL.mostarda) { const g = new THREE.Group(); g.add(box(w, h, 0.05, PAL.madeira2, { r: 0.012 })); const a = box(w - 0.12, h - 0.12, 0.02, PAL.creme, { r: 0.004, y: 0.06, z: 0.02 }); g.add(a); const c = ball(Math.min(w, h) * 0.2, art, { y: h * 0.55, z: 0.03 }); c.scale.z = 0.12; g.add(c); g.add(box(w * 0.5, h * 0.18, 0.02, color, { r: 0.004, y: 0.12, z: 0.03 })); return g; }
/* janela na parede (moldura + vidro emissivo) e a mancha de luz que ela joga no piso */
export function janela(w, h) { const g = new THREE.Group(); g.add(box(w + 0.16, h + 0.16, 0.08, PAL.creme, { r: 0.02 })); const pane = box(w, h, 0.04, '#bfe6f2', { r: 0.005, y: 0.08, z: 0.03, opts: { emissive: '#fff1c4', ei: 0.9, rough: 0.4 } }); pane.castShadow = false; g.add(pane); g.add(box(0.05, h, 0.06, PAL.creme, { r: 0.01, y: 0.08, z: 0.04 })); g.add(box(w, 0.05, 0.06, PAL.creme, { r: 0.01, y: 0.08 + h / 2 - 0.025, z: 0.04 })); g.add(box(w + 0.3, 0.06, 0.2, PAL.creme, { r: 0.02, y: -0.02, z: 0.08 })); return g; }
export function manchaDeLuz(w, d, skew = 0.6, color = '#fff0c0', a = 0.5) { const s = new THREE.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(w / 2 + skew, d); s.lineTo(-w / 2 + skew, d); const m = new THREE.Mesh(new THREE.ShapeGeometry(s), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: a, blending: THREE.AdditiveBlending, depthWrite: false })); m.rotation.x = -Math.PI / 2; m.position.y = 0.045; m.userData.a = a; return m; }
/* sala em corte: base, piso de tábuas e duas paredes de fundo (x = -L/2 e z = -L/2) */
export function sala(L = 6, hWall = 3.1, { piso = [PAL.piso, PAL.piso2], parede = PAL.parede, base = PAL.base } = {}) {
  const g = new THREE.Group(); g.add(box(L + 0.5, 0.45, L + 0.5, base, { r: 0.08, y: -0.5 }));
  const n = 10, pw = L / n; for (let i = 0; i < n; i++) { const p = box(pw - 0.012, 0.06, L, piso[i % 2], { r: 0.01, x: -L / 2 + pw / 2 + i * pw, y: -0.05 }); p.castShadow = false; g.add(p); }
  const wa = box(0.22, hWall, L + 0.22, parede, { r: 0.03, x: -L / 2 - 0.11, y: -0.05, z: -0.11 }), wb = box(L, hWall, 0.22, parede, { r: 0.03, z: -L / 2 - 0.11, y: -0.05 });
  g.add(wa, wb); g.add(box(0.06, 0.16, L, PAL.parede2, { r: 0.02, x: -L / 2 + 0.03, z: 0 })); g.add(box(L, 0.16, 0.06, PAL.parede2, { r: 0.02, z: -L / 2 + 0.03 }));
  g.userData = { walls: [wa, wb] }; return g;
}
/* etiqueta flutuante (cartão com texto, sempre de frente para a câmera) com haste */
export function etiqueta(text, { color = PAL.marinho, fg = PAL.creme, font = '700 54px Fredoka', h = 0.34 } = {}) {
  const c = document.createElement('canvas'), x = c.getContext('2d'); x.font = font; const tw = x.measureText(text).width; c.width = Math.ceil(tw + 70); c.height = 96;
  x.fillStyle = color; x.beginPath(); x.roundRect(0, 0, c.width, c.height, 30); x.fill(); x.font = font; x.fillStyle = fg; x.textBaseline = 'middle'; x.textAlign = 'center'; x.fillText(text, c.width / 2, c.height / 2 + 3);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true })); sp.scale.set(h * c.width / c.height, h, 1); sp.renderOrder = 10;
  const g = new THREE.Group(); g.add(sp); const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.5, 6), new THREE.MeshBasicMaterial({ color })); stem.position.y = -0.42; g.add(stem); const dot = new THREE.Mesh(new THREE.SphereGeometry(0.04, 10, 8), new THREE.MeshBasicMaterial({ color })); dot.position.y = -0.68; g.add(dot); return g;
}

/* ---------- animação ---------- */
/* brota do chão: escala em Y (e um pouco em XZ) com sobra; k<=0 some */
export function brota(obj, t, t0, dur = 0.5) { const k = K.clamp((t - t0) / dur); obj.visible = k > 0; if (!obj.visible) return; const e = K.ease.outBack(k); obj.scale.set(obj.userData.s0 ? obj.userData.s0 * (0.6 + 0.4 * e) : 0.6 + 0.4 * e, (obj.userData.s0 || 1) * Math.max(0.001, e), obj.userData.s0 ? obj.userData.s0 * (0.6 + 0.4 * e) : 0.6 + 0.4 * e); }
/* cai do alto e quica */
export function cai(obj, t, t0, y0 = 0, hgt = 2.2, dur = 0.7) { const k = K.clamp((t - t0) / dur); obj.visible = k > 0; if (!obj.visible) return; const b = k < 0.55 ? 1 - Math.pow(k / 0.55, 2) : Math.abs(Math.sin((k - 0.55) / 0.45 * Math.PI)) * 0.12 * (1 - k); obj.position.y = y0 + hgt * (k < 0.55 ? b : b * 1); const sq = k > 0.5 && k < 0.7 ? 1 - Math.sin((k - 0.5) / 0.2 * Math.PI) * 0.18 : 1; obj.scale.y = (obj.userData.s0 || 1) * sq; }
/* pulinhos ao andar: devolve o y do salto dado o progresso (0..1) e o nº de pulos */
export const pulo = (p, n, h = 0.16) => Math.abs(Math.sin(p * n * Math.PI)) * h;

/* ---------- palco ---------- */
export function createStage(view, { W = K.W, H = K.H, span = 9.4, target = [0, 1.15, 0], fundo = [PAL.fundo, PAL.fundo2], shadow = 2048 } = {}) {
  view.width = W; view.height = H; const out = view.getContext('2d');
  const glc = document.createElement('canvas'); glc.width = W; glc.height = H;
  const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false); renderer.setPixelRatio(1); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.08; renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene(), root = new THREE.Group(); scene.add(root);
  const asp = W / H, camera = new THREE.OrthographicCamera(-span * asp / 2, span * asp / 2, span / 2, -span / 2, 0.1, 100);
  camera.position.set(target[0] + 12, target[1] + 12 * Math.tan(THREE.MathUtils.degToRad(33)) * Math.SQRT2, target[2] + 12); camera.lookAt(...target);
  scene.add(new THREE.HemisphereLight('#fff4e6', '#c98f78', 1.15));
  const key = new THREE.DirectionalLight('#fff0dc', 2.3); key.position.set(4.5, 11, 9.5); key.castShadow = true; key.shadow.mapSize.set(shadow, shadow); const sc = key.shadow.camera; sc.left = -7; sc.right = 7; sc.top = 7; sc.bottom = -7; sc.near = 1; sc.far = 40; key.shadow.radius = 5; key.shadow.blurSamples = 16; key.shadow.bias = -0.0006; key.shadow.normalBias = 0.03; scene.add(key);
  const fill = new THREE.DirectionalLight('#bcd4ff', 0.5); fill.position.set(-8, 5, 6); scene.add(fill);
  // texturas 2D do compositor
  const blurC = K.canvas(W, H), bx = blurC.getContext('2d'), maskC = K.canvas(W, H), mx = maskC.getContext('2d');
  const grainC = K.canvas(W / 2, H / 2); { const x = grainC.getContext('2d'), id = x.createImageData(W / 2, H / 2), d = id.data, r = K.rng(4); for (let i = 0; i < d.length; i += 4) { const v = r(); d[i] = d[i + 1] = d[i + 2] = v > 0.5 ? 255 : 0; d[i + 3] = Math.abs(v - 0.5) * 34; } x.putImageData(id, 0, 0); }
  function render(t, { overlay = null, focusY = 0.56, band = 0.2, blur = 7, under = null } = {}) {
    renderer.render(scene, camera);
    out.setTransform(1, 0, 0, 1, 0, 0); out.globalAlpha = 1; out.globalCompositeOperation = 'source-over'; out.filter = 'none';
    const bg = out.createRadialGradient(W * 0.5, H * 0.52, 80, W * 0.5, H * 0.52, W * 0.72); bg.addColorStop(0, fundo[0]); bg.addColorStop(1, fundo[1]); out.fillStyle = bg; out.fillRect(0, 0, W, H);
    if (under) under(out, t);
    out.drawImage(glc, 0, 0);
    // tilt-shift: cópia borrada, mascarada por gradiente vertical (nítido na faixa de foco)
    bx.setTransform(1, 0, 0, 1, 0, 0); bx.globalCompositeOperation = 'copy'; bx.filter = `blur(${blur}px)`; bx.drawImage(view, 0, 0); bx.filter = 'none';
    const g = bx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(Math.max(0, focusY - band), 'rgba(0,0,0,0)'); g.addColorStop(Math.min(1, focusY + band), 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,1)');
    bx.globalCompositeOperation = 'destination-in'; bx.fillStyle = g; bx.fillRect(0, 0, W, H); out.drawImage(blurC, 0, 0);
    const v = out.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.72); v.addColorStop(0, 'rgba(90,40,30,0)'); v.addColorStop(1, 'rgba(90,40,30,0.3)'); out.fillStyle = v; out.fillRect(0, 0, W, H);
    out.globalCompositeOperation = 'overlay'; out.globalAlpha = 0.55; out.drawImage(grainC, (Math.floor(t * 12) * 37) % 60 - 60, (Math.floor(t * 12) * 53) % 40 - 40, W + 60, H + 40); out.globalAlpha = 1; out.globalCompositeOperation = 'source-over';
    if (overlay) overlay(out, t);
  }
  return { THREE, renderer, scene, root, camera, key, render };
}
/* cartão de título 2D (por cima da maquete) */
export function titulo(x, t, { t0 = 0, kicker, lines, px = 110, py = 760, color = PAL.marinho, chip = PAL.coral, size = 92 } = {}) {
  const k = K.ease.outCubic(K.clamp((t - t0) / 0.5)); if (k <= 0) return; x.save(); x.globalAlpha = k; x.translate(0, (1 - k) * 30);
  if (kicker) { x.font = '700 30px Fredoka'; x.letterSpacing = '3px'; const w = x.measureText(kicker).width + 44; x.fillStyle = chip; x.beginPath(); x.roundRect(px, py - 62, w, 50, 25); x.fill(); x.fillStyle = PAL.creme; x.textBaseline = 'middle'; x.fillText(kicker, px + 22, py - 35); x.letterSpacing = '0px'; }
  x.font = `700 ${size}px Fredoka`; x.fillStyle = color; x.textBaseline = 'alphabetic'; lines.forEach((l, i) => { const kk = K.ease.outBack(K.clamp((t - t0 - 0.12 - i * 0.14) / 0.45)); x.globalAlpha = Math.min(1, kk * 1.4) * k; x.fillText(l, px, py + size * 0.86 + i * size * 1.04 + (1 - kk) * 26); }); x.restore();
}
