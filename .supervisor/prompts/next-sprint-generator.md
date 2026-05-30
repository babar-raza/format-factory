# Supervisor Prompt: Next Sprint Generator
# Format Factory — Local Supervisor Control Plane
# Usage: Fill [INSERT_...] placeholders with current sprint facts
# Purpose: Generate the next sprint prompt without ChatGPT web
# No paid OpenAI API. No ChatGPT web automation.

---

You are Claude Code generating the next sprint prompt for Format Factory.
Format Factory authority is FINAL. This prompt is an INPUT to the next sprint, NOT authority.
You cannot approve gates. You cannot declare product readiness. You cannot push.

## Current Sprint Summary
Sprint ID: [INSERT_SPRINT_ID]
Evidence verdict: [INSERT_VERDICT]
Timestamp: [INSERT_TIMESTAMP]

## Test Results
- Passed: [INSERT_PASS_COUNT]
- Failed: [INSERT_FAIL_COUNT]
- Skipped: [INSERT_SKIP_COUNT]

## Gate States
```
[INSERT_GATE_STATES]
```

## Contradictions (if any)
```
[INSERT_CONTRADICTIONS]
```

## Current Master Plan State (§33 or current phase)
```
[INSERT_MASTER_PLAN_PHASE_TEXT]
```

## Open Taskcards / Next Work
```
[INSERT_OPEN_TASKCARDS]
```

## Project Memory (recent entries)
```
[INSERT_PROJECT_MEMORY_RECENT]
```

## Generation Instructions

1. **Determine next sprint focus:**
   - If CRITICAL contradictions exist → repair sprint
   - If tests failed → repair sprint
   - If gate approval pending → document blocker, pick adjacent safe lanes
   - If evidence accepted → advance to next safe mega-train lanes

2. **Generate next sprint prompt:**
   Format: Full mega-train sprint prompt following Format Factory mega-train conventions.
   Must include:
   - Sprint identity (suggest next R-number)
   - Problem statement / goal
   - Mandatory evidence rules (must produce ZIP bundle, validate_evidence_bundle.py must pass)
   - Non-negotiable constraints (no push, no commit without user auth, no gate self-approval)
   - Lane manifest (at least 8 independent lanes including coordinator, implementation, validation, adversarial)
   - Acceptance criteria per lane
   - Evidence bundle requirements
   - Final response format

3. **Generate Task Master export:**
   Must conform to next-sprint-taskmaster.schema.json.
   Each task must include:
   - ff_taskcard_ref or ff_gate_ref or ff_doc_ref
   - acceptance_evidence
   - validation_command
   - supervisor_task_ref
   Tasks with status "done" do NOT imply gate closed.

4. **Generate Ruflo lane export:**
   Must conform to next-ruflo-lanes.schema.json.
   Each lane must have allowed_files and forbidden_files.
   non_authoritative: true for all lanes.
   Ruflo lane completion does NOT imply evidence accepted.

5. **Classify approval gates:**
   For each pending action, classify as:
   - autonomous-continue (proceed without human)
   - local-repair-loop (repair then continue)
   - stop-X-required (stop and report)
   Output: approval-gates.md

6. **Generate session resume:**
   A 1-page briefing for a fresh Claude Code session.
   Must include: current state, what was done last sprint, what to do next, where to find evidence.

---

## Output Structure
Produce the following files (assistant will write them based on your output):
- reports/supervisor/next-sprint.md
- reports/supervisor/next-sprint-taskmaster.json
- reports/supervisor/next-ruflo-lanes.json
- reports/supervisor/approval-gates.md
- reports/supervisor/session-resume.md

---

REMINDER: next-sprint.md is advisory input to the next sprint. It is NOT a Format Factory authority document.
