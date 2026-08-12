// jsora evidence driver: for one scene (from a manifest entry), use jsora's
// own real public API to (1) create the project natively and save() a real
// .ora file, in a fresh page; (2) in a SECOND, independent fresh page/
// browser context, load() that exact saved file and render_to_canvas(),
// then export a PNG. Never hand-constructs ORA bytes or implements
// compositing math here -- orchestration only, matching this session's
// own directive constraint.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FIXTURES_DIR = path.resolve(__dirname, 'fixtures');
const OUT_DIR = path.resolve(__dirname, 'out');
fs.mkdirSync(OUT_DIR, { recursive: true });

function b64(file) {
  return fs.readFileSync(path.join(FIXTURES_DIR, file)).toString('base64');
}

const LAUNCH_ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'];

async function createAndSave(scene) {
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));
  await page.goto('file://' + path.resolve(__dirname, 'harness.html'));

  const layersWithData = scene.layers.map(l => ({ ...l, dataUri: 'data:image/png;base64,' + b64(l.file) }));

  const result = await page.evaluate(async ({ scene, layersWithData }) => {
    const { JSOra } = window.jsora;
    const proj = new JSOra();
    proj.new(scene.canvas_width, scene.canvas_height);
    // Add in REVERSE order (last-added = uppermost, per jsora's own
    // _insertElementAtIndex semantics at default z_index=1) so the final
    // stack order matches scene.layers[0]=uppermost, matching this
    // session's own scene_matrix.py convention.
    const reversed = [...layersWithData].reverse();
    for (const l of reversed) {
      proj.add_layer(l.dataUri, '/', {
        offsets: [l.x, l.y],
        composite_op: l.composite_op,
        opacity: l.opacity,
      });
    }
    const blob = await proj.save();
    const buf = await blob.arrayBuffer();
    return Array.from(new Uint8Array(buf));
  }, { scene, layersWithData });

  await browser.close();
  if (errors.length) throw new Error('page errors during create/save: ' + errors.join('; '));
  return Buffer.from(result);
}

async function reopenRender(scene, oraBytes) {
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));
  await page.goto('file://' + path.resolve(__dirname, 'harness.html'));

  const oraB64 = oraBytes.toString('base64');

  const result = await page.evaluate(async ({ oraB64, width, height }) => {
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
  }, { oraB64, width: scene.canvas_width, height: scene.canvas_height });

  await browser.close();
  if (errors.length) throw new Error('page errors during reopen/render: ' + errors.join('; '));
  return Buffer.from(result, 'base64');
}

async function main() {
  const manifestPath = process.argv[2];
  const sceneId = process.argv[3];
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  const scene = manifest.find(s => s.scene_id === sceneId);
  if (!scene) throw new Error('scene not found: ' + sceneId);

  console.log('creating + saving:', sceneId);
  const oraBytes = await createAndSave(scene);
  const oraPath = path.join(OUT_DIR, sceneId + '.ora');
  fs.writeFileSync(oraPath, oraBytes);
  console.log('wrote', oraPath, oraBytes.length, 'bytes');

  console.log('reopening + rendering (fresh browser context):', sceneId);
  const pngBytes = await reopenRender(scene, oraBytes);
  const pngPath = path.join(OUT_DIR, sceneId + '.png');
  fs.writeFileSync(pngPath, pngBytes);
  console.log('wrote', pngPath, pngBytes.length, 'bytes');
}

main().catch(err => {
  console.error('FATAL:', err.message);
  process.exit(1);
});
