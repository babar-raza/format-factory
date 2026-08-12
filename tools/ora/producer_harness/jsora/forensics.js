// Full forensic reproduction of the jsora multi-layer rendering failure.
// Records every environment fact requested before drawing any conclusion.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

const FIXTURES_DIR = path.resolve(__dirname, 'fixtures');
function b64(file) { return fs.readFileSync(path.join(FIXTURES_DIR, file)).toString('base64'); }
function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }

const LAUNCH_ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'];

async function runOnce(runId) {
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const version = browser.version();
  const page = await browser.newPage();
  const consoleLogs = [];
  const pageErrors = [];
  const webglErrors = [];
  page.on('console', msg => consoleLogs.push(msg.text()));
  page.on('pageerror', err => pageErrors.push(err.message));
  await page.goto('file://' + path.resolve(__dirname, 'harness.html'));

  const destB64 = b64('composite-porterduff-lighter-destination.png');
  const srcB64 = b64('composite-porterduff-lighter-source.png');

  const result = await page.evaluate(async ({ destB64, srcB64 }) => {
    const diag = {};

    // WebGL capabilities BEFORE jsora touches anything
    const probeCanvas = document.createElement('canvas');
    const gl = probeCanvas.getContext('webgl2');
    diag.webgl2_available = !!gl;
    if (gl) {
      diag.renderer = gl.getParameter(gl.RENDERER);
      diag.vendor = gl.getParameter(gl.VENDOR);
      diag.version = gl.getParameter(gl.VERSION);
      diag.shading_language_version = gl.getParameter(gl.SHADING_LANGUAGE_VERSION);
      diag.max_texture_size = gl.getParameter(gl.MAX_TEXTURE_SIZE);
      diag.extensions = gl.getSupportedExtensions();
    }
    diag.device_pixel_ratio = window.devicePixelRatio;

    const { JSOra, Renderer } = window.jsora;

    const proj = new JSOra();
    proj.new(32, 32);
    proj.add_layer('data:image/png;base64,' + destB64, '/', { offsets: [0, 0], composite_op: 'svg:src-over' });
    proj.add_layer('data:image/png;base64,' + srcB64, '/', { offsets: [12, 12], composite_op: 'svg:plus' });

    diag.layer_count = proj.iter_layers.length;
    diag.layer_order = proj.iter_layers.map(l => ({ src: l._elem.getAttribute('src'), x: l.offsets[0], y: l.offsets[1], op: l.composite_op }));

    const canvas = document.createElement('canvas');
    const renderer = new Renderer(proj);

    // Capture the WebGL context jsora itself creates (post render_to_canvas)
    await renderer.render_to_canvas(canvas);

    diag.output_canvas_width = canvas.width;
    diag.output_canvas_height = canvas.height;

    const dataUrl = canvas.toDataURL('image/png');
    diag.png_b64 = dataUrl.split(',')[1];

    // Also read raw pixels directly via a 2D context re-draw, independent of PNG encoding,
    // to separate "canvas readback" from "PNG export" as distinct potential failure points.
    const readback = document.createElement('canvas');
    readback.width = canvas.width;
    readback.height = canvas.height;
    const rctx = readback.getContext('2d');
    rctx.drawImage(canvas, 0, 0);
    const imgData = rctx.getImageData(0, 0, readback.width, readback.height);
    diag.raw_pixel_sample = {
      dest_only_5_5: Array.from(imgData.data.slice((5 * readback.width + 5) * 4, (5 * readback.width + 5) * 4 + 4)),
      source_only_25_25: Array.from(imgData.data.slice((25 * readback.width + 25) * 4, (25 * readback.width + 25) * 4 + 4)),
    };

    return diag;
  }, { destB64, srcB64 });

  await browser.close();

  const pngBytes = Buffer.from(result.png_b64, 'base64');
  delete result.png_b64;
  result.png_sha256 = sha256(pngBytes);
  result.png_bytes_length = pngBytes.length;
  result.chromium_full_version = version;
  result.console_log_count = consoleLogs.length;
  result.page_errors = pageErrors;
  result.run_id = runId;

  fs.writeFileSync(path.join(__dirname, 'out', `forensics-run${runId}.png`), pngBytes);
  return result;
}

async function main() {
  fs.mkdirSync(path.join(__dirname, 'out'), { recursive: true });
  const results = [];
  for (let i = 1; i <= 3; i++) {
    console.log(`=== Fresh browser process, run ${i} ===`);
    const r = await runOnce(i);
    console.log(JSON.stringify(r, null, 2));
    results.push(r);
  }
  const shas = results.map(r => r.png_sha256);
  const deterministic = shas.every(s => s === shas[0]);
  console.log('=== DETERMINISM CHECK ===');
  console.log('sha256 per run:', shas);
  console.log('deterministic across 3 fresh browser processes:', deterministic);
  fs.writeFileSync(path.join(__dirname, 'out', 'forensics-summary.json'), JSON.stringify({ results, deterministic }, null, 2));
}

main().catch(err => { console.error('FATAL', err); process.exit(1); });
