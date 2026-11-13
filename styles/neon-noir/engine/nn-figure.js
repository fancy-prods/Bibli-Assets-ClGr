/* nn-figure.js: figuras do neon-noir. Silhueta escura + luz de recorte; sem rosto desenhado.
 * Unidades locais: origem nos pés, y negativo para cima, altura nominal 400. Olham para +x (use flip para inverter).
 * Cada figura é {x, y, scale, flip, rims, draw({part, t}), emis(ctx,t)}; part(drawFn, rims?) desenha um grupo com rim.
 */
(function (g) {
  const K = g.Kit, NN = g.NN, F = {};
  const COL = { coat: '#15102a', coat2: '#211938', hat: '#0e0a1c', skin: '#32243a', trouser: '#0f0b1e', shoe: '#090712', sax: '#3d2f18' };
  F.COL = COL;
  function capsule(c, x1, y1, r1, x2, y2, r2) {
    const a = Math.atan2(y2 - y1, x2 - x1), nx = -Math.sin(a), ny = Math.cos(a);
    c.beginPath(); c.moveTo(x1 + nx * r1, y1 + ny * r1); c.lineTo(x2 + nx * r2, y2 + ny * r2); c.arc(x2, y2, r2, a + Math.PI / 2, a - Math.PI / 2, true);
    c.lineTo(x1 - nx * r1, y1 - ny * r1); c.arc(x1, y1, r1, a - Math.PI / 2, a + Math.PI / 2, true); c.closePath(); c.fill();
  }
  F.capsule = capsule;
  const pol = (x, y, ang, len) => [x + Math.sin(ang) * len, y + Math.cos(ang) * len]; // ang 0 = para baixo, + = para frente (+x)
  function leg(c, hx, hy, a1, a2, col, l1 = 104, l2 = 104) {
    const [kx, ky] = pol(hx, hy, a1, l1), [ax, ay] = pol(kx, ky, a2, l2);
    c.fillStyle = col; capsule(c, hx, hy, 15, kx, ky, 11); capsule(c, kx, ky, 11, ax, ay, 8);
    c.fillStyle = COL.shoe; c.save(); c.translate(ax, ay); c.rotate(-a2 * 0.5); c.beginPath(); c.moveTo(-11, -8); c.quadraticCurveTo(8, -11, 30, 3); c.lineTo(30, 8); c.lineTo(-12, 8); c.closePath(); c.fill(); c.restore();
    return [ax, ay];
  }
  function arm(c, sx, sy, a1, a2, col, l1 = 74, l2 = 66, hand = true) {
    const [ex, ey] = pol(sx, sy, a1, l1), [hx, hy] = pol(ex, ey, a2, l2);
    c.fillStyle = col; capsule(c, sx, sy, 12.5, ex, ey, 9.5); capsule(c, ex, ey, 9.5, hx, hy, 7.5);
    if (hand) { c.fillStyle = COL.skin; c.beginPath(); c.arc(hx + Math.sin(a2) * 6, hy + Math.cos(a2) * 6, 8, 0, 7); c.fill(); }
    return [hx, hy];
  }
  function head(c, x, y, { hat = 'fedora', hair = null, tilt = 0 } = {}) {
    c.save(); c.translate(x, y); c.rotate(tilt);
    c.fillStyle = COL.skin; c.fillRect(-8, 12, 15, 26);
    c.beginPath(); c.ellipse(1, 0, 19.5, 24, 0, 0, 7); c.fill();
    c.beginPath(); c.moveTo(17, -8); c.quadraticCurveTo(29, 1, 20, 6); c.quadraticCurveTo(23, 14, 15, 20); c.lineTo(8, 8); c.closePath(); c.fill(); // nariz e queixo de perfil
    if (hat === 'fedora') { c.fillStyle = COL.hat; c.beginPath(); c.moveTo(-23, -11); c.quadraticCurveTo(-25, -42, -5, -41); c.quadraticCurveTo(3, -36, 10, -42); c.quadraticCurveTo(26, -40, 25, -11); c.closePath(); c.fill();
      c.save(); c.rotate(-0.08); c.beginPath(); c.ellipse(4, -10, 46, 6.5, 0, 0, 7); c.fill(); c.restore(); c.fillStyle = '#2f2548'; c.fillRect(-23, -20, 48, 6); }
    else if (hat === 'boina') { c.fillStyle = COL.hat; c.beginPath(); c.moveTo(-23, -8); c.quadraticCurveTo(-32, -32, -2, -33); c.quadraticCurveTo(34, -32, 27, -12); c.quadraticCurveTo(0, -18, -23, -8); c.closePath(); c.fill(); }
    else if (hair === 'coque') { c.fillStyle = COL.hat; c.beginPath(); c.ellipse(-2, -6, 23, 22, 0, Math.PI * 0.95, Math.PI * 2.15); c.fill(); c.beginPath(); c.arc(-20, -21, 12, 0, 7); c.fill(); }
    else if (hair === 'curto') { c.fillStyle = COL.hat; c.beginPath(); c.ellipse(0, -6, 23, 22, 0, Math.PI * 0.9, Math.PI * 2.1); c.fill(); }
    c.restore();
  }
  /* sobretudo: ombros largos, cintura marcada, barra abaixo do joelho; sway balança a barra */
  function coat(c, br, sway, { hem = -84, flare = 60 } = {}) {
    c.fillStyle = COL.coat; c.beginPath(); c.moveTo(-12, -350 + br); c.quadraticCurveTo(-44, -346 + br, -48, -312 + br); c.quadraticCurveTo(-46, -262, -36, -226); c.quadraticCurveTo(-46, -150, -flare + sway, hem);
    c.lineTo(flare - 8 + sway, hem + 4); c.quadraticCurveTo(42, -150, 34, -226); c.quadraticCurveTo(46, -264, 44, -312 + br); c.quadraticCurveTo(40, -346 + br, 12, -350 + br); c.closePath(); c.fill();
    c.fillStyle = COL.coat2; c.beginPath(); c.moveTo(-37, -232); c.lineTo(35, -232); c.lineTo(36, -220); c.lineTo(-37, -220); c.closePath(); c.fill(); c.fillRect(6, -222, 3.5, 140);
    c.beginPath(); c.moveTo(-14, -352 + br); c.lineTo(-30, -372 + br); c.lineTo(-22, -334 + br); c.closePath(); c.fill(); c.beginPath(); c.moveTo(10, -352 + br); c.lineTo(31, -368 + br); c.lineTo(22, -326 + br); c.closePath(); c.fill();
  }
  F.parts = { leg, arm, head, pol, coat };

  /* leitor de sobretudo, em pé, lendo um livro aberto (luz do livro no rosto) */
  F.leitor = function ({ x, y, scale = 0.82, flip = false, rims, wrap, bookColor = '#ffd9a0', look = 0 } = {}) {
    return {
      x, y, scale, flip, rims, wrap,
      draw({ part, t }) {
        const br = Math.sin(t * 1.3) * 1.5, sway = Math.sin(t * 0.9) * 4;
        part((c) => { leg(c, -9, -206, -0.03, 0.02, COL.trouser); leg(c, 11, -206, 0.09, -0.04, COL.trouser); });
        part((c) => { arm(c, -30, -326 + br, 0.5, 1.75, COL.coat, 70, 58); });
        part((c) => coat(c, br, sway));
        part((c) => head(c, 4, -380 + br, { hat: 'fedora', tilt: 0.22 - look * 0.3 }));
        part((c) => { // livro aberto, visto de lado
          c.fillStyle = '#2b2140'; c.beginPath(); c.moveTo(48, -270 + br); c.lineTo(92, -300 + br); c.lineTo(96, -294 + br); c.lineTo(52, -262 + br); c.closePath(); c.fill();
          c.beginPath(); c.moveTo(48, -270 + br); c.lineTo(20, -308 + br); c.lineTo(15, -303 + br); c.lineTo(44, -262 + br); c.closePath(); c.fill();
        });
        part((c) => { arm(c, 30, -324 + br, 0.35, 1.9, COL.coat, 66, 44); });
      },
      emis(c, t) { // páginas acesas + clarão no rosto
        const br = Math.sin(t * 1.3) * 1.5, fl = 0.9 + 0.1 * Math.sin(t * 5.1);
        c.globalAlpha = fl; c.fillStyle = bookColor; c.beginPath(); c.moveTo(50, -274 + br); c.lineTo(90, -302 + br); c.lineTo(88, -306 + br); c.lineTo(48, -278 + br); c.closePath(); c.fill();
        c.beginPath(); c.moveTo(46, -276 + br); c.lineTo(22, -309 + br); c.lineTo(25, -312 + br); c.lineTo(49, -279 + br); c.closePath(); c.fill();
        const gr = c.createRadialGradient(52, -308 + br, 0, 52, -308 + br, 120); gr.addColorStop(0, K.rgba(bookColor, 0.42 * fl)); gr.addColorStop(1, K.rgba(bookColor, 0)); c.fillStyle = gr; c.fillRect(-90, -440, 290, 290);
      },
    };
  };

  /* saxofonista em pé, tronco inclinado para trás, joelhos marcando o compasso */
  F.saxofonista = function ({ x, y, scale = 0.82, flip = false, rims, wrap, saxRim } = {}) {
    return {
      x, y, scale, flip, rims, wrap,
      draw({ part, t }) {
        const beat = t * 2.1, sw = Math.sin(beat) * 0.04, br = Math.sin(beat + 1) * 2, dip = (1 - Math.cos(beat * 2)) * 2.5;
        const rot = (c) => { c.translate(0, -206 + dip); c.rotate(-0.13 + sw); c.translate(0, 206); };
        part((c) => { leg(c, -8, -206 + dip, -0.14 - dip * 0.012, 0.04 + dip * 0.03, COL.trouser); });
        part((c) => { leg(c, 8, -206 + dip, 0.3 + dip * 0.02, -0.34 - dip * 0.045, COL.trouser); });
        part((c) => { rot(c); arm(c, -28, -326 + br, 0.8, 1.45, COL.coat, 62, 54, false); });
        part((c) => { rot(c); // paletó
          c.fillStyle = COL.coat; c.beginPath(); c.moveTo(-12, -350 + br); c.quadraticCurveTo(-44, -346 + br, -48, -312 + br); c.quadraticCurveTo(-46, -250, -40, -186); c.lineTo(34, -182); c.quadraticCurveTo(44, -260, 42, -312 + br); c.quadraticCurveTo(38, -346 + br, 12, -350 + br); c.closePath(); c.fill();
          c.fillStyle = COL.coat2; c.beginPath(); c.moveTo(4, -350 + br); c.lineTo(28, -336 + br); c.lineTo(12, -272); c.closePath(); c.fill();
        });
        part((c) => { rot(c); head(c, 6, -380 + br, { hat: 'boina', tilt: 0.16 }); });
        part((c) => { rot(c); // sax: tubo curvo da boca até a campana
          c.strokeStyle = COL.sax; c.lineCap = 'round'; c.lineJoin = 'round';
          c.lineWidth = 6; c.beginPath(); c.moveTo(27, -370 + br); c.quadraticCurveTo(50, -368 + br, 54, -340 + br); c.stroke();
          c.lineWidth = 11; c.beginPath(); c.moveTo(54, -342 + br); c.quadraticCurveTo(62, -270, 68, -222); c.quadraticCurveTo(74, -184, 100, -192); c.stroke();
          c.lineWidth = 22; c.beginPath(); c.moveTo(96, -192); c.lineTo(114, -216); c.stroke();
          c.fillStyle = COL.sax; c.beginPath(); c.ellipse(120, -224, 24, 11, -0.9, 0, 7); c.fill();
        }, saxRim);
        part((c) => { rot(c); arm(c, 28, -324 + br, 0.5, 1.15, COL.coat, 58, 46); });
      },
    };
  };

  /* passante de guarda-chuva (caminha) */
  F.passante = function ({ x, y, scale = 1.5, flip = false, rims, wrap, speed = 1.6, umbrella = '#161226' } = {}) {
    return {
      x, y, scale, flip, rims, wrap,
      draw({ part, t }) {
        const ph = t * speed * Math.PI, s = Math.sin(ph), bob = Math.abs(Math.cos(ph)) * 5;
        part((c) => { leg(c, -8, -206 + bob, -s * 0.45, -Math.max(0, s) * 0.5 + 0.02, COL.trouser); });
        part((c) => { leg(c, 8, -206 + bob, s * 0.45, -Math.max(0, -s) * 0.5 + 0.02, COL.trouser); });
        part((c) => { arm(c, -28, -326 + bob, -s * 0.3, 0.25, COL.coat); });
        part((c) => coat(c, bob, -s * 6, { hem: -104 + bob }));
        part((c) => head(c, 4, -380 + bob, { hat: null, hair: 'coque', tilt: 0.06 }));
        part((c) => { arm(c, 30, -324 + bob, 0.5, 2.6, COL.coat, 60, 50); });
        part((c) => { c.strokeStyle = '#0b0914'; c.lineWidth = 5; c.beginPath(); c.moveTo(66, -338 + bob); c.lineTo(60, -528 + bob); c.stroke();
          c.fillStyle = umbrella; c.beginPath(); c.moveTo(-82, -478 + bob); c.quadraticCurveTo(-60, -574 + bob, 58, -574 + bob); c.quadraticCurveTo(178, -568 + bob, 198, -470 + bob);
          for (let i = 0; i < 5; i++) { const x1 = 198 - i * 56, x2 = x1 - 56; c.quadraticCurveTo((x1 + x2) / 2, -496 + bob, x2, -474 + bob + (i === 4 ? -4 : 0)); } c.closePath(); c.fill(); });
      },
    };
  };
  /* gato sentado (silhueta com olhos acesos) */
  F.gato = function ({ x, y, scale = 0.5, flip = false, rims, wrap, eyes = '#b6ff3c' } = {}) {
    return { x, y, scale, flip, rims, wrap, noReflect: true, noShadow: true,
      draw({ part, t }) { part((c) => { c.fillStyle = '#0d0a18'; c.beginPath(); c.ellipse(0, -52, 40, 54, 0, 0, 7); c.fill(); c.beginPath(); c.arc(16, -118, 30, 0, 7); c.fill();
        c.beginPath(); c.moveTo(-8, -138); c.lineTo(-2, -166); c.lineTo(16, -146); c.closePath(); c.fill(); c.beginPath(); c.moveTo(22, -146); c.lineTo(40, -164); c.lineTo(44, -134); c.closePath(); c.fill();
        c.strokeStyle = '#0d0a18'; c.lineWidth = 11; c.lineCap = 'round'; c.beginPath(); c.moveTo(-34, -14); c.quadraticCurveTo(-84, -8, -74 + Math.sin(t * 1.4) * 10, -70); c.stroke(); }); },
      emis(c, t) { const bl = (t % 3.7) < 0.12 ? 0 : 1; c.globalAlpha = bl; c.fillStyle = eyes; c.beginPath(); c.ellipse(10, -120, 5, 6.5, 0, 0, 7); c.ellipse(30, -120, 5, 6.5, 0, 0, 7); c.fill(); },
    };
  };
  /* caixa de diálogo: texto digitado, palavras com cor e tremor. segs: [{text, color?, shake?}] */
  NN.dialog = function (ctx, t, { x, y, w, h, speaker, color = NN.PAL.cyan, segs, t0 = 0, cps = 34, font = '500 44px "Chakra Petch"', lineH = 58 }) {
    const k = K.ease.outCubic(K.clamp((t - t0) / 0.28)); if (k <= 0) return;
    ctx.save(); ctx.globalAlpha = k; ctx.translate(x + w / 2, y + h / 2); ctx.scale(1, 0.6 + 0.4 * k); ctx.translate(-w / 2, -h / 2);
    ctx.fillStyle = 'rgba(8,5,20,0.86)'; ctx.beginPath(); ctx.roundRect(0, 0, w, h, 6); ctx.fill(); ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke();
    ctx.fillStyle = color; ctx.fillRect(0, 0, 8, h);
    if (speaker) { ctx.font = '700 26px "Chakra Petch"'; const sw = ctx.measureText(speaker).width + 36; ctx.fillStyle = color; ctx.beginPath(); ctx.roundRect(28, -22, sw, 40, 4); ctx.fill(); ctx.fillStyle = '#0b0818'; ctx.textBaseline = 'middle'; ctx.fillText(speaker, 46, -1); }
    ctx.font = font; ctx.textBaseline = 'alphabetic'; let n = Math.floor(Math.max(0, t - t0 - 0.2) * cps), cx = 44, cy = 70; const maxW = w - 80;
    for (const s of segs) for (const word of s.text.split(/(\s+)/)) {
      if (!word) continue; const ww = ctx.measureText(word).width; if (/^\s+$/.test(word)) { cx += ww; n -= 1; continue; }
      if (cx + ww > 44 + maxW) { cx = 44; cy += lineH; }
      let px = cx; for (let i = 0; i < word.length && n > 0; i++, n--) { const ch = word[i], sh = s.shake ? [Math.sin(t * 31 + i * 1.7 + px) * 2.2, Math.cos(t * 27 + i * 2.3) * 2.6] : [0, 0];
        ctx.fillStyle = s.color || '#efe9ff'; if (s.color) { ctx.shadowColor = s.color; ctx.shadowBlur = 14; } ctx.fillText(ch, px + sh[0], cy + sh[1]); ctx.shadowBlur = 0; px += ctx.measureText(ch).width; }
      cx += ww;
    }
    const done = n > 0; if (done && (t * 2.5) % 1 < 0.6) { ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(w - 46, h - 34); ctx.lineTo(w - 26, h - 34); ctx.lineTo(w - 36, h - 20); ctx.closePath(); ctx.fill(); }
    ctx.restore();
  };
  /* HUD de fita: PLAY + timecode */
  NN.hud = function (ctx, t, { label = 'PLAY', tc0 = 0, color = '#e9e4ff' } = {}) {
    ctx.save(); ctx.font = '400 34px "Share Tech Mono"'; ctx.fillStyle = color; ctx.globalAlpha = 0.72; ctx.textBaseline = 'middle';
    ctx.beginPath(); ctx.moveTo(70, 58); ctx.lineTo(70, 86); ctx.lineTo(94, 72); ctx.closePath(); ctx.fill(); ctx.fillText(label, 108, 74);
    const s = tc0 + t, pad = (v) => String(Math.floor(v)).padStart(2, '0'); ctx.textAlign = 'right'; ctx.fillText(`SP  ${pad(s / 3600)}:${pad(s / 60 % 60)}:${pad(s % 60)}:${pad((s % 1) * 30)}`, K.W - 70, 74);
    ctx.restore();
  };
  NN.Fig = F;
})(window);
