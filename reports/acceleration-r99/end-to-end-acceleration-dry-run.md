# End-to-End Acceleration Dry Run — Train I

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Dry Run Purpose

Prove the acceleration layer can take a product gap from the POC matrix and
produce a governed execution path — without actually performing the product edit.

## Selected Gap

```json
{
  "gap_id": "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
  "format": "FODS",
  "capability_path": "dogfood_status.fods_to_csv_dotnet",
  "current_status": "GAP_DOGFOOD_EXTERNAL",
  "decision": "GOVERNED_SKILL_REQUIRED",
  "governed_skill": "governed-dogfood-export",
  "poc_impact_score": 95,
  "depth_bonus": 10,
  "priority_score": 125,
  "stream": "mainstream"
}
```

## Step 1: Gap Selection (select_poc_gaps.py v3)

```bash
$ python tools/supervisor/select_poc_gaps.py \
    --stream-output-dir .local/supervisor/streams
SELECTED_PRODUCT_GAPS: 14
STREAMS: {'mainstream': 8, 'acceleration': 0, 'skills': 0, 'supervisor': 6}
```

Result: 14 gaps selected, 8 mainstream, 6 supervisor. Top mainstream gap:
`commercial-net-fods-dogfood-status-fods-to-csv-dotnet` with priority 125.

## Step 2: Skill/Handoff Routing (choose_skill_or_handoff.py v2)

```python
choose_skill_or_handoff(gap, skill_registry=registry)
# Result:
{
  "decision": "GOVERNED_SKILL_REQUIRED",
  "governed_skill": "governed-dogfood-export",
  "handoff_required": false,
  "external_gate": false,
  "reason": "Repeatable dogfood-export work must run through a governed skill."
}
```

Decision: USE_SKILL via `/add-dogfood-export` skill command.

## Step 3: Execution Plan (dry run — not executed)

If this were a real sprint, the agent would:

1. **Invoke skill**: `/add-dogfood-export` with:
   - `source_format_id`: FODS
   - `target_format_id`: CSV
   - `export_name`: fods_to_csv_dotnet
   - `target_ff_library`: format-factory-csv (.NET)
   - `exact_source_paths`: src/net/fods/FodsCsvExporter.cs (or equivalent)
   - `exact_test_paths`: tests/net/fods/FodsCsvDogfoodExportTests.cs
   - `ledger_entry_path`: reports/r90/product-code-change-ledger.json
   - `focused_test_command`: dotnet test --filter "FodsCsvDogfoodExport"

2. **Record lane**: `record_lane_execution.py start --lane-id FODS-CSV-DOGFOOD ...`

3. **Validate**: product-code-ledger-validator, focused tests, dogfood backend check

4. **Update matrix**: `/update-capability-matrix` with `fods_to_csv_dotnet: PASS`

5. **Close lane**: `record_lane_execution.py close --lane-id FODS-CSV-DOGFOOD --status completed`

6. **Generate evidence**: Write evidence-declaration.yaml, run materializer, build review package

## Step 4: Expected Changed Files

| File | Change |
|------|--------|
| src/net/fods/FodsCsvExporter.cs | New or modified export class |
| tests/net/fods/FodsCsvDogfoodExportTests.cs | 8+ focused tests |
| reports/r90/product-code-change-ledger.json | New entry |
| product-capability-matrix/poc-targets.yaml | fods_to_csv_dotnet: PASS |

## Step 5: Expected Evidence

| Artifact | Purpose |
|----------|---------|
| evidence-declaration.yaml | Work item declaration |
| lane-execution-ledger.json | Lane timing and status |
| focused-test-output.log | Raw test results |
| source-change-diffs.patch | Git diff of source changes |

## Dry Run Verdict

**DRY_RUN_PASS** — The acceleration layer successfully:
1. Selected the highest-impact gap (125 priority score)
2. Routed it to a governed skill (`governed-dogfood-export`)
3. Generated a complete execution plan with expected files, tests, and evidence
4. Did NOT perform any source edits (dry-run constraint respected)
5. Proved all tools run without errors

## Blockers for Real Execution

- FODS .NET CSV dogfood export requires a Format Factory CSV .NET library
- This gap is `GAP_DOGFOOD_EXTERNAL` because no FF CSV .NET library exists yet
- Until that library is created, the export writes CSV directly (non-dogfood)
