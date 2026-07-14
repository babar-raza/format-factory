---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
created-by: TC-EXT-010-01
invocation_mode: automatic_pipeline
product_track: governance
loc_budget: "registration only, no new detection logic"
---

# /pre-sprint-governance-hook

Documents (does **not** reimplement) the existing structural GOV_BLOCK carve-out that
already runs automatically at the start of every continuation check. This command
file exists so the carve-out has a formal, registered skill identity (skill_id,
routing entry, registry presence) instead of living only as undocumented inline
logic inside `check_continuation.py`.

## What This Skill Does

1. Documents the structural GOV_BLOCK carve-out already implemented by
   `check_continuation.py`'s "Check 8" (TC-GOVBLK-001) — it reads `rework_items`
   from the continuation signal and calls `governance_block_registry.py`'s
   `filter_structural_blocks()`.
2. Gives that carve-out a registered `skill_id` (`pre-sprint-governance-hook`)
   so `work-type-skill-map.yaml` can route the `pre_sprint_governance_hook`
   work type to a real, governed skill instead of reporting
   `BLOCKED_SKILL_GAP`.
3. Points the two consumer actuators — `sprint_executor.py`'s
   `_is_structural_govblock_stop()` and `.claude/commands/autonomous-loop.md`'s
   Step 1 NON-OVERRIDABLE STOP-reason list — back at this one canonical skill
   identity.
4. Does **not** add, remove, or change any entry in `STRUCTURAL_GOV_BLOCKS`,
   and does **not** change when or how Check 8 fires — registration only.

## Invocation Mode (IMPORTANT)

This is a **pipeline tool, not a user-invoked slash command**. It has no interactive
workflow of its own — the detection it documents runs automatically, every time
`tools/supervisor/check_continuation.py` is invoked (Check 8), for every sprint,
via both the headless (`sprint_executor.py run-loop`) and interactive
(`/autonomous-loop`) execution paths.

Do not invoke `/pre-sprint-governance-hook` as a manual first step. If you need to
inspect the underlying detection directly for diagnostics, use the CLI forms below.

## Purpose

Give `check_continuation.py`'s "Check 8" structural GOV_BLOCK carve-out — and its
underlying data source, `tools/supervisor/governance_block_registry.py` — a
registered skill identity so:

- `check-skill-coverage` / `work-type-skill-map.yaml` can route the
  `pre_sprint_governance_hook` work type to a real skill instead of reporting
  `BLOCKED_SKILL_GAP`.
- The EP-3 Skill-Driven Architecture rule (CLAUDE.md) is satisfied for this
  governance gate: it is now a documented, registered skill, not undocumented
  inline logic.
- The two actuators that consume this signal (`sprint_executor.py`'s
  `_is_external_gate()` and `.claude/commands/autonomous-loop.md`'s Step 1
  STOP-reason table) have one canonical skill to point back to.

## Underlying Implementation (read-only reference — do not modify detection logic)

- `tools/supervisor/check_continuation.py` — "Check 8" (`# --- Check 8
  (TC-GOVBLK-001): Structural GOV_BLOCK carve-out ---`). Reads `rework_items` from
  the continuation signal, calls `filter_structural_blocks()`, and returns
  `verdict=STOP, reason=structural_govblock_must_be_resolved_first` when any
  structural block is present (unless `govblock_resolved_by` is set on the signal).
- `tools/supervisor/governance_block_registry.py` — canonical
  `STRUCTURAL_GOV_BLOCKS` frozenset (6 entries as of TC-EXT-010:
  `GOV_BLOCK:monolith_detection_validator`, `GOV_BLOCK:validate_source_architecture`,
  `GOV_BLOCK:validate_multi_responsibility_file`,
  `GOV_BLOCK:validate_analytics_naming_enforced`, `GOV_BLOCK:validate_source_stubs`,
  `GOV_BLOCK:validate_promoted_code_changed_without_reopening`) plus
  `is_structural_block()` / `filter_structural_blocks()` helpers.

This command file does **not** change either module. It is a registration wrapper
only — see TC-EXT-010's scope note: "governance_block_registry.py (read-only
reference, no logic change needed)".

## CLI Usage (diagnostic / direct invocation only)

```bash
python tools/supervisor/check_continuation.py --repo-root . --track product
# → verdict=STOP, reason=structural_govblock_must_be_resolved_first when a
#   structural GOV_BLOCK is present in rework_items

python -c "
from tools.supervisor.governance_block_registry import filter_structural_blocks
print(filter_structural_blocks(['GOV_BLOCK:monolith_detection_validator', 'other_item']))
"
```

## Consumers (must recognize `structural_govblock_must_be_resolved_first` as non-overridable)

- `tools/supervisor/sprint_executor.py` (`_TRUE_EXTERNAL_GATES` /
  `_is_external_gate()` — TC-EXT-010-02)
- `.claude/commands/autonomous-loop.md` Step 1 NON-OVERRIDABLE STOP-reason list
  (TC-EXT-010-03)

## Allowed Paths

- `.claude/commands/pre-sprint-governance-hook.md` (this file — registration only)
- `.supervisor/skill-registry.yaml` (registration entry)

## Forbidden Paths

- `tools/supervisor/check_continuation.py` — existing Check 8 detection logic,
  already correct, do not modify
- `tools/supervisor/governance_block_registry.py` — read-only reference, no logic
  change needed

## Stop Conditions

- Stop if `STRUCTURAL_GOV_BLOCKS` cannot be imported from
  `governance_block_registry.py` (indicates the registry module moved or was
  deleted — escalate, do not silently skip the carve-out)

## Output Format

`check_continuation.py` prints its normal JSON verdict object
(`{"verdict": "STOP", "reason": "structural_govblock_must_be_resolved_first", ...}`)
to stdout; this command file adds no new output of its own.
