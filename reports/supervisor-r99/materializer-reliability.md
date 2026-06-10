# Train C: Materializer Reliability

## Problem
The materializer (`materialize_declared_evidence.py`) was not invoked by `autonomous_cycle.py`. It ran only as a manual step, meaning the standard loop lacked:
- SHA-256 verification of declared artifacts
- Git diff capture for src/ changes
- Missing evidence report generation
- Source snapshots for declared changes

## Fix (R99)
Added Step 2c to `autonomous_cycle.py` that calls `materialize()` between evidence inspection (Step 2b) and grading (Step 3).

## Verification Depth
The materializer now verifies:
1. **Declared evidence paths exist** — each `evidence_paths` entry in work items
2. **Changed files exist** — each file in `changed_files` list
3. **Source diffs captured** — git diff for `src/*` changes (working tree, staged, or last commit)
4. **SHA-256 computed** — for every verified artifact
5. **Ledger snapshot captured** — product-code-change-ledger.json
6. **POC matrix snapshot captured** — poc-targets.yaml (truncated to 2000 chars)
7. **Missing paths produce item-level grades** — missing evidence maps to INSUFFICIENT_EVIDENCE

## Edge Cases Handled
- File declared but deleted before materialization → recorded in missing list
- Binary files → SHA-256 works but no diff available
- Files in .local/ (non-tracked) → SHA-256 only, no git diff
- Absolute vs relative paths → resolved against repo_root

## Output Artifacts
- `materialized-evidence-manifest.yaml` — full verification results
- `missing-evidence-report.md` — human-readable list of missing artifacts
- `source-change-diffs.patch` — concatenated git diffs
- `reports/supervisor/materialized-evidence-review.md` — summary with per-item grades
