# R72 Preflight

**Sprint:** FORMAT-FACTORY-R72-DELIVERED-PACKAGE-TEST-FAILURE-REPAIR-LOCAL-RC-SEAL-001
**Date:** 2026-05-28

## R71 Classification
R71_PROOF_MODEL_PROGRESS_ACCEPTED_DELIVERY_AND_TEST_CLOSURE_REJECTED

## IV Defects Found (8 RC-blocking)
1. IV-R72-001: Uploaded artifact was inner ZIP only; outer delivery package not delivered
2. IV-R72-002: delivery-package-validation-summary.txt had PENDING_PASS_2_SHA / PENDING_BUILD
3. IV-R72-003: external-sidecar-proof-summary.txt had "to be generated" / "to be filled"
4. IV-R72-004: python-tests-summary.txt had POST_BUNDLE_AUTHORITATIVE: PENDING
5. IV-R72-005: R71 evidence tests: 41 required skips in extracted bundle replay
6. IV-R72-006: Final verdict said "10 failed" without naming the tests
7. IV-R72-007: 10 failing tests uninvestigated, unclassified, untaskcarded
8. IV-R72-008: Validator check_inner_verdict_delivery_sha_authority() scope bug (current_run=None)

## Hard Prohibitions (all confirmed)
- No push: CONFIRMED
- No PyPI/NuGet publication: CONFIRMED
- No Gate 8/11 approval: CONFIRMED
- No source/API changes unless required to fix failing test: CONFIRMED (fixes were validator + contract + test)
- No final COMPLETE unless delivery package with inner ZIP + sidecar + manifest: CONFIRMED

PREFLIGHT: PASS
