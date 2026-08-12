# jsora rendering-pipeline corruption — definitive root cause (2026-08-12, fourth continuation)

**Answer to this cycle's central diagnostic question**: jsora failed
because of a **genuine upstream semantic/architectural defect** in its
own `render.js`, not an incompatible modern runtime and not a
harness/API-use defect. This is now proven, not hypothesized — via
direct source inspection, empirical WebGL call tracing, a diagnostic
patch experiment, and (decisively) reproduction through jsora's own
unmodified official tutorial using a real, independently-produced
fixture.

## 1. Full forensic environment record

| Field | Value |
|---|---|
| Playwright image | `mcr.microsoft.com/playwright@sha256:dcc5531e97840b9b5e794f2814476b21571c5124a3fca2267d73041f56e7580e` (tag `v1.62.1-noble`) |
| Node (host driver) | v24.13.1 |
| npm | 11.8.0 |
| jsora package | `jsora@0.3.0`, npm tarball sha1 `df722df3b0d962bbcbbfbbeae10880de007628bc` (independently re-verified against the registry's own reported shasum, again this cycle) |
| jsora gitHead at publish | `12659e50727a7fbb2c6bb470f24231b2322fbad0` |
| Playwright (npm package) | 1.62.1 |
| Chromium (in-container, actual) | 151.0.7922.34 (`browser.version()`, captured directly, not assumed from the Playwright release notes) |
| GPU.js | declared `^2.6.9` in jsora's own `package.json`; bundled copyright notice inside `dist/jsora.min.js` reads "Copyright (c) 2020 gpu.js Team" (consistent with jsora's own 2020-02-21 publish date); exact bundled patch version not extractable from the minified bundle (no source map ships) |
| Browser flags | `--use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist` |
| WebGL renderer string | `WebKit WebGL` / vendor `WebKit` (a known headless-Chromium masking quirk, not indicative of actually running WebKit) |
| WebGL version | `WebGL 2.0 (OpenGL ES 3.0 Chromium)`, GLSL `WebGL GLSL ES 3.00` |
| Max texture size | 8192 |
| Device pixel ratio | 1 |
| Canvas dimensions (test scene) | 32×32 (custom scene), 64×64 (upstream tutorial's own real fixture) |
| Exit status | 0 (no crash; garbled output, not a hard failure) |
| Evidence hashes | see §4 below |

## 2. Determinism (directive §2 point 6)

Ran the identical 2-layer scene in 3 fresh, independent browser
processes. `sha256` of the resulting PNG bytes was **identical across
all 3 runs**: `972b54a7927b262ee4c9e1bf6d0187cf93112aa45f02ee34081767370159825f`.
**Deterministic, not a race condition.**

## 3. Localizing the corruption boundary (directive §2 point 2)

Read raw pixels via `getImageData()` on a plain 2D-context redraw of the
WebGL output canvas — bypassing `toDataURL()`/PNG encoding entirely.
Result: **identical garbled values** to the PNG-exported version
(`dest_only_5_5 = (0,0,0,0)`, `source_only_25_25 = (230,60,40,153)` —
the destination's own color appearing at the source-only sample point).
This proves the corruption is present in the WebGL canvas's own
rendered pixel buffer itself, **before** any PNG encoding step — ruling
out `toDataURL()`/canvas export as the cause, confirming the defect is
in compositing itself (texture upload → GPU compositing → canvas
readback), matching this session's own directive point 2's own
enumerated boundary options.

## 4. Instrumented trace (directive §5, permitted instrumentation only)

Wrapped `document.createElement`, `HTMLCanvasElement.prototype.getContext`,
`CanvasRenderingContext2D.prototype.drawImage`, and
`WebGL2RenderingContext.prototype.{texImage2D,readPixels,viewport}` via
`page.addInitScript()` — injected **before** `jsora.min.js` loads, so it
wraps the shared browser prototypes without modifying a single byte of
jsora's own code. Full trace: `tools/ora/producer_harness/jsora/evidence-2026-08-12b/instrument-trace.json`.

**The decisive trace line**:
```
{"event":"texImage2D","glcanvas":"canvas0","nargs":6,"source":"canvas0 (32x32)"}
```
`canvas0` is the single, shared canvas jsora's own `render_to_canvas()`
binds every GPU.js kernel to
(`self.gpu = new gpujs.GPU({canvas, context: gl})`, `src/render.js`).
This trace line shows jsora uploading **canvas0's own current content as
a texture, while canvas0 is simultaneously the active kernel's own
render target** — a read/write-same-WebGL-resource hazard, undefined
behavior per the WebGL2/OpenGL ES specification (reading a texture that
is also bound as the current framebuffer's own color attachment is not
defined to produce any particular result).

## 5. Source-level confirmation

Read `src/render.js` directly (the real, downloaded npm-tarball source,
not a web summary). Two distinct, real defects found:

**5a. A literal typo** (`render.js:146`):
```js
if (current_group.isolated || current_group.opacity < 1.0 || current_group.composite_op !== 'svr:src-over'){
    backdrop = document.createElement("canvas");
    ...
}else{
    backdrop = canvas;
}
```
`'svr:src-over'` (a one-character typo for `'svg:src-over'`) means this
condition is **always true** for any real group, including the implicit
root group (whose real `composite_op` is always the correctly-spelled
`'svg:src-over'`, which can never equal the misspelled comparison
string) — forcing every render through the "create an isolated backdrop"
branch even when no isolation was ever requested.

**5b. The structural cause — confirmed by a diagnostic patch experiment,
not left as an untested guess**: created a byte-identical copy of
`jsora.min.js` with **only** the one-character `svr`→`svg` fix applied
directly to the minified bundle (verified via `diff <(xxd old) <(xxd
new)`: exactly one byte changed, nothing else). Re-ran the identical
2-layer scene. **Result: byte-for-byte identical garbled output** —
`(0,0,0,0)` / `(230,60,40,153)` at the same two sample points, unchanged.
**This disproves the typo as the corruption's own root cause.** Fixing
it only changes which code path (`backdrop = canvas` directly, i.e. the
shared kernel canvas itself, vs. a separate fresh canvas that is later
re-composited onto the shared canvas) reaches the same underlying hazard
— `canvas = self._render_two(canvas, rendered_group, current_group)`
(`render.js:158`) always eventually feeds the shared kernel canvas back
into itself as an input, whether directly (post-fix) or one step later
(pre-fix), because `render_to_canvas()`'s own progressive-compositing
loop reassigns `canvas` to each step's own output and reuses it as the
next step's own input, while every step shares one physical WebGL
canvas/context.

**Why single-opaque-full-canvas-layer scenes are unaffected (already
observed this session, now explained rather than merely noted)**: the
`svg:src-over` (Normal) blend formula is `oa = ua + la·(1−ua)`,
`or = (1−ua)·backdrop + ua·mixed`. When the upper/foreground layer is
fully opaque across the entire canvas (`ua = 1` everywhere), this
reduces algebraically to `oa = 1`, `or = mixed` — **independent of
`backdrop`'s own value**. The read/write hazard's own garbage backdrop
content is masked by the math itself whenever the top layer is fully
opaque and full-canvas; it becomes visible precisely when the result
genuinely depends on backdrop content (any layer with real transparency
or partial canvas coverage) — exactly the condition every one of this
session's own multi-layer test scenes, and jsora's own official tutorial
fixture (see §6), satisfies.

## 6. Definitive confirmation: jsora's own official, unmodified tutorial fails too

Fetched `examples/tutorial.html` directly from jsora's own upstream
GitLab repository at the exact commit matching the pinned npm 0.3.0
publish (`12659e50727a7fbb2c6bb470f24231b2322fbad0`). Found the
tutorial's own write/multi-layer-creation code is entirely wrapped in a
dead `if(false){...}` block — **never executed**. The only code that
actually runs: `project.load(fetched_file)` then
`Renderer.make_merged_image()` (twice) — jsora's own intended,
documented, "load and render a real .ora" workflow, using **no code from
this project's own driver at all**.

**Real, disclosed upstream completeness defect**: the tutorial's own
referenced fixture, `examples/img/src-over-krita.ora`, **does not exist
anywhere in the upstream repository** (confirmed via GitLab's own API
tree listing at the exact pinned commit — no `examples/img/` directory
exists at all). The tutorial cannot be run to completion exactly as
published, through no fault of this session's own harness.

Substituted the missing asset with a real, independently-produced
Krita `.ora` file already committed to this project
(`tools/ora/producer_harness/krita/evidence-2026-08-12/layer-order.ora`
— a genuine 2-layer, plain-`svg:src-over` file, matching the missing
asset's own implied intent from its filename) — **no line of the
tutorial's own JavaScript was modified**, only the referenced data file
was supplied since the real one is absent upstream. Served over a local
HTTP server (required: `fetch()` does not work over `file://`).

**Result: garbled, structurally wrong output**, using jsora's own
official workflow on a real, valid input file:

- Expected (already independently verified this session via
  format-factory/GIMP/Krita agreement): a clean two-region image — a
  blue "backward-L" region (top-left, occluded where green overlaps) and
  a solid green square (bottom-right region), one clean boundary.
- Actual (jsora's own tutorial, unmodified): a blocky, structurally wrong
  pattern with isolated blue block-artifacts intruding into rows/columns
  that should be pure green, and an incorrect region extending pure blue
  across nearly the full canvas width in the lower rows — the same
  defect class as this session's own custom test scenes.

This is the decisive, dispositive evidence directive §3 asked for:
**the upstream example itself fails**, using jsora's own real fixture
format and its own real, intended public API call sequence, not this
project's own scene construction.

## 7. Runtime-compatibility matrix — bounded, per directive's own "stop incapable branches early" permission

- **Current Chromium (151.0.7922.34) + SwiftShader/ANGLE**: WebGL2
  available, kernels execute, deterministic — but produces the
  confirmed-wrong result (§2-§6 above).
- **Current Firefox (Playwright-bundled) headless, default**: WebGL2
  context creation refused outright (`AllowWebgl2:false` — headless
  Firefox disables WebGL by policy).
  `page errors: ["can't access property \"imageSmoothingEnabled\", gl is null"]`
  — jsora's own code does not guard against a null WebGL context.
- **Current Firefox + forced WebGL prefs** (`webgl.disabled=false`,
  `webgl.force-enabled=true`): context creation still fails
  (`FEATURE_FAILURE_WEBGL_EXHAUSTED_DRIVERS` — no working software/Mesa
  GL driver configured for Firefox in this specific container image).
  **Inconclusive** for Firefox specifically (an environment-configuration
  gap in this container, not evidence about Firefox's own WebGL
  semantics), disclosed as such rather than counted either way.
- **Contemporary-2020 browser builds**: not attempted. Locating and
  running archived ~2020 Chromium/Firefox builds in this environment is
  a materially larger undertaking than the evidence already gathered
  justifies, given the root cause is now proven to be a **specification-
  level API misuse pattern** (reading a texture bound as the active
  render target's own framebuffer is undefined behavior in every
  WebGL2-conformant implementation, old or new) rather than a version-
  specific quirk. Stopped here per directive's own explicit permission,
  with the reasoning disclosed rather than silently omitted.
- **GPU.js CPU-mode backend**: not reachable through jsora's own public
  API. `render.js`'s own `self.gpu = new gpujs.GPU({canvas, context: gl})`
  hardcodes a WebGL context at construction with no mode parameter
  exposed to callers — confirmed via direct source reading, not
  assumed. Per directive's own "acceptable if invoked through jsora's
  own supported configuration" — it is not; jsora's own code gives no
  such configuration surface.

## 8. Absolute ZIP paths — upstream-owned, confirmed again this cycle

Re-confirmed (directive §2 point 1): `src/index.js`'s own
`_add_layer()` constructs `const new_filename = \`/data/layer${self._filename_counter}.png\`;`
— the leading `/` is a literal, hardcoded string in jsora's own source,
not a harness misuse of a documented API, and not something any
documented public option changes. **Upstream-owned defect, confirmed via
direct source reading, not merely observed in output.**

## 9. Conclusion

jsora 0.3.0's own rendering pipeline is **fundamentally broken for any
multi-layer composite whose result genuinely depends on backdrop
content** — a specification-level WebGL resource-hazard defect in its
own `render.js`, confirmed via source inspection, instrumented tracing,
a diagnostic patch experiment that disproved a simpler hypothesis
(the `svr`/`svg` typo) before accepting the deeper one, and decisively
via jsora's own unmodified official tutorial. This is not a harness
defect, not a browser-version incompatibility, and not resolved by any
runtime configuration change available through jsora's own public API.
See `tools/ora/producer_harness/jsora/upstream-issue-packages/` for the
reproducible defect-report packages drafted from these findings.
