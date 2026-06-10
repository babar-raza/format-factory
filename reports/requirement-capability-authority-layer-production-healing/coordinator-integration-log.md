# Coordinator Integration Log

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Date: 2026-06-04

## Git State at Sprint Start

- Branch: main
- HEAD: 3a86a05 feat(r93): context-pack, D92 defect repair, governed acceleration
- Dirty entries: 356 (pre-existing from R93/R92 sprints)
- Dirty state classification: PRE_EXISTING_DOC_STATE / ALLOWED_DIRTY_STATE

## Preflight Read Log

| File | Status | Notes |
|------|--------|-------|
| CLAUDE.md | FOUND | Sprint closeout protocol, Python fallback, governance rules |
| AGENTS.md | MISSING | Not used in this repo; CLAUDE.md governs |
| GOVERNANCE.md | MISSING | Governance in docs/governance/ directory |
| plans/master-plan.md | FOUND | Sections 1–38, POC operating model active |
| state/current-state.md | FOUND | R113 latest sprint; 22 formats; Product-First POC model |
| reports/supervisor/session-resume.md | FOUND | FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER; AUTONOMOUS_CONTINUE: YES |
| docs/governance/product-first-operating-model.md | FOUND | Product-First POC operating model definition |
| docs/governance/four-stream-operating-model.md | FOUND | Mainstream/Acceleration/Skills/Supervisor stream definitions |
| docs/governance/ai-authority-boundary.md | FOUND | AI authority and boundary rules |
| product-capability-matrix/poc-targets.yaml | FOUND | 6 POC targets; FODS/FODT Gates 1-10 PASSED |
| registry/format-registry.yaml | FOUND | 22 formats |
| reports/requirement-capability-authority-layer-plan/** | MISSING | Prior plan dir does not exist (this sprint is the healing sprint) |
| .supervisor/schemas/ | FOUND | 11 JSON Schema Draft 2020-12 files |
| tools/supervisor/ | FOUND | 47+ Python scripts |

## Governance Docs Confirmed Present

- docs/governance/acceleration-definition.md — FOUND
- docs/governance/ai-authority-boundary.md — FOUND
- docs/governance/autonomous-supervisor-role.md — FOUND
- docs/governance/evidence-handling-principles.md — FOUND
- docs/governance/external-tool-architecture.md — FOUND
- docs/governance/four-stream-operating-model.md — FOUND
- docs/governance/ghidra-mcp-compliance-gate.md — FOUND
- docs/governance/independent-authority-layers.md — FOUND
- docs/governance/lane-definitions.md — FOUND
- docs/governance/machinery-success-criteria.md — FOUND
- docs/governance/mainstream-poc-mega-train.md — FOUND
- docs/governance/mainstream-product-output-floor.md — FOUND
- docs/governance/product-first-operating-model.md — FOUND
- docs/governance/requirement-capability-authority-layer.md — FOUND (existing stub)
- docs/governance/ruflo-runtime-governance.md — FOUND
- docs/governance/specification-authority-layer.md — FOUND
- docs/governance/superpowers-skill-intake.md — FOUND

## Lane Assignments Confirmed

- Lane 0 (Coordinator): TC-RCA-COORD-001, TC-RCA-VALIDATE-001, TC-RCA-EVIDENCE-001 + governance/prompt template docs
- Lane A: TC-RCA-PROD-001, TC-RCA-PROD-002, TC-RCA-PROD-003
- Lane B: TC-RCA-GRAPH-001, TC-RCA-GRAPH-002, TC-RCA-GRAPH-003, TC-RCA-GRAPH-004
- Lane C: TC-RCA-RUNTIME-001, TC-RCA-RUNTIME-002, TC-RCA-RUNTIME-003, TC-RCA-RUNTIME-004
- Lane D: TC-RCA-MIGRATE-001, TC-RCA-CONSUME-001, TC-RCA-CONSUME-002, TC-RCA-CONSUME-003
- Lane E: TC-RCA-TEST-001, TC-RCA-RISK-001, TC-RCA-FINAL-001, TC-RCA-FINAL-002

Total TCs: 22

## File Scope Guard

All output files are within:
- reports/requirement-capability-authority-layer-production-healing/
- docs/governance/
- docs/prompt-templates/
- .local/evidences/requirement-capability-authority-layer-production-healing/

Forbidden paths (read-only): src/net/**, src/python/**, tests/net/**, tests/python/**,
product-capability-matrix/poc-targets.yaml, registry/format-registry.yaml

Final scope guard verification: see final-git-status.txt (created at sprint close)
