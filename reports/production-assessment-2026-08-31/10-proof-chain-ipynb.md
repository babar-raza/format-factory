# 10 — IPYNB Proof Chain Trace

**Baseline commit:** dd909cf3a
**Evidence:** Source code reading + executed experiments

## Chain Diagram

```
AUTHORITY (Jupyter nbformat v4.5/5.10.4 spec)
    |
    | [Edge 1] OK — manual extraction with digest
    v
SAL FACTS (shared/sal-facts/ipynb.yaml)
    |
    | [Edge 2] WEAK — digest binding exists but one-way, no auto-recompilation
    v
COMPILED CONTRACT (shared/format-contracts/ipynb.yaml)
    |
    | [Edge 3] OK — compiler-generated, digest-bound
    v
OBLIGATIONS (plans/strategic/ff6/obligations/ipynb.yaml, 68 total)
    |
    | [Edge 4] *** BROKEN *** — evidence is a historical snapshot, never re-executed
    v
IMPLEMENTATION EVIDENCE (shared/format-contracts/implementation-evidence/ipynb.yaml)
    |
    | [Edge 5] *** BROKEN *** — reconciler checks file/symbol existence, not test outcomes
    v
RECONCILIATION (reports/format-contract-layer/ipynb-obligation-reconciliation.json)
    |
    | [Edge 6] *** BROKEN *** — promotion is manually-set string, reconciler is non-promoting
    v
PROMOTION (controller-state.yaml: ipynb: CERTIFIED)
    |
    | [Edge 7] OK — goal_driver.py reads the string correctly
    v
GOAL DRIVER VERDICT (CERTIFIED, 0/68 unresolved)
    |
    | [Edge 8] OK — deterministic next-task from state
    v
NEXT TASK (no further action for ipynb)
```

## Three Broken Edges

### Edge 4: Obligation → Evidence (BROKEN)
- **What it should do:** Verify that implementation evidence is current and tests pass
- **What it actually does:** Evidence entries cite historical skill transcripts with `expected_result: PASS`. The transcripts are static JSON files from 2026-08-06 recording "688 passed" at that point in time
- **Gap:** Nothing re-executes cited test selectors. Evidence is a frozen snapshot
- **Impact:** `test_timeout_preserves_partial_output_from_completed_cells` can fail without invalidating evidence
- **Status:** PROVEN — architecture inspection + known test failures

### Edge 5: Evidence → Reconciliation (BROKEN)
- **What it should do:** Verify evidence is still valid by executing tests
- **What it actually does:** contract_reconciler.py (lines 260-303):
  1. Validates evidence file against JSON Schema
  2. Opens transcript JSON, checks `result` == `expected_result` (PASS==PASS)
  3. Uses AST to confirm source symbols exist
  4. Uses AST to confirm test function names exist
  5. Checks obligation set completeness
- **Does NOT:** Run pytest, execute any selector, verify tests currently pass, check source file hashes
- **Output:** 68/68 implemented, 0 unresolved, proof_status=SUPPORTED_NONPROMOTING, promotion_effect=none
- **Status:** PROVEN — code inspection + reconciler run experiment

### Edge 6: Reconciliation → Promotion (BROKEN)
- **What it should do:** Compute certification from reconciliation and test results
- **What it actually does:** goal_driver.py line 122: `promotion.get(format_id) == CERTIFIED` — reads a static YAML string
- **Reconciler says:** promotion_effect=none, proof_strength=supporting_nonpromoting
- **Goal driver ignores:** reconciler's non-promoting assessment entirely
- **Invariant violation:** controller-state.yaml line 291: "Product promotion is computed from current proof and cannot be edited here" — FALSE, it IS a manually-editable string
- **Status:** PROVEN — false certification exploit demonstrates this completely

## The `test_timeout_preserves_partial_output_from_completed_cells` Case

### Location in chain:
1. **Evidence file:** cited as `positive_test_selector` for obligation SAL-IPYNB-OBL-63250AAB7522792F (IPYNB-EXEC-001)
2. **Transcript:** `product-source-task-ipynb-execution-adapter-001.json` records `result: PASS` from 2026-08-06
3. **Reconciler:** Checks transcript says PASS and test function exists in AST → reports implemented
4. **Reality:** Test currently fails (timeout loses completed cell output)

### Why nothing detects this:
- Reconciler checks FILE existence and AST symbol existence — both true
- Reconciler checks historical transcript says PASS — true (it did on 2026-08-06)
- Nothing re-runs the test to check if it STILL passes
- Nothing hashes the source file to detect changes since evidence was recorded
- Nothing invalidates the evidence when test fixtures change

### Additional known failures:
- 3 active corpus hashes disagree (fixtures changed since evidence was recorded)
- 2 quarantine corpus hashes disagree
- 1 redistribution-license hash disagrees

All are invisible to the reconciler because it never re-executes tests or checks file hashes.

## Evidence Classification
- Three broken edges: PROVEN (code inspection + execution experiments)
- Evidence staleness vulnerability: PROVEN (architecture + known failures)
- False certification exploit: PROVEN (worktree experiment)
- Reconciler non-promotion: PROVEN (output inspection)
