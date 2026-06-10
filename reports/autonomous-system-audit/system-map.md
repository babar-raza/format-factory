# Autonomous System Map
# Sprint: FORMAT-FACTORY-FULL-AUTONOMOUS-SYSTEM-AUDIT-AND-REPAIR-001
# Date: 2026-06-05

## Overview

16 layers identified. 5 layers can produce false terminal states.
2 layers (adoption compliance, anti-skip) have confirmed active defects.
1 layer (host runner) has unproven live invocation.

## Dataflow Summary

```
User/Skill → Mainstream (1) → src/ + tests/ + examples/
                  ↓
Skills (2) ─────→ transcript + skill_id validation
Acceleration (3) → ai_draft suggestions [advisory]
Spec Authority (4) → format requirements [authoritative]
Req/Cap Authority (5) → capability requirements [authoritative]
                  ↓
Evidence Declaration (12) → evidence-declaration.yaml
                  ↓
Supervisor Review (6) → grades + contradictions
                  ↓
Anti-Skip (13) → violation check [DEFECT: false missing_raw_logs]
Adoption Compliance (14) → compliance check [DEFECT: passes with 0 transcripts]
                  ↓
Next-Sprint Generator (8) → next-sprint.md [CAN produce false blockers]
Stop Reason Adjudicator (7) → adjudicates signals
                  ↓
POC Readiness Gate (15) → proof-backed check [gap: no proof graph projection]
                  ↓
Autonomous Train Executor (10) → execution state classification
                  ↓
Autonomous Host Runner (11) → CLI detection + invocation [gap: live not proven]
                  ↓
Gate 11 Packet (16) → preparation is agent-owned
```

## Layers with Active Defects

| # | Layer | Defect | Severity |
|---|---|---|---|
| 14 | Adoption Compliance | 0 transcripts/0 skill_ids passes for non-exempt items | HIGH |
| 13 | Anti-Skip | declared logs in reports/ not discovered in evidence_root/ | MEDIUM |
| 13 | Anti-Skip | evidence_quality_score=0 for ACCEPTED_WITH_LIMITATIONS | HIGH |
| 15 | POC Gate | accepts ledger-only without proof graph projection | MEDIUM |
| 11 | Host Runner | live invocation not proven | MEDIUM |
| 8 | Next-Sprint | can emit human-gate wording with agent_can_execute=true | MEDIUM |
| 16 | Gate 11 Packet | preparation can be confused as terminal by weak agents | LOW |

## Valid Terminal States

Only these are valid terminal states (see autonomous-execution-contract.md):
- POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING
- TRUE_EXTERNAL_GATE (commit/push/Gate8/Gate11 execution/publication)
- UNSAFE_WORKSPACE
- RUNTIME_LIMIT_WITH_CONTINUATION_PACKET
- HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS

## Invalid Terminal States (causes false stop)

- ACCEPTED (supervisor verdict)
- ACCEPTED_WITH_REWORK
- ACCEPTED_WITH_LIMITATIONS
- Evidence package built
- Next sprint generated
- Max iterations reached (checkpoint rollover instead)
- Gate 11 preparation needed
- Commit preparation needed
- anti-skip false positive
- prompt-quality warning
- Missing optional acceleration
- Host-runner dry-run only (unless host invocation truly unavailable)
