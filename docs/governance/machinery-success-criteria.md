# Machinery Success Criteria

**Added:** 2026-06-03
**Authority:** plans/master-plan.md Section 43

## Definition

"Machinery" means any lane that is not Mainstream Product: Acceleration, Skills, and Supervisor.

## Closeout Questions

Every machinery sprint must answer at closeout:

1. **What product blocker did this remove?**
   - Name the specific blocker (e.g., "FODS save-after-edit was blocked by missing skill definition").
   - If no blocker was removed, answer "None" and proceed to question 4.

2. **What product throughput did this improve?**
   - Quantify if possible (e.g., "reduced FODS API addition from 3 manual steps to 1 skill invocation").
   - If not quantifiable, describe the improvement qualitatively.

3. **What false verdict did this prevent?**
   - Name the specific false PASS or false STOP.
   - If none, answer "None."

4. **If none of the above: why was this sprint necessary?**
   - Valid answers: "Foundation for next sprint which will [specific product improvement]", "Repair of broken tool that blocks [specific product work]."
   - Invalid answers: "Improved code quality", "Added tests for machinery", "Refactored supervisor internals."

## Grading Impact

| Closeout Answer | Maximum Verdict |
|---|---|
| Removes product blocker | ACCEPTED |
| Improves product throughput | ACCEPTED |
| Prevents false verdict | ACCEPTED |
| Foundation for next product improvement (with specific plan) | ACCEPTED_WITH_LIMITATIONS |
| No product justification | OVERCLAIMED (requires rework) |

## Anti-Patterns

These patterns indicate machinery drift:
- Machinery sprint that only repairs its own evidence
- Machinery sprint that only generates reports no lane consumes
- Machinery sprint that adds tests only for machinery tools
- Acceleration sprint that only validates prompt quality without producing product acceleration
- Supervisor sprint that only audits evidence without making routing decisions
- Skills sprint that only defines skills without Mainstream consuming them
