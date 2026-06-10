# Evidence Quality Score Reconciliation

## Issue

- Supervisor `evidence_quality_score` in package-104: **0.25**
- Anti-skip `evidence_quality_score` in package-104: **1.0** (14/14 checks pass, 0 violations)

These values come from different scoring systems.

## Root Cause Analysis

### Supervisor Score (0.25)
Computed by `grade_declared_work.py` / `inspect_declared_evidence.py`:
```
score = items_with_tests_supporting / total_items
     = 1 / 4
     = 0.25
```

Item breakdown:
- WI-R2-AUTHORITY-001: `tests_supporting: []` → 0
- WI-R2-CONTRACT-001: `tests_supporting: []` → 0
- WI-R2-PYTHON-PKG-001: `tests_supporting: [6 files]` → 1
- WI-R2-DOTNET-001: `tests_supporting: []` → 0

Only 1 of 4 work items had test file paths in `tests_supporting`. The other 3 were
investigation/exemption items with no associated test files.

### Anti-Skip Score (1.0)
Computed by `anti_skip_checker.py`:
Checks file existence on disk (raw logs, lane ledger, manifests, sample outputs, etc.).
All 14 checks pass because the relevant files exist on disk.
Not a measure of `tests_supporting` population.

## Are Both Scores Valid?

**Yes.** They measure different things:
- Supervisor score: "How many work items have concrete test file proof?"
- Anti-skip score: "Are the expected governance artifact files present on disk?"

A score of 0.25 on supervisor indicates that 3/4 items rely on exemption_reason rather than
test-backed proof. This is legitimate for investigation-only sprints but should be noted.

## Fix Applied in R3

For R3, all work items that have associated tests now have `tests_supporting` populated,
including tests for the .NET XML doc changes and Python wheel builds.
Target supervisor evidence_quality_score: ≥ 0.50 (2+ of 4 items with tests_supporting).

## Validator Action

A cross-scorer consistency check should flag when `supervisor_score < 0.5` and
`anti_skip_score = 1.0`. This is not necessarily an error but warrants a comment
in the evidence quality closeout.
