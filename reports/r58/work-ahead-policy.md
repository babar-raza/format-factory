# R58 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-24

---

## Policy

R58 is a mega-train sprint. Work proceeds in parallel lanes. No lane may declare
COMPLETE unless its deliverables are tested and evidence-backed.

### Parallel execution
Trains B, C, D, E, F, G, I, J, K are independent and execute concurrently.
Train H waits for E (rebuilt wheels) and G (format advances) before final audit.
Train L waits for all A-K to be COMPLETE.
Train M waits for all A-L to be COMPLETE.

### Evidence requirements per lane
- Every lane must write a report to reports/r58/
- Every code change must have passing tests
- Every package claim must be backed by a rebuilt artifact from HEAD
- Every sidecar claim must reference a ZIP not containing that sidecar

### Non-negotiable stops
If any of the following remain at bundle time, bundle build FAILS:
- state/current-state.md latest_sprint PENDING
- Any scoreboard lane IN_PROGRESS
- Any final-verdict lane IN_PROGRESS
- Sidecar embedded inside ZIP
- Sidecar SHA does not match actual ZIP
- Wheels missing R58/R57 source features (workbook_stats, document_stats)
- Package replay skips artifact checks

### Scope of R58
R58 = closure repair + continued product expansion.
Not a narrow closure sprint.
Four tracks must advance beyond FODS/FODT.
