# R27/R32 Legacy Contract Classification

**Sprint:** FORMAT-FACTORY-R48-ARTIFACT-RC-CLEAN-CLOSEOUT-AND-PHASE-AUDIT-COMPLETION-001
**Date:** 2026-05-22

---

## Findings from State Linter

```
[WARNING] below_floor_metadata: r27-ai-platform-full-cycle.yaml: min_metadata_count=10 < 30
[WARNING] below_floor_metadata: r32-truth-matrix-gate-quality-and-drift-recovery.yaml: min_metadata_count=5 < 30
```

---

## Classification Decision

These contracts are **legacy contracts from before the metadata floor was raised to 30**.

The floor of 30 metadata files was established in R34+ as part of sprint evidence hardening.
R27 and R32 predate this requirement and their bundles are closed/finalized.

**Decision: Classify as LEGACY_PRE_FLOOR_30 — no remediation required.**

Rationale:
1. Both sprints are closed. R27 and R32 verdicts are accepted.
2. The metadata floor applies to *new* bundles, not retroactively to closed sprint bundles.
3. Rebuilding R27/R32 bundles to meet the floor would require reconstructing historical context.
4. The warning is informational — existing linter behavior is correct to warn.
5. Policy: linter warns on legacy contracts but does not fail on them.

---

## State Linter Policy Update

The state linter SHOULD warn on these contracts (it does). It SHOULD NOT treat them as
errors that block current sprint work. The lint result is `STATE_LINT: PASS` (2 warnings,
0 errors) — this is the correct behavior.

**Action: No change to linter logic. Document this classification here.**

| Contract | Sprint | Floor | Classification | Action |
|----------|--------|-------|----------------|--------|
| r27-ai-platform-full-cycle.yaml | R27 | 10 | LEGACY_PRE_FLOOR_30 | Document, no fix |
| r32-truth-matrix-gate-quality-and-drift-recovery.yaml | R32 | 5 | LEGACY_PRE_FLOOR_30 | Document, no fix |

**Taskcard:** TC-LEGACY-001 — "Legacy contract metadata floor warnings"
- Status: CLASSIFIED — documented in this report
- Owner: N/A (no active work required)
- Next action: None unless re-audit of R27/R32 evidence is requested
