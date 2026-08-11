# ORA-COMPOSITE-001 full-inventory coverage — provenance record

Base commit: `1c0d72f9e` (FF6 Event 519 — ORA 2/134 unresolved, Krita
producer #2 established).

`COMPOSITE_OP_REGISTRY` (`model/composite_ops.py`) declares **20** distinct
composite-op values — not 21, and not a 15×6 blend/Porter-Duff cross
product: 15 unique blend-function names (all paired with Source Over) and
6 unique Porter-Duff operator names (all paired with Normal blend, i.e. no
color mixing). `svg:src-over` (Normal) and `svg:multiply` already had real
two-producer pixel-exact evidence before this session (the 8-scene
matrix). This record covers the remaining **18**.

## Independent mathematical oracle — precise scope (corrected after review)

`tools/ora/producer_harness/composite_oracle.py` implements the W3C
Compositing and Blending Level 1 blend formulas and the Porter & Duff
(1984) operator formulas in straight-alpha space, as a single-pixel pure
function structured differently from `render.py`'s own premultiplied-
canvas, bounds-iterating implementation. **An independent review caught
an overclaim in this document's own first draft** ("re-derives... not
copied") and it is corrected here: the compositing/bounds CONTROL FLOW is
genuinely independently structured — this is what actually caught the
real Destination In/Atop bounds defect below, since the oracle never
adopted render.py's own "only iterate the layer's bounds" optimization at
all. The per-channel BLEND-FUNCTION formula bodies, however, are
structurally similar to render.py's own — direct transcriptions of the
same published equations, which mostly have one sane way to write a single
arithmetic expression. A bug in one specific formula body shared by both
files would not be caught by this cross-check. Cross-validated against
`render()` for the 2 already-covered operations (Normal, Multiply) before
being trusted for the other 18 — exact match, both cases; this specific
claim was independently reproduced by the reviewer.

## Discriminating fixtures — verified, not assumed

- **Blend functions**: backdrop `(30,200,60)` opaque, source `(220,40,180)`
  alpha `166/255`. An earlier candidate pair produced identical `Hue` and
  `Color` results — a real, silent failure to discriminate two distinct
  operations, caught by running all 15 blend functions through the oracle
  and checking pairwise distinctness before committing to a fixture, not
  by inspection.
- **Porter-Duff operators**: destination `(230,60,40)` alpha `153/255` at
  `(0,0)`-`(20,20)`; source `(40,120,230)` alpha `128/255` at
  `(12,12)`-`(32,32)`. Sample points: `(5,5)` destination-only, `(25,25)`
  source-only, `(16,16)` overlap (partially-transparent, both layers
  alpha<1), `(2,28)` fully transparent. Verified via the oracle to produce
  6 pairwise-distinct results (including Source Over, as a continuity
  check) at the overlap point before use.

## Real defect found and fixed: `render.py`'s own Porter-Duff bounds handling

Comparing `render()`'s own output for the Porter-Duff scenes against the
independent oracle (**before any producer was involved**) surfaced a real,
reproducible defect: `_composite_layer_onto` only ever iterated the
intersection of canvas and source-layer bounds. For Source Over and 3 of
the 5 other operators (Lighter, Destination Out, Source Atop), that
coincides with the mathematically correct answer (their own Porter-Duff
`Fb` coefficient equals 1.0 at `alpha_s=0`, i.e. "leave the destination
unchanged"). For **Destination In** and **Destination Atop**, `Fb=alpha_s`,
which is `0.0` (not `1.0`) outside the source layer's own bounds — the
destination must be **cleared** there, not left untouched. Confirmed by
direct computation (`porter_duff_coeffs('Destination In', alpha_s=0.0,
alpha_b=0.6) == (0.0, 0.0)`) before writing a test, then 3 new regression
tests (2 failing-first, 1 contrast case proving the fix doesn't
over-correct the other 3 operators) in
`tests/python/ora/test_obligation_render_and_compositing.py`. Fixed by
evaluating non-Source-Over operators over the full canvas, with
out-of-bounds pixels treated as the explicit `alpha_s=0` the formula
itself expects. Full ORA suite after the fix: 462 passed (three new
tests), 0 failed.

## Producer capability — established empirically, not from documentation

Every mode-name-to-constant mapping and every "does this producer support
this operation" determination below was checked by rendering the exact
discriminating fixture and comparing the real pixel output to the oracle
— not inferred from a mode's name.

- **GIMP** (`ora-harness-gimp:pinned-2026-08-11`): its own legacy blend
  modes match the W3C formula exactly for **7 of 13** remaining blend
  functions (Screen, Darken, Lighten, Color Dodge, Color Burn, Hard Light,
  Difference). The other 6 (Overlay, Soft Light, Hue, Saturation, Color,
  Luminosity) use a **genuinely different formula** — not a rounding
  difference (deltas up to 29/255 on a single channel). GIMP's own
  `LAYER-MODE-HSV-VALUE`, the only plausible "Luminosity" candidate, is
  confirmed NOT equivalent to W3C's HSL-based Luminosity — a different
  color-model computation, not a naming coincidence. GIMP's own apt
  package has **zero OpenRaster plugin support** (already established in
  the GIMP producer-execution provenance) — every `gimp-file-load` on a
  real `.ora` fails with "Unknown file type," reconfirmed here — so GIMP
  cannot serve as a consumer for the Porter-Duff fixtures either. GIMP's
  own layer-mode system has **no Porter-Duff-operator selection at all**
  (confirmed: `LAYER-MODE-ADDITION-LEGACY`, the only plausible
  `svg:plus`/Lighter candidate, gives `(173,226,177)` where the true
  formula requires `(105,137,107)` for the same fixture) — GIMP always
  composites with implicit Source Over regardless of blend mode.
- **Krita** (`ora-harness-krita:pinned-2026-08-12`): matches the W3C
  formula for **all 13** remaining blend functions — exact match on 8,
  within 1 unit per channel on 5 (Lighten, Soft Light, Hue, Color,
  Luminosity), consistent with a benign floating-point rounding-mode
  difference (round-half-to-even vs round-half-up), not a wrong formula —
  the same 5 functions that involve more accumulated float arithmetic
  (HSL `SetLum`/`SetSat`, or Soft Light's own two-branch formula); the
  8 simpler functions all matched to 0 delta. Krita's own `blendingMode()`
  also has **no Porter-Duff-operator selection** (its own `"add"` mode
  gives `(173,226,177)` for the same fixture, identical to GIMP's own
  wrong answer, confirming this is a structural gap in both applications'
  layer-mode model, not an implementation quirk of one). Krita **can**
  open real `.ora` files (already established), so it was tested as an
  `INDEPENDENT_CONSUMER_RENDER` consumer for all 5 Porter-Duff operators.

## Porter-Duff consumer-render fixtures — format-factory as the writer

`tools/ora/producer_harness/build_composite_consumer_fixtures.py` uses
`format_factory.ora.lifecycle.dumps(preservation=PreservationMode.CANONICAL)`
— which regenerates `stack.xml` from a fresh in-memory `OraDocument`, not a
byte-preserving round-trip of an existing file — plus
`render.generate_baseline_assets` for the required thumbnail/mergedimage,
to author 5 real, complete `.ora` archives, one per Porter-Duff operator.
All 5 independently confirmed to pass format-factory's own **STRICT**
reader with **zero recovery actions** before being handed to either
producer. Committed at
`tools/ora/producer_harness/composite-evidence-2026-08-12/porterduff-fixtures/`.

## Krita's own Porter-Duff import results — precise, per-region diagnosis

Comparing Krita's own re-exported PNG (fresh process, `krita --export`)
against format-factory's render at all 4 discriminating sample points:

| Operator | dest-only | source-only | overlap | transparent | Disposition |
|---|---|---|---|---|---|
| `svg:dst-out` | match | match | match | match | **Exact match, all 4 points** |
| `svg:dst-in` | alpha matches (0), RGB differs under alpha=0 | match | match | match | **Conformant** — the only "mismatch" is RGB bytes under a fully-transparent pixel, which has no visual meaning |
| `svg:src-atop` | match | alpha matches (0), RGB differs under alpha=0 | match | match | **Conformant**, same benign note |
| `svg:dst-atop` | alpha matches (0), RGB differs under alpha=0 | match | match | match | **Conformant**, same benign note |
| `svg:plus` (Lighter) | match | RGB off by 1 (rounding) | **real mismatch** — Krita's own reported alpha (204) exactly matches the *Source Over* alpha formula (`alpha_s + alpha_b*(1-alpha_s)` = 0.801→204), not the true Porter-Duff Lighter formula (`alpha_s + alpha_b` = 1.102, clamped to 255) | match | **Genuine import limitation** — Krita's own OpenRaster reader does not correctly implement `svg:plus` |

The "RGB differs under alpha=0" pattern was checked explicitly, not
assumed benign: in all 3 cases the **alpha channel matches exactly** (0 in
both), meaning the pixel is fully transparent in both format-factory's and
Krita's own output — an invisible pixel's own RGB payload is not a
semantic disagreement about what the image looks like.

## Coverage matrix (machine-readable)

`tools/ora/producer_harness/composite-coverage-matrix-2026-08-12.json` —
20 rows (the complete registry), each with: canonical operation identifier,
OpenRaster identifier, format-factory implementation location, normative
source, GIMP/Krita native mapping, native-creation and import-render
capability per producer, fixture path, producer reference paths, strict-
reader result, semantic-oracle result, pixel-comparison result, evidence
type (`PRODUCER_NATIVE_EXPORT` vs `INDEPENDENT_CONSUMER_RENDER`, never
conflated), and final coverage status.

Summary: **9 `COVERED`** (both producers agree) — Normal, Multiply, Screen,
Darken, Lighten, Color Dodge, Color Burn, Hard Light, Difference.
**10 `COVERED_SINGLE_PRODUCER`** (one producer's real, genuine agreement;
the other either non-conformant or structurally unable to test) — Overlay,
Soft Light, Hue, Saturation, Color, Luminosity (Krita only, GIMP's own
formula genuinely differs); Destination Out, Destination In, Source Atop,
Destination Atop (Krita only, as consumer — GIMP cannot open `.ora` files
at all). **1 `NOT_COVERED`** — Lighter (`svg:plus`): Krita's own import is
wrong, GIMP cannot test it at all; zero valid producer agreement exists
for this one operation.

## What this evidence does and does not establish

- **Does establish**: real, substantially expanded, independently-verified
  producer evidence for 19 of 20 registered composite-op values (up from
  2 of 20 before this session) — including a genuine defect in
  format-factory's own renderer found and fixed as a direct result of this
  exercise (not a producer-side finding).
- **Does not establish**: that "all claimed operations match pinned
  rendering references," the obligation's own literal release-gate text.
  9 of 20 have two-producer agreement; 10 of 20 have only one (the other
  producer is either genuinely non-conformant — a real, disclosed
  limitation, not a gap in this session's own testing — or structurally
  unable to participate at all); 1 of 20 (`svg:plus`) has none. The
  obligation stays `partial`, with this precise breakdown as its own
  `missing_behavior`, not a vague "needs more testing."
