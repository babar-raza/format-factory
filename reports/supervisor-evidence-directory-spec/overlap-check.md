# Overlap Check

## Cross-Lane File Conflicts

| File | Lanes | Conflict? | Resolution |
|------|-------|-----------|------------|
| tools/supervisor/supervisor_loop.py | C1 (plan), C3 (tools) | Potential | C1 updates docstring, C3 adds commands. Sequential edits, no conflict. |

## No Conflicts Found

All other files are owned by exactly one lane:
- Schemas (C2) are new files, no overlap
- New tools (C3) are new files, no overlap
- Tests (C7) are new files, no overlap
- Docs (C1) are new files, no overlap
- Evidence (C9) are new files in .local/, no overlap

## Cross-Sprint Conflict Check

| Existing File | This Sprint Modifies? | Risk |
|---------------|----------------------|------|
| .supervisor/policies.yaml | Yes (C5) | Low — additive sections only |
| .supervisor/config.yaml | Yes (C6) | Low — additive settings only |
| tools/supervisor/validate_evidence_for_supervisor.py | Yes (C4, deferred) | Medium — existing logic changes |
| tools/supervisor/compare_goal_to_evidence.py | Yes (C4, deferred) | Medium — existing logic changes |
| tools/supervisor/sync_local_memory.py | Yes (C6, deferred) | Medium — existing logic changes |

## Mitigation

- C4 (regression repair) changes are deferred to avoid destabilizing existing watcher pipeline
- C5/C6 changes are additive (new YAML sections, new config keys)
- All new tools import sibling modules via sys.path, avoiding circular imports
