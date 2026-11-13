#!/usr/bin/env node
/* render.cjs: renderiza uma demo web (contrato do kit.js) em PNG/JPG (um quadro) ou MP4 (sequência).
 *
 *   node shared/web/render.cjs styles/<estilo>/demo/demo.html -o out.mp4            # vídeo inteiro
 *   node shared/web/render.cjs styles/<estilo>/demo/demo.html -o quadro.png -t 3.2  # um quadro
 *   opções: --format 16x9|9x16   --scale 1 (1 = 1920×1080; 0.6667 = 1280×720)   --fps N   --from s --to s
 *           --crf 18   --jobs N (páginas em paralelo)   --quality 92 (JPG)
 * Usa o Chromium do Playwright (WebGL por SwiftShader) e o ffmpeg do sistema. Determinístico.
 */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const html = args[0], out = opt('-o', 'out.mp4');
if (!html) { console.error('uso: render.cjs demo.html -o saida.(mp4|png|jpg) [-t s]'); process.exit(1); }
const root = path.resolve(__dirname, '..', '..');
const format = opt('--format', '16x9'), scale = parseFloat(opt('--scale', '1'));
const W = format === '9x16' ? 1080 : 1920, H = format === '9x16' ? 1920 : 1080;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.glsl': 'text/plain' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
});
(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/${path.relative(root, path.resolve(html)).split(path.sep).join('/')}?driven=1&format=${format}`;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-accelerated-2d-canvas', '--disable-lcd-text', '--font-render-hinting=none'] });
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
    page.on('pageerror', (e) => console.error('[pageerror]', e.message));
    page.on('console', (m) => { if (m.type() === 'error') console.error('[console]', m.text()); });
    page.setDefaultTimeout(300000); await page.goto(url); await page.waitForFunction(() => window.READY); await page.evaluate(() => window.READY);
    return page;
  };
  const still = /\.(png|jpe?g)$/i.test(out);
  const shot = async (page, t) => {
    await page.evaluate((tt) => window.renderFrame(tt), t);
    return page.screenshot(still && /png$/i.test(out) ? { type: 'png' } : { type: 'jpeg', quality: parseInt(opt('--quality', still ? '92' : '96')) });
  };
  const first = await open();
  const demo = await first.evaluate(() => window.DEMO);
  if (still) {
    fs.writeFileSync(out, await shot(first, parseFloat(opt('-t', '0'))));
  } else {
    const fps = parseFloat(opt('--fps', demo.fps)), from = parseFloat(opt('--from', '0')), to = parseFloat(opt('--to', demo.duration));
    const n = Math.round((to - from) * fps), jobs = Math.max(1, parseInt(opt('--jobs', '3')));
    const pages = [first, ...(await Promise.all(Array.from({ length: jobs - 1 }, open)))];
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', opt('--crf', '18'), '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const bufs = new Array(n); let next = 0, written = 0;
    const flush = async () => { while (written < n && bufs[written]) { if (!ff.stdin.write(bufs[written])) await new Promise((r) => ff.stdin.once('drain', r)); bufs[written] = null; written++; } };
    let chain = Promise.resolve();
    await Promise.all(pages.map(async (page) => {
      while (next < n) { const i = next++; bufs[i] = await shot(page, from + i / fps); chain = chain.then(flush); await chain; if (i % 30 === 0) process.stderr.write(`\r${i}/${n}`); }
    }));
    await chain; ff.stdin.end(); await new Promise((r) => ff.on('close', r)); process.stderr.write(`\r${n}/${n} quadros -> ${out}\n`);
  }
  await browser.close(); server.close();
})().catch((e) => { console.error(e); process.exit(1); });
