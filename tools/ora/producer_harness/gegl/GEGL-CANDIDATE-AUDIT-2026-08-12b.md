# GEGL Candidate Audit — ORA-COMPOSITE-001 (2026-08-12, fourth continuation)

## Scope and purpose

This audit evaluates GEGL (GNOME/gegl), GIMP's own underlying,
separately-versioned, spec-derived C compositing library, as a candidate
evidence source for ORA-COMPOSITE-001's own remaining producer-evidence
gap (svg:plus with zero conforming producers; 10 other Porter-Duff/blend
operations with only one qualifying producer). Directive Section 8
("Bounded candidate discovery") and Section 9 ("Distinguish three
different questions") govern this work.

**Classification decided up front, before any container work (per the
directive's own explicit permission in Section 9): GEGL is NOT an
OpenRaster producer.** It has zero ORA-container, stack.xml, or
`.ora`-file awareness whatsoever — it is a pure raster-compositing
library operating on loaded raster buffers via its own `gegl-chain` CLI
DSL, not a format reader/writer. It therefore cannot satisfy this
project's own already-established independent-producer policy
interpretation (a `PRODUCER` must independently read/write/reopen real
`.ora` files through its own public API). Its only possible role is as a
**`REFERENCE_ORACLE_ONLY`** source for the underlying compositing
FORMULA layer specifically — directly relevant to the directive's own
Section 11 Tier-C policy language ("two independent non-format-factory
implementations of the underlying compositing formula agree"), and
useful as a correctness cross-check independent of this project's own
code, but never citable as ecosystem/interoperability evidence.

## Provenance

- Repository: `github.com/GNOME/gegl`, `operations/generated/*.c` —
  code-generated via `svg-12-porter-duff.rb` / `svg-12-blend.rb` directly
  from the W3C SVG 1.2 Compositing spec (and, per each file's own header,
  cross-referencing `https://www.w3.org/TR/compositing-1/`, the current
  W3C Compositing and Blending Level 1 spec).
- Authored by GIMP/GEGL core developer Øyvind Kolås (`pippin@gimp.org`),
  John Marshall, Daniel Sabo.
- Installed via the real, standalone `gegl` Debian/Ubuntu package (NOT
  reimplemented, ported, or approximated by this project):
  `gegl 1:0.4.48-2.4build2`, `amd64`, inside `ubuntu:24.04`.
- Container image: `ora-harness-gegl:pinned-2026-08-12b`,
  digest `sha256:c702bb576395cded7bd0cc50e143a4eb6ef1de78903e1fa622e3f360e6f31bf3`.
  `Dockerfile` in this directory.
- Invocation: real `gegl` CLI (`gegl-chain` DSL), e.g.
  `gegl <dest.png> -o <result.png> -- <op> srgb=true aux=[load path=<src.png>]`
  — `aux` = the upper/source layer, main positional input = the
  lower/backdrop layer (confirmed from each generated file's own header
  comment: `aA = aux(src) alpha, aB = in(dst) alpha`). `srgb=true` selects
  GEGL's own `GEGL_BABL_VARIANT_PERCEPTUAL_PREMULTIPLIED` working format
  (sRGB-gamma-encoded, matching this project's own straight-gamma-space
  8-bit pixel semantics) instead of its default linear-light mode.

## Result 1 — Porter-Duff family: GEGL agrees exactly, 3-way match

Ran all 5 non-default registered Porter-Duff operators GEGL implements
(`svg:plus`, `svg:dst-in`, `svg:dst-out`, `svg:src-atop`, `svg:dst-atop`)
against the already-established `composite_matrix.py::PORTER_DUFF_SCENES`
discriminating fixture (destination (230,60,40) alpha 153/255 at
(0,0)-(20,20); source (40,120,230) alpha 128/255 at (12,12)-(32,32),
32x32 canvas), full-canvas-padded via `build_gegl_fixtures.py`, and
compared the overlap-point pixel (16,16) against both format-factory's
own real `render()` output (via `generate_baseline_assets`) and
`composite_oracle.py`'s own independently-computed value:

| operator | format-factory | oracle | GEGL | verdict |
|---|---|---|---|---|
| svg:plus | (158,96,139,255) | (158,96,139,255) | (158,96,139,255) | **ALL MATCH** |
| svg:dst-in | (230,60,40,77) | (230,60,40,77) | (230,60,40,77) | **ALL MATCH** |
| svg:dst-out | (230,60,40,76) | (230,60,40,76) | (230,60,40,76) | **ALL MATCH** |
| svg:src-atop | (135,90,135,153) | (135,90,135,153) | (135,90,135,153) | **ALL MATCH** |
| svg:dst-atop | (154,84,116,128) | (154,84,116,128) | (154,84,116,128) | **ALL MATCH** |

This 3-way agreement is significant for two independent reasons:

1. It is the finding that led directly to discovering and fixing the real
   Lighter/svg:plus alpha-clamping defect in both `composite_oracle.py`
   and `render.py` (GEGL's `plus.c` disagreed with the pre-fix value;
   hand-verification against Porter & Duff (1984) confirmed GEGL was
   right — see `render.py`'s own inline comment and
   `tests/tools/test_ora_composite_oracle.py`).
2. It is an independent, third-party re-confirmation of the
   Destination-In/Destination-Atop out-of-bounds fix made in the
   immediately-prior continuation (commit `976396ede`) — GEGL was never
   consulted for that fix, so its exact agreement here is fresh corroborating
   evidence, not circular.

**Evidence classification: `REFERENCE_ORACLE_ONLY`, Porter-Duff family.**
Usable as one of the two required independent formula implementations in
a future Tier-C policy determination for svg:plus, svg:dst-in,
svg:dst-out, svg:src-atop, svg:dst-atop specifically.

## Result 2 — Overlay/Soft-Light family: GEGL itself is defective, NOT a valid reference for these two operations

Running `svg:overlay` and `gegl:soft-light` (GEGL registers soft-light
under the `gegl:` namespace rather than `svg:`, despite being generated by
the identical `svg-12-blend.rb` script from the identical spec — this
inconsistency is itself worth disclosing but is not the substantive
finding) against `composite_matrix.py`'s own blend-family discriminating
fixture (backdrop=(30,200,60) opaque, source=(220,40,180) alpha=166/255,
8x8 canvas) produced a real mismatch:

| operator | format-factory | oracle | GEGL | verdict |
|---|---|---|---|---|
| svg:overlay | (44,175,76,255) | (44,175,76,255) | (136,111,112,255) | MISMATCH |
| svg:soft-light | (56,181,77,255) | (56,181,77,255) | (4,219,77,255) | MISMATCH |

**This mismatch was root-caused, not merely reported.** The W3C
Compositing and Blending Level 1 spec's own normative combined
premultiplied blend+composite formula (fetched directly from
`https://www.w3.org/TR/compositing-1/#blending`, section 10, not relied
on from memory) is:

```
αo x Co = αs x (1 - αb) x Cs + αs x αb x B(Cb, Cs) + (1 - αs) x αb x Cb
```

Hand-deriving this project's own straight-space computation for the
`svg:overlay` scene above (backdrop opaque, so this simplifies to
`Co = αs x B(Cb,Cs) + (1-αs) x Cb`) reproduces format-factory's and the
oracle's own value (44,175,76,255) exactly, channel by channel.

Hand-expanding GEGL's own `operations/generated/overlay.c` (and the
structurally-identical `hard-light.c`) ELSE-branch formula —
`aA*aB - 2*(aB-cB)*(aA-cA) + cA*(1-aB) + cB*(1-aA)` — algebraically, and
confirming numerically with two independent fully-opaque sanity checks
that do not depend on the original fixture's specific numbers:

- `Cb=0.3, Cs=0.3` (both fully opaque): correct `Multiply(Cs,2Cb) = 0.18`;
  GEGL's own formula evaluates to `0.02`.
- `Cb=0.2, Cs=0.9` (both fully opaque, asymmetric to rule out a
  channel-swap artifact): correct `Multiply(Cs,2Cb) = 0.36`; GEGL's own
  formula evaluates to `0.84`.

Both are decisive, simple, independently-reproducible mismatches against
the unambiguous, universally-known `Multiply`/`Screen` sub-formulas —
not a subtle rounding or gamma-space difference. The IF-branch (Cb>0.5)
was checked the same way against the real fixture's own G channel
(expected 175, GEGL's own formula hand-evaluates to 111, matching its
actual observed CLI output exactly) and is equally wrong. `soft-light.c`
was spot-checked the same way (`Cb=0.1, Cs=0.2`, both opaque: correct
`0.046`, GEGL's own formula evaluates to `0.154`) and shows the same
defect class.

**Conclusion: this is a genuine, real upstream defect in GEGL's own
code-generated piecewise separable-blend operations** (at minimum
`overlay.c`, `hard-light.c`, `soft-light.c` — all sharing the same
`svg-12-blend.rb` generator and the same premultiplied-reformulation
algebra pattern), not a defect in format-factory. Format-factory's own
Overlay/Soft-Light output is independently confirmed correct against the
W3C spec's own normative formula text, fetched fresh from `w3.org` for
this audit, not carried forward from a prior session's assumption.

This is disclosed here for completeness (EP-2 finding-to-execution
lifecycle) but is explicitly OUT OF SCOPE for this obligation's own
work — `svg:overlay` and `svg:soft-light` are not among
ORA-COMPOSITE-001's 11 deficient operations (they already have one
qualifying producer from the existing GIMP/Krita evidence); no
format-factory source change is required or was made as a result of this
finding. A local (not submitted) GEGL upstream issue package is prepared
separately per Section 10's own spirit, extending its explicitly-named
list.

**Evidence classification: GEGL's Overlay/Soft-Light/Hard-Light family
is EXCLUDED from `REFERENCE_ORACLE_ONLY` status.** It must not be cited
as corroborating evidence for these three operations in any future
Tier-C determination — doing so would launder a defective upstream
result into this project's own evidence chain.

## Candidate ledger entry

| field | value |
|---|---|
| name | GEGL (GNOME/gegl) |
| repo | github.com/GNOME/gegl |
| version tested | 1:0.4.48-2.4build2 (Ubuntu 24.04 apt) |
| license | LGPL-3.0-or-later |
| maintenance | active (GNOME project, current release cadence) |
| language/runtime | C, native compiled library + CLI |
| ORA container read/write | NONE — pure raster compositor, no format awareness |
| operation mapping | Porter-Duff: svg:plus, svg:dst-in, svg:dst-out, svg:src-atop, svg:dst-atop all present and CORRECT. Separable blend: svg:overlay, gegl:soft-light (and svg:hard-light) present but DEFECTIVE. 4 nonseparable blends (svg:hue/saturation/color/luminosity) NOT implemented at all (confirmed via GitHub code search, zero results). |
| lineage | independent of format-factory, jsora, ora.js, GIMP's own layer-mode UI code, and Krita — GEGL is GIMP's own dependency, but this project never vendors or shares code with it |
| qualifying evidence type | REFERENCE_ORACLE_ONLY (Porter-Duff family only) |
| viability verdict | REJECTED as a producer (no container support, by design, decided before container work per directive Section 9); ACCEPTED as a reference oracle for 5 of 7 tested operations; the other 2 (overlay, soft-light) yielded a genuine, disclosed GEGL-side defect finding instead of usable reference evidence |
