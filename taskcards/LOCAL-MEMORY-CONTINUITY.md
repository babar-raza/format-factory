# Taskcard: LOCAL-MEMORY-CONTINUITY

## Status
COMPLETED

## Purpose
Ensure the local repo contains sufficient memory, governance, and bootstrap context that future
chat sessions or local agents can continue the project from disk without relying on external
(ChatGPT) saved memory or a long conversation history.

## Scope
- Create/update local memory files (memory/24-chatgpt-session-memory-sync-20260513.md)
- Update memory index (memory/00-index.md)
- Create continuity map (reports/planning/current-project-continuity-map-20260513.md)
- Ensure AGENTS.md and GOVERNANCE.md have the minimal required durable rules
- Create fresh-chat bootstrap entry point (docs/automation/fresh-chat-project-bootstrap.md)
- Confirm that all key project direction decisions are present in local files

## Key Memory Invariants (must be true at all times)
1. The latest memory file index (memory/00-index.md) contains an entry for every numbered memory file
2. Local authority files (plans/master-plan.md, AGENTS.md, GOVERNANCE.md, registry/format-registry.yaml) reflect current state
3. Gate 11 is not approved in any local file unless human has explicitly approved it
4. DEC-033 Option B is preserved in all local files
5. Commercial product direction (C7+ load-edit-save-convert) is documented in local files
6. AI policy (accelerator not authority) is documented in AGENTS.md and GOVERNANCE.md
7. Generated requirements mandate is documented in AGENTS.md §AF13 and GOVERNANCE.md §26.11
8. Fresh-chat bootstrap doc exists at docs/automation/fresh-chat-project-bootstrap.md

## Non-Goals
- Do NOT implement product source
- Do NOT approve gates
- Do NOT change DEC-033
- Do NOT push

## Acceptance Criteria
All 8 invariants above are satisfied.

## Evidence Requirements
Part of CHATGPT-MEMORY-LOCAL-SYNC sprint evidence bundle.

## Validation Requirements
- Verify memory/00-index.md contains memory/24 entry
- Verify AGENTS.md contains AF13 and AF14
- Verify GOVERNANCE.md contains 26.11 and 26.12
- Verify docs/automation/fresh-chat-project-bootstrap.md exists
- Verify registry gate_11 approved: false for FODS and FODT

## Next Dependency
Should be refreshed after any sprint that changes:
- Commercial product direction
- Gate state
- DEC-033 or other major decisions
- AI policy
- Generated requirements status
