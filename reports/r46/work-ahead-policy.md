# R46 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21

---

## Policy

Work-ahead is permitted only within confirmed independent lanes. A lane may not begin
if it depends on unverified output from another lane. The following rules apply:

1. **MT1 Lane 1B (validator fix) MUST complete before MT10 (bundle build)**
   The bundle build sequence created R45's PENDING defect; the fix must be in place.

2. **MT2 (artifacts) MUST complete before MT10 (bundle)**
   Artifact policy is a precondition for an artifact-contained bundle.

3. **MT3 (consumer replayability) MUST complete before final verdict**
   Consumer proof replayability is the core R46 claim.

4. **MT5 (Phase Audit 1) is independent** — can proceed in parallel with any MT.

5. **MT6 (capability deepening) is independent** — can proceed in parallel with any MT.

---

## Anti-Shrink Rule

If any lane is blocked, other lanes continue. No sprint halt unless ALL independent
lanes are blocked simultaneously.

---

## Deferred Work

The following items are explicitly deferred to R47:

- ZST RC designation
- Gate 8 human approval (ODS/ODT/QOI/XCF/DIF/PPM) — human gate, not in scope
- PGM/PBM/SYLK Gate 10
- AI acceleration (MT8) — non-authoritative, deferred to R47

---

## Final Verdict Requirements

R46 may claim `R46_TWO_PRODUCT_ARTIFACT_CONTAINED_RC_BASELINE` if and only if:
1. All 8 R46 blockers are closed
2. Actual `.whl`/`.nupkg` artifacts are present in bundle-metadata/
3. Consumer proof is replayable from bundled artifacts (not from .local/)
4. Validator catches PENDING in repo/reports/*/final-verdict.md
5. AUTHORITATIVE_TEST_RESULT ≥ 2139 (no regression from R45)
6. BUNDLE_VALIDATION: PASS with --check-no-pending
