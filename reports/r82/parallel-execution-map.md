# R82 Parallel Execution Map

## Phase 0 — Wave 0 (Preflight + Planning)
Runs first, sequential.
- 00-preflight.md ✓
- lane-ownership.md ✓
- risk-register.md ✓
- r79-defect-ledger.md/.json ✓
- r79-r80-r81-authority-investigation.md ✓
- multi-mega-train-scoreboard.md (in progress)
- true-current-system-state.md (in progress)

## Phase 1 — Critical Fixes (Parallel)
- Train F: Fix reproduce_format.py (no deps)
- Build fresh wheels (no deps, running in background)
- Train G: Add pycache validator tests (no deps)

## Phase 2 — Package Artifacts + Tests (Sequential after wheels ready)
- Train D: Copy wheels to package-artifacts/, build manifest with full hashes
- Train E: Fix installed-wheel fail-closed + new test files

## Phase 3 — Workflow Proofs (Sequential after Train D)
- Train H: FODS installed workflow from extracted package
- Train J: FODT installed workflow
- Train K: ZST dependency mode

## Phase 4 — Parallel Track Work
- Train L: .NET tests
- Train M: Gate 11 packet
- Train N: Probe format truth
- Train O: Work-ahead advancement

## Phase 5 — Validator Hardening (After Phase 3)
- Train P: R79-defect-prevention tests

## Phase 6 — Authority Sync
- Train B: True current system state
- Train C: State/master-plan normalization
- Train A: Authority normalization ledger finalized
- Train S: Final authority sync

## Phase 7 — Final Package
- Train Q: Build supervisor review package + replay
- Train R: AI gap extraction (fixture mode)
- Build evidence bundle, commit, generate final verdict

PARALLEL_EXECUTION_MAP: COMPLETE
