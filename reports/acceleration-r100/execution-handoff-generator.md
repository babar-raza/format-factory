# Execution Handoff Generator — Train D

## New Tool
`tools/supervisor/generate_execution_handoff.py`

## Functions
- `generate_handoff(gap, sprint_id)` — structured handoff for one gap
- `generate_handoffs_for_gaps(gaps, sprint_id)` — filter + generate for HANDOFF/PLAN_HARDENING decisions
- `write_handoffs(gaps_path, output_dir, sprint_id)` — CLI entry: load gaps, write YAML handoffs

## Handoff Fields
- `allowed_files` / `forbidden_files` — track-aware file constraints
- `tests_required` — work-type-aware test requirements
- `rollback` — git checkout command
- `evidence_outputs` — expected report + declaration paths
- `ledger_requirements` — lane recorder instructions
- `capability_matrix_update` — poc-targets.yaml path + expected transition
- `safety_gates` — 5 default safety constraints

## Tests
9 tests in `test_generate_execution_handoff.py`
