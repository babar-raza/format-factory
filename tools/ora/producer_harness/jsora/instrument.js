// Instrumentation-only reproduction: wraps shared browser prototypes
// (HTMLCanvasElement, CanvasRenderingContext2D, WebGL2RenderingContext)
// BEFORE jsora.min.js loads, to trace canvas creation, drawImage calls,
// and WebGL texture upload/readback -- without modifying jsora's own
// bytes at all. Permitted per this session's own directive §5.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const LAUNCH_ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'];
const FIXTURES_DIR = path.resolve(__dirname, 'fixtures');
function b64(file) { return fs.readFileSync(path.join(FIXTURES_DIR, file)).toString('base64'); }

const INSTRUMENTATION = `
window.__trace = [];
let __canvasCounter = 0;
const __origCreateElement = document.createElement.bind(document);
document.createElement = function(tag, ...rest) {
  const el = __origCreateElement(tag, ...rest);
  if (tag === 'canvas') {
    el.__id = 'canvas' + (__canvasCounter++);
    window.__trace.push({ event: 'create_canvas', id: el.__id, stack: new Error().stack.split('\\n').slice(1,4).join(' | ') });
  }
  return el;
};

function hashArr(arr) {
  let h = 0;
  for (let i = 0; i < arr.length; i++) { h = (h * 31 + arr[i]) | 0; }
  return h;
}

const __origGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, ...rest) {
  const ctx = __origGetContext.call(this, type, ...rest);
  window.__trace.push({ event: 'get_context', canvas: this.__id, type, width: this.width, height: this.height });
  return ctx;
};

const __origDrawImage = CanvasRenderingContext2D.prototype.drawImage;
CanvasRenderingContext2D.prototype.drawImage = function(source, ...rest) {
  const srcId = source && source.__id ? source.__id : (source && source.tagName ? source.tagName : 'unknown');
  const srcW = source ? (source.width || source.naturalWidth) : null;
  const srcH = source ? (source.height || source.naturalHeight) : null;
  window.__trace.push({ event: 'drawImage', dest: this.canvas.__id, source: srcId, source_w: srcW, source_h: srcH, args: rest });
  return __origDrawImage.call(this, source, ...rest);
};

for (const ctxName of ['WebGL2RenderingContext']) {
  const proto = window[ctxName] && window[ctxName].prototype;
  if (!proto) continue;
  const origTexImage2D = proto.texImage2D;
  proto.texImage2D = function(...args) {
    const canvasId = this.canvas ? this.canvas.__id : 'unknown';
    let sourceInfo = 'unknown';
    const lastArg = args[args.length - 1];
    if (lastArg && lastArg.__id) sourceInfo = lastArg.__id + ' (' + lastArg.width + 'x' + lastArg.height + ')';
    else if (lastArg && lastArg.data) sourceInfo = 'typedarray len=' + lastArg.data.length + ' hash=' + hashArr(lastArg.data);
    window.__trace.push({ event: 'texImage2D', glcanvas: canvasId, nargs: args.length, source: sourceInfo });
    return origTexImage2D.apply(this, args);
  };
  const origReadPixels = proto.readPixels;
  proto.readPixels = function(x, y, w, h, format, type, pixels, ...rest) {
    const canvasId = this.canvas ? this.canvas.__id : 'unknown';
    const result = origReadPixels.call(this, x, y, w, h, format, type, pixels, ...rest);
    const hash = pixels ? hashArr(pixels) : null;
    window.__trace.push({ event: 'readPixels', glcanvas: canvasId, x, y, w, h, pixel_hash: hash, first8: pixels ? Array.from(pixels.slice(0,8)) : null });
    return result;
  };
  const origViewport = proto.viewport;
  proto.viewport = function(x, y, w, h) {
    const canvasId = this.canvas ? this.canvas.__id : 'unknown';
    window.__trace.push({ event: 'viewport', glcanvas: canvasId, x, y, w, h });
    return origViewport.call(this, x, y, w, h);
  };
}
`;

async function main() {
  const browser = await chromium.launch({ args: LAUNCH_ARGS });
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', err => pageErrors.push(err.message));
  page.on('console', msg => console.log('PAGE:', msg.text()));

  // Inject instrumentation BEFORE any script on the page runs, so it wraps
  // the prototypes before jsora.min.js (loaded via <script> tag in
  // harness.html) ever touches them.
  await page.addInitScript(INSTRUMENTATION);
  await page.goto('file://' + path.resolve(__dirname, 'harness.html'));

  const destB64 = b64('composite-porterduff-lighter-destination.png');
  const srcB64 = b64('composite-porterduff-lighter-source.png');

  const result = await page.evaluate(async ({ destB64, srcB64 }) => {
    const { JSOra, Renderer } = window.jsora;
    const proj = new JSOra();
    proj.new(32, 32);
    proj.add_layer('data:image/png;base64,' + destB64, '/', { offsets: [0, 0], composite_op: 'svg:src-over' });
    proj.add_layer('data:image/png;base64,' + srcB64, '/', { offsets: [12, 12], composite_op: 'svg:plus' });

    const canvas = document.createElement('canvas');
    const renderer = new Renderer(proj);
    await renderer.render_to_canvas(canvas);

    const rctx2 = document.createElement('canvas').getContext('2d');
    rctx2.canvas.width = canvas.width;
    rctx2.canvas.height = canvas.height;
    rctx2.drawImage(canvas, 0, 0);
    const imgData = rctx2.getImageData(0, 0, canvas.width, canvas.height);
    const finalSample = {
      dest_only_5_5: Array.from(imgData.data.slice((5 * canvas.width + 5) * 4, (5 * canvas.width + 5) * 4 + 4)),
      source_only_25_25: Array.from(imgData.data.slice((25 * canvas.width + 25) * 4, (25 * canvas.width + 25) * 4 + 4)),
    };

    return { trace: window.__trace, finalSample };
  }, { destB64, srcB64 });

  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'out', 'instrument-trace.json'), JSON.stringify(result, null, 2));
  console.log('=== TRACE (', result.trace.length, 'events ) ===');
  for (const ev of result.trace) console.log(JSON.stringify(ev));
  console.log('=== FINAL SAMPLE ===', JSON.stringify(result.finalSample));
  if (pageErrors.length) console.log('PAGE ERRORS:', pageErrors);
}

main().catch(err => { console.error('FATAL', err); process.exit(1); });
