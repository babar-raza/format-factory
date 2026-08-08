# XLIFF Gate 10 (OSS Readiness Complete) Readiness Assessment

**Date:** 2026-08-08
**Prepared by:** claude (autonomous FF6 session, controller event FF6-EVENT-000288)
**Status:** ai_draft — PREPARATION ONLY, NOT AN APPROVAL RECORD

---

## 0. Why this document exists

FF6-EVENT-000288's own investigation flagged that xliff (like ubl) had never had a Gate 10
readiness packet prepared, unlike ipynb, safetensors, and nrrd (FF6-EVENT-000283/284). This
document closes that gap using the exact same method and citations established there —
see `reports/planning/ipynb/gate10-readiness-20260808.md` §0 for the full citation chain
(`docs/gates.md`, `docs/ai/ai-assisted-acquisition-pipeline.md`, CLAUDE.md). Summarized:
Gate 10 (not Gate 11, which is `.NET`-commercial-only) is the FF6-relevant checkpoint;
an agent may prepare the readiness packet but must never set `gate_10.status: passed`
without recorded human approval.

**This document does not set `gate_10.status`, does not set `visibility: public` anywhere,
and does not write to `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.**

---

## 1. Gate 10 pass criteria (verbatim from `docs/gates.md`) — assessed against xliff

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Production-quality Python source exists for the delivery-plan tiers | **MET, with a known scope gap** | `src/python/xliff/src/format_factory/xliff/` — 25 source files, ~4,049 LOC. 136/142 obligations `implemented` per `shared/format-contracts/implementation-evidence/xliff.yaml` (6 unresolved, reconciler-confirmed fresh at FF6-EVENT-000293 — was 7 at this packet's original writing; FF6-EVENT-000292 closed a missed-duplicate XLIFF-VALIDATE-001 obligation in the meantime). |
| 2 | Unit/integration tests exist for implemented features | **MET** | `tests/python/xliff/` — 49 test files, 543 tests passing (this session's own regression run). |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — mechanical gap, not a content gap** | Same repo-wide gap documented for ipynb: `tools/validation/generate_manifest.py --release-type oss` requires file-level `visibility: public` YAML frontmatter that no FF6 format's files carry yet. Not xliff-specific. |
| 4 | Human review of the release manifest: no `commercial`/`blocked`/unreviewed `generated` artifacts | **BLOCKED ON #3** | Cannot be performed until a manifest listing xliff's own artifacts exists. |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only` re-run this session: 0 of 59 total repo-wide violations reference `xliff` (all 59 are in unrelated `src/net/fods/*.cs`). No `src/net/xliff/` exists — consistent with FF6's pure-Python-FOSS scope. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET** | `samples/by-format/xliff/_provenance.yaml` — all 4 samples `provenance_status: confirmed`, Apache-2.0 (project-owned synthetic, generated via Python stdlib `xml.etree.ElementTree`, no third-party dependency). |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE — requires human review per criterion 4** | Not set by this document. |

**Verdict: 3 of 7 criteria cleanly met (2, 5, 6). Criterion 1 is met for the implemented
majority but carries a real, quantified content gap (6/142 obligations unresolved) that
ipynb/safetensors did not have at their own Gate 10 assessment time — see §2 for what
those 6 are. Criteria 3–4 share the same mechanical, repo-wide frontmatter gap as every
other FF6 format. Criterion 7 is the human gate itself.**

---

## 2. The 6 remaining unresolved obligations (honest accounting, not deferred to prose elsewhere)

**Correction (FF6-EVENT-000294):** re-verified fresh against
`reports/format-contract-layer/xliff-obligation-reconciliation.json` rather than trusting
this packet's own original table. The count dropped from 7 to 6 (FF6-EVENT-000292 closed
a missed-duplicate XLIFF-VALIDATE-001 obligation after this packet was first written), and
the original table's "Schematron execution (not just bundling)" row described that
now-closed obligation's own stale missing_behavior text, not a separate still-open item —
removed rather than carried forward inaccurately.

| Obligation | Capability | Nature of the gap |
|---|---|---|
| `SAL-XLIFF-OBL-0C477B7B6441FE75` | `XLIFF-LIFECYCLE-001` | A genuine tolerant/recovery read mode does not exist: `mode="preservation"` is accepted but has no distinct effect versus strict (no `recovery_actions` field, no actual recovery logic). Would require a genuine read-path architecture change, not a wiring fix. |
| `SAL-XLIFF-OBL-2602F9167F95464B`, `SAL-XLIFF-OBL-C96F6CB613A6F95D` | `XLIFF-TEXT-001`, `XLIFF-PARSE-001` (2 obligations, same underlying gap) | The Schematron F1 pattern only asserts one direction (target elements present ⇒ trgLang required), not the reverse, even though the obligation's own rule_text uses "if and only if" phrasing. Implements exactly what the formal Schematron checks; does not invent the unasserted reverse direction. |
| `SAL-XLIFF-OBL-7764F24576A4DC32` | `XLIFF-QA-001` | Length (`sizeRestriction`) violations are not implemented — needs actual numeric restriction values from the Size and Length Restriction module, which `XLIFF-MODULE-001` deliberately keeps `PRESERVATION_ONLY` (round-trips but does not parse attribute values yet). |
| `SAL-XLIFF-OBL-7DA078717EA60881`, `SAL-XLIFF-OBL-867500AA0AC3D2C1` | `XLIFF-MODEL-001` (2 obligations, same underlying gap) | `xml:space`/`xml:lang` inheritance *rules* are proven as reusable primitives (`effective_xml_space()`, `effective_xml_lang()`), but neither is a whole-tree walker — the model has no parent back-references at all, a real, scoped architecture item. |

None of these are mechanical reconciliation gaps; each was independently re-verified this
session (FF6-EVENT-000287, 288, 292) as requiring genuine new implementation work, not
stale evidence. A fresh word-for-word duplicate-rule_text sweep against every already-
implemented xliff obligation (FF6-EVENT-000292) found no further missed duplicates among
these 6.

---

## 3. Concrete next steps

1. Same repo-wide frontmatter step as every other format's Gate 10 packet (§3 of the
   ipynb document) — deferred to the same human-reviewed batch, not done unilaterally here.
2. The 4 items in §2 (covering 6 obligations) remain open product work, independent of
   Gate 10 mechanics — closing them would raise criterion 1 from "met with a known gap" to
   "cleanly met," but Gate 10's own text does not require 100% obligation closure, only
   "production-quality source... for the delivery-plan tiers." Whether 136/142 clears that
   bar is a human judgment call, not this document's to make.

## 4. Explicit non-claims

- This document does not claim xliff is "certified," "production-ready for release," or
  "Gate 10 passed."
- This document does not modify `registry/format-registry.yaml`, any `visibility` field,
  or `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.
- The 6 unresolved obligations in §2 are not hidden or minimized — they are the single
  biggest open question this document surfaces for human review.
