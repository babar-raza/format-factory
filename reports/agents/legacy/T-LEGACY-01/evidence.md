# T-LEGACY-01 Evidence

## What was done
Added deprecation warnings to 3 legacy entry points:
1. `tools/supervisor/discover_latest_evidence.py::main()` — prints to stderr
2. `tools/supervisor/watch_for_bundle.py::main()` — prints to stderr
3. `tools/supervisor/supervisor_loop.py::cmd_run_on_latest()` — prints to stderr

## Evidence
- Warnings print: "WARNING: <tool> is legacy. Use 'supervisor_loop.py autonomous-cycle --declaration <path>' instead."
- Old behavior unchanged (warnings only, no functional change)
- Tests: 84/84 passing
