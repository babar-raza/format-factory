# Capability Layer Closeout Sprint -- Final Report

## Sprint Identity
- **Sprint ID:** FORMAT-FACTORY-CAPABILITY-LAYER-REPAIR-AND-HARDENING-001 (v2)
- **Run ID:** capability-layer-repair-hardening-v2
- **Date:** 2026-06-10

## Readiness Verdict

**CAPABILITY_LAYER_VERIFIED_READY** (v2 post-repair)

The Capability & Feature Understanding Layer is verified ready after two repair rounds
that fixed all critical and high issues identified by independent verification.

### v1 Repairs (Phases 1-7)
1. `_determine_state()` per-function test matching (ISS-001/002)
2. VAL-008 field name fix (ISS-004)
3. 33 new unit tests for generator + validator (ISS-003)
4. Spec facts wiring for FOSS and commercial builders (ISS-006, partial)
5. Closeout report updated (ISS-005)

### v2 Repairs (Phases 8-12)
1. Spec facts wired into `_discover_missing_foss_formats()` -- PBM/PGM/PPM now have spec_refs (ISS-006 completion)
2. Netpbm commercial child format mapping -- 46 Netpbm records now have spec_refs (ISS-006 completion)
3. Commercial per-operation test matching -- 35 records now `implementation_verified` instead of false `test_verified` (ISS-016)
4. CSV format discovery -- removed from skip set, 18 CSV records with spec_refs now in FOSS map (ISS-015)

### Post-v2 Metrics
- **650 total records** (125 commercial + 525 FOSS)
- **366 gaps** in gap ledger (332 FOSS + 34 commercial)
- **330 records** with spec_refs (was 86 after v1)
- **Commercial state distribution:** 90 test_verified + 35 implementation_verified
- **FOSS state distribution:** 344 implementation_verified + 73 test_verified + 40 example_verified + 68 CSV/new
- **7 formats** with spec_refs in FOSS map: ZST, PBM, PGM, PPM, CSV, FODS, FODT
- **3 formats** with spec_refs in commercial map: FODS, FODT, Netpbm
- **Validator:** PASS, 0 errors, 367 advisory warnings
- **41/41** capability layer tests pass

## Capability Layer Metrics

| Metric | Value |
|--------|-------|
| Total capability records | 650 |
| Commercial records | 125 |
| FOSS records | 525 |
| Gaps in gap ledger | 366 |
| Commercial gaps | 34 |
| FOSS gaps | 332 |
| Records with spec_refs | 330 |
| Advisory actions | 1 |
| Schemas | 5 |
| Pilots completed | 8 |
| Formats in poc-targets | 11 |
| Capability layer tests | 41 |

## Known Limitations (documented, not blocking)

1. **ISS-014:** Gap ledger only produces `missing_test_coverage` gaps. `missing_implementation` code path exists but is unreachable (scanner only finds existing functions). Cannot surface missing features.
2. **ISS-007:** action-queue.json is advisory-only artifact, not consumed by supervisor pipeline.
3. **ISS-011:** VAL-005 accepts parent directory existence as valid test ref.
4. **ISS-017:** No automated regeneration gate. Maps must be regenerated manually after generator code changes.

## Definition of Done Checklist

1. Per-function test matching works (FOSS) -- YES (ISS-001 fixed, 7 unit tests)
2. Per-operation test matching works (commercial) -- YES (ISS-016 fixed, keyword matching)
3. Spec facts wired for all 7 formats with facts on disk -- YES (ISS-006 complete)
4. CSV format visible in capability map -- YES (ISS-015 fixed, 18 records)
5. Netpbm commercial spec_refs populated -- YES (child format aggregation)
6. Validator passes with 0 errors -- YES
7. All capability layer tests pass (41/41) -- YES
8. Gap ledger includes both FOSS and commercial gaps -- YES (332 + 34)
9. Closeout report honest and evidence-based -- YES (this report)
