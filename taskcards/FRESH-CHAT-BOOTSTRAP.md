# Taskcard: FRESH-CHAT-BOOTSTRAP

## Status
COMPLETED

## Purpose
Create a fresh-chat bootstrap document that a new ChatGPT or Claude session can use to restore
project context from local disk, without relying on external memory.

## Scope
- docs/fresh-chat-project-bootstrap.md — human-readable, pasteable into new chat
- docs/fresh-chat-project-bootstrap.yaml — machine-readable version with structured fields

## Non-Goals
- Do NOT implement product source
- Do NOT approve gates
- Do NOT include secrets, tokens, or raw spec text
- Do NOT store raw LLM transcripts

## Acceptance Criteria
- docs/fresh-chat-project-bootstrap.md exists and is pasteable into new chat context
- docs/fresh-chat-project-bootstrap.yaml exists with all required structured fields:
  - repo_path
  - read_first_files
  - current_decisions
  - current_capability_state
  - gate_state
  - ai_policy_summary
  - prohibited_actions
  - next_recommended_sprints
  - latest_known_memory_file
- Both documents reflect current project state (FODS/FODT Gates 1-10 PASSED, Gate 11 in progress)
- Both documents include warning not to rely only on ChatGPT saved memory
- Both documents instruct to use local repo files as authority

## Evidence Requirements
Part of CHATGPT-MEMORY-LOCAL-SYNC sprint evidence bundle.

## Allowed Files
- docs/fresh-chat-project-bootstrap.md
- docs/fresh-chat-project-bootstrap.yaml

## Prohibited Actions
- No product source
- No gate approval
- No push
- No secrets

## Validation Requirements
File existence confirmed in evidence bundle manifest.

## Next Dependency
Used by: Every new chat/agent session starting after 2026-05-13.
Updated by: Any sprint that changes major project direction.
