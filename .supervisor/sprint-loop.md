# Local Supervisor Sprint Loop — Procedure
# Format Factory — Dual Orchestration
# This document describes the repeatable local supervisor loop that replaces
# the manual human ChatGPT upload/review/next-prompt cycle.

---

## What This Replaces

**Old manual loop:**
```
Human uploads evidence bundle → ChatGPT reviews → ChatGPT writes next prompt
  → Human pastes into Claude Code → Claude Code executes → evidence bundle
  → REPEAT
```

**New automated loop:**
```
supervisor_loop.py discover → validate → contradiction-detect → generate-next-sprint
  → export-taskmaster → export-ruflo → sync-memory → Claude Code reads artifacts
  → executes → produces evidence bundle → REPEAT
```

## Sprint Loop Steps

### Step 1: Discovery
```bash
python tools/supervisor/supervisor_loop.py discover
```
- Finds latest evidence bundle in .local/evidence/**/*.zip
- Reads bundle-metadata/sprint-id.txt from inside the ZIP
- Writes .supervisor/state/current-run.json with bundle path and sprint_id

### Step 2: Review and Validation
```bash
python tools/supervisor/supervisor_loop.py review --bundle <path>
```
- Validates the ZIP is readable
- Extracts facts: test_count, fail_count, skip_count, verdict, git_head, sprint_id, gate_states
- Detects PENDING markers
- Writes reports/supervisor/evidence-review.json (schema-validated)
- Writes reports/supervisor/evidence-review.md (assembled packet)

### Step 3: Contradiction Detection
```bash
python tools/supervisor/supervisor_loop.py review --bundle <path>
# (contradiction detection is part of the review step)
```
- compare_goal_to_evidence.py runs automatically
- Reads sprint contract from tools/evidence/contracts/
- Detects: tests failed, PENDING in final state, gate overclaim, SHA mismatch
- Writes reports/supervisor/contradictions.md (CRITICAL = stops loop)

### Step 4: Next Sprint Generation
```bash
python tools/supervisor/supervisor_loop.py next --bundle <path>
```
- Assembles supervisor packet from evidence facts + contradictions
- Generates reports/supervisor/next-sprint.md (full next-sprint prompt)
- Generates reports/supervisor/next-sprint-taskmaster.json (TM import ready)
- Generates reports/supervisor/next-ruflo-lanes.json (Ruflo lane plan)
- Generates reports/supervisor/approval-gates.md (classified: autonomous-continue / stop-X)
- Generates reports/supervisor/session-resume.md (fresh-session briefing)

### Step 5: Memory Sync
```bash
python tools/supervisor/supervisor_loop.py run-on-latest
# (memory sync is automatically invoked at end of run-on-latest)
```
- sync_local_memory.py appends to .supervisor/project-memory.md
- Idempotent for same sprint_id + bundle hash

### Step 6: Claude Code Reads Artifacts
- Claude Code reads reports/supervisor/session-resume.md
- Claude Code reads reports/supervisor/next-sprint.md
- Claude Code reads reports/supervisor/approval-gates.md
- If approval-gates.md says autonomous-continue → Claude Code proceeds
- If stop-X → Claude Code reports to user and waits

### Step 7: Execution
- Claude Code executes next sprint as normal mega-train
- Produces new evidence bundle in .local/evidence/
- GOTO Step 1

## Full One-Command Loop
```bash
python tools/supervisor/supervisor_loop.py run-on-latest
```
Runs: discover → review → contradiction-detect → next → export-taskmaster → export-ruflo → sync-memory

## Exit Codes
- 0: success — all outputs written
- 1: no bundle found
- 2: validation failed / malformed bundle
- 3: CRITICAL contradiction — autonomous loop stopped
- 9: unexpected error

## Human Gate Conditions
Stop loop and report to human ONLY for:
- credentials missing
- push/merge/deploy approval needed
- Format Factory gate approval needed (Babar Raza)
- governance conflict unresolvable
- paid API required
- MCP activation required (MODE 4)
- destructive action required
