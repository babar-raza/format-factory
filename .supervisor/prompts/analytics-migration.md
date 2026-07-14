---
espanso_provenance:
  source_trigger: ":ff-inventory-analytics"
  source_block: 55
  source_line_range: [73279, 73288]
  gap_id: GAP-ESP-011
  extraction_date: "2026-07-12"
  capability_id: null
prompt_id: ESP-PROMPT-11
title: "Analytics Migration (Monolith Extraction)"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Analytics Migration (Monolith Extraction)

Governed protocol for extracting analytics functions out of monolithic codec files.
Synthesized from Espanso entries: `:ff-inventory-analytics`, `:ff-decide-analytics-migrations`,
`:ff-migrate-analytics-batches`, `:ff-verify-no-analytics`, `:ff-remove-analytics-safely`.

## When to Use

- Governance validator `GOV_BLOCK:monolith_detection_validator` or
  `GOV_BLOCK:validate_analytics_naming_enforced` is firing in `rework_items`
- A format's main codec file has analytics functions co-located (LOC > 800 or fn > 60)
- Sprint executor validate Phase 0 detects a NEW analytics violation

## When NOT to Use

- The format already has a separate `{format}_analytics.py` file (check first)
- The analytics functions are spec-required non-separable behavior
- The format has no existing product source

## Prerequisites

- Read `docs/code-quality/production-library-standard-v2.md` §8.1 (Analytics Separation Protocol)
- Confirm the format's codec file LOC and function count via `/check-source-loc`
- Confirm `GOV_BLOCK` is in `rework_items` from `check_continuation.py`

## Allowed Paths

- `src/python/{format}/{format}_analytics.py` (create)
- `src/python/{format}/{format}_file_analytics.py` (create — if ext2 naming applies)
- `src/python/{format}/{format}_codec.py` or main module (edit — removal only)
- `src/python/{format}/__init__.py` (update exports)
- `tests/{format}/test_{format}_analytics.py` (create)

## Forbidden Paths

- `src/net/` (not in scope)
- `registry/source-structure-baseline.json` `baseline_loc_cap` fields (write-once)

## Protocol (5-Step Analytics Migration)

**Step 1 — Inventory**
- List all analytics functions in the target file: `grep -n "def.*analytic\|def.*stat\|def.*count\|def.*histogram" src/python/{format}/`
- Record function names, line numbers, dependency graph

**Step 2 — Decide**
- Classify each function: MIGRATE (analytics-only, no state side-effects) or KEEP (tightly coupled)
- Write migration decision to a temp file before touching src/

**Step 3 — Migrate in Batches**
- Create `{format}_analytics.py` (or `{format}_file_analytics.py`) with moved functions
- Update `__init__.py` exports to re-export from new module
- Add import in old file where callers exist (import-only, not re-implementation)

**Step 4 — Verify Zero Analytics in Codec**
- Confirm no analytics functions remain in the codec file
- Run: `.venv/Scripts/pytest tests/{format}/ -v` — all tests must pass

**Step 5 — Remove Safely**
- Remove the import shim from Step 3 if callers have been updated
- Run governance validators: `python tools/supervisor/governance_validator_runner.py` → exit 0
- Confirm GOV_BLOCK is resolved: `check_continuation.py` no longer returns structural_govblock

## Evidence Filing (EP-5)

Declare one `planned_work_items` entry per format migrated.
Include test evidence showing the analytics file exists and tests pass.

## Completion Gate

- `{format}_analytics.py` exists with migrated functions
- `governance_validator_runner.py` → exit 0 (no GOV_BLOCK)
- `check_continuation.py` does not return `structural_govblock_must_be_resolved_first`
- All existing tests for the format still pass
