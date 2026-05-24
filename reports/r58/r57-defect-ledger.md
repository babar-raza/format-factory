# R57 Defect Ledger

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-24
**Source IV:** R58 Train A

---

| ID | Category | Description | R58 Train Repair | Status |
|----|----------|-------------|-----------------|--------|
| IV-R57-001 | Bundle integrity | Final ZIP SHA in final-verdict.md does not match actual bundle SHA | Train M (new Pass-2 build) | REPAIR_PLANNED |
| IV-R57-002 | Sidecar protocol | Sidecar committed to repo is included inside ZIP under repo/reports/ | Train B (sidecar must not be in ZIP) | REPAIR_PLANNED |
| IV-R57-003 | Sidecar schema | Sidecar uses `bundle_sha256` field; validator expects `sha256` | Train B (canonical schema) | REPAIR_PLANNED |
| IV-R57-004 | State finality | state/current-state.md shows verdict=PENDING for R57 | Train M (run state_snapshot after verdict) | REPAIR_PLANNED |
| IV-R57-005 | State staleness | INV-011 blocker text references R56→R57 mismatch | Train M (state_snapshot after R58 verdict) | REPAIR_PLANNED |
| IV-R57-006 | Scoreboard finality | Train L marked IN_PROGRESS in both final-verdict.md and scoreboard | Train M (update before bundle) | REPAIR_PLANNED |
| IV-R57-007 | Package replay | find_artifact_dir does not check PROJECT_ROOT.parent/bundle-metadata | Train D (add parent check) | REPAIR_PLANNED |
| IV-R57-008 | Artifact freshness | Bundled wheels copied from R56, missing workbook_stats/document_stats | Train E (rebuild from HEAD) | REPAIR_PLANNED |
| IV-R57-009 | Public API | workbook_stats/document_stats not exported from package __init__.py | Train F (expose in public API) | REPAIR_PLANNED |
| IV-R57-010 | Format advancement | Only CSV advanced; four-track claim not met | Train G (TSV G6, PGM, PBM, DIF) | REPAIR_PLANNED |
| IV-R57-011 | Validator coverage | Validator passed despite PENDING state, IN_PROGRESS lanes, stale wheels | Train C (add new checks) | REPAIR_PLANNED |
