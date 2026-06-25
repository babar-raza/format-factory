# /check-source-loc

**Mission:** ALLFORMAT-DEEPENING-20260625
**Skill ID:** check-source-loc
**Product Track:** source_structure
**Idempotency:** Read-only audit; safe to re-run at any time.

## Purpose

Checks the LOC (lines of code) of Python format source files against `registry/source-structure-baseline.json` caps. Reports any files exceeding their `baseline_loc_cap`. Never modifies the baseline.

## Steps

1. Read `registry/source-structure-baseline.json` — load `known_violations` dict (keyed by relative file path)
2. For each Python format in scope, identify primary source files:
   - `src/python/{format}/{format}_parser.py`
   - `src/python/{format}/{format}_codec.py`
   - `src/python/{format}/__init__.py`
   - Any other .py files in the format directory
3. Count LOC using V35's exact method:
   ```python
   loc = sum(1 for _ in open(path, encoding='utf-8', errors='replace'))
   ```
4. Compare against `baseline_loc_cap` from `known_violations` (if present)
5. For files NOT in `known_violations`: compare against standard caps (800 LOC, 60 functions)
6. Report findings

## Output Format

```
CHECK-SOURCE-LOC REPORT — {timestamp}
Format: {format}
  {relative_path}: {loc} LOC / cap={baseline_loc_cap} → {OK | VIOLATION: {excess} lines over cap}

SUMMARY:
  Formats checked: {count}
  Violations found: {count}
  Violations:
    - {path}: {loc}/{cap} ({excess} over)
```

## Rules

- **NEVER modify `baseline_loc_cap`** — it is write-once, frozen at time of initial healing
- **Only `loc` is mutable** in the baseline (after actual healing occurs via `/extract-analytics-from-monolith`)
- Files below cap: no action needed — log OK
- Files above cap: log VIOLATION; create rework item for LANE-F (TC-E-002)

## What to Do With Violations

If a file exceeds its cap:
1. Check if the analytics rotation suspension applies — if `{format}_analytics.py` already exists AND the cap was set AFTER analytics extraction, the violation is legitimate debt
2. If new code was added beyond the cap: apply `/extract-analytics-from-monolith` pattern
3. If cap itself needs updating (after healing): use `python tools/supervisor/update_source_baseline.py --path {file}` — this updates ONLY the `loc` field, never `baseline_loc_cap`

## Known Safe Files (pre-confirmed below cap)

- `src/python/xcf/xcf_parser.py`: 288 LOC — well under cap (confirmed 2026-06-25)
