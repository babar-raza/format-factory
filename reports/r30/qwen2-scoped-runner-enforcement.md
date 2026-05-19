# R30 Lane E: Qwen2 Scoped Runner Enforcement
# Date: 2026-05-19

## Defect
`tools/ai/agentic/scoped_runner.py`: `max_files` field existed in `AgenticTaskContract` but was never enforced in `ScopedRunner.run()`. A task could access unlimited files.

## Fix
Added `max_files` enforcement before path validation. If `len(files_accessed) > contract.max_files`, the result is `scope_violation` with `discarded=True`.

Also improved path validation: allowlist entries are resolved against `repo_root` to prevent relative-path traversal bypasses.

## Tests Added (Lane E in test_r30_ai_defect_closure.py)
- `test_max_files_exceeded_discards_output` — 3 files with max_files=2
- `test_max_files_within_limit_passes` — 2 files with max_files=5
- `test_forbidden_operation_rejected` — commit in operation_allowlist
- `test_model_restriction` — gpt-4 rejected, qwen only

## Status: CLOSED_VERIFIED
