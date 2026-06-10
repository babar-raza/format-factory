# Continuation Safety Gate
# Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-REPAIR-AND-ENFORCEMENT-001
# Run: spec-authority-stop-bleeding-repair-20260607-e382e5f
# Date: 2026-06-07

## Status: SPEC_AUTHORITY_ENFORCEMENT_ACTIVE

The spec_fact_refs BLOCKING enforcement gate is now active as of this sprint.

## What changed

| Component | Before this sprint | After this sprint |
|---|---|---|
| `validate_spec_fact_refs.py` | Did not exist | Created — enforces BLOCKING gate |
| `evidence_declaration.py` | No spec_fact_refs check | Wired: `_validate_spec_fact_refs()` in `validate_schema()` |
| `grade_declared_work.py` | No authority gate | Wired: rejects items with grade_impact=reject |
| `inspect_declared_evidence.py` | No `_raw_item` passthrough | Passes `_raw_item` to grader |
| `product_task_selector.py` | No authority gate | Checks `authority_status` from poc-targets.yaml |
| Gnumeric bypass ledger | `no_public_spec_available` (wrong) | `schema_authority_available` (correct) |
| Test coverage | 0 enforcement tests | 25 tests (20 enforcement + 5 selector) |

## Safe continuation conditions

The autonomous train MAY continue to mainstream product work ONLY when:
1. `autonomous-cycle exit 0` on the enforcement sprint (this sprint)
2. All 25 enforcement tests pass
3. `advisory_prompt_executable: false` remains (current state — correct)
4. No OVERCLAIMED or REJECTED items in this sprint
5. Next sprint does NOT advance Gate 11 or publish packages

## Current advisory_prompt_executable

`advisory_prompt_executable: false` — machine-action queue is NOT safe for unsupervised execution.
This is the correct state. Do NOT set to true without human review.

## Next sprint recommendation

Priority order for next sprint:
1. Verify enforcement is wired end-to-end by running supervisor cycle with a test declaration
   that has PRODUCT_SOURCE + no spec_fact_refs + no exception → must be REJECTED
2. Backfill FACT-xxx annotations in src/ for existing product code (TCA-016)
3. Add SPEC-FACT: citations to test files (TCA-017)
4. Verify remaining 9 facts in verified-facts-review.yaml

NOT recommended before above:
- Gate 11 advancement
- New product format acquisitions
- Package publication
