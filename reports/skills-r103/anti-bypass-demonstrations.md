# Anti-Bypass Demonstrations (Skills R103 Wave 5)

## Results: 9/9 PASS

| # | Demo | Input | Expected | Validator Error |
|---|------|-------|----------|----------------|
| 1 | Unregistered skill_id | BACKFILLED_PRE_GOVERNANCE | FAIL | skill_id not found in registry |
| 2 | Fabricated skill_id | add-magic-feature | FAIL | skill_id not found in registry |
| 3 | Invalid mode | yolo | FAIL | invalid mode |
| 4 | Files outside allowed | registry/format-registry.yaml | FAIL | files changed outside allowed paths |
| 5 | Missing required fields | only skill_id | FAIL | missing required fields |
| 6 | Live without ledger | live mode, no ledger_entry_id | FAIL | requires ledger_entry_id |
| 7 | Command missing sections | 3-line fake command | FAIL | missing sections |
| 8 | BACKFILLED for current sprint | live + BACKFILLED_PRE_GOVERNANCE | FAIL | skill_id not found in registry |
| 9 | Invalid result value | ACCEPTED_VERIFIED as result | FAIL | invalid result |

## New in R103 (vs R102)

- Demo 9: ACCEPTED_VERIFIED as transcript result — rejected because only PASS/FAIL are valid results
- All demos produce detailed error messages suitable for grading

## Evidence

- Machine-readable: `validator-results/anti-bypass-demos.json`
- Human-readable: this file
