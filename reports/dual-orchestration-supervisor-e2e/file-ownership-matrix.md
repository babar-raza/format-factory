# File Ownership Matrix — dual-orchestration-supervisor-e2e-20260530-165603

## Rule: Each file appears in exactly ONE lane. C0 serializes conflicts.

| File / Path | Lane | Owner | TC Ref |
|------------|------|-------|--------|
| reports/dual-orchestration-supervisor-e2e/preflight.md | C0 | Coordinator | TC-SUP-000 |
| reports/dual-orchestration-supervisor-e2e/git-status-before.txt | C0 | Coordinator | TC-SUP-000 |
| reports/dual-orchestration-supervisor-e2e/tool-availability.txt | C0 | Coordinator | TC-SUP-000 |
| reports/dual-orchestration-supervisor-e2e/governance-discovery.md | C1 | Governance | TC-SUP-000 |
| reports/dual-orchestration-supervisor-e2e/plan-anchor.md | C0 | Coordinator | TC-SUP-001 |
| reports/dual-orchestration-supervisor-e2e/execution-board.md | C0 | Coordinator | TC-SUP-015 |
| reports/dual-orchestration-supervisor-e2e/file-ownership-matrix.md | C0 | Coordinator | TC-SUP-015 |
| reports/dual-orchestration-supervisor-e2e/stop-gate-log.md | C0 | Coordinator | TC-SUP-015 |
| .supervisor/config.yaml | C1 | Governance | TC-SUP-000 |
| .supervisor/policies.yaml | C1 | Governance | TC-SUP-000 |
| .supervisor/project-memory.md | C1 | Governance | TC-SUP-000 |
| .supervisor/sprint-loop.md | C1 | Governance | TC-SUP-000 |
| .supervisor/prompts/evidence-review.md | C5 | PromptSchema | TC-SUP-006 |
| .supervisor/prompts/adversarial-review.md | C5 | PromptSchema | TC-SUP-006 |
| .supervisor/prompts/next-sprint-generator.md | C5 | PromptSchema | TC-SUP-006 |
| .supervisor/prompts/approval-gate-classifier.md | C5 | PromptSchema | TC-SUP-006 |
| .supervisor/prompts/memory-sync.md | C5 | PromptSchema | TC-SUP-006 |
| .supervisor/schemas/evidence-review.schema.json | C2 | TaskcardModel | TC-SUP-005 |
| .supervisor/schemas/next-sprint-taskmaster.schema.json | C2 | TaskcardModel | TC-SUP-005 |
| .supervisor/schemas/next-ruflo-lanes.schema.json | C2 | TaskcardModel | TC-SUP-005 |
| .supervisor/schemas/supervisor-verdict.schema.json | C2 | TaskcardModel | TC-SUP-005 |
| tools/supervisor/discover_latest_evidence.py | C4 | Scripts | TC-SUP-003 |
| tools/supervisor/validate_evidence_for_supervisor.py | C4 | Scripts | TC-SUP-004 |
| tools/supervisor/compare_goal_to_evidence.py | C4 | Scripts | TC-SUP-005 |
| tools/supervisor/generate_supervisor_packet.py | C4 | Scripts | TC-SUP-006 |
| tools/supervisor/sync_local_memory.py | C4 | Scripts | TC-SUP-007 |
| tools/supervisor/supervisor_loop.py | C4 | Scripts | TC-SUP-008 |
| tools/taskmaster/validate_taskmaster_bridge.py | C6 | TM | TC-SUP-011 |
| tools/taskmaster/validate_dual_orchestration_bridge.py | C6 | TM | TC-SUP-011 |
| tests/taskmaster/test_validate_taskmaster_bridge.py | C6 | TM | TC-SUP-019 |
| tests/taskmaster/test_validate_dual_orchestration_bridge.py | C6 | TM | TC-SUP-019 |
| docs/automation/local-supervisor-control-plane.md | C3 | Supervisor | TC-SUP-012 |
| docs/automation/human-handoff-retirement-requirements.md | C3 | Supervisor | TC-SUP-012 |
| docs/automation/phase-model-amendment.md | C3 | Supervisor | TC-SUP-012 |
| docs/taskmaster/taskmaster-supervisor-integration.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/taskmaster-to-format-factory-taskcard-bridge.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/taskmaster-format-factory-operating-profile.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/taskmaster-mcp-tool-surface.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/dual-orchestration-kpi-model.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/taskmaster-session-recovery.md | C3 | Supervisor | TC-SUP-013 |
| docs/taskmaster/taskmaster-no-drift-state-contract.md | C3 | Supervisor | TC-SUP-013 |
| docs/ai/ruflo-supervisor-integration.md | C7 | Ruflo | TC-SUP-014 |
| docs/ai/ruflo-format-factory-operating-profile.md | C7 | Ruflo | TC-SUP-014 |
| docs/ai/ruflo-mcp-tool-surface.md | C7 | Ruflo | TC-SUP-014 |
| docs/ai/ruflo-lane-coordination-model.md | C7 | Ruflo | TC-SUP-014 |
| docs/ai/ruflo-process-hygiene.md | C7 | Ruflo | TC-SUP-014 |
| docs/ai/dual-orchestration-architecture.md | C7 | Ruflo | TC-SUP-014 |
| .gitignore (append only) | C9 | Rollback | TC-SUP-009 |
| .claude/settings.json (append only) | C9 | Rollback | TC-SUP-010 |
| reports/supervisor/evidence-review.md | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/evidence-review.json | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/contradictions.md | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/next-sprint.md | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/next-sprint-taskmaster.json | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/next-ruflo-lanes.json | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/approval-gates.md | C4 | Scripts | TC-SUP-017 |
| reports/supervisor/session-resume.md | C4 | Scripts | TC-SUP-017 |
| reports/dual-orchestration-supervisor-e2e/security-scan.md | C8 | Security | TC-SUP-016 |
| reports/dual-orchestration-supervisor-e2e/no-drift-check.md | C8 | Security | TC-SUP-016 |
| reports/dual-orchestration-supervisor-e2e/adversarial-review.md | C0 | Coordinator | TC-SUP-019 |
| reports/dual-orchestration-supervisor-e2e/repair-loop-1.md | C0 | Coordinator | TC-SUP-019 |
| reports/dual-orchestration-supervisor-e2e/taskmaster-dry-run.md | C6 | TM | TC-SUP-011 |
| reports/dual-orchestration-supervisor-e2e/ruflo-dry-run.md | C7 | Ruflo | TC-SUP-012 |
| reports/dual-orchestration-supervisor-e2e/mode3-activation-readiness.md | C0 | Coordinator | TC-SUP-015 |
| reports/dual-orchestration-supervisor-e2e/final-verdict.md | C10 | Verification | TC-SUP-019 |
| reports/dual-orchestration-supervisor-e2e/final-git-status.txt | C10 | Verification | TC-SUP-019 |
| .local/evidence/dual-orchestration-supervisor-e2e-*/ | C10 | Verification | TC-SUP-019 |

## Overlap Check Result: PASS
- Each file in exactly one lane
- No two lanes own same output
- .gitignore and .claude/settings.json: C9 owns (append-only; coordinator monitors)
