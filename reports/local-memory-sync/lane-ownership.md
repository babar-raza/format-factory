# Lane Ownership
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-GOVERNANCE-SYNC-20260604-001

## This sprint has one lane: LOCAL-MEMORY-GOVERNANCE-SYNC

### Owner
Single-agent execution — no multi-lane parallelism needed for memory sync.

### Lane Responsibilities
1. Read all existing local memory/governance/state
2. Write new memory entry (memory/67)
3. Update master plan (Section 44)
4. Create/update governance docs (5 new)
5. Create prompt templates (6 new)
6. Create stream state snapshots (4 updates)
7. Create sync reports (13 new)
8. Run validation
9. Build evidence package

### File Ownership
All files under allowed paths belong to this single lane.
No overlap risk (single lane).

### Forbidden Paths (never touched)
- src/net/*
- src/python/*
- tests/net/*
- tests/python/*
- product-capability-matrix/poc-targets.yaml (proposed delta only)
- registry/format-registry.yaml
- .vscode/mcp.json
- .supervisor/policies.yaml
