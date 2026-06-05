# Evidence Handling Principles

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 44.5
**Source:** memory/67-local-memory-governance-sync-20260604.md Section 9

## Core Rule

**Do not waste time correcting evidence packaging/metadata unless it blocks execution or important proof.**

Focus on: implementation, product progress, moving the project in the right direction.

## When Evidence Repair IS Justified

Evidence repair is justified ONLY when required to:
1. Prove important work (missing materialized proof of real output)
2. Prevent false claims (overclaimed work items without backing)
3. Fix missing materialized proof that blocks independent verification
4. Unblock another stream (e.g., Supervisor cannot verify Skills output)

## When Evidence Repair is NOT Justified as Main Sprint Goal

| Scenario | Response |
|---|---|
| Non-blocking ZIP entry count mismatch | Report caveat, continue |
| Wrong-stream global-state in bundle | Report caveat, continue |
| Evidence-quality-score=0.0 but work is real | Report caveat, continue |
| Continuation-signal conflict from prior sprint | Report caveat, continue |
| Missing sample outputs in bundle | Report caveat, continue |
| Taskcard-state not fully closed in ZIP | Report caveat, continue |

These are all symptoms of imperfect tooling, not evidence of bad product work.

## What Every Sprint Must Still Require

Even when deprioritizing evidence cleanup, every sprint prompt must still require:
- Evidence bundle or review package (ZIP)
- Absolute review package path in final response (C:\Users\prora\...\)
- SHA-256 in final response
- Evidence declaration YAML written

## Review Behavior

**Future reviews must:**
1. Report evidence caveats honestly (list them, classify as blocking/non-blocking)
2. Continue safe forward work (do not block on non-blocking caveats)
3. NOT make non-blocking evidence caveats the sprint goal

**Blocking vs. non-blocking:**
- **Blocking:** Missing proof of core work items, false PASS claims, overclaimed work
- **Non-blocking:** ZIP metadata issues, wrong-stream global state, missing optional sample outputs

## Relationship to Declaration-Driven Closeout

The declaration-driven closeout (`autonomous_cycle.py --declaration`) is the REQUIRED closeout mechanism. It is not optional. But the closeout is a final step, not the sprint's primary mission.

Sprint mission → product/implementation work → closeout evidence → move on.

Do not run the sprint backward (start with evidence packaging, work backward to implementation).
