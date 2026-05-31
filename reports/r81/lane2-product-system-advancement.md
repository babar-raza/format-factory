# Lane 2 — Product/System Advancement

**sprint_id:** FORMAT-FACTORY-R81-FINAL-ARTIFACT-REPAIR-R79-CLOSURE-PRODUCT-ADVANCEMENT-VALIDATOR-HARDENING-20260530

## TC-R79-CLOSURE-001 Status

**Blocked:** R79 product changes (neutral_model.py, constants.py, pyproject.template.toml, test files) are in the working tree but not committed. Per governance rule, commits require explicit human approval. R79 clean bundle cannot be built until commit is authorized.

**Classification:** BLOCKED_GOVERNANCE_RULE — not a blocker for R81, recorded as accepted limitation.

## R79 Package-Source-Sync Hardening (Advancement Work)

Since R79 closure is blocked, advancement focuses on hardening the existing R79 test suite and clarifying installed-wheel test expectations.

### Installed-Wheel Test Classification

`tests/packaging/test_r79_installed_fods_workflow.py` contains two test classes:

1. **TestFodsInstalledWheelImport** (4 tests) — require installed FODS wheel
   - `test_import_fods_not_aspose_name` — skip if wheel absent
   - `test_wrong_namespace_fails` — skip if wheel absent
   - `test_version_from_installed_wheel` — skip if wheel absent
   - `test_track_from_installed_wheel` — skip if wheel absent

2. **TestFodsInstalledWheelApiPresence** (2 tests) — require installed wheel
   - `test_r77_sheet_apis_in_installed_wheel` — skip if wheel absent
   - `test_installed_api_count_at_least_28` — skip if wheel absent

3. **TestFodsInstalledWheelWorkflow** (2 tests) — require installed wheel
   - `test_parse_fods_from_installed_wheel` — skip if wheel absent
   - `test_workbook_sheet_management_from_installed_wheel` — skip if wheel absent

**Result in extracted environment (no wheel):** 8 skipped, 0 failed — correct behavior.
**Result in local environment (wheel installed):** 8 passed — correct behavior.

Both behaviors are correct. The claim in R80 of "8 passed" was truthful for the local environment. It needs qualification: "8 passed in local env with wheel installed; 8 skipped in extracted env without wheel."

### R79 Package-Source-Sync Tests (Advancement Verification)

`tests/packaging/test_r79_package_source_sync.py` — 19 tests, no wheel required:
- `TestPackageVersionSync`: 4 tests — FODS/FODT version and __version__ at dev0
- `TestFodsR77ApiPresence`: 5 tests — R77 sheet management APIs exported
- `TestFodtR77ApiPresence`: 4 tests — R77 paragraph management APIs exported
- `TestFodtStructuralGapRepaired`: 6 tests — GAP-FODT-STRUCT-001 repair verified

All 19 pass. See `product-system-test-log.txt`.

### FODT Structural Gap Fix (Confirmed)

GAP-FODT-STRUCT-001 is RESOLVED. Key tests in TestFodtStructuralGapRepaired:
- `test_append_paragraph_writes_to_root_blocks`: PASS — append writes to `doc["blocks"]` not `doc["body"]["blocks"]`
- `test_append_paragraph_does_not_write_to_body_blocks`: PASS — body is not touched
- `test_paragraph_count_reads_from_root_blocks`: PASS
- `test_paragraph_count_ignores_body_blocks`: PASS
- `test_remove_paragraph_modifies_root_blocks`: PASS
- `test_append_then_roundtrip_preserves_paragraph`: PASS — full roundtrip preserved

## New Taskcard Created

- **TC-R79-WHEEL-SELF-CONTAINED-001**: Include FODS wheel artifact inside evidence bundles so installed-wheel tests can pass from fresh extract.

## Advancement Verdict

| Item | Status |
|---|---|
| TC-R79-CLOSURE-001 | BLOCKED — needs human approval for commit |
| R79 source-sync tests (19) | PASS — all verified |
| FODT structural gap fix | CONFIRMED by 6 dedicated tests |
| Installed-wheel clarification | COMPLETE — claim corrected, new TC created |
| TC-R79-WHEEL-SELF-CONTAINED-001 | OPEN — future work |
