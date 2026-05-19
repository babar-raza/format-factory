# R30 Lane B: AI Synthesis Evaluator Defect Closure
# Date: 2026-05-19

## Defect
`tools/ai/synthesis/evaluator.py` line 96-98: `contradiction_check_status == "not_checked"` passed the contradiction gate when `require_no_contradictions=True`. This allowed artifacts that were never contradiction-checked to pass evaluation.

## Fix
Removed `"not_checked"` from the passing statuses. Only `"no_contradictions"` now passes.

Updated `tools/ai/pipeline/e2e_pilot.py` `stage_4_evaluate()` to set `require_no_contradictions=False` when contradiction checking was not performed (fixture mode).

Updated `tests/ai/test_r28_production_hardening.py` test helper default from `"not_checked"` to `"no_contradictions"`.

## Tests Added (Lane B in test_r30_ai_defect_closure.py)
- `test_not_checked_fails_when_contradictions_required` — core defect regression
- `test_no_contradictions_passes`
- `test_blocked_no_facts_fails`
- `test_contradictions_found_fails`
- `test_contradiction_not_required_ignores_status`
- `test_empty_status_fails`

## Status: CLOSED_VERIFIED
