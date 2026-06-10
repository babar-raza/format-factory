# Gap Queue Policy Repair
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Lane: F

## Summary
The gap queue architecture-blocked routing issue was fixed in a prior sprint
(FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001).
This sprint confirms the fix is correct and adds regression tests.

## Prior Fix (already applied)
`tools/supervisor/select_poc_gaps.py` — `detect_target_writer_status()` function:
- Probes filesystem for writer source, project, tests, raw log, sample output
- Returns frozenset of still-blocked gap IDs
- `BLOCKED_GAP_IDS = detect_target_writer_status(REPO_ROOT)` at module load

Since all 4 writers are now built: `BLOCKED_GAP_IDS = frozenset()`

## Confirmed State
- `fods-to-csv-dotnet`: UNBLOCKED (FormatFactory.Csv exists)
- `fods-to-html-dotnet`: UNBLOCKED (FormatFactory.Html exists)
- `fodt-to-markdown-dotnet`: UNBLOCKED (FormatFactory.Markdown exists)
- `fodt-to-txt-dotnet`: UNBLOCKED (FormatFactory.Txt exists)

## New Regression Tests Added
`tests/requirement_capability_authority/test_r119_export_target_writer_policy.py`
- TestBlockedGapIdsEmpty: 10 tests — PASS
- TestExporterDelegation: 7 tests — PASS
- TestExportPolicySeparation: 3 tests — 2 pass, 1 skip
- TestFodsProjectReferences: 2 tests — PASS
- TestDetectTargetWriterStatus: 2 tests — PASS

## Policy Guarantees
1. A blocked gap only routes to TargetWriterArchitecture lane when its writer is missing
2. When writer is built, gap is unblocked → routes to product integration lane
3. HTML, TXT, Markdown remain separate from CSV (each requires its own wiring)
4. No `/add-dogfood-export` should be recommended for gaps with missing writers
   (enforced by select_poc_gaps.py blocking filter)

## Lane F Verdict: ACCEPT
