---
version: "1.0"
last-updated: "2026-06-23"
phase-available: "all"
gate-required: null
created-by: TC-SKILL-HARDENING-001
spec_qname_required: "false"
overflow_split_allowed: "false"
product_track: "foss_python_analytics"
---

# /extract-analytics-from-monolith

## Step 0 — Execution Manifest (run BEFORE any other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill extract-analytics-from-monolith \
  --allowed-paths src/python/<format_id>/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for `src/python/`.

## Purpose

Extract arithmetic/analytics functions from a monolithic codec or parser file into a
dedicated `{format}_analytics.py`. Resolves `GOV_BLOCK:monolith_detection_validator`.

## When to Use

Use this skill when `source_structure_validator.py` reports:
- `worsened_violations > 0` for a codec/parser file
- A file exceeds its `baseline_loc_cap` in `registry/source-structure-baseline.json`
- `monolith_detection_validator` fires on a product source file

## Pattern (from MEMORY.md)

1. **Read the target monolith file** — identify all arithmetic/analytics functions
   (functions that compute numeric metrics, counts, averages, ratios over the format's data)

2. **Read or create `{format}_analytics.py`** — check what's already there

3. **Move analytics functions** from `{format}_codec.py` (or `{format}_parser.py`) to `{format}_analytics.py`
   - Keep ONLY load/write/parse core functions in the main codec
   - Analytics: any `def {format}_*_count`, `*_density`, `*_ratio`, `*_sum`, `*_average`, etc.

4. **Wire re-export at bottom of `{format}_analytics.py`**:
   ```python
   from .{format}_codec import (
       load_{format},
       # ... other base functions analytics.py depends on
   )
   ```

5. **Wire re-export at bottom of `{format}_codec.py`**:
   ```python
   try:
       from .{format}_analytics import *
   except ImportError:
       pass
   ```

6. **Update `__init__.py`** if any moved functions are not yet in the import list

7. **Run tests**: `.venv/Scripts/pytest tests/python/{format}/ -x -q`

8. **Run source validator**: `python tools/validators/source_structure_validator.py`
   - Verify: `worsened=0, blocks_sprint=False`

9. **Update baseline** if `{format}_analytics.py` is a new file exceeding 800 LOC:
   ```
   python tools/supervisor/update_source_baseline.py --path src/python/{format}/{format}_analytics.py
   ```

## Allowed Paths

- `src/python/{format}/{format}_codec.py`
- `src/python/{format}/{format}_parser.py`
- `src/python/{format}/{format}_analytics.py`
- `src/python/{format}/__init__.py`

## Forbidden Paths

- `tools/supervisor/` — no validator changes during this skill
- `tests/` — do not delete tests during extraction
- Any file in a different format's directory

## Required Evidence

- Before/after LOC for the monolith file
- `source_structure_validator.py` output showing `blocks_sprint=False`
- Test suite pass count (must match pre-extraction count)

## Declaration Fields

```yaml
skill_used: extract-analytics-from-monolith
lane_crossing_authorized: false
gap_ledger_ref: <GOV_BLOCK gap ID from gap-ledger.json>
```

## Required Inputs

- `format_id` — format identifier from the format registry
- `source_file` — value for `source_file`
- `analytics_target_file` — value for `analytics_target_file`
- `functions_to_move` — value for `functions_to_move`

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
