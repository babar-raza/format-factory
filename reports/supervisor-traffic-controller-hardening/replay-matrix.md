# Replay Matrix — Hardening IV

## 10 Required Scenarios

| ID | Scenario | Routing Decision | Cross-Stream Verdict | Deterministic |
|---|---|---|---|---|
| S1 | Baseline prior state (breadth=2) | CONTINUE_WITH_LIMITATIONS | SKILLS_CONSUMABLE / ACC_CONSUMABLE | Yes |
| S2 | Skills packet present, consumed | CONTINUE_WITH_LIMITATIONS | SKILLS_CONSUMABLE_NOT_YET_CONSUMED | Yes |
| S3 | Missing Skills packet | CONTINUE_WITH_LIMITATIONS | SKILLS_CONSUMPTION_GAP | Yes |
| S4 | Missing Acceleration packet | CONTINUE_WITH_LIMITATIONS | ACCELERATION_CONSUMPTION_GAP | Yes |
| S5 | Both Skills+Acceleration missing | CONTINUE_WITH_LIMITATIONS | CROSS_STREAM_GAPS (5 flags) | Yes |
| S6 | Malformed Skills packet (parse error) | CONTINUE_WITH_LIMITATIONS | SKILLS_CONSUMPTION_GAP | Yes |
| S7 | Stale Acceleration sprint_id | CONTINUE_WITH_LIMITATIONS | ACCELERATION_CONSUMABLE_PARTIAL | Yes |
| S8 | Empty product gaps | CONTINUE_WITH_LIMITATIONS | n/a | Yes |
| S9 | Weak breadth (breadth=1) | CONTINUE_WITH_LIMITATIONS | n/a | Yes |
| S10 | Clean-pass synthetic (breadth=3+, all evidence) | (eligible for cleaner) | n/a | Yes |

## Determinism Result

All 10 scenarios: **DETERMINISTIC** — same input → same output (excluding timestamps).

## Safe Fallback Confirmed

Failing scenarios (S5, S6) produce safe fallback (`CONTINUE_WITH_LIMITATIONS`) instead of crash.
No unhandled exceptions in any scenario.
