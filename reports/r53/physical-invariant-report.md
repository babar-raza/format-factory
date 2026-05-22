# Physical Invariant Report

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Tool:** `tools/evidence/check_repo_invariants.py`

## R53 Preflight Invariant Results

```
INV-001: acquisition_pack_yaml_coverage ... PASS
  - 22/22 acquisition packs have pack.yaml

INV-002: state_snapshot_files_present ... PASS
  - state/current-state.md and .json present and non-empty

INV-003: latest_sprint_contract_satisfied ... PASS
  - R52 contract: 19/19 required_repo_files present
  - Contract: r52-state-consistent-installed-artifact-baseline.yaml

INV-004: no_stale_pending_verdict ... PASS
  - Scanned 25 sprint verdict files — no stale PENDING found

INV-005: no_compiled_artifacts_tracked ... PASS
  - git ls-files: 2350 tracked files, none are compiled artifacts

INVARIANTS: PASS (5/5 invariants passed)
```

## Proposed New Invariants (R53)

The following additional invariants are recommended for future sprints.
They are described here; implementation is tracked in taskcards.

### Proposed INV-006: Current Verdict / State Consistency

**Check:** The verdict in `state/current-state.md` matches the latest committed `reports/r*/final-verdict.md`.

**Detects:** R52-style overclaims that are not immediately caught by other checks.

**Proposed logic:**
- Extract latest sprint number from current-state.md
- Read `reports/r<N>/final-verdict.md` verdict
- Compare with state's `verdict` field
- Fail if mismatch

**Implementation:** Add to `check_repo_invariants.py` as INV-006.

### Proposed INV-007: Sidecar Proof Presence for Clean-Baseline Verdicts

**Check:** If the latest sprint verdict contains `BASELINE_CLEAN` or `SELF_VERIFYING`, a sidecar proof file must exist alongside the bundle.

**Detects:** Verdicts that claim clean baseline without sidecar.

**Caveat:** Sidecar is in `.local/` (gitignored); this invariant runs in extracted-bundle mode or local mode only.

### Proposed INV-008: Memory Entry Freshness

**Check:** A `memory/<N>-r<sprint>-*.md` file exists for the current sprint.

**Detects:** Sprints that completed without updating agent memory.

### Notes

These proposed invariants will be implemented in R54 or later. The current 5 invariants all pass.
