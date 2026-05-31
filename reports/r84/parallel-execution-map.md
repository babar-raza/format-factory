# R84 Parallel Execution Map

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31

## Wave 0 (Planning — COMPLETE)
- Trains A planning, scoreboard, lane-ownership, parallel map, risk register, scope map, state assessment

## Wave 1 (Source Changes — parallel)
Run together:
- Train G: FODS feature advancement (2 new APIs: workbook_to_csv, workbook_get_cell_value)
- Train I: FODT feature advancement (2 new APIs: document_to_text, document_get_paragraph_text)
- Train M: Netpbm advancement (PBM/PGM/PPM writer roundtrip + diagnostics)
- Train N: SYLK/DIF advancement (coordinate normalization + cell type preservation)
- Train B: build_supervisor_review_package.py modification

## Wave 2 (Tests — parallel after Wave 1)
- Train E: Validator fail-closed tests (5 new test files)
- Train F/H: FODS/FODT workflow tests from top-level review package layout
- Train K: Run fresh .NET tests (background)
- Train D: Generate raw install/negative proof logs

## Wave 3 (Build — sequential)
- Run full Python test suite → save raw log
- Build package artifacts (10 wheels + 10 sdists)
- Run installed workflow tests

## Wave 4 (Bundle Build — sequential)
Critical path (must be sequential):
1. Update all metadata with real values
2. Build Pass 1 evidence bundle → get SHA1
3. Commit SHA1 to final-verdict.md
4. Build Pass 2 evidence bundle → get SHA2
5. Commit SHA2 to final-verdict.md
6. Build Pass 3 (final) evidence bundle → get SHA3
7. Generate sidecar (SHA3 + validation)
8. Build delivery package
9. Build supervisor review package (top-level self-contained)

## Wave 5 (Authority + IV)
- Train V: State sync (after bundle build)
- Train W: Final adversarial IV
- Final commit
- Trigger supervisor loop

## Critical Constraints
1. Bundle build requires clean git
2. State snapshot must run AFTER all SHAs committed
3. Supervisor review package built LAST
4. Raw logs must be physically generated before bundle build
