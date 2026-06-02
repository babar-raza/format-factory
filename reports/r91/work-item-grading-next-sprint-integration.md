---
sprint: R91
generated_by: r91-worker
---

# Work-Item Grading → Next Sprint Integration

## Summary

Work-item grades from the R91 declaration drive the structure of the next `next-sprint.md`. Accepted items are not repeated. Rework items are carried forward with exact repair instructions. New POC work is added from the gap matrix.

## Grade-to-Sprint Mapping

| Grade Status | Action in next-sprint.md |
|---|---|
| ACCEPTED | Not repeated. Mentioned in "completed baseline" section only. |
| REWORK_REQUIRED | Added to LANE-CRITICAL-REWORK with exact `rework_instruction` text |
| OVERCLAIMED | Added to LANE-CRITICAL-REWORK with scope-narrowing instruction |
| INSUFFICIENT_EVIDENCE | Added to LANE-CRITICAL-REWORK with evidence creation instruction |
| BLOCKED_EXTERNAL_GATE | Listed in "blocked — awaiting human action" section, not in lanes |
| DEFERRED_WITH_REASON | Listed in "deferred" section with reason, not in active lanes |

## next-sprint.md Structure After R91

```markdown
## Context Pack (read before starting)
[context pack header — 10 mandatory reads]

## Completed Baseline (do not repeat)
- [list of accepted R91 item_ids]

## Blocked (awaiting human action)
- [list of BLOCKED_EXTERNAL_GATE items with gate reference]

## LANE-CRITICAL-REWORK
[rework items with repair instructions]

## LANE-SAFE-PRODUCT-A: FODS .NET DeepWork
[selected POC gap from gap selector priority 1]

## LANE-SAFE-PRODUCT-B: FODT .NET DeepWork
[selected POC gap from gap selector priority 1]

## LANE-DOGFOOD: Dogfood Bridge
[next unimplemented dogfood bridge from strategy]

## LANE-PACKAGE-INSTALL: Install Proof
[package install proof for any new changed products]

## LANE-CLOSEOUT (MANDATORY — always last)
evidence-declaration + autonomous-cycle
```

## Broad Multi-Mega-Train Structure

The next sprint uses the multi-mega-train format. Each lane is an independent train that can be executed in any order (except CLOSEOUT which is always last). Trains:
- Do not depend on each other (safe to parallelize)
- Each have their own evidence output path
- Each contribute to the declaration's `planned_work_items`

## Governed Skill / Handoff Rules

Each lane in next-sprint.md includes:
- Skill to use (from `.supervisor/skill-registry.yaml`)
- Governed command path (`.claude/commands/{skill}.md`)
- Ledger entry requirement (if src changes needed)
- Acceptance criteria (verbatim from gap selector output)

## Evidence-Declaration Closeout Footer

Always present as the final section of next-sprint.md. Text is identical across all generated sprints (static template). See `reports/r91/rework-plus-new-work-generation.md` for the footer content.

## Autonomous Continuation After Next Sprint

If the next sprint's autonomous-cycle exits 0 and all stop conditions are false, the loop continues. The iteration counter increments in `.local/supervisor/continuation-signal.json`. After `max_iterations` the loop stops and reports to the user.
