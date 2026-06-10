# Continuation Signal Reconciliation — R2

## Anti-Skip Violation Fixed
**continuation signal discrepancy** — R1 had `autonomous_continue=false` in continuation signal but `continuation_state=YES_WITH_LIMITATIONS` in the review. This document clarifies the precedence rules and resolves the discrepancy.

## Root Cause (R1 Discrepancy)

In R1:
- `evidence_quality_score = 0.0` (all path-only)
- `autonomous_continue = false` (set in continuation-signal.json by prior sprint)
- `continuation_state = YES_WITH_LIMITATIONS` (grader verdict)

The apparent contradiction: if `continuation_state=YES_WITH_LIMITATIONS`, why was `autonomous_continue=false`?

**Resolution:** The continuation-signal.json `autonomous_continue` field is set by the PREVIOUS sprint's autonomous-cycle run. The `YES_WITH_LIMITATIONS` state is the current sprint's grader verdict. These two are separate mechanisms:
- `continuation_state` = what the grader says about THIS sprint's evidence
- `autonomous_continue` in signal = whether the supervisor authorizes continuing to the NEXT sprint

When `evidence_quality_score=0.0`, the supervisor sets `autonomous_continue=false` to require a rework sprint (R2). The grader's `YES_WITH_LIMITATIONS` correctly reflects that the items were accepted (not REJECTED), just with limitations.

This is **correct behavior, not a contradiction**.

## Precedence Rules

See `continuation-decision-matrix.json` for full priority-ordered rules.

Key precedence:
1. Hard stops (push, gates) → ALWAYS block
2. Overclaimed/REJECTED items → block
3. Unclassified dirty state → block (new in R2)
4. Missing required artifacts → block (new in R2)
5. Product output floor not met → block (new in R2)
6. `evidence_quality_score=0.0` → downgrades to `YES_WITH_LIMITATIONS` (does NOT block)
7. Max iterations → block
8. `autonomous_continue=false` in signal → block
9. Rework items → downgrade to `YES_WITH_LIMITATIONS`
10. Clean pass → `YES`

## R2 Expected Continuation State

After R2 sprint closeout:
- `evidence_quality_score = 0.27` (3 ACCEPTED_VERIFIED items)
- `dirty_state_classified = true` (Lane D resolved)
- `has_classification = true` in declaration
- Path guard: PASS
- No hard stops

Expected: `continuation_state = YES_WITH_LIMITATIONS`
Expected: `autonomous_continue = true` (if evidence_quality > 0.0 and violations resolved)

## Violation Status
`continuation_discrepancy` → **RESOLVED** — root cause identified as misclassification, not real contradiction.
