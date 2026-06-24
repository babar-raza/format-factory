# Lane H — Supervisor and Continuation Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-H | **Requirement:** REQ-LANE-H

## 1. autonomous_cycle.py Step Map (2395 LOC, 33 STEP markers)

### Execution Order
| Step | Line | Action | Pre/Post Grade |
|------|------|--------|----------------|
| STEP 0a-refresh | ~272-330 | SAL refresh check (non-blocking) | PRE |
| STEP 0b | ~340 | Plan lock check | PRE |
| STEP 1a | ~400 | Declaration loading + validation | PRE |
| STEP 1b | ~450 | Declaration enrichment | PRE |
| STEP 2a | ~500 | Evidence path verification | PRE |
| STEP 2b | ~600 | Test verification | PRE |
| STEP 2c | ~650 | Changed files analysis | PRE |
| STEP 2d | ~700 | Governance validators (all 56) | PRE |
| STEP 2d3 | ~720 | TC-GUARD-001 enforcement | PRE |
| STEP 3 | ~746 | **GRADING** (deterministic + LLM) | GRADE |
| STEP 3c | ~1076 | Overclaim detector (ACTIVE, hard stop) | POST |
| STEP 2e | ~892 | Lane enforcement validator | **POST** |
| ... | ... | Continuation signal, next-sprint generation | POST |

### RC-3 CONFIRMED: Lane Enforcement Is Post-Hoc
Lane enforcement runs at line 892, AFTER grading at line 746. This means:
- A mixed-lane sprint executes fully (code changes, tests, evidence)
- Grading scores the work items
- ONLY THEN does lane enforcement detect the violation
- By that point, the work is done — enforcement is retroactive, not preventive

### Cost of Post-Hoc Enforcement
A PRODUCT sprint can execute ALL its work items before Step 2e catches a MACHINERY scope violation. The entire sprint's compute and code changes are wasted.

## 2. Overclaim Detector Status
- **Location:** STEP 3c, line 1076
- **Status:** ACTIVE — checked after grading
- **Behavior:** If overclaimed items detected → added to hard_stops → autonomous continuation blocked
- **Assessment:** Working correctly as a post-grade safety net

## 3. Failure Memory Escalation Gap (RC-8)

### FM-0013 — The Worst Offender
| Field | Value |
|-------|-------|
| failure_id | FM-0013 |
| occurrence_count | 283 |
| escalated | true |
| resolved | false |
| description | Recurring validator failure |

### failure_memory.py — ESCALATION_THRESHOLD = 3
- **Location:** tools/supervisor/failure_memory.py
- **record_failure():** Increments occurrence_count, sets escalated=true at threshold
- **Threshold:** 3 (very low — FM-0013 hit 283 without resolution)
- **Gap:** No action handler beyond setting `escalated: true`
- **What happens at 283?** Same as at 3 — the flag is set, but nobody acts on it
- **No hard_stop injection:** Even at 283 occurrences, the failure never blocks continuation

### Escalation Design Needed
- At 10: severity=high
- At 50: severity=critical
- At 100: requires_root_cause_fix=true, inject into continuation hard_stops
- See TC-MACH-FM-001 for implementation

## 4. Preventive Lane Guard Design Summary
- **Injection point:** Step 1b (after declaration loading, BEFORE evidence inspection)
- **Function:** check_lane_conflict(declaration)
- **Logic:** Read declared_scope.lane; if MACHINERY AND changed_files under src/ → exit 3
- **Grace period:** .supervisor/policies.yaml lanes_grace_period_until field
- **Full design:** See lane-guard-design.md
