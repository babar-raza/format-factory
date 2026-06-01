# Supervisor Grading Rubric

## 8 Grade Levels

| Grade | Meaning | Trigger Condition |
|-------|---------|-------------------|
| ACCEPTED | Work complete, evidence verified | completed + evidence found + tests pass |
| ACCEPTED_WITH_WARNINGS | Work done but minor gaps | partial + evidence found |
| REWORK_REQUIRED | Evidence incomplete or tests fail | completed + missing paths, OR partial + no evidence, OR tests failed |
| REJECTED | Evidence fundamentally wrong | Evidence contradicts acceptance criteria |
| BLOCKED_EXTERNAL_GATE | External approval blocks completion | declared status = blocked_external_gate |
| NOT_ATTEMPTED | Not started | declared status = not_started |
| NOT_IN_SCOPE | Item not relevant to this sprint | Item explicitly excluded |
| OVERCLAIMED | Declared complete but no evidence | completed + no evidence at any declared path |

## Grading Logic

```
if declared_status == "blocked_external_gate":
    grade = BLOCKED_EXTERNAL_GATE

elif declared_status == "not_started":
    grade = NOT_ATTEMPTED

elif declared_status == "completed":
    if no evidence found at any declared path:
        grade = OVERCLAIMED
    elif some declared paths missing:
        grade = REWORK_REQUIRED
    elif tests failed:
        grade = REWORK_REQUIRED
    else:
        grade = ACCEPTED

elif declared_status == "partial":
    if evidence found:
        grade = ACCEPTED_WITH_WARNINGS
    else:
        grade = REWORK_REQUIRED
```

## Critical vs Non-Critical

**Critical rework** (blocks autonomous continuation):
- OVERCLAIMED
- REJECTED

**Non-critical rework** (does not block autonomous continuation):
- REWORK_REQUIRED
- ACCEPTED_WITH_WARNINGS

**No rework needed:**
- ACCEPTED
- BLOCKED_EXTERNAL_GATE
- NOT_ATTEMPTED
- NOT_IN_SCOPE

## Evidence Inspection Rules

1. Each evidence_path in a work item is checked for file existence at `repo_root / path`.
2. A work item has evidence if at least one declared path exists.
3. Tests are checked via the declaration's `test_results` (passed/failed counts).
4. The supervisor does NOT run tests — it reads declared results.
5. For ZIP-based evidence (optional), the supervisor checks the ZIP exists but does not extract it.

## Overall Verdict

The overall verdict is derived from the worst grade across all items:
- If any OVERCLAIMED or REJECTED: verdict includes "CRITICAL_REWORK"
- If any REWORK_REQUIRED: verdict includes "REWORK_REQUIRED"
- If all ACCEPTED/ACCEPTED_WITH_WARNINGS: verdict is "ACCEPTED"
- If any BLOCKED_EXTERNAL_GATE with no critical: verdict includes "BLOCKED"

## Autonomous Continue Decision

```
critical_count = count(OVERCLAIMED) + count(REJECTED)
autonomous_continue = (critical_count == 0)
```

When `autonomous_continue` is False, the supervisor sets exit code 3 and the loop pauses for human review.
