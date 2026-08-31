# 09 — Execution Results

**Baseline commit:** dd909cf3a
**Environment:** Windows 11, Python 3.12, disposable worktree at C:/Users/prora/AppData/Local/Temp/claude/ff-investigation-worktree

## Experiment Log

### Experiment 1: FF6 Goal Driver Resume
**Command:** `python tools/ff6/goal_driver.py resume` (from worktree)
**Exit code:** 0 (CONTINUE)
**Output:** VERDICT=CONTINUE, CERTIFIED=4/6, reports ipynb/nrrd/xliff/safetensors as CERTIFIED, ora/ubl as UNASSESSED
**Finding:** Goal driver reads promotion labels directly from controller-state.yaml. Reports 4/6 certified despite truth_boundary saying 0/6. Status: PROVEN

### Experiment 2: False Certification Exploit
**Command:** Edit controller-state.yaml in worktree to set all 6 promotion values to CERTIFIED, then run goal_driver.py resume
**Exit code:** 0 (GOAL_ACHIEVED — mission terminal!)
**Output:** VERDICT=GOAL_ACHIEVED, CERTIFIED=6/6, "All six formats are certified. The mission's own terminal is reached."
**Finding:** Setting promotion strings to CERTIFIED causes GOAL_ACHIEVED regardless of: truth_boundary (0/6), production_certifications (0), ORA having 1 unresolved obligation, no test execution. Status: PROVEN — Critical vulnerability

### Experiment 3: Generic Continuation Check (Clean Worktree)
**Command:** `python tools/supervisor/check_continuation.py` (from worktree with no .local/ state)
**Exit code:** 1 (STOP)
**Output:** `{"verdict": "STOP", "reason": "NO_SIGNAL"}`
**Finding:** Clean worktree has no continuation signal. Confirms non-bootstrappability. Status: PROVEN

### Experiment 4: Dry-Run Mutation Bug
**Command:** `python tools/supervisor/autonomous_task_generator.py --dry-run`
**Before:** product-task-candidates.json = 3,110 bytes
**After:** product-task-candidates.json = 48,400 bytes. git status shows M product-task-candidates.json
**Output message:** "20 candidates (dry-run, not written)" — THIS IS A LIE
**Finding:** --dry-run prints "not written" but writes 48KB. Root cause: line 1705 `output_path = output_path or DEFAULT_OUTPUT` converts None to real write path. Status: PROVEN

### Experiment 5: Plan Control Doctor
**Command:** `python -m tools.plan_control doctor`
**Exit code:** 0
**Output:** `ok: false, journal_head: "GENESIS", plan_count: 0, task_count: 0, source_item_count: 0`
**Findings:** 3 missing projections, unrouted plan files. Plan Control is bootstrapped but completely inert — no actual journal entries, no plans, no tasks. Status: PROVEN

### Experiment 6: Lane Selector for FF6 Formats
**Command:** `python tools/supervisor/lane_selector.py --format {fmt}` for each of ipynb, ora, nrrd, xliff, safetensors, ubl
**Exit code:** 0 for all
**Output:** `"error": "Format '{fmt}' not found in ledger"` for ALL six formats
**Finding:** Generic product-deepening system has ZERO awareness of FF6 formats. Two completely disconnected systems. Status: PROVEN

### Experiment 7: FF6 Event Chain Verification
**Command:** `python -m tools.ff6.controller_events verify`
**Exit code:** 0
**Output:** "PASS: 522 events, chain intact"
**Finding:** Hash chain integrity verified. But this only proves structural integrity, not semantic validity of projection state. Promotion labels are not derivable from the journal. Status: PROVEN (chain integrity) / INFERRED (semantic gap)

### Experiment 8: IPYNB Exact Reconciliation
**Command:** `python -m tools.format_contract.contract_reconciler --format-id ipynb --exact-obligations ...`
**Exit code:** 0
**Output:** "0/68 obligations unresolved; promotion=none"
**Finding:** All 68 obligations show status=implemented, proof_status=SUPPORTED_NONPROMOTING. The reconciler explicitly says this is NON-PROMOTING evidence — it does NOT contribute to certification. Yet goal_driver.py ignores this and reads the CERTIFIED promotion string. Status: PROVEN

### Experiment 9: Governance Validators
**Command:** `python tools/governance/run_ci_governance_check.py` (from worktree)
**Exit code:** 0
**Output:** fail=9, warn=38, pass=164, blocks=True, total=211
**Key failures:** V226 (ALL format install proofs stale), V225 (131 SAL store failures), V102 (369 missing docstrings), V194 (coordination parity), V249 (sys.path mutations). 10 validators skipped (V232-V241).
**Finding:** Governance DOES detect real problems (blocks=True). But CI uses exit code, CLAUDE.md says "exit 3 → continue regardless," and governance validators run AFTER sprint work in autonomous_cycle.py, not as a pre-gate. Status: PROVEN

### Experiment 10: Namespace Import Testing
**Command:** `import format_factory.{fmt}` for each format + `import format_factory.openraster`
**Results:**
- format_factory.ipynb: OK (132 attrs)
- format_factory.ora: OK (56 attrs)
- format_factory.nrrd: OK (75 attrs)
- format_factory.xliff: OK (95 attrs)
- format_factory.safetensors: OK (27 attrs)
- format_factory.ubl: OK (165 attrs)
- format_factory.core: OK (31 attrs)
- format_factory.openraster: ModuleNotFoundError (EXPECTED)
**Finding:** All packages import under actual namespace. product-goal.yaml's declared namespace for ORA is WRONG. Status: PROVEN

### Experiment 11: Real Product Behavior
**Command:** Load/round-trip test for each format
**Results:**
- IPYNB: loads() works, dumps() works, round-trip preserves data, BUT cells are raw dicts after round-trip (not typed objects)
- NRRD: loads() works on raw binary, produces NrrdDocument with header+payload+array. PASS
- SafeTensors: loads() works on binary format, produces SafeTensorsDocument. PASS
- UBL: loads() works on XML, produces Invoice object. PASS
- XLIFF: loads() works on XLIFF 2.0 XML, produces XliffDocument. PASS
- ORA: Cannot test without real .ora file (ZIP archive). API surface exists (56 public attrs).
**Finding:** 4/6 formats demonstrate real product behavior from installed packages. IPYNB works but has a rough API edge. ORA needs a real test file. Status: PROVEN (4/6), UNKNOWN (ORA), PARTIAL (IPYNB cell typing)

### Experiment 12: Committed vs Fresh Reconciliation (IPYNB)
**Command:** Compare committed ipynb-obligation-reconciliation.json with freshly generated
**Results:** Semantically identical (same digest). git diff shows only CRLF→LF differences (32 line endings).
**Finding:** Reconciler is deterministic given unchanged inputs. But determinism ≠ correctness — it doesn't verify test freshness. Status: PROVEN

### Experiment 13: Second Goal Driver Run (Determinism Check)
**Command:** `python tools/ff6/goal_driver.py resume` (second run with restored controller-state.yaml)
**Output:** Identical to Experiment 1: VERDICT=CONTINUE, CERTIFIED=4/6
**Finding:** Goal driver is deterministic from committed state. Status: PROVEN

## Repeatability Summary

| Experiment | Run 1 Result | Run 2 Result | Deterministic? |
|------------|-------------|-------------|----------------|
| Goal driver resume | CONTINUE, 4/6 | CONTINUE, 4/6 | YES |
| check_continuation | STOP/NO_SIGNAL | (not rerun) | Expected YES |
| Reconciler IPYNB | 0/68 unresolved | (same digest) | YES |
| Dry-run mutation | 48KB written | (not rerun — worktree dirty) | YES (deterministic bug) |
