# Lane G — Downstream Layers Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-G | **Requirement:** REQ-LANE-G

## 1. Advisory Template Generation — Root Cause Trace

### _load_gap_ledger_goals() — autonomous_task_generator.py lines 1401-1478
- **Primary source:** gap-ledger.json (reads directly)
- **Fallback:** hardcoded _EXPANSION_GOALS (only if gap-ledger reading fails)
- **Does NOT call:** capability_compiler.py
- **Does NOT read:** selected-product-gaps.json

### Work Queue Generation Path
```
autonomous_task_generator.py
  ├─ _load_gap_ledger_goals() → reads gap-ledger.json directly
  │   └─ Returns gap-based goals with gap_ledger_ref
  ├─ generate_next_work_items() → creates work items
  │   └─ When in PLAN_LOCKED mode → returns advisory templates
  └─ Output: .local/supervisor/next-work-items.json
```

### Key Finding: PLAN_LOCKED Mode
When a per-chat plan is active, `generate_next_work_items()` returns items in PLAN_LOCKED mode rather than gap-based items. The 12-of-15 advisory template items observed in the preflight state were NOT caused by missing gap selection — they were caused by the plan lock mechanism suppressing gap-based generation.

### Without Plan Lock
When no plan is locked, `_load_gap_ledger_goals()` DOES read gap-ledger directly and produces gap-referenced goals. However:
- No priority scoring is applied (all open gaps equally eligible)
- No format diversity enforcement (could select 10 gaps from same format)
- No capability_compiler integration (scoring, IR generation not used)
- This is the actual symptom of RC-1/RC-2: the selection is UNSCORED, not EMPTY

## 2. Advisory Template Trigger Condition
**Exact condition:** Advisory templates appear when:
1. Plan lock is active (PLAN_LOCKED mode), OR
2. selected-product-gaps.json is empty AND gap-ledger read fails, OR
3. _EXPANSION_GOALS fallback is used (hardcoded format list)

In normal operation (no plan lock, gap-ledger readable), work items DO have gap_ledger_ref. The inconsistency comes from UNSCORED selection, not absent selection.

## 3. Product Code Change Ledger
- **File:** reports/r90/product-code-change-ledger.json
- Recent entries show gap-driven work with gap_ledger_ref present
- Skills used: add-python-api, add-dotnet-api, add-python-object-model-feature
- Pattern: gap-referenced entries are correctly traced when they reach the ledger

## 4. Brittleness Point
The work queue degrades from SPECIFIC to GENERIC when:
- capability_compiler scoring is NOT applied before task generation
- All 99 open gaps compete equally without priority/impact/format-diversity filtering
- The LLM interprets "work on NDJSON" differently each run because no specific gap is referenced

**Fix:** Wire capability_compiler scoring → selected-product-gaps.json → autonomous_task_generator.py (TC-MACH-CAP-001 + TC-MACH-CAP-002)
