# R33 Product Work Validation Report

**Sprint:** R34
**Date:** 2026-05-20

## Focused R33 Tests
- tests/python/ods/test_ods_csv_exporter.py: 25 passed
- tests/python/qoi/test_qoi_encoder.py: 25 passed
- tests/python/zst/test_zst_r33_expansion.py: 23 passed
- tests/evidence/test_r33_overclaim_and_deepening.py: 23 passed
- **Total: 96 passed, 0 failed**

## Broader Evidence Suite
- tests/evidence: 297 passed, 1 failed (pre-existing R28 PENDING detector)

## Broader Python Suite
- tests/python: 836 passed, 2 failed (pre-existing DIF/PPM probe), 4 skipped

## R34 Scope Collision Guard Tests
- tests/evidence/test_r34_scope_collision_guard.py: 21 passed

## Failure Classification
| Test | Classification | Cause |
|------|---------------|-------|
| test_no_pending_in_committed_verdicts | pre_existing | R28 detector finds PENDING in R32 overwritten verdict |
| test_probe_nonexistent (DIF) | pre_existing | Windows path behavior for /nonexistent |
| test_probe_nonexistent (PPM) | pre_existing | Windows path behavior for /nonexistent |

## Verdict: R33_PRODUCT_WORK_VALIDATED
All R33 product work (ODS exporter, QOI encoder, ZST expansion, overclaim review) passes validation. No R34 regressions introduced.
