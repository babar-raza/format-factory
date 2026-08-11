# ORA independent-producer comparison harness

State: **`EXTERNAL_EXECUTION_READY`** — not `implemented`, not generic
`blocked`. Every piece of this harness that does not require a GIMP install
is built and tested (17 passing contract tests against mocked producer
output, `tests/tools/test_ora_producer_harness_compare.py`). The piece that
actually produces new evidence — running GIMP, in batch mode, to render
each scene independently of format-factory's own code — cannot execute in
this repository's own sandboxed environment (no GIMP install, no display
server, no package manager access confirmed; see the root-cause
investigation this session's own Explore agent ran before concluding this).

## What this answers

ORA-RENDER-001 / ORA-COMPOSITE-001 / ORA-ISOLATION-001 share one release
gate, compiled from `POL-LRA-RENDER-01` and its siblings
(`shared/format-contracts/policy/family-packs/layered_raster_archive.yaml`)
into the real product contract (`shared/format-contracts/ora.yaml`) via
`contract_compiler.py` — an authorized project policy (see this session's
own Workstream B finding), not a spec-normative claim, and not something to
quarantine. It asks for rendering that "agrees with at least two
independent producers/consumers within declared tolerances." This harness
is how that evidence gets produced, once it can run somewhere with GIMP
installed.

## What is built and tested here (no GIMP required)

| File | Purpose | Tested by |
|---|---|---|
| `scene_matrix.py` | 8 producer-agnostic scene definitions covering layer order, opacity, clipping, visibility, one blend mode, and isolated-vs-non-isolated group compositing | `test_ora_producer_harness_compare.py` (imports and renders every scene) |
| `format_factory_side.py` | Realizes a scene with format-factory's own `OraStack`/`OraLayer` model and renders it | Same |
| `compare.py` | Pure comparison math (pixel-exact + tolerance-based), manifest generation, malformed-input handling — the actual reconciler-facing logic | 17 tests, all mocked producer input |
| `gimp_scripts/generate_scene.py` | GIMP Python-Fu script that independently constructs each scene inside a real GIMP and exports `.ora` | **Not testable here** — no `gimpfu` module exists outside a real GIMP install. Syntactically follows GIMP 2.10's documented Python-Fu API; unverified against a real GIMP process. |

The drift guard (`test_gimp_script_scene_ids_are_a_subset_of_the_canonical_matrix`)
catches the GIMP script's own scene data going out of sync with
`scene_matrix.py` without needing GIMP installed to notice.

## Known gaps in `generate_scene.py`

- **Isolated/non-isolated group scenes are not yet scripted.** GIMP layer
  groups (`gimp-image-insert-layer` with a group parent) map to
  OpenRaster's `isolation` attribute in a way this session could not
  verify against a real GIMP `.ora` export (no GIMP install to check
  against). Scripting this blind, without being able to confirm GIMP's own
  exporter actually sets `isolation="isolate"` the way expected, would risk
  silently mis-mapping the one scene this harness cares about most —
  correctly left as a documented gap rather than a guessed implementation.
- Only one blend mode (`svg:multiply`) is scripted, matching
  `LAYER_MODE_MULTIPLY`'s GIMP-side constant, which is confirmed correct
  for GIMP's legacy (non-"default") layer-mode set. GIMP 2.10 added a
  second "default" mode group with different blend math for some modes —
  this script uses the legacy constants throughout for consistency; a real
  GIMP run should confirm this is what actually gets exported.
- `pdb.file_openraster_save`'s exact signature/plugin name should be
  reconfirmed against the target GIMP version before running — plugin
  procedure names have shifted across GIMP major versions (2.8 vs. 2.10 vs.
  3.x's GObject-Introspection API, which does not use `gimpfu`/`pdb` at
  all). This script targets **GIMP 2.10**, the version reachable via
  `apt-get install gimp` on Ubuntu 22.04/24.04 as of this writing.

## Exact external command (Ubuntu, matching this repo's own CI convention)

This repository's own `.github/workflows/ci.yml` runs every job on
`ubuntu-latest`. The following extends that same convention — it is **not**
wired into `ci.yml` (per this session's own instruction: do not create or
trigger a remote workflow without explicit authorization) — it is the exact
sequence a human or an authorized CI change would run:

```bash
# 1. Install GIMP 2.10 (ships Python-Fu / gimpfu out of the box on Ubuntu)
sudo apt-get update && sudo apt-get install -y gimp xvfb

# 2. Clone/checkout this repository at the commit under test, then, from
#    the repo root, run each scene through GIMP's own headless batch mode
#    (xvfb-run provides a virtual display; GIMP's batch mode still expects
#    one even with no GUI shown):
mkdir -p /tmp/ora-harness-out
for scene in single-opaque-layer layer-order partial-opacity \
             offset-and-clipping hidden-layer multiply-blend; do
  xvfb-run -a gimp -i -b \
    "(python-fu-generate-scene RUN-NONINTERACTIVE \"$scene\" \"/tmp/ora-harness-out/$scene.ora\")" \
    -b '(gimp-quit 0)' \
    --batch-interpreter python-fu-eval \
    tools/ora/producer_harness/gimp_scripts/generate_scene.py
done

# 3. Extract each producer .ora's own embedded mergedimage.png (or export a
#    plain PNG from GIMP directly, if mergedimage.png does not exist for a
#    given scene -- OpenRaster's own spec leaves mergedimage.png optional),
#    then run the comparison:
python -c "
from pathlib import Path
import zipfile
from tools.ora.producer_harness.compare import compare_scene, write_manifest

results = []
for scene_id in ['single-opaque-layer', 'layer-order', 'partial-opacity',
                  'offset-and-clipping', 'hidden-layer', 'multiply-blend']:
    ora_path = Path(f'/tmp/ora-harness-out/{scene_id}.ora')
    with zipfile.ZipFile(ora_path) as z:
        png_bytes = z.read('mergedimage.png')
    results.append(compare_scene(
        scene_id, png_bytes,
        producer_name='GIMP', producer_version='2.10.x (record exact patch version)',
    ))
write_manifest(results, Path('/tmp/ora-harness-out/comparison-manifest.json'))
print(open('/tmp/ora-harness-out/comparison-manifest.json').read())
"
```

### Required packages

- `gimp` (2.10.x) and `xvfb`, via `apt-get` on an Ubuntu runner (or
  equivalent for another distribution).
- This repository's own Python environment (`pip install -e .` from the
  repo root, or just `PYTHONPATH=.` against the checked-out source tree —
  no additional Python packages beyond what `format_factory.ora` itself
  needs).

### Expected runtime

GIMP batch-mode startup is the dominant cost (2-5 seconds per invocation on
a typical CI runner); with 6 currently-scripted scenes, expect roughly
15-40 seconds total, well within any CI job's own timeout budget.

### Expected outputs

- One `.ora` file per scripted scene in `/tmp/ora-harness-out/` (or
  wherever the output path is redirected), each GIMP's own genuinely
  independent export.
- `comparison-manifest.json`, matching the `ora-producer-harness/
  comparison-manifest@1` schema `compare.py`'s own `write_manifest()`
  writes — `result: "PASS"` only if every scripted scene is
  `within_tolerance`.

### Success criteria

- Every scripted scene's own GIMP export must load through
  `format_factory.ora`'s own `loads()` (STRICT mode — GIMP's own OpenRaster
  exporter is a maintained, actively-developed implementation, unlike the
  vendored MyPaint fixtures found non-conformant this session; if GIMP's
  own export also fails STRICT, that is itself a real, reportable finding,
  not a harness bug to work around).
- Each scene's `mergedimage.png` must be full-canvas resolution (verify
  this directly, the way this session verified MyPaint's own
  `fill_outlines.ora` was NOT, before trusting it as a comparison target).
- `compare_scene(...)`'s own `pixel_exact_match` or `within_tolerance` (for
  a documented, non-zero tolerance) must be `True` for every scene before
  this evidence can be cited toward ORA-RENDER-001/COMPOSITE-001/
  ISOLATION-001's own release gate.

## Once real GIMP output exists

1. Vendor the real `.ora` outputs into a clearly-labeled directory
   (matching this session's own `tests/python/ora/fixtures/
   third-party-gpl-mypaint/` convention, but licensed under GIMP's own
   terms — GIMP is GPL-3.0+, so the same vendoring-shape discipline that
   memo established applies again here).
2. Run `write_manifest(...)` against the real comparison and commit the
   resulting `comparison-manifest.json` as `execution_evidence` in
   `shared/format-contracts/implementation-evidence/ora.yaml`, following
   this repo's own existing `execution_evidence_ids` convention.
3. Only then update the 4 affected obligations' own `missing_behavior` —
   and only for the scenes actually proven, not by extrapolation. GIMP
   alone still supplies only ONE independent producer; ORA-RENDER-001's own
   gate says "at least two" — a second (MyPaint, once/if its own
   conformance gaps are separately addressed, or another real OpenRaster
   application) remains necessary before any of these 4 obligations can
   honestly move past `partial`.
