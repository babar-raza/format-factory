# Lane Ownership Map
# Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
# RUN_ID: dotnet-dogfood-architecture-gap
# Generated: 2026-06-05

## Lane Ownership Table

| Lane | Owner Role | Primary Output Files | Forbidden Files | Status |
|------|------------|----------------------|-----------------|--------|
| COORD | Coordinator | reports/dotnet-dogfood-architecture-gap/00-preflight.md, lane-ownership.md, file-ownership-map.json, overlap-check.md, risk-register.md, scoreboard.md | src/**, registry/**, plans/master-plan.md | PENDING |
| A | Architecture Investigator | reports/dotnet-dogfood-architecture-gap/01-dotnet-writer-audit.md, 02-gap-confirmation.json | src/**, registry/**, plans/master-plan.md | PENDING |
| B | Source Explorer | reports/dotnet-dogfood-architecture-gap/03-fods-source-map.md, 04-fodt-source-map.md | src/**, registry/**, plans/master-plan.md | PENDING |
| C | Test Evidence Collector | reports/dotnet-dogfood-architecture-gap/05-existing-test-inventory.md | src/**, registry/**, plans/master-plan.md | PENDING |
| D | Gap Ledger Builder | reports/dotnet-dogfood-architecture-gap/06-blocked-gap-ledger.json | src/**, registry/**, plans/master-plan.md | PENDING |
| E | POC-Targets Reader | reports/dotnet-dogfood-architecture-gap/07-poc-targets-snapshot.md | src/**, registry/**, plans/master-plan.md | PENDING |
| F | Gap Selector Validator | tools/supervisor/select_poc_gaps.py (read-only audit only), reports/dotnet-dogfood-architecture-gap/08-gap-selector-audit.md | src/**, registry/**, plans/master-plan.md | PENDING |
| G | Next-Sprint Preparer | reports/supervisor/next-sprint.md (may propose edit), reports/dotnet-dogfood-architecture-gap/09-next-sprint-delta.md | src/**, registry/**, plans/master-plan.md | PENDING |
| H | Skill Handoff Generator | reports/dotnet-dogfood-architecture-gap/10-skill-handoff-proposals.yaml | src/**, registry/**, plans/master-plan.md | PENDING |
| I | Test Scaffolder | tests/supervisor/test_validate_dotnet_dogfood_architecture.py, reports/dotnet-dogfood-architecture-gap/11-test-scaffold-report.md | src/**, registry/**, plans/master-plan.md | PENDING |
| J | Declaration Writer | .local/evidences/dotnet-dogfood-architecture-gap/evidence-declaration.yaml | src/**, registry/**, plans/master-plan.md, reports/supervisor/next-sprint.md | PENDING |
| K | Adversarial Challenger | reports/dotnet-dogfood-architecture-gap/12-adversarial-challenge.md | src/**, registry/**, plans/master-plan.md | PENDING |

## Notes

- All lanes are READ-ONLY for source files (`src/**`), gate authority (`registry/**`), and operational authority (`plans/master-plan.md`).
- Lane G is the ONLY lane authorized to propose edits to `reports/supervisor/next-sprint.md`.
- Lane F is the ONLY lane authorized to audit `tools/supervisor/select_poc_gaps.py` — no edits permitted in this sprint.
- The Coordinator (COORD) serializes access to shared files to prevent overlap.
- Status transitions: PENDING → IN_PROGRESS → COMPLETE | BLOCKED
