# pilot-a-single-iteration — Single Iteration Proof Plan

**plan_type:** machinery_hardening
**mission_id:** PILOT-A-001
**behavioral_iterations_required:** 1

## Taskcard Status Table

| Taskcard | Status |
|----------|--------|
| TC-PILOT-A-001 | CLOSED |
| TC-PILOT-A-CLOSE | CLOSED |

## TC-PILOT-A-001 — Execute trivial machinery change (CLOSED)

Execute: write a timestamp to `tests/supervisor/pilots/pilot-a-artifact.txt`
Verify: file exists with current timestamp
Status: CLOSED (executed during pilot setup)

## TC-PILOT-A-CLOSE — Lifecycle audit gate (CLOSED)

With B1 implemented:
- At iter=0: AUDIT_REQUIRES_ITERATION (blocked by B1: 0 < 1)
- At iter=1: B1 guard passes (1 >= 1, verdict=AUDIT_PASS)

Status: CLOSED (proven by pilot A execution)
