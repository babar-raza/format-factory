# Handoff Template: add-roundtrip-test
Version: 1.0 | Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

---

## Role

You are a Format Factory roundtrip test agent operating under the `add-roundtrip-test` skill.
Your job is to add a save-reload roundtrip test that proves a loaded document can be saved
and reloaded with identical content. This validates parser and writer consistency.
You operate under TIER 2 (FAIL_WITH_REWORK) enforcement.

---

## Skill ID

`add-roundtrip-test`

---

## Allowed Files

Populate from the governed handoff YAML:
- `tests/net/{format_id}/{TestClass}RoundtripTests.cs` (.NET)
- OR `tests/python/{format_id}/test_roundtrip_{feature}.py` (Python)

Source files are READ-ONLY for this skill.

---

## Forbidden Files

The following paths are ALWAYS forbidden:
- `src/net/*` — read-only for this skill
- `src/python/*` — read-only for this skill
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`
- `.vscode/mcp.json`
- `.claude-plugin/*`

---

## Expected Source Diff

`git diff -- src/` should be EMPTY (test-only change).
`git diff -- tests/` should show the new roundtrip test file.

---

## Expected Test Files

Create roundtrip test file with:
- 8+ test methods
- Steps per test: load document → save to bytes/stream → reload from bytes/stream → assert equal
- Tests covering: simple document, with metadata, empty document, special characters

For .NET:
```bash
dotnet test tests/net/{format_id}/ --filter "Roundtrip" 2>&1 | tee reports/{sprint}/raw-logs/test-roundtrip-{format_id}.log
```

For Python:
```bash
python -m pytest tests/python/{format_id}/test_roundtrip_{feature}.py -v 2>&1 | tee reports/{sprint}/raw-logs/test-roundtrip-{format_id}.log
```

---

## Validation Commands

```bash
# .NET
dotnet test tests/net/{format_id}/ --filter "Roundtrip"

# Python
python -m pytest tests/python/{format_id}/test_roundtrip_{feature}.py -v

# Transcript
python tools/supervisor/validate_skill_transcript.py <transcript_path>
```

---

## Transcript Schema

```json
{
  "invocation_id": "<unique-id>",
  "skill_id": "add-roundtrip-test",
  "mode": "live",
  "inputs": {
    "format_id": "<format>",
    "test_type": "roundtrip",
    "exact_test_paths": ["tests/{platform}/{format_id}/..."],
    "focused_test_command": "dotnet test ... --filter Roundtrip"
  },
  "allowed_files": ["tests/{platform}/{format_id}/..."],
  "actual_files_changed": ["tests/{platform}/{format_id}/..."],
  "tests_run": ["RoundtripTests"],
  "result": "PASS",
  "timestamp": "<ISO 8601>",
  "ledger_entry_id": null
}
```

---

## Ledger Schema

Roundtrip tests are test-only. No ledger entry required (no source modification).
If a ledger entry is desired, use change_type=`add_roundtrip_test`.

---

## Capability Matrix Update

If the roundtrip closes a known gap (e.g., `roundtrip_save_reload` previously PARTIAL):
- Update poc-targets.yaml: `roundtrip_save_reload` → `IMPLEMENTED`

---

## Rollback Note

```bash
# .NET
git checkout tests/net/{format_id}/{TestClass}RoundtripTests.cs
dotnet test tests/net/{format_id}/

# Python
git checkout tests/python/{format_id}/test_roundtrip_{feature}.py
python -m pytest tests/python/{format_id}/
```

---

## Evidence Declaration Entries

```yaml
work_items:
  - item_id: W3-ROUNDTRIP-{FORMAT}
    title: "Add roundtrip test for {format_id}"
    skill_id: add-roundtrip-test
    status: DONE
    evidence_paths:
      - tests/{platform}/{format_id}/{TestClass}RoundtripTests.cs
      - reports/{sprint}/raw-logs/test-roundtrip-{format_id}.log
      - reports/{sprint}/skill-transcripts/transcript-{id}.json
    test_refs:
      - RoundtripTests: 8
```

---

## Auto-Repair Guidance

| Problem | Repair Action |
|---------|--------------|
| Roundtrip mismatch | Compare load → save → reload; fix serialization order |
| Byte-level diff | Normalize whitespace or encoding before comparison |
| Writer not producing valid output | Check parser/writer contract; fix writer |

---

## Stop Conditions

STOP if:
- You are asked to modify src/ files to fix the roundtrip (that requires add-dotnet-api or add-python-api skill)
- Git push is required before continuing

---

## Continuation Conditions

CONTINUE if:
- Test assertion fails → fix expected value or serialization logic
- Test compilation error → fix syntax
- Transcript validation fails → fix fields and revalidate
