# ORA-BASELINEASSET-001 visual-assurance execution — provenance record

Executes the procedure in
`reports/format-contract-layer/ora-baseline-asset-visual-assurance-amendment.md`
(§3), against the already-verified `multiply-blend` and `layer-order`
scenes from `tools/ora/producer_harness/scene_matrix.py`.

## What was generated

`tools/ora/producer_harness/build_baseline_asset_fixtures.py` built each
scene as a real `OraDocument` and called format-factory's own
`generate_baseline_assets()` (`render.py:1055`) — the code path under
test, never exercised by any prior evidence this session built. For both
scenes, `thumbnail-<id>.png` and `mergedimage-<id>.png` are byte-identical
(both scenes are well under `THUMBNAIL_MAX_EDGE=256`, so
`generate_thumbnail()` takes its "encode unchanged" path, confirmed by an
assertion in the build script itself, not merely expected).

## Independent-consumer pixel readback

**GIMP** (`ora-harness-gimp:pinned-2026-08-11`,
`gimp_scripts/check_baseline_asset_pixels.scm`): loaded each real
mergedimage.png via `gimp-file-load` (GIMP's own PNG decoder, not
format-factory's) and read back every pixel via
`gimp-drawable-get-pixel`. 1024 pixels (multiply-blend, 32×32) + 4096
pixels (layer-order, 64×64) = 5120 total, dumped as CSV, log at
`gimp-pixel-dump.log`.

**Krita** (`ora-harness-krita:pinned-2026-08-12`,
`krita/scripts/check_baseline_asset_pixels.py`): loaded each real
mergedimage.png via `Krita.instance().openDocument()` (Krita's own PNG
decoder) and bulk-read every pixel via `doc.pixelData(0, 0, w, h)`. Same
5120 pixels, log at `krita-baseline-pixel-dump.log`, sentinel `PASS`.

## Comparison result — exact match

Compared both independent read-backs against format-factory's own known
pixel content (the `DecodedRaster` that `generate_baseline_assets()` was
given to encode, recorded in `expected-manifest.json`):

| Scene | Pixels | GIMP mismatches | Krita mismatches |
|---|---|---|---|
| multiply-blend | 1024 | 0 | 0 |
| layer-order | 4096 | 0 | 0 |

Every one of 5120 pixels, both producers, both scenes: exact byte-for-byte
agreement (RGBA, including alpha). This directly satisfies §3 step 5 of
the amendment (tolerance = 0, exact match) — real independent decoders,
not a self-consistent round trip, confirm format-factory's own PNG
encoder produces bytes that mean exactly what format-factory intended.

## Contact sheets and canary self-check

`tools/ora/producer_harness/build_baseline_asset_contact_sheets.py` built
one deterministic contact sheet per scene (`contact-sheets/`): 4 panels
(format-factory | GIMP-decoded | Krita-decoded | amplified diff, ×16,
max-over-producers), separated by a fixed yellow gutter, 10× nearest-
neighbor upscaled. Both real sheets: `max_delta=0`, diff panel exactly
`(0,0,0,255)` everywhere.

Per a valid concern raised by one of the two independent reviewers below
("a solid-black diff panel is equally consistent with a broken diff tool
that always emits black") — built one additional **canary** sheet
(`CANARY-injected-defect-layer-order.png`), injecting a deliberate,
known-wrong 10×10 red patch into the *expected* side only (GIMP/Krita
read-backs unchanged) before running the identical diff code. Result:
`max_delta=255`, `100/4096` pixels flagged, and the diff panel shows a
visible white square at exactly the injected patch's own location on an
otherwise-black background — proof the diff/amplification code path
genuinely detects and visualizes a real discrepancy, not merely emitting
black unconditionally. This is a machinery self-check, not asset
evidence; the real (non-canary) sheets are the actual evidence.

## Independent vision-capable review

Two fresh general-purpose agents, each given only the two real contact
sheets (not the canary) and no prior conclusion, independently inspected
both images (visually via the Read tool, then confirmed with their own
independent pixel-level verification — a choice both reviewers made
unprompted, not requested).

**Reviewer 1 verdict: PASS** (both scenes). Confirmed panels 1–3
byte-identical, diff panel true zero, no clipping/offset/opacity/halo/
color-shift/blend-anomaly defects. Flagged a real, honest limitation:
the `multiply-blend` scene is a single flat full-canvas color with no
internal structure, so it cannot exercise edge/partial-coverage defects
— a true statement about this specific 2-scene sample, not a defect in
what was found.

**Reviewer 2 verdict: PASS** (both scenes), reached independently via
its own separate pixel-level analysis. Confirmed the same byte-identical
result and additionally: (a) correctly identified that `layer-order`'s
apparent white background is actually alpha=0 transparency composited
onto a white canvas by the PNG viewer, not a real white fill layer — a
precise, correct observation, not a false-positive defect; (b) raised
the diff-tool self-verification concern addressed by the canary check
above; (c) independently confirmed no anti-aliasing exists at any
boundary in either scene (both use only hard-edged, axis-aligned
rectangles), naming this as a real, disclosed gap in scene diversity —
the same class of finding as reviewer 1's, reached independently.

Both reviewers reached the same verdict via genuinely independent
methodologies (one used PIL/numpy per-panel byte comparison, the other
used PIL/numpy with explicit yellow-gutter-column boundary detection) —
agreement here is real corroboration, not two agents echoing each other,
since neither saw the other's report.

## Honest scope disclosure

This procedure was executed for 2 of the scenes in `scene_matrix.SCENES`
(the ones both reviewers correctly flagged as having no anti-aliased or
partial-opacity content) — not the full 8-scene canonical matrix, and
not every scene combination `generate_baseline_assets()` could ever be
asked to encode. It proves the PNG-encoding path used by this session's
own most heavily-verified scenes decodes correctly in two independent,
real applications; it does not prove every possible scene (e.g. one
requiring real thumbnail downscaling, explicitly out of the amendment's
own §3 step 5 scope) would.

## Committed files (paths relative to `baseline-asset-evidence-2026-08-12/`)

- `mergedimage-{multiply-blend,layer-order}.png`,
  `thumbnail-{multiply-blend,layer-order}.png` — real
  `generate_baseline_assets()` output.
- `expected-manifest.json` — format-factory's own known-correct pixel
  content per scene, hex-encoded.
- `visual-assurance-manifest.json` — the machine-readable summary this
  obligation's own execution-evidence entry
  (`ORA-BASELINEASSET-VISUAL-ASSURANCE-PROOF`) points at: per-scene
  mismatch counts, the canary self-check result, and both reviewers'
  verdicts.
- `krita-baseline-pixel-dump.sentinel` — Krita's own driver-exit status
  (`PASS`).
- `contact-sheets/contact-sheet-{multiply-blend,layer-order}.png`,
  `contact-sheets/contact-sheet-manifest.json` — real evidence, both
  reviewers' subject.
- `contact-sheets/CANARY-injected-defect-layer-order.png` — machinery
  self-check only, not asset evidence.

**Not committed** (repo-wide `.gitignore` excludes `*.log`, matching
this harness's own existing convention — no prior GIMP/Krita execution
this session committed a raw log either): `gimp-pixel-dump.log`
(5120-line CSV, all pixels for both scenes) and
`krita-baseline-pixel-dump.log` (same). Both are mechanically
reproducible by rerunning the exact `docker run` invocations below
against the committed `check_baseline_asset_pixels.scm`/`.py` scripts
and the committed PNG fixtures — nothing about them is unique,
hand-edited, or otherwise irreplaceable. The mismatch counts they
produced (0/1024, 0/4096) are recorded in `visual-assurance-manifest.json`
and cross-checked by both independent vision-capable reviewers against
the contact sheets built directly from them.

## Reproducing this execution

```bash
# 1. Regenerate the fixtures (thumbnail.png/mergedimage.png + expected-manifest.json)
python tools/ora/producer_harness/build_baseline_asset_fixtures.py <out-dir>

# 2. GIMP pixel readback (Git Bash on Windows needs MSYS_NO_PATHCONV=1)
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tools/ora/producer_harness/gimp_scripts:/scripts:ro" \
  -v "<out-dir>:/out" \
  ora-harness-gimp:pinned-2026-08-11 \
  gimp -i -d -f \
    -b '(begin (load "/scripts/check_baseline_asset_pixels.scm"))' \
    -b '(gimp-quit 0)'
# stdout contains one "script-fu-Warning: <scene>,<x>,<y>,<r>,<g>,<b>,<a>" line per pixel

# 3. Krita pixel readback
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tools/ora/producer_harness/krita/scripts:/scripts:ro" \
  -v "<out-dir>:/out" \
  -e ORA_HARNESS_SCRIPT=/scripts/check_baseline_asset_pixels.py \
  -e ORA_HARNESS_LOG=/out/krita-baseline-pixel-dump.log \
  -e ORA_HARNESS_SENTINEL=/out/krita-baseline-pixel-dump.sentinel \
  ora-harness-krita:pinned-2026-08-12 \
  krita --nosplash

# 4. Build contact sheets from the two logs above
python tools/ora/producer_harness/build_baseline_asset_contact_sheets.py <out-dir> <out-dir>/contact-sheets
```
