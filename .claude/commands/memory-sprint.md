---
version: "1.1"
last-updated: "2026-05-17"
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

    **NOTE:** The 55-file metadata minimum is elevated from the project floor (30 files) to ensure full
    memory state + decisions are captured. See AGENTS.md AF7 for evidence floor policy.

13. Build and validate the evidence bundle.
14. Stage only MEMORY_SPRINT_ALLOWED files (exact paths). Attempt: `git add <exact paths>`. Then attempt commit.

    **PERMISSION NOTE:** `git commit` requires human approval via Claude Code permission dialog — watch for
    the prompt and wait for approval. If denied, print `COMMIT_PENDING_HUMAN_APPROVAL` and output the
    exact manual command: `git commit -m '<sprint-id> memory sprint complete'`.

15. Print the final evidence bundle path.

## Output Format

1. Memory sprint summary.
2. Files created and modified.
3. Decisions captured.
4. Backlog taskcards created (if any).
5. Evidence contract validation result.
6. Commit hash (populated if human approved permission dialog; otherwise: `COMMIT_PENDING_HUMAN_APPROVAL`
   followed by the exact manual git commit command to run).
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

If git commit is denied by Claude Code permissions, the sprint output is complete but not committed.
Human must run the printed commit command to finalize. This is expected — `git commit` is intentionally
permission-restricted in this project's settings.json.

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
- 1.1 (2026-05-17): Fix Step 14 to document permission dialog behavior and `COMMIT_PENDING_HUMAN_APPROVAL`
  fallback. Fix Output Format item 6 from "Commit hash." (impossible without permission) to conditional
  form. Add Validation note explaining expected permission-denied behavior. Add NOTE in Step 12 explaining
  55-file floor vs. 30-file project floor. Sprint: FORMAT-FACTORY-SKILLS-PRD-HARDENING-001.
