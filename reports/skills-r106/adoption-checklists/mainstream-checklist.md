# Mainstream Adoption Checklist (Skills R106) -- Enforcement Gates

This checklist replaces the R105 advisory version. Every gate is enforced by a named validator.
Failure at any REQUIRED gate blocks acceptance (grade capped at OVERCLAIMED or REWORK_REQUIRED).

---

## GATE M-01: Skill Routing (REQUIRED)

- **What:** Identify the `skill_id` for the product work from `.supervisor/skill-registry.yaml`.
- **Check:** Work item in evidence declaration contains `skill_id` field.
- **Validator:** `grade_declared_work.py` checks for `skill_id` on items with `src/` evidence paths.
- **Failure:** OVERCLAIMED -- "Product source changed without skill_id routing."
- **Responsible:** Mainstream worker.

| Condition | Pass/Fail |
|-----------|-----------|
| `skill_id` present and registered in `skill-registry.yaml` | PASS |
| `skill_id` present but not in registry | FAIL (OVERCLAIMED) |
| `skill_id` absent, item touches `src/` | FAIL (OVERCLAIMED) |
| `skill_id` absent, item does NOT touch `src/` | N/A (gate does not apply) |

---

## GATE M-02: Command File Consumption (REQUIRED)

- **What:** Read the command file at `.claude/commands/{skill_id}.md` before executing.
- **Check:** Transcript `inputs.command_file` matches the registry `command_file` path.
- **Validator:** `validate_skill_transcript.py` cross-references `skill_id` against registry.
- **Failure:** OVERCLAIMED -- "Transcript skill_id does not match a valid command file."
- **Responsible:** Mainstream worker.

---

## GATE M-03: Allowed Files Scope (REQUIRED)

- **What:** Only modify files listed in the handoff `exact_source_paths` and `exact_test_paths`.
- **Check:** Transcript `actual_files_changed` is a subset of `allowed_files`.
- **Validator:** `validate_skill_transcript.py` compares `actual_files_changed` against `allowed_files`.
- **Failure:** REWORK_REQUIRED -- "Files changed outside allowed scope."
- **Responsible:** Mainstream worker.

---

## GATE M-04: Product Code Ledger (REQUIRED for LIVE src edits)

- **What:** Create a ledger entry in `reports/r90/product-code-change-ledger.json` BEFORE editing source.
- **Check:** Transcript `ledger_entry_id` is non-null; ledger validator confirms entry exists and covers changed files.
- **Validator:** `validate_product_code_ledger.py` -- exit 0 = pass.
- **Command:** `.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py`
- **Failure:** OVERCLAIMED -- "LIVE src-editing skill without ledger_entry_id."
- **Responsible:** Mainstream worker.

| Condition | Pass/Fail |
|-----------|-----------|
| `mode: LIVE`, `ledger_entry_id` present, validator exit 0 | PASS |
| `mode: LIVE`, `ledger_entry_id` missing | FAIL (OVERCLAIMED) |
| `mode: LIVE`, `ledger_entry_id` present, validator exit != 0 | FAIL (REWORK_REQUIRED) |
| `mode: DRYRUN` | N/A (ledger not required) |

---

## GATE M-05: Transcript Generation (REQUIRED)

- **What:** Write a transcript JSON to `reports/{run_id}/skill-transcripts/` after skill execution.
- **Check:** File exists at declared evidence path; contains all required fields.
- **Validator:** `validate_skill_transcript.py <transcript.json>` -- exit 0 = pass.
- **Command:** `.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py <path>`
- **Required fields:** `invocation_id`, `skill_id`, `mode`, `inputs`, `allowed_files`, `actual_files_changed`, `tests_run`, `result`, `timestamp`.
- **Failure:** Missing => OVERCLAIMED. Invalid schema => OVERCLAIMED. `result: FAIL` => REWORK_REQUIRED.
- **Responsible:** Mainstream worker.

---

## GATE M-06: Focused Tests (REQUIRED)

- **What:** Run the focused test command specified in the handoff and record results.
- **Check:** Transcript `tests_run` is non-empty; test results in evidence show pass.
- **Validator:** `grade_declared_work.py` checks `tests_with_content` and test pass/fail.
- **Failure:** No tests run => REWORK_REQUIRED. Tests failed => REWORK_REQUIRED.
- **Responsible:** Mainstream worker.

---

## GATE M-07: Evidence Declaration (REQUIRED)

- **What:** Include transcript path in `evidence_paths` of the evidence declaration YAML.
- **Check:** `inspect_declared_evidence.py` finds transcript file at declared path.
- **Validator:** Built into inspection pipeline.
- **Failure:** Missing path => `evidence_paths_missing` populated => REWORK_REQUIRED.
- **Responsible:** Mainstream worker.

---

## Handoff Consumption (RECOMMENDED -- not gate-blocking)

When a generated execution handoff exists in `reports/skills-r{N}/generated-handoffs/`, the mainstream worker SHOULD consume it. This is not gate-blocking, but consuming handoffs improves traceability and reduces rework. Tracked as a quality signal in supervisor review.

---

## Quick Reference: Validator Commands

```
# Validate transcript
.local/venv/Scripts/python tools/supervisor/validate_skill_transcript.py reports/<run_id>/skill-transcripts/<file>.json

# Validate ledger
.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py

# Full grading (supervisor runs this)
.local/venv/Scripts/python tools/supervisor/grade_declared_work.py --inspection <i.json> --declaration <d.yaml> --output-dir <dir>
```
