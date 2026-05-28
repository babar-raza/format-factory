# R71 Defect Ledger

**Sprint:** FORMAT-FACTORY-R72-DELIVERED-PACKAGE-TEST-FAILURE-REPAIR-LOCAL-RC-SEAL-001
**Date:** 2026-05-28

| ID | File | Issue | Severity | R72 Status |
|---|---|---|---|---|
| IV-R72-001 | `.local/r71-delivery-package.zip` (not uploaded) | Delivered artifact was inner ZIP only; delivery package not present in delivered set | RC-blocking | FIXED_IN_R72 (Train B) |
| IV-R72-002 | inner ZIP: `bundle-metadata/delivery-package-validation-summary.txt` | Contains PENDING_PASS_2_SHA, PENDING_SIDECAR_SHA, PENDING_BUILD | RC-blocking | FIXED_IN_R72 (Train G) |
| IV-R72-003 | inner ZIP: `bundle-metadata/external-sidecar-proof-summary.txt` | Contains "to be generated after Pass 2 build" and "to be filled" | RC-blocking | FIXED_IN_R72 (Train G) |
| IV-R72-004 | inner ZIP: `bundle-metadata/python-tests-summary.txt` | Contains `POST_BUNDLE_AUTHORITATIVE: PENDING` | RC-blocking | FIXED_IN_R72 (Train G) |
| IV-R72-005 | `tests/evidence/test_r71_final_delivery_mode_*.py` | 41 required skips in extracted bundle replay | RC-blocking | FIXED_IN_R72 (Train D) |
| IV-R72-006 | `reports/r71/final-verdict.md` | "10 failed (all pre-existing)" without failing-test ledger | RC-blocking | FIXED_IN_R72 (Train C) |
| IV-R72-007 | R71 failing tests | 10 failures uninvestigated, unclassified, untaskcarded | RC-blocking | FIXED_IN_R72 (Train C) |
| IV-R72-008 | `tools/evidence/validate_evidence_bundle.py` | `check_inner_verdict_delivery_sha_authority()` scoping bug: `current_run=None` causes all verdicts checked, breaks `test_auto_proof_bundle.py` | RC-blocking | FIXED_IN_R72 (Train C/F) |

DEFECT_LEDGER: 8 defects (8 RC-blocking)
