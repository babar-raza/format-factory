// Runs jsora's own real, unmodified examples/tutorial.html (fetched
// directly from its own upstream GitLab repo at the exact commit
// matching the pinned npm 0.3.0 publish, gitHead
// 12659e50727a7fbb2c6bb470f24231b2322fbad0) via a local HTTP server
// (fetch() requires http:, not file:). The ONE necessary substitution:
// the tutorial's own referenced asset examples/img/src-over-krita.ora
// does not exist anywhere in the upstream repository (confirmed via
// GitLab's own API tree listing) -- substituted with a real,
// independently-produced Krita .ora file already committed to this
// project (tools/ora/producer_harness/krita/evidence-2026-08-12/
// layer-order.ora, a genuine 2-layer, plain svg:src-over file, matching
// the missing asset's own implied intent). No JavaScript in
// tutorial.html itself is modified.
const { chromium } = require('playwright');
const http = require('http');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, 'upstream-repo-layout');
const LAUNCH_ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'];

function serve() {
  return http.createServer((req, res) => {
    const filePath = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(404); res.end('not found: ' + filePath); return; }
      res.writeHead(200);
      res.end(data);
    });
  }).listen(0);
}

async function main() {
  const server = serve();
  const port = server.address().port;
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const page = await browser.newPage();
  const consoleLogs = [];
  const pageErrors = [];
  page.on('console', msg => consoleLogs.push(msg.text()));
  page.on('pageerror', err => pageErrors.push(err.message));

  await page.goto(`http://localhost:${port}/examples/tutorial.html`);
  // The tutorial's own examples() function is invoked at the bottom of
  // its own <script> block on page load; wait for it to finish (2
  // sequential make_merged_image() calls, both awaited).
  await page.waitForTimeout(3000);

  const canvasCount = await page.evaluate(() => document.querySelectorAll('canvas').length);
  const canvasData = await page.evaluate(() => {
    const canvases = Array.from(document.querySelectorAll('canvas'));
    return canvases.map(c => ({ width: c.width, height: c.height, dataUrl: c.toDataURL('image/png') }));
  });

  await browser.close();
  server.close();

  console.log('console logs:', JSON.stringify(consoleLogs, null, 2));
  console.log('page errors:', JSON.stringify(pageErrors, null, 2));
  console.log('canvas count appended to DOM:', canvasCount);

  fs.mkdirSync(path.join(__dirname, 'out'), { recursive: true });
  canvasData.forEach((c, i) => {
    const buf = Buffer.from(c.dataUrl.split(',')[1], 'base64');
    fs.writeFileSync(path.join(__dirname, 'out', `upstream-tutorial-canvas${i}.png`), buf);
    console.log(`canvas ${i}: ${c.width}x${c.height}, wrote upstream-tutorial-canvas${i}.png (${buf.length} bytes)`);
  });
}

main().catch(err => { console.error('FATAL', err); process.exit(1); });
