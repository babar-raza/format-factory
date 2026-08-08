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
| 1 | Production-quality Python source exists for the delivery-plan tiers | **MET, with a known scope gap** | `src/python/xliff/src/format_factory/xliff/` — 25 source files, ~4,049 LOC. 135/142 obligations `implemented` per `shared/format-contracts/implementation-evidence/xliff.yaml` (7 unresolved, reconciler-confirmed as of this session). |
| 2 | Unit/integration tests exist for implemented features | **MET** | `tests/python/xliff/` — 49 test files, 543 tests passing (this session's own regression run). |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — mechanical gap, not a content gap** | Same repo-wide gap documented for ipynb: `tools/validation/generate_manifest.py --release-type oss` requires file-level `visibility: public` YAML frontmatter that no FF6 format's files carry yet. Not xliff-specific. |
| 4 | Human review of the release manifest: no `commercial`/`blocked`/unreviewed `generated` artifacts | **BLOCKED ON #3** | Cannot be performed until a manifest listing xliff's own artifacts exists. |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only` re-run this session: 0 of 59 total repo-wide violations reference `xliff` (all 59 are in unrelated `src/net/fods/*.cs`). No `src/net/xliff/` exists — consistent with FF6's pure-Python-FOSS scope. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET** | `samples/by-format/xliff/_provenance.yaml` — all 4 samples `provenance_status: confirmed`, Apache-2.0 (project-owned synthetic, generated via Python stdlib `xml.etree.ElementTree`, no third-party dependency). |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE — requires human review per criterion 4** | Not set by this document. |

**Verdict: 3 of 7 criteria cleanly met (2, 5, 6). Criterion 1 is met for the implemented
majority but carries a real, quantified content gap (7/142 obligations unresolved) that
ipynb/safetensors did not have at their own Gate 10 assessment time — see §2 for what
those 7 are. Criteria 3–4 share the same mechanical, repo-wide frontmatter gap as every
other FF6 format. Criterion 7 is the human gate itself.**

---

## 2. The 7 remaining unresolved obligations (honest accounting, not deferred to prose elsewhere)

Per FF6-EVENT-000287's own fresh re-read (the most recent full pass over xliff's
obligation set) and re-confirmed unchanged by FF6-EVENT-000288:

| Obligation area | Nature of the gap |
|---|---|
| Tolerant recovery mode | Would require a genuine read-path architecture change (hard-fail → tolerant-plus-diagnostic), not a wiring fix. |
| `trgLang` reverse-direction handling | Confirmed absent from the real OASIS XLIFF 2.1 spec text itself — not an implementation gap but a spec-silence case where the current behavior may already be correct; not re-classified as `implemented` without a spec citation proving the reverse-direction claim exists, so it stays honestly `missing`. |
| Schematron execution (not just bundling) | The Schematron/NVDL *artifacts* are bundled and inventoried (FF6-EVENT-000277), but *executing* ISO Schematron rules requires an XSLT2-capable toolchain. This session confirmed no such toolchain is available in this environment — a real external dependency gap, not a code gap. |
| Whole-tree `xml:space`/`xml:lang` inheritance walker | Needs parent-back-reference tree walking not currently modeled — a real, scoped architecture item. |
| `sizeRestriction` VALUE-format profile resolution | Needs whole-tree profile resolution beyond the current per-element check — a real, scoped architecture item. |

None of these are mechanical reconciliation gaps; each was independently re-verified this
session (FF6-EVENT-000287, FF6-EVENT-000288) as requiring genuine new implementation work,
not stale evidence.

---

## 3. Concrete next steps

1. Same repo-wide frontmatter step as every other format's Gate 10 packet (§3 of the
   ipynb document) — deferred to the same human-reviewed batch, not done unilaterally here.
2. The 5 items in §2 remain open product work, independent of Gate 10 mechanics — closing
   them would raise criterion 1 from "met with a known gap" to "cleanly met," but Gate 10's
   own text does not require 100% obligation closure, only "production-quality source...
   for the delivery-plan tiers." Whether 135/142 clears that bar is a human judgment call,
   not this document's to make.

## 4. Explicit non-claims

- This document does not claim xliff is "certified," "production-ready for release," or
  "Gate 10 passed."
- This document does not modify `registry/format-registry.yaml`, any `visibility` field,
  or `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.
- The 7 unresolved obligations in §2 are not hidden or minimized — they are the single
  biggest open question this document surfaces for human review.
