# Real GIMP producer-harness execution — provenance record

Base commit this execution was performed against: `6df67b3d63c3b0ac807fc947c0ea2aee64703b6b`.

This is a factual record of one real, autonomous execution of the ORA
producer-comparison harness against a real, independently-developed
application (GIMP), run entirely inside a disposable container on this
session's own host — no host-level package installation, no external human
action. It complements (does not replace) `README.md` and the vendored
MyPaint corpus's own `PROVENANCE.md`.

## Container / image identity

| Field | Value |
|---|---|
| Image tag | `ora-harness-gimp:pinned-2026-08-11` |
| Image ID | `sha256:5a7a0f1b376e6f1bdd87323e56004fc76a64eeab8b6382076fbb795f043a0575` |
| Image created | `2026-08-11T11:27:37.818958439Z` |
| Base image | `ubuntu:22.04` |
| Runtime used | Docker Desktop 28.4.0 (Windows, WSL2 backend) — detected and used per the
  required detection order (Docker found first; Podman/other OCI runtimes/CI
  runner were not needed) |
| Dockerfile | `tools/ora/producer_harness/Dockerfile` (this commit) |
| Entrypoint | `tools/ora/producer_harness/entrypoint.sh` (this commit) — manual Xvfb
  startup + `xdpyinfo` readiness poll, not `xvfb-run` (see Dockerfile's own
  comment for why: `xvfb-run`'s SIGUSR1 handshake did not reliably fire under
  this host's Docker Desktop/WSL2 backend) |

## OS / package versions (recorded at build time, `/opt/versions.txt` inside the image)

```
base_image: ubuntu:22.04
gimp_version: GNU Image Manipulation Program version 2.10.30
gimp_package_version: 2.10.30-1ubuntu0.1
xvfb_package_version: 2:21.1.4-2ubuntu1.7~22.04.16
x11_utils_package_version: 7.7+5build2
built_at_utc: 2026-08-11T11:25:36Z
```

GIMP's Python-Fu batch interpreter is **not available** in this apt package
(Ubuntu 22.04 dropped Python 2, which GIMP 2.10's Python-Fu requires — the
package emits `GIMP-Warning: The batch interpreter 'python-fu-eval' is not
available` and any `-b '(python-fu-eval ...)'` batch command silently
no-ops). Script-Fu (Scheme) **is** available and is what this harness
actually uses (`gimp_scripts/generate_scenes.scm`). The `gimp` apt package
also ships **zero OpenRaster plugin support** (confirmed via PDB query
returning `count=0` for any procedure matching `openraster`, and via a full
filesystem search of `/usr/lib/gimp/2.0/plug-ins/` finding no
`file-ora*`/`file-openraster*` binary) — so this harness constructs each
scene with GIMP's own layer/group compositing engine and exports the
flattened result as a plain PNG, not a real `.ora` container. This proves
independent *compositing* agreement, not OpenRaster *container* interop with
GIMP specifically (a separate question, covered by `ORA-CONTAINER-001`, not
this obligation set).

## Exact commands run

Build (proxy build-args required for `apt-get` DNS resolution inside this
host's Docker Desktop network — `http.docker.internal:3128`, read from
`docker info`'s own `HTTP Proxy` field):

```
docker build --build-arg http_proxy=http://http.docker.internal:3128 \
  --build-arg https_proxy=http://http.docker.internal:3128 \
  -t ora-harness-gimp:pinned-2026-08-11 tools/ora/producer_harness
```

Scene generation (all 8 scenes, one process, one Script-Fu session so
`(load ...)` state is shared — two separate `-b` flags do not share
Script-Fu global state in this GIMP build, confirmed empirically):

```
docker run --rm \
  -v "<repo>/tools/ora/producer_harness/gimp_scripts:/scripts:ro" \
  -v "<host-output-dir>:/out" \
  ora-harness-gimp:pinned-2026-08-11 \
  gimp -i -d -f \
    -b '(begin (load "/scripts/generate_scenes.scm") (run-all-scenes "/out"))' \
    -b '(gimp-quit 0)'
```

Consumer-acceptance check (format-factory-generated PNG opened by real GIMP,
for `ORA-BASELINEASSET-001`'s own independent-consumer-acceptance gate):

```
docker run --rm -v "<host-output-dir>:/out:ro" ora-harness-gimp:pinned-2026-08-11 \
  gimp -i -d -f \
    -b '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE
          "/out/format-factory-generated-mergedimage.png"
          "format-factory-generated-mergedimage.png"))))
          (gimp-message (string-append "LOADED width="
            (number->string (car (gimp-image-width image))) " height="
            (number->string (car (gimp-image-height image))) " layers="
            (number->string (car (gimp-image-get-layers image)))))
          (gimp-image-delete image))' \
    -b '(gimp-quit 0)'
```

## Exit status / stdout / stderr

All 3 invocations above exited `0`. Scene-generation run's own final lines:

```
entrypoint.sh: Xvfb ready on :99 after 1 poll attempts
using gegl copy   [x22 -- one per fill/merge operation across the 8 scenes]
script-fu-Warning: all scenes generated

batch command executed successfully
```

("script-fu-Warning" is Script-Fu's own informational-message channel for
`gimp-message`, not an actual warning/error — no diagnostic-severity output
was produced by any of the 3 runs.)

Consumer-acceptance run's own final lines:

```
entrypoint.sh: Xvfb ready on :99 after 1 poll attempts
script-fu-Warning: LOADED width=32 height=32 layers=1

batch command executed successfully
```

32×32 / 1 layer exactly matches the source raster `encode_png()` was given
(`isolated-group-with-opacity` scene, rendered by format-factory's own
`render()` and encoded by format-factory's own `encode_png()` —
`src/python/ora/src/format_factory/ora/render.py`), confirming GIMP accepted
and correctly decoded format-factory's own generated PNG asset.

## Output checksums

SHA-256 of every PNG this execution produced (`<host-output-dir>`, GIMP's own
output unless noted):

| File | Bytes | SHA-256 |
|---|---|---|
| `single-opaque-layer.png` | 634 | `162a9fe043c23e720664ac750827ce316c7417d4983da859d46181e1c5feb31d` |
| `layer-order.png` | 658 | `539ebd8e48685f68766f91729555408b589ac56bfcb6e84d64661ab3a1e22ec7` |
| `partial-opacity.png` | 632 | `ebc580817f004913303c37b4ade2b95811c7c3aa651ad8412732e4673ce03531` |
| `offset-and-clipping.png` | 578 | `2f3184ec85ec587396e8e0afbc51a3fd25b1fd47bf4636281057912854a342a9` |
| `hidden-layer.png` | 576 | `ea99fce315b41f47c0d5bc7797e20292ef393648efd5b4cb0d5854a0050fc17c` |
| `multiply-blend.png` | 581 | `bc0e9c689f479a4a324f3a3469b8dea21e8108b2f14e2ea50b2998627138a48a` |
| `isolated-group-with-opacity.png` | 576 | `dbc96d2cc3f56dec1cc4c486af01f4e9b204d754363e16c0aec9e7c01553de8f` |
| `non-isolated-group.png` | 579 | `b482f84bb4dbf889139d7b39a0a40917f0b12e4a178eb38b822b81f465ba2100` |
| `format-factory-generated-mergedimage.png` (format-factory's own output, fed **into** GIMP, not produced by it) | 101 | `1b78cd3a7a1cf59e2e9d1ae13b8b87b17145da6b924da965349cede1e97b6d00` |

**Update (2026-08-12):** the 8 GIMP-produced PNGs are now committed verbatim
at `tools/ora/producer_harness/evidence-gimp-2026-08-11/` (checksums
re-verified identical to the table above) — an earlier version of this
document described these as scratch-only artifacts; that is no longer
accurate. `format-factory-generated-mergedimage.png` (fed *into* GIMP, not
produced by it) is not duplicated there since it is reproducible directly
from `render.py`'s own `encode_png()` output for this scene, and is not
independent-producer evidence itself.

## Comparison results (GIMP vs. format-factory's own renderer)

All 8 scenes, pixel-exact (`tolerance=0`), via
`tools/ora/producer_harness/compare.py::compare_scene`:

| scene_id | pixel_exact_match | byte_diff_fraction | max_channel_delta |
|---|---|---|---|
| `single-opaque-layer` | True | 0.0 | 0 |
| `layer-order` | True | 0.0 | 0 |
| `partial-opacity` | True | 0.0 | 0 |
| `offset-and-clipping` | True | 0.0 | 0 |
| `hidden-layer` | True | 0.0 | 0 |
| `multiply-blend` | True | 0.0 | 0 |
| `isolated-group-with-opacity` | True | 0.0 | 0 |
| `non-isolated-group` | True | 0.0 | 0 |

**8/8 exact.** This is the *second* full run's result, after two genuine
implementation defects found during the *first* full run were fixed (see
`generate_scenes.scm`'s own header comments and `scene_matrix.py`'s own
`non-isolated-group` scene docstring for the complete root-cause accounts):

1. `fill-solid-layer` selected `(0,0,width,height)` in image-global
   coordinates regardless of the target layer's own offset — harmless for
   every offset-`(0,0)` layer, but silently under-filled `layer-order`'s own
   offset-`(16,16)` top layer. Fixed by querying the layer's real offset via
   `gimp-drawable-offsets` before selecting.
2. The original `non-isolated-group` scene used group `opacity=0.5`, which
   `OraStack.is_isolated_group` (per the OpenRaster spec's own literal text)
   *always* forces into isolated compositing regardless of the declared
   `isolation` attribute — so that scene could never have exercised
   non-isolated compositing against format-factory's own renderer at all,
   no matter what GIMP produced. Root-caused (not guessed, and only after
   two straight GIMP-side "fixes" — a real `PASS-THROUGH` group, then manual
   per-child opacity distribution — both correctly implemented genuine
   pass-through semantics and both, correctly, disagreed with format-factory's
   own necessarily-isolated rendering of the unsound scene) and fixed by
   redesigning the scene itself: group `opacity=1.0` (so isolation is not
   forced) with one child using a non-default composite-op (`svg:multiply`),
   which is the only condition under which isolated vs. non-isolated
   compositing can differ at all when Porter-Duff `over` is associative.
   Verified computationally against format-factory's own renderer before
   being committed: the corrected non-isolated scene renders byte-identical
   to the same 3 layers with no group wrapper (`(49,31,2,255)`, matching
   `test_non_isolated_auto_group_is_equivalent_to_no_group_at_all`'s own
   principle) and differs from the isolated variant of the identical
   children (`(124,49,6,255)`).

## What this evidence does and does not establish

- **Does establish:** GIMP, a real, independently-developed compositing
  application, run genuinely independently of format-factory's own code
  (no shared implementation, no shared authorship of the compositing math),
  agrees pixel-exactly with format-factory's own renderer across a scene
  matrix deliberately covering every semantic
  `POL-LRA-RENDER-01`/`ORA-RENDER-001`/`ORA-COMPOSITE-001`/`ORA-ISOLATION-001`
  name in their own rule text: layer order, clipping/offset, opacity,
  visibility, one documented blend mode (`svg:multiply`), and both isolated
  and non-isolated group compositing. GIMP also successfully opened a
  format-factory-*generated* PNG asset without error, at the correct
  dimensions — direct evidence for `ORA-BASELINEASSET-001`'s own
  independent-consumer-acceptance gate.
- **A real limitation, disclosed rather than smoothed over:** GIMP's own
  apt package ships no OpenRaster plugin at all (confirmed above), so this
  execution's own evidence is a plain flattened PNG comparison, produced
  and compared within the same process/session as scene construction — it
  does **not** include a save-as-`.ora`-then-reopen-in-a-fresh-process
  round trip. This is real, independent PIXEL COMPOSITING agreement (the
  actual concern of `ORA-RENDER-001`/`ORA-COMPOSITE-001`/`ORA-ISOLATION-001`'s
  own rule text — compositing math, not container framing, which is
  `ORA-CONTAINER-001`'s own separate concern), but is not the same
  evidentiary strength as a full container round trip.
- **Update (2026-08-12): a second producer was subsequently obtained.**
  This session's own later work (`tools/ora/producer_harness/krita/`)
  built and ran Krita — a second, real, independently-developed OpenRaster
  producer — achieving 8/8 pixel-exact scenes via genuine `.ora` files
  Krita serialized itself, reopened in a fresh process, and re-exported;
  see `tools/ora/producer_harness/krita/PROVENANCE-krita-execution-2026-08-12.md`
  for the full account, including that document's own precise, per-obligation
  release-gate wording (the 4 obligations do **not** share identical
  release-gate text — only `ORA-RENDER-001`'s own text literally says "at
  least two"). MyPaint's own vendored real-world corpus (see the
  third-party fixtures' own `PROVENANCE.md`) remains supplementary
  reading/compatibility evidence only — none of its 3 files provide a
  usable full-resolution ground truth for pixel comparison, and it is not
  counted as a producer toward this gate. See
  `implementation-evidence/ora.yaml`'s own current entries for the
  precise, per-obligation disposition after both producers' evidence.
