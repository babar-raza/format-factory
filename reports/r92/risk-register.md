---
sprint: R92
generated_by: r92-worker
---

# R92 Risk Register

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Risks

| ID | Risk | Severity | Status | Mitigation |
|----|------|----------|--------|------------|
| R1 | Materializer creates too many side-effects, breaking working tree | HIGH | MITIGATED | Materializer is read-only; captures snapshots to .local/ only |
| R2 | Declaration-only evidence accepted without any repo verification | HIGH | MITIGATED | Train A verifies all R91 declared items against committed repo |
| R3 | Governed skill change breaks existing tests | MEDIUM | MITIGATED | Run focused dotnet test after each governed change |
| R4 | Context window exhaustion before autonomous-cycle runs | MEDIUM | MITIGATED | Priority order: materializer + product change + autonomous-cycle > cosmetic reports |
| R5 | PENDING markers in report files | LOW | MITIGATED | Scoreboard filled at closeout; all PENDING replaced before final commit |
| R6 | Review package builder fails due to missing zip support | LOW | MITIGATED | Use Python stdlib zipfile; graceful missing-artifact handling |
| R7 | Autonomous-cycle exit 3 due to grading issue | LOW | MITIGATED | Materializer pre-verified R91 items; declaration accurate |

## Inherited Blockers (R91 carry-forward)

| Blocker | Classification | Status |
|---------|---------------|--------|
| Gate 11 G11-G approval | BLOCKED_EXTERNAL_GATE | NOT_STARTED (requires Babar Raza) |
| Git push | BLOCKED_HUMAN_APPROVAL | NOT_STARTED (requires user) |
| PyPI/NuGet publication | BLOCKED_HUMAN_APPROVAL | NOT_STARTED (requires user) |
