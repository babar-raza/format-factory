# R36 Final Verdict

**Sprint:** FORMAT-FACTORY-R36-REGISTRY-ALIGNMENT-DEEPENING-AND-RECOVERY-CONTINUATION-001
**Date:** 2026-05-20

## VERDICT: R36_CLEAN_RECOVERY_CONTINUATION_COMPLETE

## Summary

R36 closes the registry alignment gap left by R35. format-registry.yaml now has gate_correction sections for all 4 overclaimed probe-only formats (FODP/FODG/Gnumeric/ABW) and scope_finalization sections for all 4 image formats (XCF/PPM/PGM/PBM). 19 new deepening tests added (ODS +7, QOI +7, ZST +5). 8 registry alignment guard tests ensure corrections stay synchronized.

## Key R36 Deliverables

1. **format-registry.yaml gate corrections:** 4 gate_correction sections added (FODP/FODG/Gnumeric/ABW)
2. **format-registry.yaml scope finalizations:** 4 scope_finalization sections added (XCF/PPM/PGM/PBM)
3. **Deepening tests:** ODS 94->101, QOI 95->102, ZST 52->57
4. **Registry alignment guards:** 8 new tests (test_r36_registry_alignment_guards.py)
5. **Matrix updated:** Test counts and R36 deepening notes

## Test Results

| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| ODS exporter | 40 | 0 | 0 |
| QOI encoder | 40 | 0 | 0 |
| ZST expansion | 32 | 0 | 0 |
| R36 registry guards | 8 | 0 | 0 |
| .NET FODS | 157 | 0 | 0 |
| .NET FODT | 145 | 0 | 0 |

## New Tests: 27

- ODS export edge cases: 7
- QOI round-trip edge cases: 7
- ZST validation edge cases: 5
- Registry alignment guards: 8

## Safety Proof

- No tools/ai/** modified
- No tests/ai/** modified
- No source files moved or deleted
- No publication_authorized=true
- No commercial_product_ready=true
- No G11-G approved
- No broad format expansion
- No AI synthesis/embeddings/vector DB
- Exact-path staging only
