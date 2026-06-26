# Plan Hardening Output — SAL-VHIP-001 Closure Actions
# Date: 2026-06-25 | Mode: closure_actions_only

## Hardening Score: 20/22

### Items Scoring YES (20)
1. All claimed states verified against live repo ✓
2. File paths for commit are valid (git status confirmed) ✓
3. Commit scope is minimal (4 files only) ✓
4. No forbidden paths in scope ✓
5. Source-structure-baseline format confirmed (loc/baseline_loc_cap/functions/baseline_functions_cap/category) ✓
6. master-plan.md current section is 74 (ORACLE-LAYER-HARDENING-001) — new section is 75 ✓
7. V-NEW-001 logic verified by direct execution ✓
8. Regex tightening verified by direct test ✓
9. qname=None fix verified by live scan (14794 → 0) ✓
10. ZST upgrade verified (15 → 120 verified) ✓
11. gap-ledger backfill already in HEAD (1221/1242 = 98%) ✓
12. All 4 pilots verified PASS ✓
13. No new test failures (3 pre-existing only) ✓
14. .local/ is gitignored — evidence files don't need commit ✓
15. Commit message pre-defined ✓
16. Baseline entry format confirmed via sample inspection ✓
17. No destructive operations in closure path ✓
18. Single lane owner (this agent) ✓
19. Deferred items (WIRE-001/006) documented with rationale ✓
20. governance_validators_sal.py 89 LOC — well under any reasonable cap ✓

### Items Scoring PARTIAL/NO (2)
- P1: Evidence bundle not built as ZIP (advisory — .local/ is gitignored)
- P2: V-NEW-001 not tested via full governance_validator_runner CLI (tested in isolation only)

## Hardened Closure Action Plan

### Action 1: Register governance_validators_sal.py in source-structure-baseline.json
- File: registry/source-structure-baseline.json
- Entry key: tools/supervisor/governance_validators_sal.py
- Values: loc=89, baseline_loc_cap=89, functions=1, baseline_functions_cap=1, category=governance_extension
- Stop condition: if file already present, skip (idempotent)
- Risk: LOW

### Action 2: Commit SAL sprint files
- Files to stage:
  - tools/supervisor/validate_spec_fact_refs.py (M — tightened format check)
  - tools/scripts/backfill_gap_spec_fact_refs.py (?? new — gap-ledger backfill script)
  - tools/specification-authority-layer/patch_workbench_qnames.py (?? new — qname fix script)
  - tools/supervisor/governance_validators_sal.py (?? new — V-NEW-001 validator)
  - registry/source-structure-baseline.json (after Action 1)
- Commit message: feat(sal): SAL-VHIP-001 — workbench qname fix, ZST upgrade, gap backfill, V-NEW-001 validator
- Stop condition: if pre-commit hook fails, fix and retry
- Risk: LOW

### Action 3: Add Section 75 to plans/master-plan.md
- After Section 74 (ORACLE-LAYER-HARDENING-001 CLOSED) at line ~4268
- Content: SAL-VHIP-001 summary with completed items, deferred items, acceptance criteria
- Risk: LOW

### Action 4: Invoke close-task.md
- Verify: implementation done ✓, verification done ✓, commit done (after Action 2), master plan updated ✓
- Report files changed, commit hash, master plan section updated, closure status: CLOSED
- Risk: LOW

## Verdict: PLAN_HARDENED_FROM_AUDIT_READY_FOR_EXECUTION

NEXT_PROMPT_READY: yes
