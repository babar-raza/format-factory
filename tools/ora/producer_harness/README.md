# ORA independent-producer comparison harness

State: **executed** — GIMP 2.10.30 was run for real, autonomously, inside a
disposable pinned Docker container (`ora-harness-gimp:pinned-2026-08-11`),
against the full 8-scene canonical matrix. Full account, exact commands,
checksums, and stdout/stderr: `PROVENANCE-gimp-execution-2026-08-11.md`.
Result: **8/8 scenes pixel-exact**. This is genuine, verified evidence of
independent-producer compositing agreement — not a claim that the shared
"at least two independent producers/consumers" release gate is fully met
(it isn't: this achieves one of the required two — see "What remains open"
below).

## What this answers

ORA-RENDER-001 / ORA-COMPOSITE-001 / ORA-ISOLATION-001 share one release
gate, compiled from `POL-LRA-RENDER-01` and its siblings
(`shared/format-contracts/policy/family-packs/layered_raster_archive.yaml`)
into the real product contract (`shared/format-contracts/ora.yaml`) via
`contract_compiler.py` — an authorized project policy, not a spec-normative
claim. It asks for rendering that "agrees with at least two independent
producers/consumers within declared tolerances." `ORA-BASELINEASSET-001`
has a related but distinct gate: "generated viewing assets are accepted and
visually checked by independent consumers." This harness produces evidence
for both.

## What is built and tested here

| File | Purpose | Tested by |
|---|---|---|
| `scene_matrix.py` | 8 producer-agnostic scene definitions covering layer order, opacity, clipping, visibility, one blend mode, and isolated-vs-non-isolated group compositing | `test_ora_producer_harness_compare.py` (imports and renders every scene) |
| `format_factory_side.py` | Realizes a scene with format-factory's own `OraStack`/`OraLayer` model and renders it | Same |
| `compare.py` | Pure comparison math (pixel-exact + tolerance-based), manifest generation, malformed-input handling — the actual reconciler-facing logic | 17 tests, all mocked producer input |
| `gimp_scripts/generate_scenes.scm` | **The real, working, GIMP-Script-Fu (Scheme) generator** — executed against a real GIMP 2.10.30 install; constructs every scene with GIMP's own layer/group compositing engine and exports a flattened PNG | Real execution only (Script-Fu cannot run outside GIMP's own bundled interpreter) — see `PROVENANCE-gimp-execution-2026-08-11.md` |
| `gimp_scripts/generate_scene.py` | Original GIMP **Python-Fu** draft | **Superseded, not used.** GIMP 2.10's apt package on Ubuntu 22.04 does not ship a working Python-Fu batch interpreter (it requires Python 2, which Ubuntu 22.04 dropped) — confirmed via `GIMP-Warning: The batch interpreter 'python-fu-eval' is not available`. Kept for historical reference only. |
| `Dockerfile` / `entrypoint.sh` | Pinned, disposable GIMP execution environment (Ubuntu 22.04 + GIMP 2.10.30 apt package + Xvfb, with a manual Xvfb-readiness poll instead of `xvfb-run`, whose SIGUSR1 handshake did not reliably fire under this host's Docker Desktop/WSL2 backend) | Real execution — see provenance doc |

The drift guard (`test_gimp_script_scene_ids_are_a_subset_of_the_canonical_matrix`)
still checks `generate_scene.py`'s own scene-ID list against `scene_matrix.py`
(it predates the Script-Fu script and was never repointed — the two Scheme
and Python scene lists are kept in sync manually per each file's own header
comment, not by an automated check).

## What actually happened, briefly (full account in the provenance doc)

GIMP 2.10's apt package on Ubuntu 22.04 ships **no OpenRaster plugin at
all** (confirmed: 0 PDB procedures match `openraster`; no
`file-ora*`/`file-openraster*` plugin binary anywhere in the image) — so
this harness does not produce real `.ora` files. It constructs each scene
with GIMP's own compositor and exports the flattened result as a plain PNG,
which is exactly what `compare.py` needs and is disclosed everywhere this
evidence is used: it proves independent *compositing* agreement, not
OpenRaster *container* interop with GIMP specifically (a separate concern,
`ORA-CONTAINER-001`).

Two genuine defects were found and root-caused (not guessed) via exact
pixel diffing against format-factory's own render output, both now fixed in
`generate_scenes.scm` — see that file's own header comments and
`scene_matrix.py`'s own `non-isolated-group` docstring for the complete
accounts:

1. A coordinate bug in `fill-solid-layer`: it selected a fixed
   `(0, 0, width, height)` region in image-global coordinates regardless of
   the target layer's own offset, silently under-filling any non-zero-offset
   layer (invisible for every offset-`(0,0)` scene, which is most of them).
2. `scene_matrix.py`'s original `non-isolated-group` scene used group
   `opacity=0.5`, which `OraStack.is_isolated_group` — directly implementing
   the OpenRaster spec's own literal "isolation is isolate, opacity is below
   one, or composite-op differs from svg:src-over" text — *always* forces
   into isolated compositing, regardless of the declared `isolation`
   attribute. That scene could never have exercised non-isolated compositing
   against format-factory's own renderer, no matter what GIMP produced. The
   fix belonged in the scene definition, not the GIMP script: group
   `opacity=1.0` (not forcibly isolated) with one child using a non-default
   composite-op (`svg:multiply`) — the only condition under which isolated
   vs. non-isolated compositing can differ at all, since Porter-Duff `over`
   is otherwise associative.

A separate check loaded a format-factory-*generated* PNG
(`encode_png()` of a real `render()` output) into the same real GIMP
instance, confirming successful decode at the correct dimensions — direct,
automated independent-consumer-acceptance evidence for
`ORA-BASELINEASSET-001`.

## What remains open

The shared release gate says "at least **two** independent
producers/consumers." This harness's real execution achieves exactly
**one** (GIMP) with full pixel-comparison evidence. The vendored MyPaint
corpus (`tests/python/ora/fixtures/third-party-gpl-mypaint/`) is a real,
independent, second application's output, and all 3 of its files now load
successfully under `ReadMode.TOLERANT` — but none provides a usable
full-resolution ground truth for pixel comparison (only one file embeds a
`mergedimage.png`, and it is a 64×64 thumbnail, not the document's real
canvas resolution). Scripting MyPaint itself as a second controlled-scene
producer (GIMP's own role here) was investigated and found architecturally
infeasible within a reasonable session scope: MyPaint's own apt package is
a GTK/GObject-Introspection interactive painting application with no
documented batch/procedural scripting interface comparable to GIMP's own
Script-Fu/PDB. `ORA-RENDER-001` / `ORA-COMPOSITE-001` / `ORA-ISOLATION-001`
/ `ORA-BASELINEASSET-001` therefore all stay `partial`, not `implemented` —
see `shared/format-contracts/implementation-evidence/ora.yaml`'s own
`missing_behavior` entries for each obligation's precise, current gap.

## Reproducing this execution

See `PROVENANCE-gimp-execution-2026-08-11.md` for the exact `docker build`
/ `docker run` commands, image digest, and checksums. In short:

```bash
docker build --build-arg http_proxy=<your-proxy> --build-arg https_proxy=<your-proxy> \
  -t ora-harness-gimp:pinned-2026-08-11 tools/ora/producer_harness

docker run --rm \
  -v "$(pwd)/tools/ora/producer_harness/gimp_scripts:/scripts:ro" \
  -v "<host-output-dir>:/out" \
  ora-harness-gimp:pinned-2026-08-11 \
  gimp -i -d -f \
    -b '(begin (load "/scripts/generate_scenes.scm") (run-all-scenes "/out"))' \
    -b '(gimp-quit 0)'
```

Then compare with `tools/ora/producer_harness/compare.py::compare_scene`
against `tools/ora/producer_harness/format_factory_side.py::render_scene`
for each scene in `scene_matrix.SCENES`.
