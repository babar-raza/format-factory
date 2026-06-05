# Self-Review Repair Plan — Supervisor Product-First Sprint
# Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Context
Three gaps identified in Phase 1 self-review requiring remediation:
1. Import path bug in `ai_supervisor_advisor.py` (absolute import fails when module loaded via sys.path)
2. Missing test coverage for `review_semantic_drift()`, `compute_product_output_floor()`, `PARTIAL_HELPER_ONLY`, `PARTIAL_NO_GOVERNED_TRANSCRIPTS`, `PARTIAL_NO_DOGFOOD`
3. Declaration items TC-CLOSE-003 and TC-CLOSE-004 left as `not_started` despite work being done

## Gap Table

| Gap ID | Description | Taskcard |
|--------|-------------|----------|
| GAP-01 | Absolute import `tools.supervisor.product_velocity_scorer` in `ai_supervisor_advisor.py` fails when module loaded from sys.path | SR-01 |
| GAP-02 | Missing test coverage for 5 untested code paths | SR-02 |
| GAP-03 | TC-CLOSE-003/TC-CLOSE-004 `not_started` in declaration despite autonomous-cycle having been run | SR-03 |

---

## SR-01 — Fix absolute import in ai_supervisor_advisor.py
**Status:** Done
**Gap:** GAP-01
**Role:** Senior engineer
**Scope:**
- Fix: `tools/supervisor/ai_supervisor_advisor.py` lines ~100-102
- Allowed paths: `tools/supervisor/ai_supervisor_advisor.py` only
- Forbidden: all other files

**Problem:** Line 100 reads:
```python
from tools.supervisor.product_velocity_scorer import (
    score_machinery_overhead, compute_product_output_floor
)
```
This works when CWD is repo root but fails when `tools/supervisor/` is on `sys.path` (as tests do).

**Fix:** Use a relative import pattern that works in both contexts:
```python
try:
    from product_velocity_scorer import score_machinery_overhead, compute_product_output_floor
except ImportError:
    from tools.supervisor.product_velocity_scorer import score_machinery_overhead, compute_product_output_floor
```

**Acceptance checks:**
```
# Must pass from repo root
python -c "import sys; sys.path.insert(0,'tools/supervisor'); from ai_supervisor_advisor import review_semantic_drift; r=review_semantic_drift('mainstream',{}); assert r['non_authoritative'] is True; print('PASS')"
# Must pass via direct import too
python -c "from tools.supervisor.ai_supervisor_advisor import review_semantic_drift; r=review_semantic_drift('supervisor',{}); assert r['non_authoritative'] is True; print('PASS')"
```

**Deliverables:** Fixed import in `ai_supervisor_advisor.py`; both import paths work.

**Hard rules:** Keep all existing public function signatures. No new dependencies.

---

## SR-02 — Add missing test coverage
**Status:** Done
**Gap:** GAP-02
**Role:** Senior engineer
**Scope:**
- Fix: `tests/supervisor/test_supervisor_product_first_traffic_controller.py` — add tests to existing classes
- Allowed: that test file only
- Forbidden: modifying any other test file or source file

**Missing tests:**
1. `review_semantic_drift()` returns `non_authoritative: True` (exercises SR-01 fix)
2. `compute_product_output_floor()` returns True when `families_touched > 0`
3. `classify_mainstream_package()` → `PARTIAL_HELPER_ONLY` (high overhead + no product actions)
4. `classify_mainstream_package()` → `PARTIAL_NO_GOVERNED_TRANSCRIPTS` (families≥3, diffs≥3, 0 transcripts)
5. `classify_mainstream_package()` → `PARTIAL_NO_DOGFOOD` (families≥3, diffs≥3, transcripts≥1, 0 matrix deltas)

**Acceptance checks:**
```
python -m pytest tests/supervisor/test_supervisor_product_first_traffic_controller.py -v
# Must show >= 28 PASSED (23 original + 5 new)
```

**Deliverables:** 5 new test methods in existing test classes; all pass.

---

## SR-03 — Update declaration status for TC-CLOSE-003 and TC-CLOSE-004
**Status:** Done
**Gap:** GAP-03
**Role:** Senior engineer
**Scope:**
- Fix: `.local/evidences/supervisor-product-first/evidence-declaration.yaml`
- Also update: `completed_work_items` list and `incomplete_work_items` list
- Allowed: that YAML file only

**Problem:** TC-CLOSE-003 (CLI discovery + autonomous-cycle run) and TC-CLOSE-004 (build review package + SHA-256) were completed in the sprint but left as `not_started` in the declaration. The autonomous-cycle ran (exit 0) and the review package was built (SHA `f927ebbd...`). These should be `completed`.

**Fix:** Change `status: not_started` to `status: completed` for both; add `zip_export_path` and delivery info; move from `incomplete_work_items` to `completed_work_items`; re-run autonomous-cycle and rebuild review package.

**Acceptance checks:**
```
python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/supervisor-product-first/evidence-declaration.yaml
# Exit 0
python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/supervisor-product-first/evidence-declaration.yaml
# BUILD: SUCCESS
```

**Deliverables:** Updated declaration with all items completed; new review package ZIP with updated SHA.
