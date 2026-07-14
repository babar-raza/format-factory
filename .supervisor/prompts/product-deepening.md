---
espanso_provenance:
  source_trigger: ":ff-two-lane-product-deepening"
  source_block: 32
  source_line_range: [37612, 39764]
  gap_id: GAP-ESP-009
  extraction_date: "2026-07-12"
  capability_id: null
prompt_id: ESP-PROMPT-9
title: "Product Deepening (Two-Lane)"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Product Deepening (Two-Lane)

Canonical protocol for format deepening work using the two-lane discipline.
Synthesized from Espanso entries: `:ff-two-lane-product-deepening`,
`:ff-product-deepening-train`, `:ff-resume-product-deepening`.

## When to Use

- Next sprint is a product deepening sprint (per `next-sprint.md` or `next-work-items.json`)
- No per-chat plan is currently active (per CLAUDE.md plan precedence rule)
- Autonomous continuation signal returns CONTINUE

## When NOT to Use

- A per-chat plan is active — execute the plan instead
- Machinery has GOV_BLOCK items in `rework_items` — resolve those first
- Oracle is NOT VERIFIED or CASES_DEFINED for the target format (EP-4 machinery readiness)
- Governance validators are failing for the target format

## Prerequisites (EP-4 Machinery Readiness Check)

Before selecting a format for deepening:
1. Oracle status for format: must be `VERIFIED` or `CASES_DEFINED`
2. The skill to be invoked exists in `.supervisor/skill-registry.yaml`
3. SAL fact count > 0 for the format (check `reports/sal-qname-gap-*.json`)
4. Governance validators pass: `python tools/supervisor/governance_validator_runner.py` → exit 0

If any check fails: fix the machinery defect first, then resume deepening.

## Two-Lane Discipline

**Lane A — Feature Deepening** (new format APIs, methods, analytics):
- Invoke `/format-feature-expansion` skill
- Or `/add-python-api` for specific method additions
- Evidence: new functions with tests; `test_layer: 1`

**Lane B — DOM Deepening** (object model completeness):
- Invoke `/select-deepening-lane` to classify format as FULL_DOM, PARTIAL_DOM, or FLAT
- Use `/add-python-object-model-feature` for model additions
- Evidence: spec_qname fields populated; DOM validator passes

Do not mix lane A and lane B work in a single sprint declaration.

## Autonomous Continuation

After each sprint:
1. Run sprint closeout (evidence declaration → autonomous-cycle → check_continuation.py)
2. If `check_continuation.py` → CONTINUE: read `next-sprint.md` and execute the next format
3. If GOV_BLOCK items in `rework_items`: resolve before continuing (CLAUDE.md §GOV_BLOCK Exception)
4. Max iterations is not a stop — reset and continue (CLAUDE.md §Max Iterations)

## Evidence Filing (EP-5 Per-Work-Item Grading)

Declare one `planned_work_items` entry per format per lane per sprint.
Do NOT declare one entry for an entire sprint across multiple formats.

## Forbidden Actions

- Do not use direction-reminder Espanso entries as protocols
- Do not skip lane selection before deepening
- Do not produce product code without first invoking a governed skill (EP-3)
- Do not commit stubs or `raise NotImplementedError()` in product src/ (EP-1)

## Completion Gate

- Evidence declaration filed with per-item entries
- `autonomous_cycle.py` exits 0 or 3 (non-blocking)
- `check_continuation.py` returns CONTINUE for next format
