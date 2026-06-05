# Handoff Template: add-dogfood-pipeline (add-dogfood-export)
Version: 1.0 | Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

---

## Role

You are a Format Factory dogfood pipeline agent operating under the `add-dogfood-export` skill.
Your job is to implement a multi-step pipeline test: source data → export → validate output.
The pipeline proves the full round-trip: load a document, transform/export it, verify the
exported content is correct and parseable.
You operate under TIER 2 (FAIL_WITH_REWORK) enforcement.

---

## Skill ID

`add-dogfood-export`

---

## Allowed Files

Populate from the governed handoff YAML:
- `tests/net/{format_id}/{TestClass}DogfoodPipelineTests.cs`

Source files are READ-ONLY for this skill.

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

`git diff -- src/net/` should be EMPTY.
`git diff -- tests/net/{format_id}/` should show the new pipeline test file.

---

## Expected Test Files

Create `tests/net/{format_id}/{TestClass}DogfoodPipelineR{sprint}Tests.cs` with:
- 8+ test methods
- Pipeline steps: load → transform → export → validate
- Tests covering: basic pipeline, error handling, empty input, large input

Capture test run:
```bash
dotnet test tests/net/{format_id}/ --filter "Pipeline" 2>&1 | tee reports/{sprint}/raw-logs/test-pipeline-{format_id}.log
```

---

## Validation Commands

```bash
dotnet build src/net/{format_id}/
dotnet test tests/net/{format_id}/ --filter "Pipeline"
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
    "pipeline_steps": ["load", "transform", "export", "validate"],
    "exact_test_paths": ["tests/net/{format_id}/{TestClass}DogfoodPipelineTests.cs"]
  },
  "allowed_files": ["tests/net/{format_id}/..."],
  "actual_files_changed": ["tests/net/{format_id}/..."],
  "tests_run": ["{TestClass}DogfoodPipelineTests"],
  "result": "PASS",
  "timestamp": "<ISO 8601>",
  "ledger_entry_id": null
}
```

---

## Ledger Schema

Pipeline tests are test-only changes. No ledger entry required unless source files are modified.

---

## Capability Matrix Update

If the pipeline capability closes a known gap, update poc-targets.yaml with:
- `dogfood_pipeline` → `IMPLEMENTED`

---

## Rollback Note

```bash
git checkout tests/net/{format_id}/{TestClass}DogfoodPipelineTests.cs
dotnet test tests/net/{format_id}/  # verify green
```

---

## Evidence Declaration Entries

```yaml
work_items:
  - item_id: W3-DOGFOOD-PIPELINE-{FORMAT}
    title: "Add dogfood pipeline test for {format_id}"
    skill_id: add-dogfood-export
    status: DONE
    evidence_paths:
      - tests/net/{format_id}/{TestClass}DogfoodPipelineTests.cs
      - reports/{sprint}/raw-logs/test-pipeline-{format_id}.log
      - reports/{sprint}/skill-transcripts/transcript-{id}.json
    test_refs:
      - "{TestClass}DogfoodPipelineTests": 8
```

---

## Auto-Repair Guidance

| Problem | Repair Action |
|---------|--------------|
| Pipeline step fails | Debug that step; fix assertion; rerun |
| Transform produces wrong output | Trace actual output; fix expected value |
| Memory leak in pipeline | Use `using` statements for IDisposable objects |

---

## Stop Conditions

STOP if:
- You are asked to modify src/net/* source files
- Git push is required before continuing

---

## Continuation Conditions

CONTINUE if:
- Test assertion fails → fix expected value and rerun
- Test compilation error → fix syntax and rerun
- Transcript validation fails → fix fields and revalidate
