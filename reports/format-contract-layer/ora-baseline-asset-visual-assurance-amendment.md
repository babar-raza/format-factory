# Governance amendment: visual-assurance procedure for `SAL-ORA-OBL-52746ABC41B3E790`

**Status: ACCEPTED_WITH_CHANGES (2026-08-12).** Independent review (a
fresh general-purpose agent, given this document, the full 17-entry
`layered_raster_archive.yaml` release-gates list, and the 3 cited SAL
facts, with no prior conclusion stated) confirmed the core §2 conclusion
("no literal human required") is textually justified and the §2 sibling
survey, while it omitted one entry (STACK), contained no actual
counter-example — the omission was incompleteness, not cherry-picking.
The reviewer required 4 specific repairs, all applied in this revision:
(1) name a concrete pixel-comparison tolerance in step 5 and resolve the
undefined "threshold" reference in step 10; (2) explicitly justify why
comparing against GIMP/Krita's own output — rather than the applications
themselves emitting a verdict — satisfies "checked by independent
consumers"; (3) add the omitted STACK entry to the sibling-gate survey;
(4) cite concrete file/line evidence that `generate_baseline_assets()` is
a genuinely separate code path from the already-verified compositing
pipeline. See §2 and §3 below for the repaired text.

## 1. What this amends

`SAL-ORA-OBL-52746ABC41B3E790` (`ORA-BASELINEASSET-001`)'s own release
gate (`plans/strategic/ff6/obligations/ora.yaml`):

> release_gates: "Generated viewing assets are accepted and visually
> checked by independent consumers."

This document does not reword that text. It answers what satisfies it and
proposes an executable procedure — an additive operationalization, not a
weakening.

## 2. Tracing the clause (B1) — does it require a human?

**Origin.** The phrase is not spec text. Searched all 3 pinned OpenRaster
authority sources this obligation cites (`SRC-ORA-002`, `SRC-ORA-003`,
via `SAL-ORA-00009`, `SAL-ORA-00019`, `SAL-ORA-00020`) — none of the three
underlying SAL facts contain "visually checked," "human," "manual,"
"inspect," or any reviewer concept at all. They are purely structural
facts: baseline-profile support semantics, and thumbnail.png/
mergedimage.png dimension/bit-depth/interlace constraints. The phrase
originates entirely in the policy layer:
`shared/format-contracts/policy/family-packs/layered_raster_archive.yaml`
(`POL-LRA-BASELINE-ASSET-01`'s sibling `release_gates` line), authored in
a single commit, `17aece4e5` ("feat(format-contract): harden OpenRaster
profile surface", Babar Raza, 2026-07-29). The commit message gives no
further elaboration; the file was authored as a batch capability-hardening
pass across 17 release-gate lines for this one family pack, not as a
targeted, individually-justified requirement for this one gate.

**Does it say "human"?** No — nowhere in the chain (SAL facts, policy
pack, obligation register) does the word "human," "manual," or "person"
appear in connection with this clause.

**What does "independent consumers" mean elsewhere in the identical
file?** Checked every one of the 17 `release_gates` entries in
`layered_raster_archive.yaml` (full list, corrected to include every
entry using "independent," not a partial selection): "Tree order and
nesting survive semantic round trips and **independent rendering**"
(STACK, `POL-LRA-STACK-01`); "Group edits remain accepted and **visually
equivalent in independent applications**" (GROUP); "**Isolation semantics
agree with independent application renders** for every applicable
profile" (ISOLATION); "**Rendering is reproducible and agrees with at
least two independent producers/consumers** within declared tolerances"
(RENDER); "Writer output passes strict self-validation and **independent
application interoperability**" (WRITE). Every one of these five uses
"independent" to mean independent **applications**, and RENDER's own
phrase — "independent producers/**consumers**" — is the single closest
textual parallel to BASELINEASSET's own "independent **consumers**" of
any gate in the file, a stronger match than the ones cited above it.
Zero of the 17 use "human," "manual," or "reviewer." This obligation's
own gate is the only one using the word "visually" as a modifier rather
than "equivalent" or "agrees" — a real, deliberate wording difference,
not a synonym, but one most consistent with distinguishing *what kind*
of check (pixel/visual content, not merely structural/binary validity),
not *who* performs it.

**Does an application need to itself emit a verdict to "check" something?**
No — and requiring that would be inconsistent with how every sibling gate
in this exact file has already been operationalized this session. Neither
GIMP's Script-Fu API nor Krita's Python scripting API has ever been asked
to emit a semantic pass/fail judgment anywhere in this project; that
capability does not exist in either tool. `ORA-RENDER-001`,
`ORA-ISOLATION-001`, and this session's own `ORA-COMPOSITE-001` narrowing
all satisfied their own "agrees with independent application renders" /
"independent producers/consumers" language the same way: format-factory's
own comparison tooling (`tools/ora/producer_harness/compare.py`) diffs
format-factory's output against what GIMP/Krita themselves produced, and
agreement in that diff is what "independent application agreement" has
meant in practice throughout. "Checked by independent consumers" is read
the identical way here: the independent consumer's own decoder/renderer
supplies the reference the asset is checked *against*; the comparison
mechanism itself (format-factory's diff tool, then a vision-capable
agent) performs the checking, using that independent reference as ground
truth. Reading BASELINEASSET-001 to require the application itself to
emit a verdict — a capability no application integrated into this
project has ever had — would make this gate uniquely unsatisfiable by any
mechanism this project could ever build, for either format, an outcome
nothing in the text itself demands and no sibling gate has ever been held
to.

**Conclusion.** Literal human inspection is not textually indispensable.
The clause requires evidence stronger than mere structural acceptance
("the file opens, dimensions are correct" — already established this
session for both GIMP and Krita) but nothing in its own authority chain
requires a person to provide that evidence, provided the stronger
evidence is genuinely visual/pixel-level and produced by real,
independent (non-format-factory) applications. This reading is not
chosen because a human step is inconvenient — the alternative reading
("visually" strictly requires literal human eyes) has zero textual
support anywhere upstream, while the "independent = independent
application" reading has 100% consistent support from every sibling gate
in the exact same authoring pass.

**What defect class was this actually meant to catch?** Not what the
already-existing evidence covers: `ORA-RENDER-001`/`ORA-COMPOSITE-001`/
`ORA-ISOLATION-001` already prove the *compositing math* is correct
(`render()`'s own pixel output, independently verified). `generate_
baseline_assets()` (`src/python/ora/src/format_factory/ora/render.py:
1055-1076`) is a **separate code path**, concretely: it calls
`render_document()` (the already-verified compositing entry point) once,
then feeds that single result through two encoding functions that are
never exercised by the compositing-correctness proofs above —
`encode_png()` (`render.py:348`) directly for the merged image, and
`generate_thumbnail()` (`render.py:404`, itself calling `encode_png()`
again, optionally after `_box_downscale()` at `render.py:377` when the
source exceeds `THUMBNAIL_MAX_EDGE = 256`,
`codec/png_metadata.py:40`) for the thumbnail. Every composite-op/render/
isolation proof this session built stops at `render_document()`'s own
in-memory `DecodedRaster` — none of them ever calls `encode_png()` or
`generate_thumbnail()` at all, confirmed by grepping this session's own
harness code for those two names (absent). A self-consistent round trip
(format-factory encodes via `encode_png()`, format-factory's own
`decode_png()` at `render.py:147` reads it back) cannot catch an encoder
bug both functions share, since they are written by the same author
against the same assumptions and neither has ever been checked against
an external decoder. The real, disclosed gap this clause protects
against is exactly that: **PNG-encoding fidelity as seen by a real,
independently-implemented decoder** — wrong bit-depth handling, an
accidentally-set interlace flag, a channel-order or color-type mismatch —
none of which a same-codebase round trip can surface, and none of which
the render-correctness proofs above touch at all, since they test *what*
gets rendered, not *how the encoded bytes* are later reconstructed by
someone else's decoder.

## 3. Proposed procedure (B2)

This follows the directive's own named template precisely — a fresh
pixel-comparison-only design was considered and rejected as **narrower**
than what was actually asked for; the visual-review layer below is
included even though §2 concludes it is not textually mandatory, because
it catches a genuinely different defect class (see §3 step 8) that pure
pixel-decode-fidelity checking cannot: a correctly-*encoded* but
semantically *wrong* image (right bytes, wrong content) would pass a
naive pixel round trip if the wrong content was what format-factory
itself intended to encode in the first place.

1. **Strict decoding.** The generated asset (thumbnail.png,
   mergedimage.png) passes format-factory's own `ReadMode.STRICT`
   decode with zero recovery actions.
2. **Dimensions/color mode.** thumbnail.png: non-interlaced, 8 bits/
   channel, ≤256×256 (`SAL-ORA-00019`). mergedimage.png: 8 or 16 bits/
   channel (`SAL-ORA-00020`).
3. **Nonempty/nondegenerate.** Not fully transparent, not a single flat
   color, when the source scene is not itself flat — computed directly
   from the known source scene, not assumed.
4. **Alpha occupancy / bounding box.** The generated asset's own
   non-transparent bounding box matches the source scene's own known
   layer geometry.
5. **Pixel comparison against two independent producer references,
   tolerance = 0 (exact match).** Generate the baseline asset from a
   scene **already independently verified** by this session's own
   Workstream A oracle/GIMP/Krita pipeline (e.g. `multiply-blend`, or one
   of the 8 canonical scenes) — so the question "is this the right image"
   is already answered by existing evidence, and this step isolates the
   encoding question specifically. Compare format-factory's own generated
   PNG bytes, pixel-for-pixel, against what GIMP and Krita themselves
   produce when asked to render the identical known-correct scene.
   Exact match is achievable and meaningful, not merely aspirational,
   because every scene used is smaller than `THUMBNAIL_MAX_EDGE = 256`
   (`codec/png_metadata.py:40`) in both dimensions — `generate_thumbnail()`
   (`render.py:404`) encodes such a raster unchanged, with no resampling
   step, so thumbnail.png and mergedimage.png are pixel-identical to each
   other and to `render_document()`'s own already-verified output for
   every scene this procedure uses. **Scoping note:** a scene requiring
   real thumbnail downscaling (>256px) is out of this amendment's own
   scope — comparing a box-downsampled image against GIMP/Krita's own,
   differently-implemented resize algorithms would require a genuine
   resampling-tolerance policy this document does not attempt to set, and
   no obligation currently requires exercising that path.
6. **Diff heatmaps.** Per-pixel absolute difference, amplified for
   visibility, for every comparison in step 5.
7. **Deterministic contact sheets.** One image per scene: scene ID,
   GIMP reference, Krita reference, format-factory output, amplified
   diff, and key metrics (max/mean channel delta) laid out with
   unambiguous, non-overlapping labels.
8. **Independent visual review by at least two fresh vision-capable
   agents**, given the contact sheets with no prior conclusion stated,
   asked to identify: clipping, missing layers, incorrect offsets,
   opacity errors, halos, color shifts, blend anomalies, empty or
   duplicated output, or misleading contact-sheet presentation itself.
   This step exists specifically to catch defect classes outside
   pixel-exact comparison's own reach — e.g. a correct-looking diff
   that is nonetheless visually wrong in a way the chosen metric does
   not weight (a thumbnail correctly encoding the wrong crop region,
   for instance, would still be internally pixel-consistent).
9. **Structured verdicts.** PASS / FAIL / INCONCLUSIVE per reviewer per
   scene, recorded verbatim, not summarized into a single number.
10. **Human escalation — narrow, not default.** Only when: the two
    vision reviewers disagree; step 5's exact-match comparison fails for
    any scene in scope (there is no tolerance to "exceed" — mismatch
    itself is the trigger, per step 5's tolerance=0 definition); a
    reviewer marks INCONCLUSIVE; or a scene requiring real downscaling is
    ever brought in scope without a resampling-tolerance policy first
    being authored. Absent any of these, the amended procedure is
    self-sufficient and this obligation may reconcile on its own
    evidence.

## 4. What this amendment does NOT do

- Does not reword `POL-LRA-BASELINE-ASSET-01` or its own `release_gates`
  text. The literal clause is unchanged; this is an interpretive,
  additive operationalization.
- Does not retroactively mark `ORA-BASELINEASSET-001` implemented. The
  procedure above must still be executed (Workstream B3) before any
  status transition.
- Does not weaken the "independent consumers" plural requirement — both
  GIMP and Krita are used wherever both can perform the check.
- Does not remove or replace the existing decode-acceptance evidence
  (GIMP/Krita successfully opening a format-factory PNG) — it is real,
  valid evidence, just not sufficient alone, and stays cited.
- Does not touch `promotion.*`, any other obligation, or any other
  format. `layered_raster_archive` is used by `ora` alone
  (`shared/format-contracts/policy/format-family-map.yaml`), so this
  amendment's practical blast radius is this one format today, even
  though the source file is shared machinery in principle.
- Does not eliminate human escalation entirely — §3 step 10 preserves a
  narrow, named path to it, matching the directive's own instruction not
  to fabricate completion if genuine ambiguity survives automated and
  agent-based review.

## 5. Independent review

Submitted for independent review with exactly these inputs, no prior
reviewer conclusion stated: this document (pre-repair draft),
`POL-LRA-BASELINE-ASSET-01`'s own text, the full `layered_raster_archive.
yaml` release-gates list (17 entries), and `SAL-ORA-00009`/
`SAL-ORA-00019`/`SAL-ORA-00020`'s own text. Reviewer instructed to check
specifically: (1) is the "no human required" conclusion in §2 textually
justified by the cited evidence, not merely asserted; (2) does the
proposed procedure in §3 preserve the gate's real intent (catching a
technically-valid-but-visually-wrong baseline asset) rather than
substituting a weaker check; (3) is the "independent consumers =
independent applications" reading circular or genuinely supported by the
sibling-gate survey.

**Verdict: ACCEPTED_WITH_CHANGES.** The reviewer independently
re-tallied the 17 release-gates entries and confirmed no counter-example
to the "independent = independent application" reading exists anywhere
in the file (the amendment's own survey had merely omitted STACK, not
cherry-picked around a contradiction) and confirmed none of the three
SAL facts, the policy text, or the obligation register mention a human
reviewer. It required 4 repairs — a named tolerance for step 5 (and the
resulting fix to step 10's dangling threshold reference), an explicit
justification for why comparison-against-independent-output satisfies
"checked BY independent consumers" without requiring the application
itself to emit a verdict, the completed STACK entry, and concrete file/
line evidence that `generate_baseline_assets()` is a genuinely separate,
previously-unexercised code path. All 4 are applied above (§2, §3); this
is the repaired, accepted text, not the version the reviewer evaluated.
