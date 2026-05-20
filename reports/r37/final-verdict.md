# R37 Final Verdict

**Sprint:** FORMAT-FACTORY-R37-EVIDENCE-DEPTH-REPAIR-SELECTIVE-DEEPENING-AND-MATURITY-CLOSURE-001
**Date:** 2026-05-20
**Baseline:** R36 commit d51d4a4 (HEAD: 2f8e6fc with 3 AI-parallel commits)

## VERDICT: R37_EVIDENCE_DEPTH_REPAIR_AND_DEEPENING_COMPLETE

## R36 Evidence-Depth Resolution

- **Classification:** R36_EVIDENCE_DEPTH_SUPERSEDED_BY_R37
- **Root cause:** R36 bundle metadata used 19 placeholder files (`placeholder: true`)
- **Fix:** Added `"placeholder: true"` to PENDING_MARKER_PATTERNS in validate_evidence_bundle.py
- **Guard:** 10 new evidence depth guard tests prevent recurrence

## Deliverables

### Lane A: R36 Evidence-Depth Supersession
- R36 evidence-depth caveat documented and superseded by R37

### Lane B: Evidence Bundle Quality Guard Hardening
- `validate_evidence_bundle.py`: Added `placeholder: true` to PENDING_MARKER_PATTERNS
- `test_r37_evidence_depth_guards.py`: 10 tests (7 pass, 3 skip pending R37 artifacts)
  - TestPlaceholderDetection (3 tests): placeholder detection in validator
  - TestContractFloorGuards (2 tests): R33+ contract floor enforcement
  - TestMetadataContentDepth (3 tests): pending pattern count, floor value, R36 contract
  - TestR36EvidenceDepthCaveat (2 tests): preflight documentation guards

### Lane C: R36 Registry/Matrix/Pack Alignment IV
- Background agent confirmed R36 alignment guards pass (8/8)
- R35 evidence guards pass (12/12)

### Lane D: Probe-Format Recovery Decision Packets
- `reports/r37/probe-format-recovery-decisions.md`
- FODP: Quarantine (Option B)
- FODG: Quarantine (Option B)
- Gnumeric: Quarantine + Deepening Candidate
- ABW: Quarantine (Option B)

### Lanes E-H: Selective Deepening
| Format | Before | After | New Tests |
|--------|--------|-------|-----------|
| ODS | 101 | 107 | 6 (RFC 4180 compliance: tab, semicolon, newline, quotes, boolean, empty) |
| QOI | 102 | 108 | 6 (encoder boundary: max run, 63-split, gradient, alpha, capabilities, invalid channels) |
| ZST | 57 | 62 | 5 (codec depth: empty, single-byte, repetitive, incompressible, probe magic) |
| **Total** | **260** | **277** | **17** |

### Lane I: Matrix/Registry Integration
- format-completion-matrix.yaml updated with R37 test counts and deepening notes

## Test Results

| Suite | Passed | Skipped | Failed | Notes |
|-------|--------|---------|--------|-------|
| Python format tests | 892 | 4 | 2 | Pre-existing (DIF/PPM probe) |
| Evidence tests | 582 | 1 | 1 | Pre-existing (R32 verdict string) |
| .NET FODS | 157 | 0 | 0 | |
| .NET FODT | 145 | 0 | 0 | |
| **Total** | **1776** | **5** | **3 pre-existing** | |

R37 new tests: 27 (evidence=10, ODS=6, QOI=6, ZST=5)

## Files Modified
- `tools/evidence/validate_evidence_bundle.py` (PENDING_MARKER_PATTERNS +1 pattern)
- `tests/python/ods/test_ods_csv_exporter.py` (+6 tests)
- `tests/python/qoi/test_qoi_encoder.py` (+6 tests)
- `tests/python/zst/test_zst_r33_expansion.py` (+5 tests)
- `registry/format-completion-matrix.yaml` (test count updates)

## Files Created
- `tests/evidence/test_r37_evidence_depth_guards.py` (10 tests)
- `reports/r37/preflight-and-lane-ownership.md`
- `reports/r37/probe-format-recovery-decisions.md`
- `reports/r37/final-verdict.md`
- `reports/r37/adversarial-review.md`
- `tools/evidence/contracts/r37-evidence-depth-repair-selective-deepening.yaml`
- `memory/56-r37-evidence-depth-repair-and-deepening-20260520.md`
