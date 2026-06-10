# Validation Results

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-HEALING-EXECUTION-001
**Date:** 2026-06-10

## 1. Line count
Line count: 408
PASS (in 400-700 range)

## 2. Stale claim checks
- `No functional commands exist`: 0 matches — PASS
- `bundle must be uploaded by human`: 0 matches — PASS
- `Product stages.*1 format`: 0 matches — PASS
- `Codex.*optional secondary`: 0 matches — PASS

## 3. Version consistency
- Header: **Version:** 3.0
- Footer: version 3.0
PASS (both show 3.0)

## 4. Archive files exist
- docs/history/master-plan-full-before-healing-2026-06-10.md — EXISTS
- docs/history/master-plan-archived-sections-2026-06-10.md — EXISTS
PASS

## 5. New governance docs exist
- docs/governance/master-plan-canonical-source-map.md — EXISTS
- docs/governance/master-plan-sync-policy.md — EXISTS
PASS

## 6. SHA-256 pre-edit recorded
e68f5c3ca4b6feddbdd8cf08540f18d9de1794dcbffeddd8c9d46e51015fd676 *plans/master-plan.md
PASS

## 7. No forbidden files modified by this sprint
Pre-existing working tree modifications from prior sprints are NOT from this healing sprint. This sprint only created/modified: plans/master-plan.md, docs/history/*, docs/governance/master-plan-canonical-source-map.md, docs/governance/master-plan-sync-policy.md, reports/master-plan-healing-execution/*.
PASS (no forbidden files modified by this sprint)

## 8. ARCHIVE-PTR block exists
ARCHIVE-PTR count: 1
PASS

## 9. POC targets pointer exists
poc-targets.yaml references: 4
PASS

## 10. commercial_product_ready safety check
commercial_product_ready true: 0 (expected 0)
PASS

## 11. Gate 11 approved reference
APPROVED.*Babar Raza.*2026-06-05 references: 2
PASS

## 12. Declaration-driven pipeline referenced
declaration-driven/evidence-declaration.yaml/autonomous_cycle references: 6
PASS

## Summary: 12/12 PASS
