# Prompt and Handoff Guardrails — .NET Dogfood Architecture Gaps

**Sprint:** FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
**Lane:** G — Prompt and Handoff Guardrails
**Date:** 2026-06-05
**Status:** ENFORCED

---

## Export Target Support Policy

A product may not claim export support unless the Format Factory system owns a reusable target
writer library for that format and runtime.

Specifically:

- A .NET dogfood export from format A to format B requires a `format-factory-<B>-dotnet` library
  that is built, tested, and registered in the FF format registry.
- The existence of a parser for format A does NOT imply the existence of a writer for format B.
- The fact that a Python FOSS writer exists for format B does NOT grant .NET dogfood export
  capability for format B.
- Each target format (CSV, HTML, Markdown, TXT, etc.) in each runtime (.NET, Python) requires
  its own independently governed writer library.

This policy prevents phantom export claims where an agent asserts "FODS exports to CSV" when
no `format-factory-csv-dotnet` writer library has been built.

---

## Guardrail Rule

```
IF gap.classification == GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED
THEN
  DO NOT assign /add-dogfood-export to this gap
  DO NOT generate a G5 dogfood train for this gap
  ROUTE TO architecture-decision lane
  RECORD in blocked-dogfood-gap-ledger.json
  DEFER to future sprint: CREATE-DOTNET-<FORMAT>-WRITER-001
```

This rule applies regardless of whether the gap appears in:
- next-sprint.md
- a generated mega-train prompt (G5 section)
- a gap extraction fixture
- any agent's working plan

---

## Implementation Pattern: BLOCKED_ARCHITECTURE_GAPS Frozenset

The canonical frozenset of blocked gap IDs is:

```python
BLOCKED_ARCHITECTURE_GAPS: frozenset = frozenset({
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet",
})
```

Each ID maps to a specific format-runtime pair with no corresponding FF writer library:

| Gap ID | Missing Library |
|--------|----------------|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | format-factory-csv-dotnet |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | format-factory-html-dotnet |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | format-factory-markdown-dotnet |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | format-factory-txt-dotnet |

When a future sprint creates one of these writer libraries and registers it in the FF format
registry, the corresponding gap ID MUST be removed from this frozenset and re-evaluated.

---

## Where This Is Now Enforced

### 1. select_poc_gaps.py — BLOCKED_GAP_IDS

`tools/supervisor/select_poc_gaps.py` contains a `BLOCKED_GAP_IDS` set that prevents these
gaps from being selected as actionable product work during gap selection. Gaps with IDs in
`BLOCKED_GAP_IDS` are classified as `GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED` and excluded
from the selected-product-gaps output.

**File:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\supervisor\select_poc_gaps.py`

### 2. next-sprint.md — Patched

`reports/supervisor/next-sprint.md` TASK-009, TASK-010, TASK-011, TASK-012 have been replaced
with `[architecture_blocked]` entries. Each entry:
- Tags the task as `[architecture_blocked]` (parseable status tag)
- States `[ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]` (human-readable)
- Names the root cause (missing writer library)
- Cites the decision record for traceability
- Points to actionable-gap-replacement-candidates.json for alternative work
- Proposes a candidate future sprint ID

**File:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\reports\supervisor\next-sprint.md`

### 3. generate_next_worker_prompt.py — IMPLEMENTED

`tools/supervisor/generate_next_worker_prompt.py` now contains the `BLOCKED_ARCHITECTURE_GAPS`
frozenset and filters it in the G5 dogfood train synthesis section (`synthesize_trains()`).
The filter checks `g.get("id", g.get("gap_id", ""))` against the frozenset before adding
a gap to `actionable_dogfood`.

This means even if a fixture file contains these gap IDs with a non-HOLD sprint suggestion,
the prompt generator will not emit a G5 train for them.

**File:** `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\supervisor\generate_next_worker_prompt.py`
**py_compile:** PASS (exit 0)

---

## Decision Traceability

- Decision record: `reports/dotnet-dogfood-architecture-gap/architecture-gap-decision-record.md`
- Blocked gap ledger: `reports/dotnet-dogfood-architecture-gap/blocked-dogfood-gap-ledger.json`
- Reroute rules: `reports/dotnet-dogfood-architecture-gap/selected-gap-reroute-rules.md`
- Alternative candidates: `reports/dotnet-dogfood-architecture-gap/actionable-gap-replacement-candidates.json`
- This file: `reports/dotnet-dogfood-architecture-gap/prompt-handoff-guardrails.md`
- Handoff patch: `reports/dotnet-dogfood-architecture-gap/mainstream-handoff-patch.md`
