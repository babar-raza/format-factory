# R72 Work-Ahead: Closeout Pipeline Improvement Plan

**Sprint:** FORMAT-FACTORY-R72-DELIVERED-PACKAGE-TEST-FAILURE-REPAIR-LOCAL-RC-SEAL-001
**Date:** 2026-05-28

## Defects That Should Be Caught Automatically

From R71 IV:
1. POST_BUNDLE_AUTHORITATIVE: PENDING not caught before bundle build (IV-R72-004)
2. delivery-package-validation-summary.txt with PENDING not caught (IV-R72-002)
3. external-sidecar-proof-summary.txt with "to be filled" not caught (IV-R72-003)

## Proposed Pipeline Improvements

### Pre-Build Check (closeout_pipeline.py addition)
Add mandatory pre-build scan:
- Scan all metadata files for PENDING tokens
- Reject build if POST_BUNDLE_AUTHORITATIVE: PENDING found
- Reject build if PENDING_BUILD found in delivery summary
- Reject build if "to be filled" found in external sidecar summary

### Delivery Package Validator Enhancement
Add check to validate_evidence_bundle.py:
- `check_delivery_summary_final()`: verify no PENDING in delivery-package-validation-summary.txt
- `check_sidecar_summary_final()`: verify no "to be filled" in external-sidecar-proof-summary.txt
- `check_post_bundle_filled()`: verify POST_BUNDLE_AUTHORITATIVE is not PENDING

### Failing-Test Ledger Requirement
Add contract-level field: `require_failing_test_ledger: true`
- Validator checks that failing-test-ledger.json exists in reports/{run}/
- Validator checks that each failure has a classification

## Priority
HIGH — these are RC-blocking defects that delayed R71 by a full sprint.
