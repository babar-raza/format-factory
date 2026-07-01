# Taskcard: CHATGPT-MEMORY-LOCAL-SYNC

## Status
COMPLETED

## Purpose
Sync durable project direction, commercial product requirements, AI strategy, generated-requirements
strategy, and controlled swarm workflow from the ChatGPT session into local repo memory and
governance files. Ensure future chats/agents can continue from disk without relying on ChatGPT saved memory.

## Scope
- Memory file creation (memory/24-chatgpt-session-memory-sync-20260513.md)
- Memory index update (memory/00-index.md)
- Fresh-chat bootstrap docs (docs/automation/fresh-chat-project-bootstrap.md, .yaml)
- Continuity map (reports/planning/current-project-continuity-map-20260513.md, .yaml)
- Governance gap check and updates (AGENTS.md AF13-AF14, GOVERNANCE.md 26.11-26.12)
- Governance reports (reports/governance/chatgpt-memory-local-sync-20260513.md, .yaml)
- Taskcards (CHATGPT-MEMORY-LOCAL-SYNC.md, FRESH-CHAT-BOOTSTRAP.md, LOCAL-MEMORY-CONTINUITY.md)
- Evidence contract (tools/evidence/contracts/chatgpt-memory-local-sync.yaml)
- Evidence bundle (.local/chatgpt-memory-local-sync-20260513.zip)
- Metadata (.local/chatgpt-memory-local-sync-20260513-metadata/)

## Non-Goals
- Do NOT implement product source code
- Do NOT approve Gate 11
- Do NOT change DEC-033
- Do NOT create .NET FOSS source
- Do NOT push to remote
- Do NOT run package publish

## Acceptance Criteria
- memory/24-chatgpt-session-memory-sync-20260513.md created with 18 required sections
- docs/automation/fresh-chat-project-bootstrap.md and .yaml created and pasteable
- reports/planning/current-project-continuity-map-20260513.md and .yaml created
- reports/governance/chatgpt-memory-local-sync-20260513.md and .yaml created
- AGENTS.md §AF13 and §AF14 added
- GOVERNANCE.md §26.11 and §26.12 added
- memory/00-index.md updated with memory/24 entry
- Evidence contract with 20 semantic checks created
- Evidence bundle passing BUNDLE_VALIDATION --check-no-pending
- No product source modified
- No Gate 11 approval
- DEC-033 Option B preserved

## Evidence Requirements
- Evidence contract: tools/evidence/contracts/chatgpt-memory-local-sync.yaml
- Evidence bundle: .local/chatgpt-memory-local-sync-20260513.zip
- Metadata directory: .local/chatgpt-memory-local-sync-20260513-metadata/
- BUNDLE_VALIDATION: PASS --check-no-pending

## Allowed Files
See sprint authorization: memory/, docs/fresh-chat-project-bootstrap.*, reports/governance/,
reports/planning/, taskcards/CHATGPT-MEMORY-LOCAL-SYNC.md, taskcards/FRESH-CHAT-BOOTSTRAP.md,
taskcards/LOCAL-MEMORY-CONTINUITY.md, AGENTS.md (narrow only), GOVERNANCE.md (narrow only),
tools/evidence/contracts/chatgpt-memory-local-sync.yaml, .local/ metadata directory

## Prohibited Actions
See AGENTS.md AF13-AF14 and sprint authorization. No source, no tests, no Gate 11, no push,
no DEC-033 change, no broad staging.

## Validation Requirements
- python tools/evidence/check_current_state_consistency.py
- python tools/governance/check_methodology_links.py
- BUNDLE_VALIDATION: PASS

## Next Dependency
- GENERATED-REQUIREMENTS-IV-SPRINT (independent verification of generated requirements)
- Then: DOTNET-ENTITY-EXPANSION-SWARM (implement broader entity coverage)
