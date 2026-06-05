# Handoff Template: add-python-api
Version: 1.0 | Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

---

## Role

You are a Format Factory Python API implementation agent operating under the `add-python-api` skill.
Your job is to add one new API function to an existing Python format module (FODS, FODT, ZST, PPM, SYLK, DIF)
with at least 8 tests, a product-ledger entry, and a passing test run.
You operate under TIER 1 (FAIL_CLOSED) enforcement — all 9 minimum viable packet fields required.

---

## Skill ID

`add-python-api`

---

## Allowed Files

Populate from the governed handoff YAML received from Skills lane:
- `src/python/{format_id}/{module}.py` — main implementation file
- `tests/python/{format_id}/test_{format_id}_{feature}.py` — test file
- `reports/r90/product-code-change-ledger.json` — ledger entry

Do NOT write to any path not listed in the handoff's `allowed_files` field.

---

## Forbidden Files

The following paths are ALWAYS forbidden regardless of handoff content:
- `src/net/*`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `product-capability-matrix/poc-targets.yaml`
- `.vscode/mcp.json`
- `.supervisor/policies.yaml`
- `reports/supervisor/approval-gates.md`
- `.claude-plugin/*`

---

## Expected Source Diff

After execution, `git diff -- src/python/{format_id}/` should show:
- One new public function added
- Function with type hints and docstring
- No other functions modified

Capture with:
```bash
git diff -- src/python/{format_id}/ > reports/{sprint}/raw-logs/source-diff-{format_id}-{api_name}.txt
```

---

## Expected Test Files

Create `tests/python/{format_id}/test_r{sprint}_{format_id}_{feature}.py` with:
- Minimum 8 test functions
- Tests covering: happy path, empty input, edge cases, type errors
- Using pytest conventions (def test_*, assert statements)

Capture test run:
```bash
python -m pytest tests/python/{format_id}/ -v 2>&1 | tee reports/{sprint}/raw-logs/test-{format_id}-{api_name}.log
```

---

## Validation Commands

```bash
# 1. Run focused tests
python -m pytest tests/python/{format_id}/test_{feature}.py -v

# 2. Validate transcript
python tools/supervisor/validate_skill_transcript.py <transcript_path>

# 3. Validate adoption compliance
python -c "
from tools.supervisor.validate_adoption_compliance import validate_adoption
result = validate_adoption(declaration_work_item)
assert result['compliant'], result
print('Compliant:', result['compliant'])
"
```

---

## Transcript Schema

Produce a JSON transcript at `reports/{sprint}/skill-transcripts/transcript-{invocation_id}.json`:

```json
{
  "invocation_id": "<unique-id>",
  "skill_id": "add-python-api",
  "mode": "live",
  "inputs": {
    "format_id": "<format>",
    "api_name": "<function>",
    "exact_source_paths": ["src/python/{format_id}/{module}.py"],
    "exact_test_paths": ["tests/python/{format_id}/test_{feature}.py"],
    "focused_test_command": "python -m pytest ...",
    "execution_plan": "<handoff_yaml_path>"
  },
  "allowed_files": ["src/python/..."],
  "actual_files_changed": ["src/python/..."],
  "tests_run": ["test_{feature}"],
  "result": "PASS",
  "timestamp": "<ISO 8601>",
  "ledger_entry_id": "<entry-id>"
}
```

---

## Ledger Schema

Add one entry to `reports/r90/product-code-change-ledger.json`:

```json
{
  "entry_id": "<unique-id>",
  "sprint_id": "<sprint>",
  "skill_id": "add-python-api",
  "format_id": "<format>",
  "change_type": "add_api",
  "api_name": "<function>",
  "files_changed": ["src/python/..."],
  "tests_added": 8,
  "timestamp": "<ISO 8601>"
}
```

---

## Capability Matrix Update

After successful implementation, update `product-capability-matrix/poc-targets.yaml`:
- Set the capability status to `IMPLEMENTED`
- Add `evidence_sprint` referencing this sprint
- Run: `python tools/supervisor/validate_product_code_ledger.py`

---

## Rollback Note

If the implementation needs to be reverted:
```bash
git checkout src/python/{format_id}/{module}.py
git checkout tests/python/{format_id}/test_{feature}.py
python -m pytest tests/python/{format_id}/  # verify green
```

---

## Evidence Declaration Entries

Add to `.local/evidences/{sprint}/evidence-declaration.yaml`:

```yaml
work_items:
  - item_id: W3-ADD-PYTHON-API-{FORMAT}
    title: "Add {api_name} to {format_id} Python"
    skill_id: add-python-api
    status: DONE
    evidence_paths:
      - src/python/{format_id}/{module}.py
      - tests/python/{format_id}/test_{feature}.py
      - reports/{sprint}/skill-transcripts/transcript-{id}.json
      - reports/{sprint}/raw-logs/test-{format_id}-{api_name}.log
    test_refs:
      - test_{feature}: 8
    ledger_entry_path: reports/r90/product-code-change-ledger.json
```

---

## Auto-Repair Guidance

| Problem | Repair Action |
|---------|--------------|
| Import error | Fix module path; re-run; do not stop |
| Test failure | Debug; fix source or test; rerun |
| Transcript validation fail | Check required fields; fix; rerun validator |
| Adoption compliance fail | Add missing evidence_path; rerun |
| Missing ledger entry | Add entry to ledger JSON; revalidate |

---

## Stop Conditions

STOP and record a blocker if:
- Git push is needed before continuing
- Gate 8 or Gate 11 approval is required
- You are asked to edit `src/net/*` or any forbidden path
- External credentials or paid API keys are needed

---

## Continuation Conditions

CONTINUE (never stop) if:
- Python import error → fix module path and rerun
- Test fails → debug and fix
- Transcript validation fails → fix JSON fields and revalidate
- Ledger entry is malformed → fix JSON and revalidate
