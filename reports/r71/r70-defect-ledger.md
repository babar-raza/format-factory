# R70 Defect Ledger

**Sprint:** FORMAT-FACTORY-R71-PROOF-MODEL-RESET-LOCAL-RC-SEAL-AND-WORKAHEAD-001
**Date:** 2026-05-27

| ID | File | Issue | Severity |
|---|---|---|---|
| IV-R71-001 | inner ZIP: `repo/reports/r70/final-verdict.md` | `BUNDLE_VALIDATION_PASS_2_SHA: af7c9b76...` (stale — pre-sidecar-correction build) | RC-blocking |
| IV-R71-002 | inner ZIP: `repo/reports/r70/final-verdict.md` | `DELIVERY_PACKAGE_SHA: PENDING` (outer package SHA cannot be inside inner ZIP) | RC-blocking |
| IV-R71-003 | `tests/evidence/test_r70_final_delivery_mode_*.py` | All skip in extracted bundle context (depend on .local/) | RC-blocking |
| IV-R71-004 | `bundle-metadata/package-artifact-manifest.yaml` etc. | `final_git_head` is ambiguous across manifests | hygiene |
| IV-R71-005 | `tools/evidence/validate_evidence_bundle.py` | Validator does not enforce layered proof model | hygiene |

DEFECT_LEDGER: 5 defects (3 RC-blocking, 2 hygiene)
R70_CLASSIFIED: R70_DELIVERY_PACKAGE_VALID_BUT_PROOF_MODEL_WRONG
