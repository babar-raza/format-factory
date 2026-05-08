---
version: "1.0"
last-updated: "2026-05-08"
phase-available: "all"
gate-required: null
created-by: memory-planning-methodology-and-agent-handoff sprint
---

# /memory-sprint

Create a memory sprint to capture strategic decisions, architecture notes, or user preferences into durable local repo artifacts.

## Steps

1. Read memory/00-index.md, plans/master-plan.md, AGENTS.md, GOVERNANCE.md.
2. Read all existing memory files listed in the index.
3. Read docs/planning-methodology.md.
4. Read the latest evidence bundle to understand current sprint state.
5. Run git log --oneline -5, git status --short, and python tools/evidence/check_current_state_consistency.py.
6. Classify any dirty files as MEMORY_SPRINT_ALLOWED or stream-owned (do not stage MAIN_SPRINT_OWNED).
7. Create new memory file(s) capturing the specified decisions.
8. Update memory/00-index.md with the new file entry and stream history entry.
9. Update AGENTS.md, GOVERNANCE.md, plans/master-plan.md, and ROADMAP.md (additive only, no gate changes).
10. Create taskcards (status: proposed_pending_human_approval) for any out-of-scope backlog items.
11. Create the evidence contract for this memory sprint.
12. Create metadata files (minimum 55).
13. Build and validate the evidence bundle.
14. Stage only MEMORY_SPRINT_ALLOWED files. Commit.
15. Print the final evidence bundle path.

## Output Format

1. Memory sprint summary.
2. Files created and modified.
3. Decisions captured.
4. Backlog taskcards created (if any).
5. Evidence contract validation result.
6. Commit hash.
7. Stream declaration:
   - MEMORY SPRINT ONLY
   - NO MAIN SPRINT GATE CHANGED
   - NO SECONDARY EXECUTION STARTED
   - NO PRODUCT SOURCE CREATED
   - NO EMBEDDINGS OR VECTOR DB CREATED
   - NO PRODUCTION LLM CALL MADE
   - NO NEW SPECS DOWNLOADED
   - NO PUSH MADE
8. Final line: EVIDENCE_BUNDLE: <absolute Windows path to zip>

## Validation

Evidence bundle must pass BUNDLE_VALIDATION with at least 55 metadata files.
No MAIN SPRINT gate status may change.
No product source may be created.
No embeddings or vector DB may be created.

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
