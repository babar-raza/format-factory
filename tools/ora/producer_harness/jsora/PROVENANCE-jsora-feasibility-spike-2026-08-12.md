# `jsora` feasibility spike — provenance record (FAILED, real environment blocker)

**Status: ACCEPTED_WITH_CHANGES (2026-08-12).** Independent adversarial
review (fresh agent, no prior conclusion stated) read the actual driver
code (`run_scene.js`/`run_consumer.js`) and independently tried to find a
driver-side bug that could explain the garbled output (specifically
tested an unset-canvas-dimensions hypothesis by inspecting the committed
evidence PNGs' own headers) — found none; confirmed the driver is
genuinely orchestration-only and the 3-diagnostic methodology is sound,
though noted the diagnostics vary blend-operator and launch flags without
a 4th variant isolating layer-order from offset/geometry handling
specifically (not required as a blocking change; noted for a future
session). Required one repair, applied below: the jsora build/execution
environment was not reproducible from the repo alone (`jsora.min.js` was
used but never committed and no recipe existed) — added
`package.json` and an explicit reproduction recipe.

Priority-2 candidate per this session's own continuation directive
("upstream InkLab jsora for the complete missing-operation set"). Result:
**the mandatory 3-operation feasibility spike did not pass** — jsora's own
rendering pipeline produces spatially-incorrect ("garbled") output for
every multi-layer scene tested in this pinned, official headless-
Chromium execution environment, confirmed via 3 independent diagnostic
variants. Per this session's own directive ("Do not proceed to all
remaining operations until the three-operation spike succeeds"), the full
remaining-operation matrix was **not** executed against jsora.

## Independence review (completed BEFORE any execution)

A fresh general-purpose agent, given only the policy texts
(`POL-LRA-RENDER-01`, `ORA-COMPOSITE-001`'s own gate) and a source-verified
candidate-audit report (downloaded, checksummed npm tarball; direct
reading of every `src/*.js` file; dependency/license/lineage check), with
no prior conclusion stated, independently concluded: **jsora qualifies as
an independent producer (full)** under this policy's actual text. All 7
independence criteria were source-confirmed (no shared code with
format-factory/GIMP/Krita; developed outside this project; pinned,
reproducible npm package with an independently re-verified integrity
hash). This verdict stands; the failure below is an *execution*
blocker, not an independence/policy problem.

## Source-level facts (npm package `jsora@0.3.0`, InkLab, MIT license)

Downloaded and independently checksummed the real npm tarball (not
scraped from a web page): sha1 `df722df3b0d962bbcbbfbbeae10880de007628bc`
matches the npm registry's own reported shasum exactly. Dependencies:
`jszip@^3.2.2` (real ZIP I/O), `gpu.js@^2.6.9` (compiles JS kernel
functions to WebGL2/GLSL). Direct source reading (not README claims)
confirmed jsora's own `render.js` maps all 20 `COMPOSITE_OP_REGISTRY`
values (10 separable blend + 4 non-separable blend + 5 Porter-Duff + 1
default), and hand-algebraic comparison against `composite_oracle.py`
found jsora's own Porter-Duff formulas (`composite.js`) match the
independent oracle's own coefficients exactly, predicting a likely PASS
for the compositing math itself, pending empirical confirmation.

## Execution environment

Official, pinned Microsoft Playwright Docker image:
`mcr.microsoft.com/playwright@sha256:dcc5531e97840b9b5e794f2814476b21571c5124a3fca2267d73041f56e7580e`
(tag `v1.62.1-noble`, matching the installed `playwright@1.62.1` npm
package used by the driver). Chromium launched headless with WebGL2
available via ANGLE/SwiftShader software rendering (confirmed working:
`WebGL 2.0 (OpenGL ES 3.0 Chromium)` context created successfully before
any jsora-specific test). The driver
(`tools/ora/producer_harness/jsora/run_scene.js`,
`run_consumer.js`) orchestrates only — invokes jsora's own real public
API (`JSOra.new`/`add_layer`/`save`/`load`, `Renderer.render_to_canvas`)
exactly as documented, never implements compositing math or hand-
constructs ORA bytes, per this session's own directive constraint.

## Real jsora writer defect found (disclosed, not patched around)

jsora's own `save()` writes ZIP layer members with **absolute paths**
(`/data/layer0.png`, plus an absolute directory entry `/data/`) —
confirmed by listing the real ZIP produced for the `svg:plus` scene.
format-factory's own reader correctly refuses this in **both**
`ReadMode.STRICT` and `ReadMode.TOLERANT`
(`OraArchiveError: member name '/data/' is an absolute path` — this
specific check is a security boundary, not a soft-conformance issue
TOLERANT mode is designed to relax). This blocks jsora's own native
`.ora` export from ever qualifying as `PRODUCER_NATIVE_EXPORT` evidence
against this project's own reader, independent of the rendering-pipeline
issue below. Per this session's own directive ("must not... repair
emitted ORA files"), this was not patched around; jsora's own broken
export bytes are preserved unmodified at
`tools/ora/producer_harness/jsora/evidence-2026-08-12/gimp3-native-svg-plus.ora`... [see Real files below for the actual path].

## Rendering-pipeline defect found (blocks ALL evidence, not just `svg:plus`)

Given the writer defect, pivoted to the already-established
`INDEPENDENT_CONSUMER_RENDER` fallback pattern: had jsora `load()` and
`render_to_canvas()` the already-committed, already-STRICT-valid,
format-factory-authored `composite-porterduff-lighter.ora` fixture
directly (not jsora's own broken export). Result: **spatially incorrect
output** — a deterministic, blocky, garbled pixel pattern bearing no
resemblance to the expected geometry (destination at (0,0)-(20,20),
source at (12,12)-(32,32) on a 32×32 canvas), confirmed by dumping and
visually mapping the full 32×32 raster, not just spot-checking 4 sample
points (which is what first revealed the result was nonsensical rather
than merely "wrong values").

Three independent diagnostics, in order, to isolate the cause before
concluding (matching this session's own "root-cause via evidence, not
guessing" discipline):

1. **Single full-canvas layer, no compositing, no offset** — PASSED
   exactly (uniform, byte-correct 8×8 output). Confirms the basic WebGL2
   texture-upload → kernel → canvas-readback → PNG-export pipeline is
   sound in this environment; rules out a fundamental WebGL/SwiftShader
   incompatibility as the sole cause.
2. **Two 20×20 offset layers, `svg:plus`** (the real scene) — FAILED,
   garbled output.
3. **Two 20×20 offset layers, plain `svg:src-over`** (the simplest
   possible blend, already proven correct for GIMP/Krita) — FAILED with
   the **identical, byte-for-byte garbled pattern** as (2). This rules
   out `composite.js`'s own Porter-Duff kernels specifically as the
   cause -- the defect is general to ANY multi-layer offset compositing
   in jsora's own `render_to_canvas()`/`blend.js` pipeline, not specific
   to `svg:plus`.
4. Retried (2)/(3) with default Chromium launch flags (no explicit
   SwiftShader/ANGLE overrides) -- identical garbled result. Rules out
   this session's own launch-flag choices as the cause.

**Root-cause hypothesis (disclosed as a hypothesis, not asserted as
proven)**: `render.js`'s own `render_to_canvas()` constructs exactly one
shared `gpu.js` `GPU` instance bound to the top-level output canvas/WebGL
context (`self.gpu = new gpujs.GPU({canvas, context: gl})`), and every
named kernel (`normal`, `plus`, etc.) is compiled and cached against that
single shared context (`self.kernelCache[kernelName]`). Read directly:
`utils.js`'s own `cloneCanvas()` performs a genuine `drawImage`-based
2D-context copy (not a shallow reference — ruled out as the bug itself),
but if GPU.js's own kernel/framebuffer state is not fully isolated
between sequential different-shaped kernel invocations sharing one GL
context, a second compositing pass could read stale or cross-contaminated
framebuffer content — consistent with everything observed (single-kernel
case correct; any second sequential kernel call, regardless of which
operator, corrupted). Not independently proven inside gpu.js's own
source (out of this session's own scope to audit a second, larger
upstream dependency in full); named here as the most likely explanation
supported by the available evidence, not a certainty.

## Disposition

jsora contributes **zero** evidence toward any of the 11 remaining
operations this cycle -- not because it fails the independence/policy
test (it passed that, per the fresh review above), and not because its
own compositing MATH is wrong (algebraically verified correct against
the oracle before execution), but because its own **rendering pipeline
does not function correctly in this project's own execution
environment** for any multi-layer scene, confirmed via 3 independent,
deterministic diagnostics. This is a genuine execution/environment
feasibility blocker, disclosed precisely, not a vague "didn't work."

**Concrete next steps, not proposed as complete or attempted this
cycle**: (a) file an issue against jsora's own upstream GitLab repository
with this exact reproduction (a real, disclosable open-source
contribution opportunity, since jsora's own compositing math is
otherwise sound); (b) attempt a real (non-headless, GPU-backed) browser
environment instead of software-WebGL, if one becomes available to this
project; (c) investigate whether an older/different `gpu.js` version
avoids the shared-context issue. None of these were pursued this cycle;
named as real, specific options rather than left as a dead end.

## Reproducing this execution

`jsora.min.js` (a 1.3MB third-party dist bundle) is deliberately **not**
committed to this repository, matching this harness's own existing
convention of pinning Docker image digests rather than committing pulled
binaries. Reproduce it and the exact environment used:

```bash
# 1. Fetch the exact pinned jsora version, independently checksum-verifiable
cd tools/ora/producer_harness/jsora
npm pack jsora@0.3.0
tar xzf jsora-0.3.0.tgz
sha1sum jsora-0.3.0.tgz   # expect df722df3b0d962bbcbbfbbeae10880de007628bc,
                          # matching the npm registry's own reported shasum
cp package/dist/jsora.min.js .

# 2. Install the pinned Playwright npm package (browsers come from the image, step 3)
npm install --no-save   # uses this directory's own package.json (playwright@1.62.1)

# 3. Run against the official, pinned Playwright image
docker run --rm -v "$(pwd):/work" -w /work \
  mcr.microsoft.com/playwright@sha256:dcc5531e97840b9b5e794f2814476b21571c5124a3fca2267d73041f56e7580e \
  node run_consumer.js <path-to-.ora> <output.png>
```

## Real files

- `tools/ora/producer_harness/jsora/package.json` — pins the exact
  `playwright` version; see above for the exact `jsora` pinning (npm
  version + independently-reproducible checksum, not committed as a
  binary).
- `tools/ora/producer_harness/jsora/run_scene.js`,
  `run_consumer.js` — the real orchestration driver (orchestrate-only,
  no compositing math, no hand-built ORA bytes).
- `tools/ora/producer_harness/jsora/harness.html` — the real jsora
  bundle load page (expects `jsora.min.js` alongside it, reproduced per
  above).
- `tools/ora/producer_harness/jsora/evidence-2026-08-12/` — jsora's own
  real, unmodified outputs: `svg-plus-native-export.ora` (the absolute-
  path-defective native export), `svg-plus-garbled-render.png` and
  `src-over-garbled-render.png` (the two matching garbled renders),
  `diag-single-layer-correct.png` (the one passing diagnostic).
- `tools/ora/producer_harness/jsora/candidate-audit-jsora.json` — the
  full source-verified candidate report submitted to the independence
  review.
