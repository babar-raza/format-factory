# R65 State/Invariant Repair

## Root Cause
check_repo_invariants.py:250 — INV-003 tried `root / entry` where entry is a dict (`{path: "..."}`) from R64 contract's required_repo_files.

## Fix
Added `_resolve_path(entry)` helper at line 249 that handles both dict and string entries:
- dict → entry.get("path", "")
- string → str(entry)

## Regression Test
Invariant tests: 6/6 PASS after fix (previously 2 FAILED)

## State Update
- state/current-state.md: physical_invariant_check_error marked REPAIRED_R65
- blockers-status.txt will agree with state (no contradictions)

STATE_INVARIANT_REPAIR_STATUS: COMPLETE
