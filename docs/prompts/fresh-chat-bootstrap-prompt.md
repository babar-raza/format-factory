# Fresh Chat Bootstrap Prompt

**Mode:** PLAN MODE ONLY
**Purpose:** Use this as the first message in a fresh chat session to orient a new agent on the format-factory project state and planning style.

---

MODE:
PLAN MODE ONLY.

Sprint type:
PLAN MODE -- Fresh Chat Bootstrap.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Goal:
Orient yourself on the current project state so you can help the human continue work
without relying on conversation history. Read the required files, verify current state,
and confirm what the next action is.

Do not make any repo changes. Do not commit. Do not push. This is orientation only.

Read these files in order:

1. plans/master-plan.md (focus on Section 33: Run Commit Ledger, and current FODS/FODT status)
2. ROADMAP.md (focus on Phase 3 and Infrastructure Milestones)
3. AGENTS.md (focus on recent sections, currently through Section AC)
4. GOVERNANCE.md (focus on recent sections, currently through Section 22)
5. memory/00-index.md (read the index, then read the files listed under "Priority reading")
6. memory/09-current-state-before-phase1.md (current gate status)
7. memory/11-prompting-and-agent-style-rules.md (user preferences)
8. docs/planning-methodology.md (planning style and sprint type rules)
9. docs/agent-execution-handoff-standard.md (execution rules)
10. docs/fresh-chat-continuity-brief.md (strategic context summary)
11. registry/format-registry.yaml (current gate statuses)

Also run:
- git log --oneline -10
- git status --short
- python tools/evidence/check_current_state_consistency.py

After reading, produce a concise orientation summary:

1. Current phase and gate status (FODS and FODT).
2. What was completed in the most recent run.
3. What the next authorized action is.
4. What is blocked or pending human approval.
5. What is in backlog (not yet authorized).
6. Whether the working tree is clean.
7. Suggested next prompt type (MAIN SPRINT gate, MEMORY SPRINT, VERIFICATION, etc.).

Do not produce a next prompt yet. Confirm understanding with the human first.
Do not commit. Do not push.

Final line:
NEXT_PROMPT_READY: yes (once human confirms orientation is correct)
