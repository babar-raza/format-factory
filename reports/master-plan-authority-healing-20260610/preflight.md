# Preflight — Master Plan Authority Healing Sprint

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-AUTHORITY-HEALING-001
**Run ID:** master-plan-authority-healing-20260610
**Date:** 2026-06-11

## Git State

**Branch:** main
**Last 5 commits:**
- 8e45224 fix(ci): add --continue-on-collection-errors to pytest
- ab622a4 fix(ci): remove -x flag so tests run past collection errors
- bc8c871 fix(ci): add pydantic and httpx to dev deps for tests/ai collection
- 2e67ffc fix(ci): harden CI workflow for first green run
- 3a3ba1a feat: product deepening + supervisor pipeline + governance (30+ sprints checkpoint)

## Master Plan State (Before Edit)

- **File:** `plans/master-plan.md`
- **Lines:** 408
- **Version:** 3.0
- **Last healed:** 2026-06-10 (FORMAT-FACTORY-MASTER-PLAN-HEALING-EXECUTION-001)

## Pointer Files Verified (All 20 Exist)

1. `product-capability-matrix/poc-targets.yaml` — EXISTS
2. `reports/supervisor/session-resume.md` — EXISTS
3. `registry/format-registry.yaml` — EXISTS
4. `reports/supervisor/approval-gates.md` — EXISTS
5. `reports/supervisor/next-sprint.md` — EXISTS
6. `docs/governance/*.md` — EXISTS (13 files)
7. `docs/governance/master-plan-canonical-source-map.md` — EXISTS
8. `docs/governance/master-plan-sync-policy.md` — EXISTS
9. `docs/governance/four-stream-operating-model.md` — EXISTS
10. `docs/governance/ai-authority-boundary.md` — EXISTS
11. `docs/governance/autonomous-supervisor-role.md` — EXISTS
12. `docs/governance/mainstream-product-output-floor.md` — EXISTS
13. `docs/governance/acceleration-definition.md` — EXISTS
14. `docs/governance/external-tool-architecture.md` — EXISTS
15. `docs/governance/independent-authority-layers.md` — EXISTS
16. `docs/history/master-plan-full-before-healing-2026-06-10.md` — EXISTS (2229 lines, full backup)
17. `docs/history/master-plan-archived-sections-2026-06-10.md` — EXISTS (~1060 lines)
18. `reports/master-plan-healing-execution/archive-pointer-map.json` — EXISTS
19. `.supervisor/skill-registry.yaml` — EXISTS
20. `docs/governance/mainstream-poc-mega-train.md` — EXISTS

## Critical Issues Found

1. **GAP-AUTH-001 (CRITICAL):** Gate 11 wording — master plan says "Gate 11 APPROVED" but registry shows `gate_11.status: commercial_readiness_in_progress, approved_by: null`. poc-targets.yaml sub-gate field: `gate_11_g11g: APPROVED_BY_BABAR_RAZA_2026_06_05`. Need precise reconciliation.

2. **GAP-AUTH-002 (CRITICAL):** Gate sequential rule typo — line 234 says "Sequential (Gate N before Gate N-1)" — backwards. Should be "Gate N-1 before Gate N".

3. **GAP-AUTH-003 (HIGH):** Missing Living Master Plan Policy (7 rules from original §5) — not present in healed plan.

4. **GAP-AUTH-004 (HIGH):** Missing Persistent Artifact Model table (`.local/` boundary, commit/no-commit table).

5. **GAP-AUTH-005 (HIGH):** Missing Reuse-Before-Regenerate decision table.

6. **GAP-AUTH-006 (MEDIUM):** Missing Format Expansion Guardrails (system must not be limited to Aspose-supported formats).

7. **GAP-AUTH-007 (MEDIUM):** Missing full Visibility Classification table (default rules per artifact type).

8. **GAP-AUTH-008 (LOW):** poc-targets.yaml line 6 comment says `commercial_product_ready: true` but actual fields say `false` — contradiction within poc-targets.yaml (NOT fixed in this sprint — requires human review).
