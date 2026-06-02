# R89 Train B: Declaration-Driven Closeout Consistency

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## R88 IV Finding: Exit Code Contradiction
- `reports/r88/autonomous-cycle-end-to-end-proof.md` says exit code 3
- R88 supervisor review accepted the bundle with BUNDLE_VALIDATION: PASS

Resolution: **Not a contradiction.** The exit code 3 was from the E2E proof run
(Train E) using a partial 5-item declaration. The final acceptance was from a
separate full run using the complete 21-train declaration. The proof run
intentionally tested with incomplete data to verify error handling.

## R88 IV Finding: Test Count Mismatch
- R88 evidence-declaration.yaml: `tests_run: 6839, passed: 6783, failed: 30`
- R88 state-sync report: `Total: 2809 passed`

Resolution: The 6839 figure included csv-shadow duplicates and full pytest collection
with conftest path conflicts. The authoritative count was 2809 (per state-sync).
R89 corrects this by fixing the csv shadow, yielding 2953 total (see Train A).

## Consistency Rules for Future Declarations
1. `tests_run` MUST match the deduplicated count from the authoritative test command
2. `test_results.failed` MUST be 0 for a PASS grade (pre-existing exclusions documented separately)
3. Exit codes from proof-of-concept runs must not be conflated with final pipeline results
4. When multiple autonomous-cycle runs occur, the declaration should reference the final run

## Status: COMPLETE
