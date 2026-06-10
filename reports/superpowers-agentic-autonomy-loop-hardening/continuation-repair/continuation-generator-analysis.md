# Continuation Generator Analysis
Sprint: FORMAT-FACTORY-AUTONOMY-LOOP-HARDENING-AFTER-H4-001
Lane: L1

## Problem

After FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001 completed (H4 proof, exit 0),
the supervisor continuation generator produced `reports/supervisor/next-sprint.md` with:

- Sprint ID: `FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001`
- Stream: `mainstream`
- Focus: "Product deepening — .NET commercial + Python FOSS + dogfood + packaging"
- Tasks: TASK-001 (product gaps), TASK-002 (commit candidate)

This is a **stale product prompt routing failure**. The generator does not know that the
human operator submitted a specific next sprint (AUTONOMY-LOOP-HARDENING-AFTER-H4-001).

## Root Cause

The `generate_next_worker_prompt.py` script reads from `selected-product-gaps*.json` and
the mainstream stream to produce the next sprint prompt. It has no mechanism to:

1. Detect that a human-submitted sprint brief overrides generated output
2. Preserve the agentic autonomy continuation context after an autonomy-focused sprint
3. Write an autonomy-continuation sprint instead of a product sprint

## Impact

If the autonomous continuation loop is active and reads `reports/supervisor/next-sprint.md`
naively as the next sprint, it would execute product work instead of the autonomy loop
hardening sprint. This defeats the purpose of building an agentic loop.

## Verified Override (This Sprint)

The user submitted FORMAT-FACTORY-AUTONOMY-LOOP-HARDENING-AFTER-H4-001 as the explicit
next sprint brief. This sprint OVERRIDES `reports/supervisor/next-sprint.md`.

Override authority: human operator explicit submission > supervisor-generated next-sprint.md

## Continuity Policy (Documented)

The following policy should govern autonomy continuation:

### Priority Order for Next Sprint Selection

1. **Human-submitted sprint brief** (explicit user message) — HIGHEST PRIORITY
2. **`.local/supervisor/continuation-signal.json` `next_sprint_path`** — if it points
   to a specific autonomy sprint (not `reports/supervisor/next-sprint.md`)
3. **`reports/supervisor/next-sprint.md`** — supervisor-generated, LOWEST PRIORITY
   for autonomy continuation sprints

### Override Trigger Conditions

The generated `next-sprint.md` should be OVERRIDDEN when:
- The current sprint is an autonomy-focused sprint (H-level advancement)
- A manually-submitted sprint brief is present in the conversation
- The continuation-signal `source_sprint_id` is an autonomy sprint

### Recommended Future Fix

Add an `autonomy_sprint_override_path` field to `continuation-signal.json` pointing to
the next autonomy sprint brief. The continuation loop should check this field first before
reading `next-sprint.md`.

Example signal enhancement:
```json
{
  "autonomous_continue": true,
  "autonomy_sprint_override_path": "reports/superpowers-agentic-autonomy-loop-hardening/final-handoff/next-execution-prompt.md",
  "next_sprint_path": "reports/supervisor/next-sprint.md"
}
```

## Verdict

Override applied for this sprint. Loop hardening sprint (FORMAT-FACTORY-AUTONOMY-LOOP-HARDENING-AFTER-H4-001)
is the active sprint. Product next-sprint.md is NOT executed this iteration.
