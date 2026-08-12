# Bounded fallback candidates — source-level capability evaluation (2026-08-12)

**Status: ACCEPTED_WITH_CHANGES (2026-08-12).** Independent adversarial
review (fresh agent, no prior conclusion stated, independently re-fetched
Drawpile's own live wiki page and confirmed it matches verbatim) found
the Drawpile rejection's own "source-confirmed" label had been applied
uniformly to two claims of very different strength: the 9-operation
overlap (genuinely source-confirmed) and the `svg:plus`-specific
question (genuinely presumptive, resting only on the wiki's own silence,
not a positive statement). Repaired below by splitting the claim
explicitly rather than leaving one label covering both.

Per this session's own directive (§8): evaluated only after the priority-1
(GIMP 3.x) and priority-2 (jsora) candidates were exhausted, both with
real, disclosed negative results (see `PROVENANCE-gimp3-svg-plus-spike-
2026-08-12.md` and `jsora/PROVENANCE-jsora-feasibility-spike-2026-08-12.md`).
Source-level checks only, per the directive's own explicit instruction
("perform a source-level capability check before container work"). No
container was built for any candidate below; each rejection is grounded
in a cited source, not assumed.

## MyPaint — REJECTED (already established this session, not re-investigated)

Already investigated in an earlier segment of this same session
(see `shared/format-contracts/implementation-evidence/ora.yaml`'s own
`SAL-ORA-OBL-A979A77370914BCA` history): "a GTK/GObject-Introspection
interactive painting application with no documented batch/procedural API
comparable to GIMP's own Script-Fu/PDB." Not re-searched, per this
session's own directive ("do not search repeatedly for existing ORA
corpora" and general instruction against redundant research already
settled this session).

## Scribus — REJECTED (wrong tool class, presumptive)

Scribus 1.6 (stable 1.6.6, 2026-04-13) added OpenRaster import support.
However, Scribus is a **desktop-publishing (DTP)** application, not a
raster/layer editor — its own purpose is page layout, not pixel editing.
No source evidence was found that Scribus re-composites individual ORA
layers with their own `composite-op` semantics on import; DTP
applications of this class conventionally import a single flattened
preview asset (`mergedimage.png`) for page placement, not the editable
layer stack. Not confirmed via source reading (a full source audit of
Scribus's own OpenRaster import code was not performed, given the
disproportionate cost relative to the low prior probability implied by
the tool's own stated purpose) — disclosed as a presumptive rejection
based on tool-class reasoning, not a confirmed source-level finding, in
case a future session finds reason to check more rigorously.

## Drawpile — REJECTED (source-confirmed for 9 of 10 single-producer ops;
presumptive for the 1 actually-uncovered operation)

Real, mature OpenRaster support (since v0.7, ~2013), with genuine
per-layer editing capability (unlike Scribus) and recent (2023, 2025)
ORA-specific development activity. Drawpile's own project wiki
(`github.com/drawpile/Drawpile/wiki/OpenRaster`, independently re-fetched
and confirmed to match verbatim during review) explicitly lists 11
composite-ops as **unimplemented / TODO for its own 2.x line**:
`svg:overlay`, `svg:hard-light`, `svg:soft-light`, `svg:difference`,
`svg:color`, `svg:luminosity`, `svg:hue`, `svg:saturation`, `svg:dst-in`,
`svg:dst-out`, `svg:dst-atop`. This part of the rejection **is**
source-confirmed, not presumptive: for these 9 operations (all except
`svg:plus` and `svg:src-atop`, which already has real Krita-only
coverage so contributes nothing new even if Drawpile supported it),
Drawpile's own documentation directly states it cannot help, with no
ambiguity.

For `svg:plus` specifically — the one operation this cycle actually
needs and where Drawpile could theoretically still contribute — the
wiki's silence (not listed as unimplemented) is **not** positive
evidence of support; the page states only what is missing, not an
exhaustive supported list. This part of the rejection carries the same
epistemic weight as Scribus's and Pinta's own rejections below
(presumptive, based on absence of a confirmed automation surface, not a
direct source-level finding) — flagged explicitly here after an
independent review noted the original version of this section
overstated its own confidence by applying one "source-confirmed" label
to both the 9-operation finding (genuinely strong) and the `svg:plus`
question (genuinely weak) without distinguishing them. No CLI/batch/
headless automation surface was found in available documentation for
either case (would require Xvfb + GUI automation, a materially higher
engineering cost than the Docker/Script-Fu or Docker/PyKrita lanes
already built).

## Pinta — REJECTED (no automation surface found; coverage unconfirmed)

Real `.ora` read/write support confirmed (File > Save As → OpenRaster).
However: (1) no command-line, batch, or headless automation mode was
found in Pinta's own documentation or man page — Pinta is explicitly a
simplified, GUI-only alternative to GIMP, and would require the same
Xvfb + GUI/accessibility-automation lane as Drawpile, at similar
engineering cost; (2) no positive evidence was found that Pinta's own
blend-mode implementation covers the Porter-Duff operators
(`svg:plus`/`svg:dst-in`/`svg:dst-out`/`svg:src-atop`/`svg:dst-atop`) at
all — one source notes Pinta writes non-standard `pinta-*`-prefixed
composite-op values for some of its own custom modes, a real, disclosed
sign of incomplete/non-standard OpenRaster compositing-vocabulary
coverage, though not a direct statement about the specific 5 Porter-Duff
operators this project still needs. Given the combination of unconfirmed
capability and confirmed absence of any non-GUI automation path, not
pursued further without stronger positive evidence justifying the cost.

## Disposition

None of the 4 named bounded-fallback candidates present a credible,
cost-proportionate path to closing `ORA-COMPOSITE-001`'s own remaining
gap this cycle. This is **not** a claim that the gap is irreducible —
per this session's own directive, that conclusion requires evaluating
"every viable primary-source candidate," which has not been done (only
6 candidates total across this and prior sessions: GIMP 2.10, Krita,
GIMP 3.x, jsora, plus source-level checks on MyPaint/Scribus/Drawpile/
Pinta). A fifth, not-yet-identified open-source OpenRaster implementation
may exist and was not searched for exhaustively this cycle (the
directive's own §8 names this as an explicit, unexplored fifth option).
