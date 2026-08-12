# [Draft, not submitted] GIMP 3.0.4: "Addition" layer mode does not conform to OpenRaster svg:plus / Porter-Duff Lighter

**Project**: GIMP
**Version**: 3.0.4 (Alpine Linux 3.23.5 `apk` package, confirmed via
`gimp --version`)
**Component**: `gimp_operation_layer_mode_blend_addition` (GEGL-backed
layer-mode implementation) and/or its own OpenRaster export/import
mapping to `svg:plus`
**Severity**: Correctness — imported/exported `svg:plus` layers do not
match the Porter-Duff Lighter formula OpenRaster requires

## Reproduction

Full provenance, both directions (native GIMP-3 export of an
Addition-mode layer, and GIMP-3 import+render of a strict externally-
authored `svg:plus` `.ora`), already committed at
`tools/ora/producer_harness/gimp3/PROVENANCE-gimp3-svg-plus-spike-2026-08-12.md`,
using the discriminating fixture: destination (230,60,40) alpha 153/255
at (0,0)-(20,20); source (40,120,230) alpha 128/255 at (12,12)-(32,32),
32×32 canvas.

## Expected result

Per the OpenRaster spec's own `svg:plus` mapping to the Porter-Duff
Lighter operator: at the source-only region, output should equal the
source layer's own straight RGBA unchanged (`(40,120,230,128)` — since
`Fa=Fb=1` when the backdrop alpha is 0). At the overlap region, output
should equal `(158,96,139,255)` (combined alpha correctly clamped to
1.0 before use as the unpremultiply divisor; independently confirmed
via GEGL's own `operations/generated/plus.c` and via direct hand
verification against Porter & Duff (1984)).

## Actual result

| Point | GIMP 3.0.4 | Expected | Match |
|---|---|---|---|
| source-only (25,25) | `(0,0,0,0)` | `(40,120,230,128)` | **MISMATCH** |
| overlap (16,16) | `(231,104,173,153)` | `(158,96,139,255)` | **MISMATCH** |

## Root cause (partially confirmed)

`gimp_operation_layer_mode_blend_addition`'s own RGB-channel guard
(`if (in[alpha] != 0.0f && layer[alpha] != 0.0f)`) skips writing
`comp[c]` for `c < alpha` whenever the backdrop's alpha is zero,
explaining why no color is written at the source-only point. This does
**not** explain the observed `alpha=0` there — the same function's own
`comp[alpha] = layer[alpha]` line is unconditional and would predict
`alpha≈128`, not 0; some other stage in GIMP's own compositing pipeline
produces the final zero, not identified in this investigation. Stated
precisely as a partial root-cause, not overclaimed as fully solved.

## Proposed issue text

> **Title**: "Addition" layer mode / OpenRaster `svg:plus` export-import
> does not conform to the Porter-Duff Lighter formula
>
> Comparing GIMP 3.0.4's own native "Addition" layer-mode export and
> its own OpenRaster import+render of a strict, spec-conformant
> `svg:plus` file against the OpenRaster spec's own Porter-Duff Lighter
> definition shows two concrete mismatches: (1) at a point covered only
> by the source layer, GIMP's own render produces fully transparent
> black instead of the source layer's own unchanged pixel; (2) at the
> overlap region, GIMP's own composited RGB does not match the
> Porter-Duff Lighter formula's expected value (independently confirmed
> against GEGL's own `operations/generated/plus.c` and against Porter &
> Duff (1984) directly). The RGB-channel behavior at point (1) traces to
> `gimp_operation_layer_mode_blend_addition`'s own zero-backdrop-alpha
> guard, but the alpha=0 result there is not yet explained by that
> function alone — some other stage appears to zero it. Minimal
> reproduction fixture and exact pixel deltas attached.
