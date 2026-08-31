# 19 — Migration Plan (Dependency-Ordered)

**Baseline commit:** dd909cf3a
**Objective:** Transform the current system into the target architecture (artifact 18) in 20 dependency-ordered steps

## Dependency Graph

```
R1 (Freeze) ─────────────────────────────────────────────────────────┐
├── R2 (Authority decision) ──┬── R7 (Bootstrap) ──┬── R17 (Scheduler)──┐
│   │                         │                     │                    │
│   ├── R14 (Plan Control)────┤                     │                    │
│   ├── R15 (Deepening)───────┤                     │                    │
│   └── R16 (Consolidate)─────┘                     │                    │
│                                                   │                    │
├── R3 (Contradiction gate) ── R4 (Remove manual cert)                   │
│                               └── R5 (Derived cert) ── R6 (Hashes)     │
│                                                                        │
├── R8 (Dry-run fix)                                                     │
├── R9 (IPYNB fixes)                                                     │
├── R10 (CI normalization)                                               │
├── R11 (ORA namespace)                                                  │
├── R12 (UBL count)                                                      │
├── R13 (Ledger idempotency)                                             │
│                                                                        │
R18 (One vertical cycle) ◄───────────────────────────────────────────────┘
└── R19 (Remaining formats)
    └── R20 (Delete obsolete)
```

## Phase 1: Stabilize (R1, R3, R8, R9, R10, R11, R12, R13)
**Objective:** Fix immediate defects without changing architecture. All items independent of each other.

### R1: Freeze New Control-Plane Expansion
- **Action:** Pin baseline commit dd909cf3a. Capture CI/environment state. No new supervisors, validators, or task generators until R16 complete.
- **Files modified:** None (policy)
- **State migration:** N/A
- **Compatibility:** No code changes
- **Out of scope:** Does not fix existing defects
- **Duration:** Immediate
- **Rollback:** N/A

### R3: Contradiction Gate
- **Action:** New `tools/ff6/controller_state_validator.py` — fail-closed check that promotion, truth_boundary, and production_certifications agree
- **Files:** New validator + tests
- **State migration:** Current contradictory state must be resolved (truth_boundary updated to match reality, or promotion labels reset to UNASSESSED)
- **Compatibility:** Must not break existing tools that read controller-state.yaml
- **Out of scope:** Does not fix certification logic (that's R4)
- **Test:** Current contradictory state → FAIL; consistent state → PASS
- **Rollback:** Remove validator

### R8: Dry-Run Fix
- **Action:** Fix line 1705 of autonomous_task_generator.py. Propagate dry-run to all mutation functions. Audit all --dry-run/--check/--status commands.
- **Files:** autonomous_task_generator.py + any other mutating "read-only" commands
- **State migration:** N/A (bug fix)
- **Compatibility:** No API change — dry-run now actually means dry-run
- **Out of scope:** Does not fix the task generator's gen-1-only format selection
- **Test:** `git diff` after any dry-run command shows zero changes
- **Rollback:** Revert file

### R9: IPYNB Product Fixes
- **Action:** Fix timeout test failure, update corpus fixtures, ensure test extras are complete
- **Files:** src/python/ipynb/, tests/python/ipynb/
- **State migration:** Evidence records updated with current hashes
- **Compatibility:** Public API unchanged
- **Out of scope:** IPYNB cell typing (dict vs object) — API design decision for later
- **Test:** `pytest tests/python/ipynb/` — 0 failures
- **Rollback:** Revert source changes

### R10: CI Normalization
- **Action:** Add gen-2 package installation to CI. Resolve Python version requirement conflict (root ≥3.9 vs gen-2 ≥3.11). Add dependency lock.
- **Files:** .github/workflows/ci.yml, pyproject.toml files
- **State migration:** N/A
- **Compatibility:** CI must still pass for gen-1 formats
- **Out of scope:** CD/release automation
- **Test:** CI installs all 7 packages and runs all format tests
- **Rollback:** Revert CI changes

### R11: ORA Namespace Resolution
- **Action:** Determine intended name (format_factory.ora based on actual state). Update product-goal.yaml, production_program.py, product_action_guard.py, test assertions, all documentation.
- **Files:** ~12 files with phantom "openraster" references
- **State migration:** product-goal.yaml fields updated
- **Compatibility:** No published package exists — name change is pre-publication
- **Out of scope:** ORA product implementation depth
- **Test:** `import format_factory.ora` succeeds; no "openraster" references in codebase
- **Rollback:** Revert namespace changes

### R12: UBL Obligation Count
- **Action:** Reconcile all sources to current register count. Add count-consistency validation.
- **Files:** controller-state.yaml, UBL-related config
- **State migration:** Stale count updated
- **Compatibility:** No API change
- **Out of scope:** UBL obligation completeness
- **Test:** All sources agree on count
- **Rollback:** Revert

### R13: Evidence Ledger Idempotency
- **Action:** Pin YAML emitter, deterministic sort, fix preservation logic.
- **Files:** tools/ff6/build_evidence_ledger.py
- **State migration:** N/A
- **Compatibility:** Existing evidence records preserved
- **Out of scope:** Evidence freshness (R6)
- **Test:** Two consecutive rebuilds produce identical output
- **Rollback:** Revert

## Phase 2: Fix Certification Chain (R4, R5, R6)
**Objective:** Make certification a derived computation that regresses automatically.

### R4: Remove Manual Certification Authority
- **Depends on:** R3 (contradiction gate catches current state)
- **Action:** Goal driver computes certification, does not read promotion strings
- **Files:** goal_driver.py, controller-state.yaml
- **State migration:** Promotion block becomes a derived output, not an input. Historical promotions preserved in event journal.
- **Compatibility:** goal_driver.py API (resume, status) unchanged; output values change
- **Out of scope:** Full evidence-chain validation (R6)
- **Test:** Setting promotion=CERTIFIED without proof → NOT CERTIFIED
- **Rollback:** Revert goal_driver.py

### R5: Derived Certification
- **Depends on:** R4
- **Action:** New certify.py or integrated into goal_driver: certification = all obligations at IMPLEMENTED + current test PASS + package installable + no blockers
- **Files:** New or modified goal_driver.py/certify.py
- **State migration:** Certification count recomputed from current evidence → likely 0/6 initially
- **Compatibility:** Downstream tools that read certification must handle regression
- **Out of scope:** Auto-execution of stale test selectors
- **Test:** Current state → 0/6 certified (honest assessment)
- **Rollback:** Revert

### R6: Evidence Hash Tracking
- **Depends on:** R5
- **Action:** Add source/test/corpus file SHA-256 to each evidence record. Auto-invalidate when any hash changes.
- **Files:** contract_reconciler.py, evidence stores
- **State migration:** Existing evidence records get current hashes added. Some may immediately invalidate.
- **Compatibility:** Reconciler input/output schema extended (backward compatible — old records without hashes treated as stale)
- **Out of scope:** Full test re-execution (manual trigger for now)
- **Test:** Modify source file → evidence invalidated → certification regresses
- **Rollback:** Remove hash fields

## Phase 3: Consolidate Control Systems (R2, R14, R15, R16)
**Objective:** Establish one authority per concern and remove competing paths.

### R2: Authority Decision Record
- **Depends on:** R1
- **Action:** For every concern (mission, task, claim, evidence, certification, continuation, terminal): document single authority, migration plan for others
- **Files:** New decision record
- **State migration:** Documents current state and target
- **Compatibility:** No code changes — policy document
- **Out of scope:** Implementation of decisions (R14-R16)
- **Rollback:** Remove document

### R14: Plan Control Disposition
- **Depends on:** R2, R7
- **Action:** Based on R2 decision — either adopt Plan Control's useful concepts into single authority, or formally retire
- **Files:** tools/plan_control/ (retire or integrate)
- **State migration:** If retiring: preserve concept documentation, remove code. If integrating: migrate state.
- **Compatibility:** No external consumers of Plan Control exist (it's inert)
- **Out of scope:** Building new plan-control capability (R17 scheduler handles work selection)
- **Rollback:** Restore files from git

### R15: Generic Deepening Disposition
- **Depends on:** R2, R14
- **Action:** Either extend unified scheduler to cover gen-1 formats, or scope generic deepening with explicit boundary
- **Files:** lane_selector.py, task_generator.py, deepening ledger
- **State migration:** If merging: gen-1 formats enter unified scheduler. If scoping: boundary enforced in code.
- **Compatibility:** Gen-1 format work must still be possible
- **Out of scope:** Gen-1 format certification (FF6 mission scope)
- **Rollback:** Revert

### R16: Consolidate Continuation and Failure Semantics
- **Depends on:** R2, R7, R14, R15
- **Action:** Replace 18 bypass rules with typed failure outcomes. Remove Supreme Directive override of non-external STOPs. Make governance pre-execution gate.
- **Files:** CLAUDE.md, sprint_executor.py, autonomous_cycle.py, check_continuation.py
- **State migration:** Governance validators move from post-sprint to pre-sprint position
- **Compatibility:** Existing governance validators unchanged; enforcement timing changes
- **Out of scope:** New validator development
- **Test:** Governance failure prevents continuation
- **Rollback:** Revert

## Phase 4: Build Target System (R7, R17)
**Objective:** Build the single official command and unified scheduler.

### R7: Clean-Clone Bootstrap
- **Depends on:** R2, R5
- **Action:** One command reads only committed files to determine mission state, next work, blockers
- **Files:** New entry point (tools/ff6/run.py or similar)
- **State migration:** .local/ becomes cache-only, not authority
- **Compatibility:** Existing .local/ state is not deleted — just no longer authoritative
- **Out of scope:** Full scheduler (R17)
- **Test:** Delete .local/ → run command → correct state and next task
- **Rollback:** Remove entry point

### R17: Breadth/Depth Scheduler
- **Depends on:** R7, R16
- **Action:** Unified scheduler selects across obligations, capabilities, depth, defects, evidence. Anti-starvation controls.
- **Files:** New scheduler module
- **State migration:** Replaces task_generator + lane_selector + goal_driver next-task logic
- **Compatibility:** Must select from same obligation/capability universe
- **Out of scope:** Automated execution (R18 proves the cycle manually first)
- **Test:** Three consecutive runs select different work targeting different gaps
- **Rollback:** Remove scheduler

## Phase 5: Prove and Migrate (R18, R19, R20)
**Objective:** Prove complete vertical cycle, migrate all formats, retire obsolete paths.

### R18: One Complete Vertical Cycle
- **Depends on:** R5, R6, R7, R10, R17
- **Action:** Execute full chain for one format through new architecture: clean start → task → implement → test → accept → state update → next run sees delta
- **Files:** One format's complete chain
- **State migration:** First real delta through new system
- **Compatibility:** New and old systems may coexist temporarily
- **Out of scope:** Other five formats
- **Test:** Chain fully documented; next run selects different work
- **Rollback:** Revert format changes

### R19: Remaining Format Migration
- **Depends on:** R18
- **Action:** Apply R18 pattern to remaining five formats
- **Files:** Remaining five format chains
- **State migration:** Per-format
- **Compatibility:** Each format migrated independently
- **Rollback:** Per-format revert

### R20: Retire Obsolete Paths
- **Depends on:** R14, R15, R16, R18
- **Action:** Prove no consumers remain. Contain (quarantine, deprecation). Then delete.
- **Files:** All identified obsolete components
- **State migration:** Consumer references removed before code deletion
- **Compatibility:** Error messages for removed entry points
- **Test:** Removed entry points produce clear errors; no test or workflow references them
- **Rollback:** Restore from git

## Timeline Estimate

| Phase | Items | Estimated effort | Parallelizable |
|-------|-------|-----------------|----------------|
| 1: Stabilize | R1,R3,R8-R13 | 3-5 days | Yes (all independent) |
| 2: Certification | R4,R5,R6 | 2-3 days | Sequential |
| 3: Consolidate | R2,R14,R15,R16 | 3-5 days | Partially |
| 4: Build target | R7,R17 | 3-5 days | Sequential |
| 5: Prove | R18,R19,R20 | 5-8 days | R19 items parallel |
| **Total** | **20 items** | **16-26 days** | |
