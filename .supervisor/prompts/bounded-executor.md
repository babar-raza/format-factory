---
espanso_provenance:
  source_trigger: ":ff-execute-short-context-plan"
  source_block: 36
  source_line_range: [45455, 46446]
  gap_id: GAP-ESP-002
  extraction_date: "2026-07-03"
  capability_id: bounded-execution
prompt_id: ESP-PROMPT-1
title: "Bounded Plan Executor (Short-Context)"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: short
---

# Bounded Plan Executor — Short-Context Taskcard Runner

## Short-Context View (use this if context is limited)

You are executing a Format Factory plan one taskcard at a time.

**Rule 1:** Read the plan file. Find the first PENDING taskcard. Execute only that one.
**Rule 2:** All state must live in the repository — never in chat memory.
**Rule 3:** After each taskcard: update its status in the plan file, write a checkpoint.
**Rule 4:** Mark DONE only when the done-check passes AND you verified the actual result.
**Rule 5:** Stop after one taskcard. The next session will read the plan and continue.

---

## Full Protocol

### Prerequisites
- An active plan file must exist in the repository (`plans/` or `plans/.claude/`)
- The plan must contain taskcards with explicit PENDING / IN_PROGRESS / DONE status fields
- The agent must be able to read and write the plan file

### When to Use
- Agent has a short or limited context window
- Resuming after context compaction
- Executing a plan that is too large to hold in working memory
- When the per-chat plan lock specifies a single execution mode

### When NOT to Use
- When the full `/autonomous-loop` is available and context permits
- When no plan file is loaded (use ledger work instead)
- When taskcards have no explicit done-checks

### Execution Loop

```
STEP 1: LOCATE PLAN
  → Read active-plan-lock.json for the canonical plan path
  → If absent: search plans/.claude/ for the most recently modified plan
  → Bind EXACTLY ONE plan file. Do not execute across multiple plans.

STEP 2: READ PLAN STATE
  → Parse ALL taskcards and their current status
  → Identify the first PENDING taskcard (by order in the plan)
  → If none found: report plan complete and stop

STEP 3: RECORD TASK START
  → Update taskcard status to IN_PROGRESS in the plan file (write to repo)
  → Log: "Starting taskcard <TC-ID>"

STEP 4: LOAD MINIMUM CONTEXT
  → Read only files required by THIS taskcard
  → Do not load the entire portfolio or unrelated evidence

STEP 5: EXECUTE EXACT STEPS
  → Follow the taskcard implementation_steps exactly
  → Do not redesign unless a step is impossible, unsafe, or factually stale
  → Do not combine this taskcard with the next one

STEP 6: RUN DONE-CHECK
  → The taskcard must specify a verification_steps or done_check field
  → Run the exact check described
  → If it passes: mark DONE
  → If it fails: keep IN_PROGRESS, write a checkpoint with failure details

STEP 7: VERIFY ACTUAL RESULT
  → Confirm the output exists, the test passes, or the artifact is correct
  → Never mark DONE because code was written — only when the done-check passed

STEP 8: UPDATE PLAN STATUS
  → Write DONE (or BLOCKED with reason) to the plan file
  → Include the verification evidence (file path, test name, or output)

STEP 9: WRITE CHECKPOINT
  → Append to `.local/supervisor/bounded-exec-checkpoint.json`:
    {
      "plan_path": "<path>",
      "taskcard_id": "<TC-ID>",
      "status": "DONE|BLOCKED",
      "timestamp": "<ISO-8601>",
      "next_pending": "<TC-ID or null>"
    }

STEP 10: SELECT NEXT OR STOP
  → If more PENDING taskcards remain: report next TC-ID and stop
  → The calling agent or next session will pick up from the checkpoint
```

### Repository State Contract
- The plan file is the authoritative state — not chat memory
- Every status transition must be written to the plan file immediately
- A crashed or timed-out session can always resume from the plan file
- The checkpoint file provides an optional fast-resume hint but is not required

### Forbidden Actions
- Combining multiple taskcards in one pass
- Marking DONE without running the done-check
- Redesigning the plan unless a taskcard is proven impossible
- Loading evidence or context for future taskcards
- Creating new plans mid-execution

### Evidence
- Each completed taskcard produces evidence in `.local/evidences/<run_id>/`
- Reference the taskcard ID in the evidence declaration
- Minimum: log the done-check result and the file(s) changed

### Completion Gate
The session is complete when:
- Exactly one taskcard moved from PENDING to DONE (or BLOCKED)
- The plan file is updated
- The checkpoint is written
- The next PENDING taskcard ID is reported to the caller
