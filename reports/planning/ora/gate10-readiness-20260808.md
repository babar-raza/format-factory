# ORA (OpenRaster) Gate 10 (OSS Readiness Complete) Readiness Assessment

**Date:** 2026-08-08
**Prepared by:** claude (autonomous FF6 session, controller event FF6-EVENT-000288)
**Status:** ai_draft — PREPARATION ONLY, NOT AN APPROVAL RECORD

---

## 0. Why this document exists

`plans/strategic/ff6/controller-state.yaml`'s own next-action text for ora
("close the remaining 8 unresolved ora obligations") gave no signal on Gate 10 readiness
specifically, and FF6-EVENT-000284 explicitly flagged ora's own Gate 10 readiness as
unassessed when ipynb/safetensors/nrrd packets were prepared. This document closes that
gap using the same method and citations established there — see
`reports/planning/ipynb/gate10-readiness-20260808.md` §0 for the full citation chain
(`docs/gates.md`, `docs/ai/ai-assisted-acquisition-pipeline.md`, CLAUDE.md).

**This document does not set `gate_10.status`, does not set `visibility: public` anywhere,
and does not write to `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.**

---

## 1. Gate 10 pass criteria (verbatim from `docs/gates.md`) — assessed against ora

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Production-quality Python source exists for the delivery-plan tiers | **MET, with a known scope gap** | `src/python/ora/src/` — 14 source files, ~2,010 LOC. 126/134 obligations `implemented` per `shared/format-contracts/implementation-evidence/ora.yaml` (8 unresolved, reconciler-confirmed this session). |
| 2 | Unit/integration tests exist for implemented features | **MET** | `tests/python/ora/` — 13 test files, 320 tests passing (this session's own regression run). |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — mechanical gap, not a content gap** | Same repo-wide gap documented for every other FF6 format: `tools/validation/generate_manifest.py --release-type oss` requires file-level `visibility: public` YAML frontmatter that no FF6 format's files carry yet. Not ora-specific. |
| 4 | Human review of the release manifest: no `commercial`/`blocked`/unreviewed `generated` artifacts | **BLOCKED ON #3** | Cannot be performed until a manifest listing ora's own artifacts exists. |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only` re-run this session: 0 of 59 total repo-wide violations reference `ora`/`ORA`. No `src/net/ora/` exists — consistent with FF6's pure-Python-FOSS scope. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET (fixed in this document's own session)** | `samples/by-format/ora/_provenance.yaml` did not exist when this assessment began — see the note below. It has been created, backfilling all 3 existing `valid/` samples with `provenance_status: confirmed`, Apache-2.0, tracing each to the commit (`356a0008`) that added them. `samples/by-format/ora/invalid/` has no fixture files at all (a separate, pre-existing content gap, not a provenance-record gap — not addressed here). |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE — requires human review per criterion 4** | Not set by this document. |

**Verdict: 3 of 7 criteria cleanly met (2, 5, 6 — 6 fixed during this assessment). Criterion 1
is met for the implemented majority but carries a real, quantified content gap (8/134
obligations unresolved). Ora's Gate 10 profile now matches xliff/ubl's own shape (3/7 clean,
blocked on the same shared mechanical gap) rather than being uniquely worse — the one
ora-specific gap this document found (missing provenance file) was small and mechanical
enough to close directly rather than merely flag.**

---

## 2. The 8 remaining unresolved obligations (honest accounting)

Per this session's own repeated re-verification (FF6-EVENT-000285, 288) — all confirmed
blocked on real, scoped gaps, not stale reconciliation:

| Obligation area | Nature of the gap |
|---|---|
| `ORA-COMPOSITE-001`, `ORA-RENDER-001`, `ORA-ISOLATION-001`, `ORA-STREAM-001`, `ORA-BASELINEASSET-001` (5 of 8) | All require a rendering/compositing engine — genuinely out of scope for incremental wiring; a large architecture investment. |
| `ORA-MASK-001` | Spec-silent — the OpenRaster spec itself does not define the claimed behavior; correctly left `missing` rather than invented. |
| `ORA-PRESERVE-001` (remaining clause) | Needs a nullable-defaults model-architecture change, already independently assessed as large-scope. |
| `ORA-EDIT-001` (stale-view-invalidation half) | Needs the same rendering/compositing engine as the cluster above, plus a metadata-invalidation concept not yet designed. |

---

## 3. Concrete next steps

1. Same repo-wide frontmatter step as every other format's Gate 10 packet — deferred to
   the same human-reviewed batch.
2. Populate `samples/by-format/ora/invalid/` with real invalid fixtures (currently empty)
   — separate from criterion 6's provenance-record gap (now fixed), this is a genuine
   content gap: no negative/error-path sample exists for ora at all, unlike every other
   FF6 format's `invalid/` directory.
3. The rendering/compositing-engine cluster (5 of ora's 8 obligations) is the single
   largest genuinely-scoped architecture item across all six FF6 formats — larger than
   anything found in nrrd, xliff, or ubl's own remaining gaps.

## 4. Explicit non-claims

- This document does not claim ora is "certified," "production-ready for release," or
  "Gate 10 passed."
- This document does not modify `registry/format-registry.yaml`, any `visibility` field,
  or `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.
- Creating `samples/by-format/ora/_provenance.yaml` (during this same session, once the
  gap was found) documents 3 pre-existing sample files; it does not add new sample
  content, and does not claim the `invalid/` gap noted in §3 is resolved.
