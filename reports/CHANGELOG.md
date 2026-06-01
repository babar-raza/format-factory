# Changelog — Declaration-Driven Pipeline Production Integration

Date: 2026-06-01

## Changes

### tools/supervisor/autonomous_cycle.py
- Added `bridge_to_legacy_format()` function (Step 7 in cycle)
- Writes `evidence-review.json` + `contradictions.json` to `reports/supervisor/`
- Maps cycle review grades/counts to legacy JSON format

### tools/supervisor/supervisor_loop.py
- `cmd_autonomous_cycle()` now calls `cmd_next()` after cycle completes (exit 0 or 3)
- `cmd_run_on_latest()` prints deprecation warning to stderr

### tools/supervisor/evidence_declaration.py
- Added `_validate_jsonschema()` — optional runtime schema validation
- Called at top of `validate_schema()` before field-level checks

### tools/supervisor/discover_latest_evidence.py
- `main()` prints deprecation warning to stderr

### tools/supervisor/watch_for_bundle.py
- `main()` prints deprecation warning to stderr

### plans/master-plan.md
- Section 40.5 updated: `autonomous-cycle --declaration` replaces `run-on-latest --bundle`
- Section 41 added: Declaration-driven supervisor pipeline documentation

### .local/evidences/r86-real-sprint-validation/
- Created R86 evidence declaration for real-sprint validation
- Autonomous-cycle graded 7 items ACCEPTED, exit 0
- session-resume.md regenerated with R86 sprint data

## Test Commands
```bash
# Run all supervisor tests
.local/venv/Scripts/python -m pytest tests/supervisor/ -v --tb=short

# Run autonomous-cycle E2E
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/r86-real-sprint-validation/evidence-declaration.yaml

# Verify deprecation warning
.local/venv/Scripts/python tools/supervisor/discover_latest_evidence.py --json 2>&1 | head -3
```
