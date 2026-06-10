# Mainstream Adoption Checklist (Skills R107) -- Enforcement Gates

This checklist supersedes the R106 version. All R106 gates are retained.
R107 additions are marked with **(R107 NEW)** and wire enforcement into the
supervisor grading pipeline so that violations are caught automatically, not
just documented.

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

### R107 Enforcement Integration (R107 NEW)

- `inspect_declared_evidence.py` now enriches each work item's inspection output
  with `skill_id_present: true|false` and `skill_id_registered: true|false`.
- `grade_declared_work.py` reads these fields and applies the grade cap
  automatically -- no manual review step needed.
- **Testable assertion:** If `evidence_paths` contains any path matching
  `src/net/**` or `src/python/**` and `skill_id` is null, the grading output
  MUST contain `grade: OVERCLAIMED` with `violation: CSE-01`.

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

### R107 Enforcement Integration (R107 NEW)

- `inspect_declared_evidence.py` now locates transcript files among evidence
  paths (matching `**/skill-transcripts/*.json`) and inlines summary fields
  (`transcript_found`, `transcript_valid`, `transcript_result`) into the
  inspection JSON for each work item.
- `grade_declared_work.py` consumes these enriched fields directly instead of
  requiring a separate validation pass.
- **Testable assertion:** If a work item declares `skill_id` but no transcript
  file is found in `evidence_paths_found`, the inspection output MUST set
  `transcript_found: false` and the grading output MUST contain
  `grade: OVERCLAIMED` with `violation: CSE-02`.

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

## GATE M-08: Transcript Evidence for src-Editing Items (REQUIRED) (R107 NEW)

- **What:** Any work item whose `evidence_paths` include files under `src/net/` or `src/python/` MUST also include at least one transcript file in `evidence_paths`.
- **Check:** `inspect_declared_evidence.py` scans `evidence_paths_found` for `src/` prefixes. When found, it verifies that at least one path matches `**/skill-transcripts/*.json`.
- **Validator:** Integrated into `inspect_declared_evidence.py` (Lane B wiring).
- **Failure:** OVERCLAIMED -- "Source-editing work item declared without transcript evidence."
- **Responsible:** Mainstream worker.

| Condition | Pass/Fail |
|-----------|-----------|
| Item has `src/` path + transcript path in evidence | PASS |
| Item has `src/` path but no transcript in evidence | FAIL (OVERCLAIMED) |
| Item has no `src/` path | N/A (gate does not apply) |

### Why This Gate Exists

R106 required `skill_id` (M-01) and transcript generation (M-05) as separate
gates, but did not require that the transcript be co-declared as evidence for
the same work item that touches source. This left a loophole: a worker could
declare `skill_id`, write a transcript for a different item, and pass both
gates independently. M-08 closes that loophole by requiring co-location of
transcript evidence and source evidence on the same work item.

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

---

## R107 Testable Enforcement Summary

| Gate | Testable Assertion | Validator File |
|------|--------------------|----------------|
| M-01 | `src/` path without `skill_id` => OVERCLAIMED | `grade_declared_work.py` |
| M-05 | `skill_id` without transcript => OVERCLAIMED | `grade_declared_work.py` via inspector enrichment |
| M-08 | `src/` path without co-located transcript => OVERCLAIMED | `inspect_declared_evidence.py` |

These assertions are testable via unit tests in `tests/supervisor/` (Lane F coverage).
