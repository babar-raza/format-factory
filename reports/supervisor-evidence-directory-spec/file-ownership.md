# File Ownership

## New Files (this sprint)

| File | Lane | Taskcard |
|------|------|----------|
| .supervisor/schemas/evidence-declaration.schema.json | C2 | TC-SUP-DIR-003 |
| .supervisor/schemas/evidence-manifest.schema.json | C2 | TC-SUP-DIR-004 |
| .supervisor/schemas/item-grade.schema.json | C2 | TC-SUP-DIR-007 |
| .supervisor/schemas/supervisor-review.schema.json | C2 | TC-SUP-DIR-007 |
| .supervisor/schemas/next-work-items.schema.json | C2 | TC-SUP-DIR-008 |
| .supervisor/schemas/supervisor-cycle-manifest.schema.json | C2 | TC-SUP-DIR-009 |
| tools/supervisor/evidence_declaration.py | C3 | TC-SUP-DIR-005 |
| tools/supervisor/inspect_declared_evidence.py | C3 | TC-SUP-DIR-006 |
| tools/supervisor/grade_declared_work.py | C3 | TC-SUP-DIR-007 |
| tools/supervisor/generate_next_worker_prompt.py | C3 | TC-SUP-DIR-008 |
| tools/supervisor/autonomous_cycle.py | C3 | TC-SUP-DIR-009 |
| tests/supervisor/test_evidence_declaration.py | C7 | TC-SUP-DIR-013 |
| docs/automation/autonomous-evidence-directory-supervisor-loop.md | C1 | TC-SUP-DIR-002 |
| docs/automation/supervisor-worker-contract.md | C1 | TC-SUP-DIR-002 |
| docs/automation/supervisor-grading-rubric.md | C1 | TC-SUP-DIR-002 |
| docs/automation/autonomous-continuation-policy.md | C1 | TC-SUP-DIR-002 |
| docs/automation/supervisor-generated-prompt-standard.md | C1 | TC-SUP-DIR-002 |
| docs/automation/product-factory-priority-policy.md | C1 | TC-SUP-DIR-002 |
| docs/automation/supervisor-failure-recovery.md | C1 | TC-SUP-DIR-002 |
| docs/automation/supervisor-taskcard-state-model.md | C1 | TC-SUP-DIR-002 |

## Modified Files (this sprint)

| File | Lane | Taskcard |
|------|------|----------|
| tools/supervisor/supervisor_loop.py | C3 | TC-SUP-DIR-002, TC-SUP-DIR-009 |

## Files Requiring R85 Repair (TC-SUP-DIR-010, deferred)

| File | Issue |
|------|-------|
| tools/supervisor/validate_evidence_for_supervisor.py | Verdict logic, final-verdict selection |
| tools/supervisor/compare_goal_to_evidence.py | CRITICAL contradiction for validation failure |
| tools/supervisor/sync_local_memory.py | bundle_validation_pass, test delta |
