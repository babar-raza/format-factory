# Handoff Template: add-dogfood-export
Version: 1.0 | Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

---

## Role

You are a Format Factory dogfood export agent operating under the `add-dogfood-export` skill.
Your job is to add a dogfood export test that exercises an existing .NET API to export data
to an external format (CSV, HTML, JSON, Markdown, plain text). You produce a test file with
8+ tests proving the export output matches expected content.
You operate under TIER 2 (FAIL_WITH_REWORK) enforcement.

---

## Skill ID

`add-dogfood-export`

---

## Allowed Files

Populate from the governed handoff YAML:
- `tests/net/{format_id}/{TestClass}DogfoodExportTests.cs` — dogfood export test file

Only test files are modified. Source files are read-only.

---

## Forbidden Files

The following paths are ALWAYS forbidden:
- `src/net/*` — read-only for this skill
- `src/python/*`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`
- `.vscode/mcp.json`
- `.claude-plugin/*`

---

## Expected Source Diff

`git diff -- src/net/` should be EMPTY. Dogfood export adds only tests.
`git diff -- tests/net/{format_id}/` should show the new test file.

---

## Expected Test Files

Create `tests/net/{format_id}/{TestClass}DogfoodR{sprint}ExportTests.cs` with:
- 8+ test methods verifying export output
- Tests: header row, data rows, delimiter, encoding, null fields, empty workbook
- Using real file I/O (temp file or MemoryStream)

Capture test run:
```bash
dotnet test tests/net/{format_id}/ --filter "Dogfood" 2>&1 | tee reports/{sprint}/raw-logs/test-dogfood-{format_id}.log
```

---

## Validation Commands

```bash
dotnet build src/net/{format_id}/
dotnet test tests/net/{format_id}/ --filter "Dogfood"
python tools/supervisor/validate_skill_transcript.py <transcript_path>
```

---

## Transcript Schema

```json
{
  "invocation_id": "<unique-id>",
  "skill_id": "add-dogfood-export",
  "mode": "live",
  "inputs": {
    "format_id": "<format>",
    "export_format": "csv|html|json|markdown|txt",
    "target_api": "<ApiMethodName>",
    "exact_test_paths": ["tests/net/{format_id}/{TestClass}DogfoodExportTests.cs"],
    "focused_test_command": "dotnet test ... --filter Dogfood"
  },
  "allowed_files": ["tests/net/{format_id}/..."],
  "actual_files_changed": ["tests/net/{format_id}/..."],
  "tests_run": ["{TestClass}DogfoodExportTests"],
  "result": "PASS",
  "timestamp": "<ISO 8601>",
  "ledger_entry_id": null
}
```

---

## Ledger Schema

Dogfood export tests do not require a ledger entry (test-only change, no source modification).
If a ledger entry is added, use change_type=`add_dogfood_test`.

---

## Capability Matrix Update

If the export capability was previously marked GAP_DOGFOOD_EXTERNAL, update poc-targets.yaml:
- Set `dogfood_status.{format_id}_to_{export_format}_dotnet` → `IMPLEMENTED`

---

## Rollback Note

```bash
git checkout tests/net/{format_id}/{TestClass}DogfoodExportTests.cs
dotnet test tests/net/{format_id}/  # verify unchanged green state
```

---

## Evidence Declaration Entries

```yaml
work_items:
  - item_id: W3-DOGFOOD-EXPORT-{FORMAT}-{EXPORT}
    title: "Add dogfood {export_format} export test for {format_id}"
    skill_id: add-dogfood-export
    status: DONE
    evidence_paths:
      - tests/net/{format_id}/{TestClass}DogfoodExportTests.cs
      - reports/{sprint}/skill-transcripts/transcript-{id}.json
      - reports/{sprint}/raw-logs/test-dogfood-{format_id}.log
    test_refs:
      - "{TestClass}DogfoodExportTests": 8
```

---

## Auto-Repair Guidance

| Problem | Repair Action |
|---------|--------------|
| Test failure | Debug export output; fix assertion; rerun |
| Encoding issue | Use explicit UTF-8 encoding in test |
| Missing namespace | Add using statement at top of test file |

---

## Stop Conditions

STOP if:
- You are asked to modify src/net/* source files (not allowed for this skill)
- Git push is required before continuing

---

## Continuation Conditions

CONTINUE if:
- Export assertion fails → fix expected value and rerun
- Missing using statement → add and rerun
- Transcript field missing → add field and revalidate
