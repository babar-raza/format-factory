# R36 — Registry Alignment and Deepening Continuation

**Sprint:** FORMAT-FACTORY-R36-REGISTRY-ALIGNMENT-DEEPENING-AND-RECOVERY-CONTINUATION-001
**Date:** 2026-05-20
**Baseline:** R35 commit 27ba09a (clean recovery baseline)

## What R36 Fixed

R35 applied gate corrections to pack.yaml and format-completion-matrix.yaml but missed format-registry.yaml. R36 closes this gap:

- **format-registry.yaml:** Added gate_correction for FODP/FODG/Gnumeric/ABW, scope_finalization for XCF/PPM/PGM/PBM
- **Registry alignment guard tests:** 8 tests ensure registry and pack.yaml corrections stay synchronized

## Deepening

| Format | Before | After | New Tests |
|--------|--------|-------|-----------|
| ODS | 94 | 101 | 7 (multi-sheet, empty doc, file export) |
| QOI | 95 | 102 | 7 (single pixel, column/row, checkerboard, file round-trip) |
| ZST | 52 | 57 | 5 (validate_file, non-zstd data, binary round-trip, compression levels) |

## Evidence

- R33 product work: 116/116 revalidated
- .NET FODS: 157/157, FODT: 145/145
- R36 registry guards: 8/8
- New deepening: 19/19
- Total new tests this sprint: 27

## Third Bundle

r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation-20260519.zip exists in .local/evidence-bundles/. It is the AI parallel track bundle. Out of R36 scope.
