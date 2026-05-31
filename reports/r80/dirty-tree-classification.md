# Dirty Tree Classification

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Classification Method

Baseline: HEAD = 9b4e9e3 (last R78 commit). All changes since HEAD classified below.

## Category A — Supervisor Sprint Work (Dual Orchestration)

These were created/modified by the `dual-orchestration-supervisor-e2e-20260530-165603` sprint.
All are untracked new files (except .gitignore + .claude/settings.json which are append-only).

| File/Dir | Type | Safe? |
|---|---|---|
| .claude/settings.json | tracked, modified | YES — append-only (17 new allow entries) |
| .gitignore | tracked, modified | YES — append-only (12 new lines) |
| .supervisor/ | untracked new | YES — supervisor control plane |
| docs/ai/dual-orchestration-architecture.md | untracked new | YES |
| docs/ai/ruflo-*.md (5 files) | untracked new | YES |
| docs/automation/ (3 files) | untracked new | YES |
| docs/taskmaster/ (7 files) | untracked new | YES |
| reports/dual-orchestration-supervisor-e2e/ | untracked new | YES |
| reports/supervisor/ | untracked new | YES |
| tools/evidence/contracts/dual-orchestration-supervisor-e2e-20260530-165603.yaml | untracked new | YES |
| tools/supervisor/ (6 scripts) | untracked new | YES |
| tools/taskmaster/ (2 validators) | untracked new | YES |

## Category B — R79 Product Sprint Work

These are R79 code/test changes. All represent forward product progress.

| File | Type | Sprint | Safe? |
|---|---|---|---|
| packaging/python/pyproject.template.toml | tracked, modified | R79 (D78-05 SDist excludes) | YES |
| src/python/fods/constants.py | tracked, modified | R79 (D78-04 version fix) | YES |
| src/python/fodt/constants.py | tracked, modified | R79 (D78-04 version fix) | YES |
| src/python/fodt/neutral_model.py | tracked, modified | R79 (D78-13 structural gap fix) | YES |
| state/current-state.json | tracked, modified | R79 state sync | YES |
| state/current-state.md | tracked, modified | R79 state sync | YES |
| tests/python/fodt/test_r77_fodt_paragraph_management.py | tracked, modified | R79 test fix | YES |
| tests/python/fodt/test_r78_fodt_end_to_end_workflow.py | tracked, modified | R79 test fix | YES |
| reports/r79/ (all files) | untracked new | R79 reports | YES |
| tests/packaging/test_r79_installed_fods_workflow.py | untracked new | R79 tests | YES |
| tests/packaging/test_r79_package_source_sync.py | untracked new | R79 tests | YES |
| tools/evidence/contracts/r79-package-source-sync-first-real-fods-product-rc-zst-dependency-replay.yaml | untracked new | R79 contract | YES |

## Category C — R80 Sprint Work (this sprint)

All new under `reports/r80/` — no conflicts with other categories.

## Category D — Unexpected/Unsafe Files

None found. Git status reviewed: all changes accounted for in categories A, B, C.

## Safety Assessment

- NO governance files modified (AGENTS.md, GOVERNANCE.md, plans/master-plan.md, registry/ all clean)
- NO R78 committed work overwritten
- NO .vscode/mcp.json present
- NO .taskmaster/, .ruflo/, .swarm/ present
- .gitignore and .claude/settings.json are append-only (verified via git diff)
