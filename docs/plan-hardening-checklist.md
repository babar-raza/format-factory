# Plan Hardening Checklist

**Document type:** Checklist
**Created:** 2026-05-08 (memory-planning-methodology-and-agent-handoff sprint)
**Visibility:** internal
**Use:** Before converting any prose plan into an execution prompt, verify all items below. If any item is NO, fix it before proceeding.

---

## Section 1: Scope and State

1. Does the plan have an exact scope?
   - YES: The plan lists specific files to create, modify, or read.
   - NO: The plan says "update relevant files" or "handle as needed."

2. Does the plan identify current state from repo files?
   - YES: The plan references specific commits, registry entries, or file states.
   - NO: The plan relies on summaries or agent memory alone.

3. Does the plan inspect all referenced files?
   - YES: Every file mentioned in the plan has been read by the agent before planning.
   - NO: The plan mentions files the agent has not read in this session.

4. Does the plan separate facts from assumptions?
   - YES: Facts are cited with source (file path + line number or section). Assumptions are labeled.
   - NO: The plan presents agent inferences as facts without citation.

5. Does the plan identify stale state?
   - YES: Any "Latest commit: PENDING" markers or outdated status fields are listed.
   - NO: The plan does not check for stale state.

6. Does the plan identify contradictions?
   - YES: Conflicting claims between files are listed and one is designated authoritative.
   - NO: The plan accepts all file content as consistent without checking.

---

## Section 2: Paths and Permissions

7. Does the plan define allowed paths?
   - YES: A specific list of files and directories the agent may create or modify.
   - NO: The plan says "create the needed files" without listing them.

8. Does the plan define forbidden paths?
   - YES: Explicit list of files and directories the agent must not touch.
   - NO: Forbidden paths are not named (or only implied).

9. Does the plan separate MAIN SPRINT, SECONDARY SPRINT, and MEMORY SPRINT owned files?
   - YES: Each file in git status is classified by stream ownership.
   - NO: The plan stages files without checking stream ownership.

---

## Section 3: Validation and Evidence

10. Does the plan define validation commands?
    - YES: Exact command lines with expected output format.
    - NO: The plan says "check that it works" or "verify the output."

11. Does the plan define evidence outputs?
    - YES: Evidence contract path, metadata directory, bundle output path, min_metadata_count.
    - NO: The plan mentions an evidence bundle without specifying the contract or output path.

12. Does the plan define taskcard updates?
    - YES: Each affected taskcard is named with its current and target status.
    - NO: Taskcard updates are vague ("update relevant taskcards").

13. Does the plan define current-state file updates?
    - YES: Files like memory/09, plans/master-plan.md Section 33, and registry entries are updated specifically.
    - NO: The plan does not mention current-state file updates.

---

## Section 4: Control Flow

14. Does the plan define stop conditions?
    - YES: Every major check has a stop condition (e.g., "if BUNDLE_VALIDATION: FAIL, stop and print BLOCKED").
    - NO: The plan proceeds regardless of check outcomes.

15. Does the plan define final statuses?
    - YES: The possible final states are defined (PASS, FAIL, BLOCKED, NEEDS_REPAIR).
    - NO: The plan ends ambiguously.

16. Does the plan prevent broad stash and broad cleanup?
    - YES: No git stash -u, no git reset --hard, no git clean -fd unless explicitly scoped and justified.
    - NO: The plan includes broad cleanup commands as default behavior.

---

## Section 5: Architecture and Governance

17. Does the plan preserve discovered gaps?
    - YES: Any out-of-scope gap is added to ROADMAP.md, master-plan.md backlog, a taskcard, and memory.
    - NO: The plan silently skips discovered gaps.

18. Does the plan prevent hidden manual human work where the agent can act?
    - YES: The plan includes agent-executable steps for all feasible work, not placeholders for the human.
    - NO: The plan includes steps labeled "(human to do this part)" for work the agent could do.

19. Does the plan prevent product source when not authorized?
    - YES: Forbidden paths include src/python/fods/, src/python/fodt/, src/net/.
    - NO: Product source paths are not listed as forbidden.

20. Does the plan prevent LLM/embedding misuse?
    - YES: No production LLM API calls, no embedding creation, no vector DB creation unless explicitly authorized.
    - NO: The plan calls LLM endpoints or creates embeddings without explicit human authorization.

---

## Section 6: Final Output

21. Does the plan require the final evidence bundle path?
    - YES: The last line of the agent final response must be: EVIDENCE_BUNDLE: <absolute Windows path to zip>.
    - NO: The plan does not require the bundle path in the response.

22. Does the plan include a self-challenge section?
    - YES: Minimum 17 yes/no questions covering all major sprint requirements.
    - NO: Self-challenge is missing or has fewer than 10 questions.

---

## Scoring

Count YES answers.

- 22/22: Plan is execution-ready.
- 18-21/22: Plan needs minor additions before execution.
- 14-17/22: Plan needs significant hardening before execution.
- Below 14/22: Do not execute. Return to PLAN MODE and restructure.

Record the score in the plan hardening metadata file for this sprint.
