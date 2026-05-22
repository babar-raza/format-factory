# Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

## R53 Completion Signal

This sprint completes when:
1. All 22+ report files present in reports/r53/
2. FODS formula preservation tests (7) pass
3. Sidecar proof tests (8) pass
4. Full non-AI test suite passes (with 1 known pre-existing failure)
5. BUNDLE_VALIDATION: PASS with --check-no-pending
6. Sidecar proof written and validated
7. Memory entry created
8. Final feat commit made

## R54 Opening Invariants

State snapshot returns R53 verdict.
All R52+R53 evidence tests pass (874+ expected, 1 pre-existing failure).
All 7 formula preservation tests pass.
All 8 sidecar proof tests pass.

## R54 Opening Items

### HIGH PRIORITY

1. FODT heading preservation (TC-0057): implement text:outline-level write-back
2. Installed-wheel smoke from extracted bundle (GAP-003)
3. dotnet test invocation fix (GAP-010)

### MEDIUM PRIORITY

4. FODT list preservation (TC-0058)
5. FODT table preservation (TC-0059)
6. AI acceleration round 3 (live endpoint, FODT structure review)
7. Agent Metrics live post proof (GAP-007)
8. Phase Audit 5 execution (product feature map, unsupported feature disclosure)

### LOW PRIORITY

9. FODT Markdown export (after TC-0057/0058 closed)
10. INV-006/007/008 implementation (proposed invariants from R53)
11. R27/R32 metadata floor warning closure (update old contracts or accept permanently)

## Work-Ahead Rule

Any lane that finishes early in R54 must:
1. Mark own tasks complete
2. Look for next safe adjacent work (e.g., MT6 formula done → attempt TC-0057)
3. Continue to next safe task — do not stop sprint
4. If blocked, record blocker and continue to independent lane

## Evidence Continuity

R53 sidecar proof path: `.local/evidence-bundles/r53-self-verifying-baseline.sha256-proof.json`
R52 sidecar proof path: `.local/evidence-bundles/r52-state-consistent-installed-artifact-baseline.sha256-proof.json`

Future agents may replay either sidecar to verify bundle integrity.
