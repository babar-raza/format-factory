# Preflight Report — dual-orchestration-supervisor-e2e
# Generated: 2026-05-30T16:56:03

## Sprint Identity
- sprint_id: dual-orchestration-supervisor-e2e-20260530-165603
- mode: MODE 1 through MODE 3 (stopping before MODE 4 MCP activation)

## Repo State
- branch: main
- HEAD: 9b4e9e38a254b24ccb558e2b9dcb21d5f59c3506
- clean: YES (no tracked modifications; R78 untracked files unchanged)

## R78 Untracked Files (must not be touched)
- examples/python/fods/edit_save_export_fods.py
- examples/python/fodt/edit_save_export_fodt.py
- reports/r78/
- tests/evidence/test_r78_state_validators.py
- tests/python/fods/test_r78_fods_end_to_end_workflow.py
- tests/python/fodt/test_r78_fodt_end_to_end_workflow.py
- tools/evidence/contracts/r78-true-state-and-first-product-finish-reproducibility.yaml
- tools/repro/

## Tool Versions
- Python: 3.13.2
- Node.js: v24.13.1
- npm: 11.8.0
- npx: 11.8.0
- .local/venv/Scripts/python: 3.13.2 (AVAILABLE — authoritative for tests)

## Forbidden Directory State
- .supervisor/: ABSENT OK
- .taskmaster/: ABSENT OK
- .ruflo/: ABSENT OK
- .vscode/mcp.json: ABSENT OK
- MCP servers: NONE configured

## Governance Files Discovered
- AGENTS.md: present
- GOVERNANCE.md: present
- plans/master-plan.md: present
- registry/format-registry.yaml: present
- .claude/settings.json: present (78 allow entries, valid JSON)
- .gitignore: present

## Evidence Builder Interface
- build_evidence_bundle.py: --repo-root, --contract, --output, --metadata-dir, --auto-proof
- validate_evidence_bundle.py: --contract, --bundle, --no-strict-git, --check-no-pending, --sidecar-proof

## Evidence Bundles Available
- .local/evidence/: searched — no .zip files found (bundles may be in subdirectories or not copied locally)
- Plan note: if no real bundle found, use synthetic negative-test fixtures + report limitation

## Plan Source
- C:\Users\prora\.claude\plans\graceful-percolating-parrot.md (healed plan)
- Plan status: PLAN_HEALED_READY_FOR_SINGLE_GO_EXECUTION_HANDOFF
