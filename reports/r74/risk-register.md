# R74 Risk Register

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RISK-R74-001 | Build-order circular SHA issue repeats | HIGH | RC-blocking | Three-pass protocol; verify bundled final-verdict content after each build |
| RISK-R74-002 | Validator hardening introduces false positives on historical files | MEDIUM | Test failures | Scope new patterns to current-run metadata only |
| RISK-R74-003 | ZST fix breaks other example tests | LOW | Test failures | Run full example test suite after fix |
| RISK-R74-004 | Package rebuild SHA changes invalidate manifest | MEDIUM | Delivery blocked | Rebuild packages before updating manifest |
| RISK-R74-005 | .NET SDK unavailable | LOW | Train G partial | Document blocker precisely; skip consumer smoke |
| RISK-R74-006 | State snapshot tool generates stale data | LOW | INV-011 persists | Run snapshot after all R74 changes committed |

RISK_REGISTER: COMPLETE
