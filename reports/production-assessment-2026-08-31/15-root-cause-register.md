# 15 — Root Cause Register

**Baseline commit:** dd909cf3a
**Evidence:** All investigation phases

## Root Cause 1: Certification Is Declared, Not Derived
- **Classification:** ROOT CAUSE
- **Evidence:** goal_driver.py line 122 reads promotion string; false certification exploit produces GOAL_ACHIEVED with 0 real proof
- **First failing boundary:** goal_driver.py — no validation between promotion label and actual evidence
- **Affected scope:** All 6 FF6 formats; mission completion state; downstream task selection
- **Why controls missed it:** controller-state.yaml invariant (line 291) CLAIMS promotion is computed from proof, but the code doesn't enforce this
- **Confidence:** PROVEN (exploit demonstrated)
- **Evidence that would change conclusion:** Finding a code path that actually derives promotion from evidence and updates the label

## Root Cause 2: Evidence Is a Frozen Snapshot, Never Re-Validated
- **Classification:** ROOT CAUSE
- **Evidence:** contract_reconciler.py checks file/symbol existence via AST, never executes tests; evidence entries cite historical transcripts with timestamps from 2026-08-06
- **First failing boundary:** contract_reconciler.py — reconcile_obligations() validates structure not behavior
- **Affected scope:** All obligation→evidence→reconciliation chains for all formats
- **Why controls missed it:** Reconciler was designed for structural completeness checking, not runtime validation. The truth_boundary field honestly says "characterization only" but downstream consumers don't enforce this
- **Confidence:** PROVEN (code inspection + reconciler experiments)
- **Evidence that would change conclusion:** Finding a separate process that re-executes all evidence selectors

## Root Cause 3: Multiple Disconnected Control Systems With No Conflict Resolution
- **Classification:** STRUCTURAL WEAKNESS
- **Evidence:** 6 control systems identified; generic deepening has no FF6 awareness (lane_selector returns format_not_found for all 6); Plan Control is bootstrapped but inert; two parallel task-selection winners
- **First failing boundary:** No integration point exists between FF6 controller and generic supervisor
- **Affected scope:** Task selection, continuation, mission state
- **Why controls missed it:** Systems were built incrementally without replacing predecessors. CLAUDE.md manages conflicts through textual precedence rules, not code
- **Confidence:** PROVEN (experiments across all systems)
- **Evidence that would change conclusion:** Finding a code-level integration between generic and FF6 systems

## Root Cause 4: Non-Bootstrappable Continuation State
- **Classification:** STRUCTURAL WEAKNESS
- **Evidence:** check_continuation.py returns NO_SIGNAL from clean clone; .local/ is gitignored; Supreme Directive overrides NO_SIGNAL by reading next-sprint.md directly, bypassing all state checking
- **First failing boundary:** continuation-signal.json is not committed and cannot be reconstructed from committed state
- **Affected scope:** Clean clone bootstrapping; cross-machine reproducibility; agent onboarding
- **Why controls missed it:** The Supreme Directive treats NO_SIGNAL as a non-external-gate STOP and overrides it. The override "works" but loses all state checking
- **Confidence:** PROVEN (clean worktree experiment)
- **Evidence that would change conclusion:** Finding a committed bootstrap mechanism that creates the initial signal

## Root Cause 5: Systematic Override of Safety Controls
- **Classification:** STRUCTURAL WEAKNESS
- **Evidence:** 18 bypass rules in CLAUDE.md; 17 of 23 STOP reasons overridden; 120 except-and-continue blocks in autonomous_cycle.py; governance runs AFTER sprint work
- **First failing boundary:** CLAUDE.md Supreme Directive — "nothing may block forward progress except TRUE_EXTERNAL_GATEs"
- **Affected scope:** All governance validators, continuation checks, evidence validation
- **Why controls missed it:** The bypass rules were designed to prevent stalling on infrastructure failures. But they also prevent governance from blocking product work
- **Confidence:** PROVEN (CLAUDE.md text + sprint_executor.py code inspection)
- **Evidence that would change conclusion:** Finding effective pre-execution gates that can't be bypassed

## Root Cause 6: ORA Namespace Mismatch Across Multiple Systems
- **Classification:** IMMEDIATE DEFECT
- **Evidence:** product-goal.yaml declares format_factory.openraster; actual package is format_factory.ora; production_program.py has phantom source_package_id; tests assert phantom paths
- **First failing boundary:** product-goal.yaml — original declaration was wrong; no automated validation exists
- **Affected scope:** ORA package metadata, production program, documentation, test assertions
- **Why controls missed it:** goal_driver.py only reads format_id (not import_namespace), so the mismatch doesn't affect the critical path. No validator checks namespace consistency
- **Confidence:** PROVEN (import test + file analysis)
- **Evidence that would change conclusion:** N/A — this is a concrete defect

## Root Cause 7: Dry-Run Commands Mutate State
- **Classification:** IMMEDIATE DEFECT
- **Evidence:** autonomous_task_generator.py --dry-run writes 48KB to product-task-candidates.json; prints "not written" while actually writing
- **First failing boundary:** Line 1705: `output_path = output_path or DEFAULT_OUTPUT` converts None→real path
- **Affected scope:** Any tool with --dry-run, --check, --status, --doctor
- **Why controls missed it:** The dry-run flag is only checked in main(), not propagated to the function that actually writes
- **Confidence:** PROVEN (experiment showed file grew from 3KB to 48KB)
- **Evidence that would change conclusion:** N/A — this is a concrete, demonstrated bug

## Root Cause 8: CI Does Not Test What Is Published
- **Classification:** STRUCTURAL WEAKNESS
- **Evidence:** CI installs only pip install -e ".[dev]"; none of the 6 FF6 gen-2 packages are installed; gen-2 requires Python >=3.11 but root requires >=3.9; .NET build silently skips missing projects
- **First failing boundary:** .github/workflows/ci.yml — no gen-2 package installation step
- **Affected scope:** All 6 FF6 packages; namespace validation; dependency validation
- **Why controls missed it:** CI was built for gen-1 packages (flat layout, bare imports). Gen-2 packages were added without updating CI
- **Confidence:** PROVEN (ci.yml grep + package structure inspection)
- **Evidence that would change conclusion:** Finding a separate CI workflow that tests gen-2 packages

## Root Cause 9: Controller-State Contains Unfalsifiable Contradiction
- **Classification:** ROOT CAUSE
- **Evidence:** Same file contains promotion=4/6 CERTIFIED, truth_boundary=0/6, production_certifications=0, invariant="promotion computed from proof"
- **First failing boundary:** controller_events.py — writes to controller-state.yaml but doesn't enforce consistency between sections
- **Affected scope:** Certification state; mission completion; agent decision-making
- **Why controls missed it:** The truth_boundary is a text narrative, not a machine-readable constraint. The promotion block is the only section that goal_driver.py reads for certification.
- **Confidence:** PROVEN (file inspection + goal_driver code analysis)
- **Evidence that would change conclusion:** Finding a mechanism that enforces truth_boundary constraints on the promotion block

## Summary Classification

| # | Classification | Confidence | Scope |
|---|---------------|------------|-------|
| RC1 | Root cause | PROVEN | All formats — certification |
| RC2 | Root cause | PROVEN | All formats — evidence |
| RC3 | Structural weakness | PROVEN | System-wide — task selection |
| RC4 | Structural weakness | PROVEN | System-wide — bootstrapping |
| RC5 | Structural weakness | PROVEN | System-wide — safety |
| RC6 | Immediate defect | PROVEN | ORA format |
| RC7 | Immediate defect | PROVEN | Diagnostic tools |
| RC8 | Structural weakness | PROVEN | CI — all FF6 formats |
| RC9 | Root cause | PROVEN | Certification — controller state |
