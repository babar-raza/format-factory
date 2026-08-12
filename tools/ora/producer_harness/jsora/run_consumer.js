// jsora as INDEPENDENT CONSUMER: load() and render a real, already-strict-
// validated, format-factory-authored .ora fixture (not jsora's own native
// export, which has a confirmed real writer defect -- absolute ZIP member
// paths, rejected by format-factory's own security checks in both STRICT
// and TOLERANT mode -- see PROVENANCE doc). Matches this session's own
// already-established INDEPENDENT_CONSUMER_RENDER fallback pattern.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const LAUNCH_ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'];

async function reopenRender(oraBytes) {
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));
  await page.goto('file://' + path.resolve(__dirname, 'harness.html'));

  const oraB64 = oraBytes.toString('base64');

  const result = await page.evaluate(async ({ oraB64 }) => {
    const { JSOra, Renderer } = window.jsora;
    const bin = atob(oraB64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blob = new Blob([bytes]);

    const proj = new JSOra();
    await proj.load(blob);

    const canvas = document.createElement('canvas');
    const renderer = new Renderer(proj);
    await renderer.render_to_canvas(canvas);

    const dataUrl = canvas.toDataURL('image/png');
    return dataUrl.split(',')[1];
  }, { oraB64 });

  await browser.close();
  if (errors.length) throw new Error('page errors during reopen/render: ' + errors.join('; '));
  return Buffer.from(result, 'base64');
}

async function main() {
  const oraPath = process.argv[2];
  const outPngPath = process.argv[3];
  const oraBytes = fs.readFileSync(oraPath);
  console.log('reopening + rendering (fresh browser context):', oraPath);
  const pngBytes = await reopenRender(oraBytes);
  fs.writeFileSync(outPngPath, pngBytes);
  console.log('wrote', outPngPath, pngBytes.length, 'bytes');
}

main().catch(err => {
  console.error('FATAL:', err.message);
  process.exit(1);
});
