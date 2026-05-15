# R13 — R12 Baseline Verification
Sprint: FORMAT-FACTORY-R13-ZST-SUPPORT-MATRIX-AUDIT-SIMULATION-AND-GATE1-PACKET-SWARM-001
Lane: B (R12 Baseline Verification)
Date: 2026-05-15

## Purpose
Verify R12 claims as an accepted baseline before extending with R13 work.
This is a verification gate only — R12 is not being reworked.

## R12 Artifact Existence Checks

| Artifact | Exists | Path |
|----------|--------|------|
| R12 commit d655ab9 | YES | git log confirms |
| R12 evidence bundle | YES | .local/r12-bundle.zip |
| R12 contract | YES | tools/evidence/contracts/r12-acquisition-engine-iv-swarm.yaml |
| acquisition_graph_simulator.py | YES | tools/skills/acquisition_graph_simulator.py |
| test_acquisition_graph_simulator.py | YES | tests/skills/test_acquisition_graph_simulator.py |
| test_public_spec_governance.py | YES | tests/skills/test_public_spec_governance.py |
| R12 IV report | YES | reports/verification/r12-acquisition-runtime-independent-verification-20260514.md |
| ZST governed audit | YES | reports/planning/zst-governed-candidate-audit-20260514.md |
| Cross-category ranking | YES | reports/planning/cross-category-ranking-validation-20260514.md |

## Schema Field Verification (R12 Lane D extensions)

Confirmed in `schemas/skills/format-onboarding.schema.yaml`:
- [x] acquisition_risk_classification (lines 178-186)
- [x] spec_normalization_status (lines 188-196)
- [x] oracle_classification (lines 198-206)
- [x] sample_provenance_notes (lines 208-212)
- [x] public_spec_quality (lines 214-226)

All 5 R12 governance fields: CONFIRMED PRESENT.

## Validation Commands

### [1] check_current_state_consistency.py
**Result: CURRENT_STATE_CONSISTENCY: PASS**

### [2] check_methodology_links.py
**Result: METHODOLOGY_LINK_CHECK: PASS (54 checks)**

### [3] pytest test_acquisition_graph_simulator + test_public_spec_governance
**Result: 86 passed in 0.44s**

## R12 Governance Invariants Check

| Invariant | Verified |
|-----------|---------|
| acquisition_not_authorized=true | YES — contract confirms; no ZST acquisition performed |
| ZST Gate 1 NOT approved | YES — registry has no ZST entry |
| src/net NOT changed by R12 | YES — git diff d655ab9 confirms no src/net changes |
| src/python NOT changed by R12 | YES — git diff d655ab9 confirms no src/python changes |
| Gate 11 NOT approved by R12 | YES — R12 reports + contract confirm |
| commercial_product_ready=false | YES — contract sprint_verdicts confirms |
| aspose_supported=None | YES — ZST audit says None throughout |

## R12 Cross-Category Ranking (confirmed from report)

| Rank | Format | Score | Tier |
|------|--------|-------|------|
| 1 | zst | 8.95 | ACQUISITION_READY |
| 2 | ora | 8.85 | ACQUISITION_READY |
| 3 | gnumeric | 8.75 | ACQUISITION_READY |
| 4 | abw | 8.75 | ACQUISITION_READY |
| 5 | qoi | 8.60 | ACQUISITION_READY |
| 6 | egg | 5.55 | CANDIDATE_READY |
| 7 | hwpx | 5.35 | CANDIDATE_READY |
| 8 | xar | 5.15 | CANDIDATE_READY |
| 9 | alz | 3.25 | NEEDS_INVESTIGATION |
| 10 | hwp | 3.05 | NEEDS_INVESTIGATION |

Source: reports/planning/cross-category-ranking-validation-20260514.md

## Baseline Verdict
R12_BASELINE_STATUS: **VERIFIED_BASELINE_FOR_R13**

R13 may proceed. No R12 repair required.
