# Plan Hardening Prompt Template

**Mode:** PLAN MODE ONLY
**Sprint type:** PLAN MODE
**Purpose:** Use this template when asking an agent to review, challenge, and harden an existing draft plan.

---

MODE:
PLAN MODE ONLY.

Sprint type:
PLAN MODE -- Plan Review and Hardening.

Sprint name:
Harden: <describe the plan being reviewed>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary input:
<path to the draft plan document, or paste the plan below>

Goal:
Review the attached plan. Challenge every claim against repo truth. Identify stale state,
contradictions, missing validation steps, missing evidence requirements, and overbroad scope.
Produce a hardened execution-ready version of the plan.

This is PLAN MODE ONLY. Do not create or modify any repo files. Do not create any evidence bundle.
Do not commit. Do not push.

Read first:

Read the following files before reviewing the plan:
<list every file the plan references, e.g.:>
1. plans/master-plan.md
2. AGENTS.md
3. GOVERNANCE.md
4. docs/planning-methodology.md
5. docs/plan-hardening-checklist.md
6. registry/format-registry.yaml (if the plan mentions gate status)
7. relevant taskcards
8. relevant evidence contracts

Also run:
- git log --oneline -10
- git status --short
- python tools/evidence/check_current_state_consistency.py

Hardening review checklist (verify all 22 items from docs/plan-hardening-checklist.md):

For each NO answer, identify the specific gap and write the fix.

Hardening output format:

Produce the hardened plan as a structured document with:
1. Confirmed facts (with file path citations).
2. Corrected claims (original vs. corrected, with reason).
3. Removed ambiguities (list what was removed and why).
4. Added validation steps.
5. Added stop conditions.
6. Added forbidden paths.
7. Added self-challenge section.
8. Final plan score (X/22 from plan hardening checklist).

Do not push.
Do not create files.
Do not commit.

Final line:
NEXT_PROMPT_READY: yes (once the hardened plan is ready for execution handoff)
