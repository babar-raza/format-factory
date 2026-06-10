# Transcript: R104-ANTI-001-BACKFILLED-REJECTED

- **Skill:** add-dotnet-object-model-feature
- **Mode:** anti-bypass-demo
- **Result:** FAIL
- **Timestamp:** 2026-06-03T09:36:53.276939Z

## Notes
Anti-bypass demo: BACKFILLED_PRE_GOVERNANCE marker detected. Skill system rejects backfilled claims that skip governance. Expected FAIL.

## Inputs
```json
{
  "format_id": "fods",
  "feature_name": "BackfilledFeature",
  "exact_source_paths": [
    "src/net/fods/FodsDocument.cs"
  ],
  "exact_test_paths": [
    "tests/net/fods/FodsBackfilledTests.cs"
  ],
  "ledger_entry_path": "reports/r90/product-code-change-ledger.json",
  "backfill_marker": "BACKFILLED_PRE_GOVERNANCE"
}
```

## Files
- Allowed: ['src/net/fods/FodsDocument.cs', 'tests/net/fods/FodsBackfilledTests.cs']
- Changed: []
- Tests: []